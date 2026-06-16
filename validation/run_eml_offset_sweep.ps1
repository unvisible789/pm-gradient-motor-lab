param(
    [double[]]$OffsetsDeg = @(-12, -6, 6, 12),
    [string]$BaseConfig = "field_sim/femm/variants/asym_b_lead2p0_trail140.json",
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

foreach ($offset in $OffsetsDeg) {
    $tag = if ($offset -lt 0) { "neg{0}" -f [math]::Abs([int]$offset) } elseif ($offset -gt 0) { "pos{0}" -f [int]$offset } else { "zero" }
    $label = "ASYM_B_EML_{0}" -f $tag
    $output = "data/field_sim/femm_asym_b_eml_offset_{0}_period45_step1.csv" -f $tag

    Write-Output ("=== ASYM_B EML offset {0} deg -> {1} ===" -f $offset, $output)
    python validation/prepare_femm_geometry_variant.py `
        --label $label `
        --config-json $BaseConfig `
        --eml-angular-offset-deg $offset
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output `
        -StepDeg $StepDeg `
        -MinAngleDeg $MinAngleDeg `
        -MaxAngleDeg $MaxAngleDeg `
        -RebuildGeometry
}

Write-Output "EML offset sweep complete."