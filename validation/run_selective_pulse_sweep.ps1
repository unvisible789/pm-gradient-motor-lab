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
from validation.pulse_control import load_pulse_windows, pulse_current_levels_for_geometry
root = Path('.')
config = json.loads((root / '$VariantConfig').read_text(encoding='utf-8'))
assist, lockout = load_pulse_windows(root / '$PulseStrategy')
levels = pulse_current_levels_for_geometry(config)
print(json.dumps({
    'assist_windows': assist,
    'lockout_windows': lockout,
    'current_levels_a': levels,
    'eml_count': int(config['eml_unit_count']),
    'eml_offset_deg': float(config['eml_angular_offset_deg']),
    'period_deg': 45.0,
}))
"@
$payload = $levelsJson | ConvertFrom-Json
$assistWindows = @($payload.assist_windows)
$currentLevels = $payload.current_levels_a
$emlCount = [int]$payload.eml_count
$emlOffset = [double]$payload.eml_offset_deg
$periodDeg = [double]$payload.period_deg

$pulseCurrentA = 0.0
if ($PulseLevel -ne "coiloff") {
    $pulseCurrentA = [double]$currentLevels.$PulseLevel
}
Write-Output ("Pulse level={0} current_a={1}" -f $PulseLevel, $pulseCurrentA)

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
"angle_deg,torque_nm,coil_current_a,active_eml,pulse_on" | Set-Content -Path $outputPath -Encoding ASCII

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
        Invoke-Femm $femm ('mi_modifycircprop("EML' + $circuit + '","i",0)') | Out-Null
    }

    $pulseOn = 0
    $activeEml = Get-ActiveEmlIndex $angle
    $appliedCurrent = 0.0
    if ($pulseCurrentA -gt 0 -and (Test-InAssistWindow $angle)) {
        Invoke-Femm $femm ('mi_modifycircprop("EML' + $activeEml + '","i",' + $pulseCurrentA.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + ')') | Out-Null
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