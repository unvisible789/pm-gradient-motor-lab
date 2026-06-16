param(
    [string[]]$Variants = @(
        "asym_a_lead1p5_trail142",
        "asym_c_lead2p5_trail138",
        "asym_d_lead3p0_trail137"
    ),
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

foreach ($name in $Variants) {
    $config = "field_sim/femm/variants/$name.json"
    if ($name -notmatch "^asym_([a-d])_") {
        throw "Variant name must start with asym_<letter>_: $name"
    }
    $letter = $Matches[1]
    $output = "data/field_sim/femm_asym_${letter}_period45_step1.csv"

    Write-Output "=== Running $name -> $output ==="
    python validation/prepare_femm_geometry_variant.py --label $name --config-json $config
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output `
        -StepDeg $StepDeg `
        -MinAngleDeg $MinAngleDeg `
        -MaxAngleDeg $MaxAngleDeg `
        -RebuildGeometry
}

Write-Output "ASYM family sweeps complete."