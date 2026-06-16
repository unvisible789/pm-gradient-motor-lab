param(
    [Parameter(Mandatory = $true)][double]$OffsetDeg,
    [string]$BaseConfig = "field_sim/femm/variants/asym_b_lead2p0_trail140.json"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

$tag = if ($OffsetDeg -lt 0) { "neg{0}" -f [math]::Abs([int]$OffsetDeg) } elseif ($OffsetDeg -gt 0) { "pos{0}" -f [int]$OffsetDeg } else { "zero" }
$label = "ASYM_B_EML_{0}" -f $tag
$output = "data/field_sim/femm_asym_b_eml_offset_{0}_period45_step1.csv" -f $tag

Write-Output ("=== ASYM_B EML offset {0} deg -> {1} ===" -f $OffsetDeg, $output)
python validation/prepare_femm_geometry_variant.py --label $label --config-json $BaseConfig --eml-angular-offset-deg $OffsetDeg
powershell -ExecutionPolicy Bypass -File .\validation\run_femm_sweep.ps1 -OutputCsv $output -StepDeg 1 -MinAngleDeg 0 -MaxAngleDeg 45 -RebuildGeometry