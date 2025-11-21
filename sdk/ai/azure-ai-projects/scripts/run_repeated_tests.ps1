# run_tests_loop.ps1

$iterations = 5
$delayMinutes = 30

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "=== Starting test run $i of $iterations ===" -ForegroundColor Cyan

    # Run your test command
    uv run python .\scripts\run_multi_project_tests.py --config .\test_config\full_run_test_config.json

    if ($i -lt $iterations) {
        Write-Host "=== Waiting $delayMinutes minutes before next run... ===" -ForegroundColor Yellow
        Start-Sleep -Seconds ($delayMinutes * 60)
    }
}

Write-Host "=== All test runs completed ===" -ForegroundColor Green
