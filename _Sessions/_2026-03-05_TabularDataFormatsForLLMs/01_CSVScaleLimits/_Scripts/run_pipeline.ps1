<#
.SYNOPSIS
  Full test-to-documentation pipeline for CSV scale limit experiments.

.DESCRIPTION
  Runs the complete pipeline:
    1. (Optional) Execute scale limit test for a model configuration
    2. Aggregate all results into all_results.json + all_results.md
    3. Update INFO_01 data sections via AUTO markers

.PARAMETER ModelId
  Model identifier for the test (e.g., "gpt-5-mini"). Required for step 1.

.PARAMETER Method
  Reasoning method (e.g., "reasoning_effort", "thinking", "adaptive_thinking").

.PARAMETER Effort
  Reasoning effort level: low, medium, high.

.PARAMETER SkipTest
  Skip the test execution (step 1), only aggregate and update docs.

.EXAMPLE
  # Run test + aggregate + update docs
  .\run_pipeline.ps1 -ModelId "gpt-5-mini" -Method "reasoning_effort" -Effort "medium"

  # Only aggregate existing results and update docs (no new test)
  .\run_pipeline.ps1 -SkipTest
#>

param(
  [string]$ModelId,
  [string]$Method = "reasoning_effort",
  [string]$Effort = "medium",
  [switch]$SkipTest,
  [int]$MaxRows = 16384,
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
  if (-not $ModelId) {
    Write-Host "ERROR: -ModelId required when running a test. Use -SkipTest to skip." -ForegroundColor Red
    exit 1
  }

  Write-Host "`n[Step 1/3] Running scale limit test..." -ForegroundColor Yellow
  Write-Host "  Model: $ModelId"
  Write-Host "  Method: $Method"
  Write-Host "  Effort: $Effort"
  Write-Host "  Max rows: $MaxRows"
  Write-Host "  Verify runs: $VerifyRuns"

  $testArgs = @(
    (Join-Path $ScriptDir "04_batch_scale_test.py"),
    "--model", $ModelId,
    "--method", $Method,
    "--effort", $Effort,
    "--max-rows", $MaxRows,
    "--verify-runs", $VerifyRuns,
    "--test-path", $TestRoot
  )

  python @testArgs
  if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Test execution failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
  }
  Write-Host "[Step 1/3] Test complete." -ForegroundColor Green
} else {
  Write-Host "`n[Step 1/3] Skipped (--SkipTest)" -ForegroundColor DarkGray
}

# -- Step 2+3: Aggregate results + update INFO_01 --
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
