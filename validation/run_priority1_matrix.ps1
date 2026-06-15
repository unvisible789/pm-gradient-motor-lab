param(
    [double]$StepDeg = 1,
    [double]$MinAngleDeg = 0,
    [double]$MaxAngleDeg = 45,
    [string]$VariantDirectory = "field_sim/femm/variants",
    [string]$OutputDirectory = "data/field_sim"
)

$ErrorActionPreference = "Stop"

$variants = Get-ChildItem -Path $VariantDirectory -Filter "*.json" | Sort-Object Name
if ($variants.Count -eq 0) {
    throw "No variants found in $VariantDirectory. Run python validation\write_priority1_variants.py first."
}

foreach ($variant in $variants) {
    $name = [IO.Path]::GetFileNameWithoutExtension($variant.Name)
    $output = Join-Path $OutputDirectory ("femm_p1_{0}_step{1}.csv" -f $name, ($StepDeg.ToString() -replace "\.", "p"))
    Write-Output ("=== Priority 1 variant: {0} ===" -f $name)
    python validation\prepare_femm_geometry_variant.py --label $name --config-json $variant.FullName
    powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 `
        -OutputCsv $output `
        -StepDeg $StepDeg `
        -MinAngleDeg $MinAngleDeg `
        -MaxAngleDeg $MaxAngleDeg `
        -RebuildGeometry
}

Write-Output "Priority 1 matrix complete."
