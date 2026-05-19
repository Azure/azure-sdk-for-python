<#
.SYNOPSIS
    Sample local environment setup for azure-search-documents live tests.

.DESCRIPTION
    Copy this file to Set-LiveTestEnvironment.ps1 and replace placeholders with
    local values. Do not commit Set-LiveTestEnvironment.ps1 because it may
    contain secrets.
#>

$env:SEARCH_SERVICE_ENDPOINT = "https://<search-service-name>.search.windows.net"
$env:SEARCH_SERVICE_NAME = "<search-service-name>"
$env:SEARCH_STORAGE_CONNECTION_STRING = "<storage-connection-string>"
$env:SEARCH_STORAGE_CONTAINER_NAME = "<storage-container-name>"

# Uncomment when recording live tests.
# $env:AZURE_TEST_RUN_LIVE = "true"

# Uncomment if you need to authenticate before live tests.
# az login --tenant "<tenant-id>"
