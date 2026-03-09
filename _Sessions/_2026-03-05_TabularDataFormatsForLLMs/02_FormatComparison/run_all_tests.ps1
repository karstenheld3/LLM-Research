# Run all 35 format comparison tests in parallel using PowerShell jobs
# Usage: .\run_all_tests.ps1

$ScriptDir = "$PSScriptRoot\_Scripts"
$TestPath = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Format Comparison Tests - 35 Parallel" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define all test configurations
$tests = @(
    # gpt-5.2 (7 tests) - baseline 215, ~30 min each
    @{Model="gpt-5.2"; Format="csv_raw"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="kv_colon_space"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="markdown_table"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="json"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="xml"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="yaml"; Rows=215; Effort="medium"},
    @{Model="gpt-5.2"; Format="toml"; Rows=215; Effort="medium"},
    
    # claude-sonnet (7 tests) - baseline 168, ~42 min each
    @{Model="claude-sonnet-4-5-20250929"; Format="csv_raw"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="kv_colon_space"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="markdown_table"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="json"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="xml"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="yaml"; Rows=168; Effort=$null},
    @{Model="claude-sonnet-4-5-20250929"; Format="toml"; Rows=168; Effort=$null},
    
    # claude-opus (7 tests) - baseline 177, ~48 min each
    @{Model="claude-opus-4-5-20251101"; Format="csv_raw"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="kv_colon_space"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="markdown_table"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="json"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="xml"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="yaml"; Rows=177; Effort=$null},
    @{Model="claude-opus-4-5-20251101"; Format="toml"; Rows=177; Effort=$null},
    
    # gpt-5 (7 tests) - baseline 356, ~72 min each
    @{Model="gpt-5"; Format="csv_raw"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="kv_colon_space"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="markdown_table"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="json"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="xml"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="yaml"; Rows=356; Effort="low"},
    @{Model="gpt-5"; Format="toml"; Rows=356; Effort="low"},
    
    # gpt-5-mini (7 tests) - baseline 500, ~105 min each
    @{Model="gpt-5-mini"; Format="csv_raw"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="kv_colon_space"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="markdown_table"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="json"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="xml"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="yaml"; Rows=500; Effort="medium"},
    @{Model="gpt-5-mini"; Format="toml"; Rows=500; Effort="medium"}
)

Write-Host "Starting $($tests.Count) tests..." -ForegroundColor Yellow
Write-Host ""

$jobs = @()
$startTime = Get-Date

foreach ($test in $tests) {
    $model = $test.Model
    $format = $test.Format
    $rows = $test.Rows
    $effort = $test.Effort
    
    $cmd = "python `"$ScriptDir\03_find_scale_limit.py`" --test-path `"$TestPath`" --model $model --format $format --initial-rows $rows"
    if ($effort) {
        $cmd += " --reasoning-effort $effort"
    }
    
    Write-Host "  Starting: $model / $format" -ForegroundColor Gray
    
    $job = Start-Job -ScriptBlock {
        param($cmd, $scriptDir)
        Set-Location $scriptDir
        Invoke-Expression $cmd
    } -ArgumentList $cmd, $ScriptDir
    
    $jobs += @{Job=$job; Model=$model; Format=$format}
}

Write-Host ""
Write-Host "$($jobs.Count) jobs started. Waiting for completion..." -ForegroundColor Yellow
Write-Host ""

# Wait for all jobs and report results
$completed = 0
while ($jobs | Where-Object { $_.Job.State -eq 'Running' }) {
    $done = $jobs | Where-Object { $_.Job.State -eq 'Completed' -and -not $_.Reported }
    foreach ($j in $done) {
        $completed++
        $j.Reported = $true
        Write-Host "[$completed/$($jobs.Count)] DONE: $($j.Model) / $($j.Format)" -ForegroundColor Green
    }
    
    $failed = $jobs | Where-Object { $_.Job.State -eq 'Failed' -and -not $_.Reported }
    foreach ($j in $failed) {
        $completed++
        $j.Reported = $true
        Write-Host "[$completed/$($jobs.Count)] FAIL: $($j.Model) / $($j.Format)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 10
}

# Final report
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All tests complete!" -ForegroundColor Cyan
Write-Host "  Duration: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Cleanup jobs
$jobs | ForEach-Object { Remove-Job $_.Job -Force }
