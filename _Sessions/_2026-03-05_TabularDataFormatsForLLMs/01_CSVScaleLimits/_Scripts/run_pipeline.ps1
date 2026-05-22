<#
.SYNOPSIS
  Full test-to-documentation pipeline for CSV scale limit experiments.

.DESCRIPTION
  Runs the complete pipeline:
    1. (Optional) Execute scale limit test for a model configuration
    2. Aggregate all results into all_results.json + all_results.md
    3. Deep analysis of per-iteration data into deep_analysis.json + deep_analysis.md
    4. Verify AUTO markers updated in INFO_01

.PARAMETER Model
  Model identifier (e.g., "gpt-5-mini"). Maps to execution.model in test-config.json.

.PARAMETER ReasoningEffort
  Reasoning effort level: low, medium, high. Maps to execution.reasoning_effort in test-config.json.

.PARAMETER SkipTest
  Skip the test execution (step 1), only aggregate and update docs.

.PARAMETER InitialRows
  Initial row count for binary search. Maps to --initial-rows in 03_find_scale_limit.py. Default: 500.

.PARAMETER VerifyRuns
  Number of verification runs at boundary. Maps to execution.number_of_runs. Default: 3.

.EXAMPLE
  # Run test + aggregate + update docs
  .\run_pipeline.ps1 -Model "gpt-5-mini" -ReasoningEffort "medium"

  # Only aggregate existing results and update docs (no new test)
  .\run_pipeline.ps1 -SkipTest
#>

param(
  [string]$Model,
  [ValidateSet("low", "medium", "high")]
  [string]$ReasoningEffort = "medium",
  [switch]$SkipTest,
  [int]$InitialRows = 500,
  [int]$VerifyRuns = 3
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$TestRoot = Split-Path $ScriptDir -Parent
$InfoFile = Join-Path $TestRoot "_INFO_01_CSVScaleLimits-TestResults.md"
$OverridesFile = Join-Path $ScriptDir "overrides.json"

Write-Host "`n==== CSV Scale Limit Pipeline ====" -ForegroundColor Cyan
Write-Host "Test root: $TestRoot"
Write-Host "Script dir: $ScriptDir"

# -- Step 1: Run test (optional) --
if (-not $SkipTest) {
  if (-not $Model) {
    Write-Host "ERROR: -Model required when running a test. Use -SkipTest to skip." -ForegroundColor Red
    exit 1
  }

  Write-Host "`n[Step 1/4] Running scale limit test..." -ForegroundColor Yellow
  Write-Host "  Model: $Model"
  Write-Host "  Reasoning effort: $ReasoningEffort"
  Write-Host "  Initial rows: $InitialRows"
  Write-Host "  Verify runs: $VerifyRuns"

  $testArgs = @(
    (Join-Path $ScriptDir "03_find_scale_limit.py"),
    "--model", $Model,
    "--reasoning-effort", $ReasoningEffort,
    "--initial-rows", $InitialRows,
    "--verify-runs", $VerifyRuns,
    "--test-path", $TestRoot
  )

  python @testArgs
  if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Test execution failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
  }
  Write-Host "[Step 1/4] Test complete." -ForegroundColor Green
} else {
  Write-Host "`n[Step 1/4] Skipped (--SkipTest)" -ForegroundColor DarkGray
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

# -- Step 3: Deep analysis + update INFO_01 section 9 --
Write-Host "`n[Step 3/4] Deep analysis (per-iteration data)..." -ForegroundColor Yellow

$deepArgs = @(
  (Join-Path $ScriptDir "07_deep_analysis.py"),
  "--test-path", $TestRoot,
  "--update-file", $InfoFile
)

python @deepArgs
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: Deep analysis failed (exit code $LASTEXITCODE)" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "[Step 3/4] Deep analysis complete." -ForegroundColor Green

# -- Step 4: Verify --
Write-Host "`n[Step 4/4] Verifying..." -ForegroundColor Yellow
$markerCount = (Select-String -Path $InfoFile -Pattern "AUTO:.*:start" -AllMatches).Count
Write-Host "  AUTO markers in INFO_01: $markerCount sections"
Write-Host "  JSON: $(Join-Path $TestRoot 'all_results.json')"
Write-Host "  Deep: $(Join-Path $TestRoot 'deep_analysis.json')"
Write-Host "[Step 4/4] Done." -ForegroundColor Green

Write-Host "`n==== Pipeline Complete ====" -ForegroundColor Cyan
Write-Host "Next: Review changes in INFO_01, then commit."
