param(
    [string]$VariantConfig = "field_sim/femm/variants/gap_159p0.json",
    [string]$PulseStrategy = "field_sim/femm/pulse_strategy.gap159_eml12.json",
    [string]$OutputCsv = "data/field_sim/femm_pulse_gap159_coiloff_period45_step1.csv",
    [ValidateSet("coiloff", "low", "medium", "high")]
    [string]$PulseLevel = "coiloff",
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45,
    [switch]$RebuildGeometry
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
Write-Warning "Legacy quasistatic positive-window assist screen: one-turn FEMM surrogate, not a timed-release dynamic model or energy-generation test. Active 45-degree state periodicity is unverified."

function Convert-ToFemPath([string]$PathValue) {
    return ($PathValue -replace "\\", "/")
}

function Invoke-Femm([object]$Femm, [string]$Command) {
    $result = $Femm.mlab2femm($Command)
    if ($result -match "^error:" -or $result -match "run-time error") {
        throw "FEMM command failed: $Command`n$result"
    }
    return $result
}

$label = "pulse_gap159_$PulseLevel"
Write-Output "=== Selective pulse sweep: $label -> $OutputCsv ==="

python validation/prepare_femm_geometry_variant.py --label $label --config-json $VariantConfig
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$levelsJson = python -c @"
import json
from pathlib import Path
from validation.pulse_control import load_pulse_windows, eml_coil_area_mm2, ampere_turns_from_density_ma_per_mm2, PULSE_CURRENT_LEVELS
root = Path('.')
config = json.loads((root / '$VariantConfig').read_text(encoding='utf-8'))
assist, lockout = load_pulse_windows(root / '$PulseStrategy')
area = eml_coil_area_mm2(stator_inner_radius_mm=float(config['stator_inner_radius_mm']), stator_outer_radius_mm=float(config['stator_outer_radius_mm']), eml_arc_deg=float(config['eml_arc_deg']))
# The generator assigns one turn to each surrogate FEMM region. J*area gives
# equivalent ampere-turns, NOT the physical APW winding current.
levels = {name: ampere_turns_from_density_ma_per_mm2(density, area) for name, density in PULSE_CURRENT_LEVELS.items()}
print(json.dumps({
    'assist_windows': assist,
    'lockout_windows': lockout,
    'single_turn_equivalent_current_a': levels,
    'eml_count': int(config['eml_unit_count']),
    'eml_offset_deg': float(config['eml_angular_offset_deg']),
    'period_deg': 45.0,
}))
"@
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$payload = $levelsJson | ConvertFrom-Json
$assistWindows = @($payload.assist_windows)
$currentLevels = $payload.single_turn_equivalent_current_a
$emlCount = [int]$payload.eml_count
$emlOffset = [double]$payload.eml_offset_deg
$periodDeg = [double]$payload.period_deg

$pulseCurrentA = 0.0
if ($PulseLevel -ne "coiloff") {
    $pulseCurrentA = [double]$currentLevels.$PulseLevel
}
Write-Output ("Pulse level={0} FEMM one-turn equivalent current_a={1}; physical winding current unknown" -f $PulseLevel, $pulseCurrentA)

function Test-InAssistWindow([double]$AngleDeg) {
    $local = $AngleDeg % $periodDeg
    if ($local -lt 0) { $local += $periodDeg }
    foreach ($window in $assistWindows) {
        $start = [double]$window.start_deg
        $end = [double]$window.end_deg
        if ($local -ge $start -and $local -le $end) { return $true }
    }
    return $false
}

function Get-ActiveEmlIndex([double]$AngleDeg) {
    $local = $AngleDeg % $periodDeg
    if ($local -lt 0) { $local += $periodDeg }
    $index = [int][Math]::Floor(($local + $periodDeg / 2.0 - $emlOffset) / $periodDeg)
    return (($index % $emlCount) + $emlCount) % $emlCount
}

$root = Convert-ToFemPath (Get-Location).Path
$baseFem = Convert-ToFemPath "geometry/pm_gradient_motor_base.fem"
$buildScript = Convert-ToFemPath (Join-Path (Get-Location) "field_sim/femm/build_pm_gradient_motor.lua")
$outputPath = Join-Path (Get-Location) $OutputCsv
$outputDir = Split-Path -Parent $outputPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$femm = New-Object -ComObject femm.ActiveFEMM
Invoke-Femm $femm ('setcurrentdirectory("' + $root + '")') | Out-Null

if ($RebuildGeometry) {
    Invoke-Femm $femm ('dofile("' + $buildScript + '")') | Out-Null
}

Invoke-Femm $femm ('open("' + $baseFem + '")') | Out-Null
"angle_deg,torque_nm,femm_single_turn_current_a,active_eml,pulse_on" | Set-Content -Path $outputPath -Encoding ASCII

$previousAngle = $MinAngleDeg
$start = Get-Date
$index = 0
$count = [int][Math]::Floor(($MaxAngleDeg - $MinAngleDeg) / $StepDeg)

for ($i = 0; $i -le $count; $i++) {
    $angle = $MinAngleDeg + $i * $StepDeg
    $delta = $angle - $previousAngle
    if ([Math]::Abs($delta) -gt 1e-12) {
        Invoke-Femm $femm 'mi_seteditmode("group")' | Out-Null
        Invoke-Femm $femm 'mi_selectgroup(2)' | Out-Null
        Invoke-Femm $femm ('mi_moverotate(0,0,' + $delta.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + ')') | Out-Null
        Invoke-Femm $femm 'mi_clearselected()' | Out-Null
    }

    for ($circuit = 0; $circuit -lt $emlCount; $circuit++) {
        Invoke-Femm $femm ('mi_modifycircprop("EML' + $circuit + '",1,0)') | Out-Null
    }

    $pulseOn = 0
    $activeEml = Get-ActiveEmlIndex $angle
    $appliedCurrent = 0.0
    if ($pulseCurrentA -gt 0 -and (Test-InAssistWindow $angle)) {
        Invoke-Femm $femm ('mi_modifycircprop("EML' + $activeEml + '",1,' + $pulseCurrentA.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + ')') | Out-Null
        $pulseOn = 1
        $appliedCurrent = $pulseCurrentA
    }

    Invoke-Femm $femm 'mi_analyze(1)' | Out-Null
    Invoke-Femm $femm 'mi_loadsolution()' | Out-Null
    Invoke-Femm $femm 'mo_groupselectblock(2)' | Out-Null
    $torqueRaw = Invoke-Femm $femm 'mo_blockintegral(22)'
    Invoke-Femm $femm 'mo_clearblock()' | Out-Null
    Invoke-Femm $femm 'mo_close()' | Out-Null

    $torque = ($torqueRaw -replace "[\[\]]", "").Trim()
    ($angle.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + "," + $torque + "," +
        $appliedCurrent.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + "," +
        $activeEml + "," + $pulseOn) | Add-Content -Path $outputPath -Encoding ASCII
    $previousAngle = $angle
    $index++

    if (($index -eq 1) -or ($index % 15 -eq 0) -or ($i -eq $count)) {
        $elapsed = [Math]::Round(((Get-Date) - $start).TotalSeconds, 1)
        Write-Output ("progress angle={0} pulse_on={1} current_a={2} points={3} elapsed_seconds={4}" -f $angle, $pulseOn, $appliedCurrent, $index, $elapsed)
    }
}

$elapsedTotal = [Math]::Round(((Get-Date) - $start).TotalSeconds, 1)
Write-Output ("completed output={0} points={1} elapsed_seconds={2}" -f $OutputCsv, $index, $elapsedTotal)
