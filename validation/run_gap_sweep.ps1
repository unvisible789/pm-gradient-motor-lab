param(
    [string[]]$Tags = @("158p5", "159p5", "160p0", "161p0"),
    [double]$StepDeg = 1
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

# Reuse existing 159.0 result if present.
$src159 = "data/field_sim/femm_opt_opt_stator_inner_gap_plus1mm_period45_step1.csv"
$dst159 = "data/field_sim/femm_opt_gap_159p0_period45_step1.csv"
if ((Test-Path $src159) -and -not (Test-Path $dst159)) {
    Copy-Item $src159 $dst159
    Write-Output "Reused $src159 -> $dst159"
}

foreach ($tag in $Tags) {
    $name = "gap_$tag"
    $config = "field_sim/femm/variants/$name.json"
    $output = "data/field_sim/femm_opt_gap_${tag}_period45_step1.csv"
    if (Test-Path $output) {
        $lines = (Get-Content $output | Measure-Object -Line).Lines
        if ($lines -ge 46) {
            Write-Output "Skipping complete $output"
            continue
        }
    }
    Write-Output "=== $name -> $output ==="
    python validation/prepare_femm_geometry_variant.py --label $name --config-json $config
    if ($LASTEXITCODE -ne 0) { continue }
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output -StepDeg $StepDeg -MinAngleDeg 0 -MaxAngleDeg 45 -RebuildGeometry
}
Write-Output "Gap sweep complete."