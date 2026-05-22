<#
.SYNOPSIS
  Full test-to-documentation pipeline for format comparison experiments.

.DESCRIPTION
  Runs the complete pipeline:
    1. (Optional) Execute scale limit test for a model + format configuration
    2. Aggregate all results into all_results.json + all_results.md, update INFO_01
    3. Generate findings from results, update INFO_02
    4. Verify AUTO markers

.PARAMETER Model
  Model identifier (e.g., "gpt-5-mini").

.PARAMETER Format
  Data format to test (e.g., "json", "yaml", "xml").

.PARAMETER ReasoningEffort
  Reasoning effort level: low, medium, high. Default: medium.

.PARAMETER SkipTest
  Skip the test execution (step 1), only aggregate and update docs.

.PARAMETER InitialRows
  Initial row count for binary search. Default: 500.

.EXAMPLE
  # Run test + aggregate + update docs
  .\run_pipeline.ps1 -Model "gpt-5-mini" -Format "json" -ReasoningEffort "medium"

  # Only aggregate existing results and update docs (no new test)
  .\run_pipeline.ps1 -SkipTest
#>

param(
  [string]$Model,
  [string]$Format,
  [ValidateSet("low", "medium", "high")]
  [string]$ReasoningEffort = "medium",
  [switch]$SkipTest,
  [int]$InitialRows = 500
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$TestRoot = Split-Path $ScriptDir -Parent
$InfoFile = Join-Path $TestRoot "_INFO_01_FormatComparison-TestResults.md"
$FindingsFile = Join-Path $TestRoot "_INFO_02_FormatComparison-Findings.md"
$ResultsJson = Join-Path $TestRoot "all_results.json"
$OverridesFile = Join-Path $ScriptDir "overrides.json"

Write-Host "`n==== Format Comparison Pipeline ====" -ForegroundColor Cyan
Write-Host "Test root: $TestRoot"
Write-Host "Script dir: $ScriptDir"

# -- Step 1: Run test (optional) --
if (-not $SkipTest) {
  if (-not $Model -or -not $Format) {
    Write-Host "ERROR: -Model and -Format required when running a test. Use -SkipTest to skip." -ForegroundColor Red
    exit 1
  }

  Write-Host "`n[Step 1/3] Running scale limit test..." -ForegroundColor Yellow
  Write-Host "  Model: $Model"
  Write-Host "  Format: $Format"
  Write-Host "  Reasoning effort: $ReasoningEffort"
  Write-Host "  Initial rows: $InitialRows"

  $testArgs = @(
    (Join-Path $ScriptDir "03_find_scale_limit.py"),
    "--model", $Model,
    "--format", $Format,
    "--reasoning-effort", $ReasoningEffort,
    "--initial-rows", $InitialRows,
    "--test-path", $TestRoot
  )

  python @testArgs
  if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Test execution failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
  }
  Write-Host "[Step 1/4] Test complete." -ForegroundColor Green
} else {
  Write-Host "`n[Step 1/4] Skipped (-SkipTest)" -ForegroundColor DarkGray
}

# -- Step 2: Aggregate results + update INFO_01 --
Write-Host "`n[Step 2/4] Aggregating results..." -ForegroundColor Yellow

$aggArgs = @(
  (Join-Path $ScriptDir "06_aggregate_results.py"),
  "--test-path", $TestRoot,
  "--update-file", $InfoFile
)

if (Test-Path $OverridesFile) {
  $aggArgs += @("--overrides", $OverridesFile)
}

python @aggArgs
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Aggregation failed (exit code $LASTEXITCODE)" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "[Step 2/4] Aggregation complete." -ForegroundColor Green

# -- Step 3: Generate findings + update INFO_02 --
Write-Host "`n[Step 3/4] Generating findings..." -ForegroundColor Yellow

$findArgs = @(
  (Join-Path $ScriptDir "08_generate_findings.py"),
  "--results-file", $ResultsJson,
  "--update-file", $FindingsFile
)

python @findArgs
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Findings generation failed (exit code $LASTEXITCODE)" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "[Step 3/4] Findings complete." -ForegroundColor Green

# -- Step 4: Verify --
Write-Host "`n[Step 4/4] Verifying..." -ForegroundColor Yellow
$info1Markers = (Select-String -Path $InfoFile -Pattern "AUTO:.*:start" -AllMatches).Count
$info2Markers = (Select-String -Path $FindingsFile -Pattern "AUTO:.*:start" -AllMatches).Count
Write-Host "  AUTO markers in INFO_01: $info1Markers sections"
Write-Host "  AUTO markers in INFO_02: $info2Markers sections"
Write-Host "  JSON: $ResultsJson"
Write-Host "  Findings: $(Join-Path $TestRoot 'all_findings.md')"
Write-Host "[Step 4/4] Done." -ForegroundColor Green

Write-Host "`n==== Pipeline Complete ====" -ForegroundColor Cyan
Write-Host "Next: Review changes in INFO_01 + INFO_02, then commit."
