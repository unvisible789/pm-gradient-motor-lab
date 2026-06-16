param(
    [double]$StepDeg = 1
)

$ErrorActionPreference = "Stop"

$runs = @(
    @{ Level = "coiloff"; Output = "data/field_sim/femm_pulse_gap159_coiloff_period45_step1.csv" },
    @{ Level = "low"; Output = "data/field_sim/femm_pulse_gap159_low_period45_step1.csv" },
    @{ Level = "medium"; Output = "data/field_sim/femm_pulse_gap159_medium_period45_step1.csv" },
    @{ Level = "high"; Output = "data/field_sim/femm_pulse_gap159_high_period45_step1.csv" }
)

$rebuild = $true
foreach ($run in $runs) {
    if (Test-Path $run.Output) {
        $lines = (Get-Content $run.Output | Measure-Object -Line).Lines
        if ($lines -ge 46) {
            Write-Output "Skipping complete $($run.Output)"
            continue
        }
    }
    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", ".\validation\run_selective_pulse_sweep.ps1",
        "-PulseLevel", $run.Level,
        "-OutputCsv", $run.Output,
        "-StepDeg", $StepDeg
    )
    if ($rebuild) {
        $args += "-RebuildGeometry"
        $rebuild = $false
    }
    & powershell @args
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed $($run.Level) pulse sweep"
        exit $LASTEXITCODE
    }
}

Write-Output "Pulse assist matrix complete."