Push-Location $PSScriptRoot
try {
    & autorest SWAGGER.md
} finally {
    Pop-Location
}
