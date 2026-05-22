<#
.SYNOPSIS
  Full test-to-documentation pipeline for format comparison experiments.

.DESCRIPTION
  Runs the complete pipeline:
    1. (Optional) Execute scale limit test for a model + format configuration
    2. Aggregate all results into all_results.json + all_results.md
    3. Update AUTO markers in INFO_01

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
  Write-Host "[Step 1/3] Test complete." -ForegroundColor Green
} else {
  Write-Host "`n[Step 1/3] Skipped (-SkipTest)" -ForegroundColor DarkGray
}

# -- Step 2: Aggregate results + update INFO_01 --
Write-Host "`n[Step 2/3] Aggregating results..." -ForegroundColor Yellow

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
Write-Host "[Step 2/3] Aggregation complete." -ForegroundColor Green

# -- Step 3: Verify --
Write-Host "`n[Step 3/3] Verifying..." -ForegroundColor Yellow
$markerCount = (Select-String -Path $InfoFile -Pattern "AUTO:.*:start" -AllMatches).Count
Write-Host "  AUTO markers in INFO_01: $markerCount sections"
Write-Host "  JSON: $(Join-Path $TestRoot 'all_results.json')"
Write-Host "  Markdown: $(Join-Path $TestRoot 'all_results.md')"
Write-Host "[Step 3/3] Done." -ForegroundColor Green

Write-Host "`n==== Pipeline Complete ====" -ForegroundColor Cyan
Write-Host "Next: Review changes in INFO_01, then commit."
