# Load environment variables from .env file
# Usage: . .\load-env.ps1

$envFile = Join-Path $PSScriptRoot "..\..\..\..\.env"

if (Test-Path $envFile) {
    Write-Host "Loading environment variables from .env file..." -ForegroundColor Green
    
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  Set $name" -ForegroundColor Gray
        }
    }
    
    Write-Host "`nEnvironment variables loaded successfully!" -ForegroundColor Green
} else {
    Write-Host ".env file not found at $envFile" -ForegroundColor Yellow
}
