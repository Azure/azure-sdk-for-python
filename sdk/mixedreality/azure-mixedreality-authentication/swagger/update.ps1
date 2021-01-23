Push-Location $PSScriptRoot
try {
    & autorest README.md
} finally {
    Pop-Location
}
