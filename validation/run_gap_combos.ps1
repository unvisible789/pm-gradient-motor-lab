param([string[]]$Names = @("combo_gap159_arc20", "combo_gap159_arc10", "combo_gap159_halbach15"))

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

foreach ($name in $Names) {
    $config = "field_sim/femm/variants/$name.json"
    $output = "data/field_sim/femm_opt_${name}_period45_step1.csv"
    Write-Output "=== $name -> $output ==="
    python validation/prepare_femm_geometry_variant.py --label $name --config-json $config
    if ($LASTEXITCODE -ne 0) { continue }
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output -StepDeg 1 -MinAngleDeg 0 -MaxAngleDeg 45 -RebuildGeometry
}
Write-Output "Gap combo runs complete."