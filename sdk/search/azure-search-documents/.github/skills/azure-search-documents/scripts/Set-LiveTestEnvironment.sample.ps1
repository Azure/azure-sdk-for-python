<#
.SYNOPSIS
    Sample local environment setup for azure-search-documents live tests.

.DESCRIPTION
    Copy this file to Set-LiveTestEnvironment.ps1 and replace placeholders with
    local values. Do not commit Set-LiveTestEnvironment.ps1 because it may
    contain secrets.

    Use a dedicated, disposable Search service. Before each live test, the
    preparer deletes all indexes, aliases, knowledge bases, knowledge sources,
    indexers, data sources, and skillsets on that service. Never target a
    shared or production service, and do not run these tests in parallel.
#>

$env:SEARCH_SERVICE_ENDPOINT = "https://<search-service-name>.search.windows.net"
$env:SEARCH_SERVICE_NAME = "<search-service-name>"
$env:SEARCH_STORAGE_CONNECTION_STRING = "<storage-connection-string>"
$env:SEARCH_STORAGE_CONTAINER_NAME = "<storage-container-name>"
$env:SEARCH_AZURE_OPENAI_ENDPOINT = "https://<azure-openai-resource>.openai.azure.com"
$env:SEARCH_AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "<embedding-deployment>"
$env:SEARCH_AZURE_OPENAI_EMBEDDING_MODEL = "<embedding-model>"

# Uncomment when recording live tests.
# $env:AZURE_TEST_RUN_LIVE = "true"
# $env:AZURE_SKIP_LIVE_RECORDING = "false"

# Option 1: authenticate with Azure CLI and uncomment the auth selector.
# az login --tenant "<tenant-id>"
# $env:AZURE_TEST_USE_CLI_AUTH = "true"

# Option 2: configure a test service principal. Keep these values only in the
# untracked Set-LiveTestEnvironment.ps1 file.
# $env:AZURE_TENANT_ID = "<tenant-id>"
# $env:AZURE_CLIENT_ID = "<client-id>"
# $env:AZURE_CLIENT_SECRET = "<client-secret>"
