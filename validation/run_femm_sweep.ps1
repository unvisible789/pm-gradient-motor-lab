param(
    [string]$BaseFemFile = "geometry/pm_gradient_motor_base.fem",
    [string]$BuildLua = "field_sim/femm/build_pm_gradient_motor.lua",
    [string]$OutputCsv = "data/field_sim/femm_torque_angle.csv",
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 360,
    [double]$StepDeg = 2,
    [int]$RotorGroup = 2,
    [switch]$RebuildGeometry,
    [switch]$Reverse
)

$ErrorActionPreference = "Stop"

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

$root = Convert-ToFemPath (Get-Location).Path
$baseFem = Convert-ToFemPath $BaseFemFile
$buildScript = Convert-ToFemPath (Join-Path (Get-Location) $BuildLua)
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
"angle_deg,torque_nm" | Set-Content -Path $outputPath -Encoding ASCII

$startAngle = $MinAngleDeg
if ($Reverse) {
    $startAngle = $MaxAngleDeg
}
$previousAngle = $startAngle
$start = Get-Date
$index = 0
$count = [int][Math]::Floor(($MaxAngleDeg - $MinAngleDeg) / $StepDeg)

for ($i = 0; $i -le $count; $i++) {
    if ($Reverse) {
        $angle = $MaxAngleDeg - $i * $StepDeg
    } else {
        $angle = $MinAngleDeg + $i * $StepDeg
    }
    $delta = $angle - $previousAngle
    if ([Math]::Abs($delta) -gt 1e-12) {
        Invoke-Femm $femm 'mi_seteditmode("group")' | Out-Null
        Invoke-Femm $femm ('mi_selectgroup(' + $RotorGroup + ')') | Out-Null
        Invoke-Femm $femm ('mi_moverotate(0,0,' + $delta.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + ')') | Out-Null
        Invoke-Femm $femm 'mi_clearselected()' | Out-Null
    }

    Invoke-Femm $femm 'mi_analyze(1)' | Out-Null
    Invoke-Femm $femm 'mi_loadsolution()' | Out-Null
    Invoke-Femm $femm ('mo_groupselectblock(' + $RotorGroup + ')') | Out-Null
    $torqueRaw = Invoke-Femm $femm 'mo_blockintegral(22)'
    Invoke-Femm $femm 'mo_clearblock()' | Out-Null
    Invoke-Femm $femm 'mo_close()' | Out-Null

    $torque = ($torqueRaw -replace "[\[\]]", "").Trim()
    ($angle.ToString("G17", [Globalization.CultureInfo]::InvariantCulture) + "," + $torque) |
        Add-Content -Path $outputPath -Encoding ASCII
    $previousAngle = $angle
    $index++

    if (($index -eq 1) -or ($index % 15 -eq 0) -or ($i -eq $count)) {
        $elapsed = [Math]::Round(((Get-Date) - $start).TotalSeconds, 1)
        Write-Output ("progress angle={0} points={1} elapsed_seconds={2}" -f $angle, $index, $elapsed)
    }
}

$elapsedTotal = [Math]::Round(((Get-Date) - $start).TotalSeconds, 1)
Write-Output ("completed output={0} points={1} elapsed_seconds={2}" -f $OutputCsv, $index, $elapsedTotal)
