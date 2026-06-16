param(
    [string]$MatrixJson = "field_sim/femm/optimization_variant_matrix.json",
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45,
    [int[]]$Priorities = @(2, 3)
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

$matrix = Get-Content $MatrixJson -Raw | ConvertFrom-Json
foreach ($entry in $matrix.variants) {
    if ($Priorities -notcontains $entry.priority) { continue }
    $name = $entry.name
    $config = "field_sim/femm/variants/$name.json"
    $output = "data/field_sim/femm_opt_${name}_period45_step1.csv"
    Write-Output ("=== {0} (priority {1}) -> {2} ===" -f $name, $entry.priority, $output)
    python validation/prepare_femm_geometry_variant.py --label $name --config-json $config
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("FAILED prepare: {0}" -f $name)
        continue
    }
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output `
        -StepDeg $StepDeg `
        -MinAngleDeg $MinAngleDeg `
        -MaxAngleDeg $MaxAngleDeg `
        -RebuildGeometry
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("FAILED sweep: {0}" -f $name)
    }
}
Write-Output "Optimization matrix complete."