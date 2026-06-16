param(
    [string[]]$Variants = @(
        "teb_a_2deg_134_145",
        "teb_c_4deg_130_145",
        "teb_d_3deg_126_145"
    ),
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

foreach ($name in $Variants) {
    $config = "field_sim/femm/variants/$name.json"
    if ($name -notmatch "^teb_([a-d])_") {
        throw "Variant name must start with teb_<letter>_: $name"
    }
    $letter = $Matches[1]
    $output = "data/field_sim/femm_teb_${letter}_period45_step1.csv"

    Write-Output "=== Running $name -> $output ==="
    python validation/prepare_femm_geometry_variant.py --label $name --config-json $config
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output `
        -StepDeg $StepDeg `
        -MinAngleDeg $MinAngleDeg `
        -MaxAngleDeg $MaxAngleDeg `
        -RebuildGeometry
}

Write-Output "TEB family sweeps complete."