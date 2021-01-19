# 1) Install Node.js (https://nodejs.org/en/)
#      MacOS
#         brew update
#         brew install node

# 2) Install AutoRest
#      npm install -g autorest

# Get latest version of AutoRest
# autorest --latest

# Variables

$Language="python"

$AzureQuantum_OpenAPI_URLRoot="https://raw.githubusercontent.com"
$AzureQuantum_OpenAPI_Repo="Azure/azure-rest-api-specs"
$AzureQuantum_OpenAPI_Branch="master"
$AzureQuantum_API_Version="Microsoft.Quantum/preview/2019-11-04-preview"
$AzureQuantum_AutoRestConfig_FileName="readme.md"
$AzureQuantum_AutoRestConfig_Language_FileName="readme.$Language.md"

$AzureQuantum_OpenAPI_DataPlane_Repo=$AzureQuantum_OpenAPI_Repo
$AzureQuantum_OpenAPI_DataPlane_Branch=$AzureQuantum_OpenAPI_Branch
$AzureQuantum_OpenAPI_DataPlane_Path="specification/quantum/data-plane"
$AzureQuantum_OpenAPI_DataPlane_Version=$AzureQuantum_API_Version
$AzureQuantum_OpenAPI_DataPlane_FileName="quantum.json"
$AzureQuantum_OpenAPI_DataPlane_URL="$AzureQuantum_OpenAPI_URLRoot/$AzureQuantum_OpenAPI_DataPlane_Repo/$AzureQuantum_OpenAPI_DataPlane_Branch/$AzureQuantum_OpenAPI_DataPlane_Path/$AzureQuantum_OpenAPI_DataPlane_Version/$AzureQuantum_OpenAPI_DataPlane_FileName"
$AzureQuantum_AutoRestConfig_DataPlane_URL="$AzureQuantum_OpenAPI_URLRoot/$AzureQuantum_OpenAPI_DataPlane_Repo/$AzureQuantum_OpenAPI_DataPlane_Branch/$AzureQuantum_OpenAPI_DataPlane_Path/$AzureQuantum_AutoRestConfig_FileName"
$AzureQuantum_AutoRestConfig_DataPlane_Language_URL="$AzureQuantum_OpenAPI_URLRoot/$AzureQuantum_OpenAPI_DataPlane_Repo/$AzureQuantum_OpenAPI_DataPlane_Branch/$AzureQuantum_OpenAPI_DataPlane_Path/$AzureQuantum_AutoRestConfig_Language_FileName"

# Folders

$AzureSDK_Folder=[System.IO.Path]::GetFullPath("$PSScriptRoot/../../")

$TempFolder=[System.IO.Path]::GetFullPath("$PSScriptRoot/../temp")
Remove-Item $TempFolder -Recurse

$OpenAPI_Folder="$TempFolder/openapi-specs"

$OpenAPI_DataPlane_Folder="$OpenAPI_Folder/data-plane"
$OpenAPI_DataPlane_FilePath="$OpenAPI_DataPlane_Folder/$AzureQuantum_API_Version/quantum.json"
$AutoRestConfig_DataPlane_FilePath="$OpenAPI_DataPlane_Folder/readme.md"
$AutoRestConfig_DataPlane_Language_FilePath="$OpenAPI_DataPlane_Folder/readme.$Language.md"

New-Item -Path $OpenAPI_DataPlane_Folder -ItemType Directory

# Downloads

Write-Output "Downloading Azure Quantum Data Plane OpenAPI spec..."
Write-Output "  From: $AzureQuantum_OpenAPI_DataPlane_URL"
Write-Output "  To: $OpenAPI_DataPlane_FilePath"
New-Item -Path ([System.IO.Path]::GetDirectoryName($OpenAPI_DataPlane_FilePath)) -ItemType Directory
Invoke-WebRequest -Uri $AzureQuantum_OpenAPI_DataPlane_URL -OutFile $OpenAPI_DataPlane_FilePath
Write-Output ""

Write-Output "Downloading Azure Quantum Data Plane AutoRest config for $Language spec..."
Write-Output "  From: $AzureQuantum_AutoRestConfig_DataPlane_URL"
Write-Output "  To: $AutoRestConfig_DataPlane_FilePath"
Invoke-WebRequest -Uri $AzureQuantum_AutoRestConfig_DataPlane_URL -OutFile $AutoRestConfig_DataPlane_FilePath
Write-Output ""

Write-Output "Downloading Azure Quantum Data Plane AutoRest config for $Language spec..."
Write-Output "  From: $AzureQuantum_AutoRestConfig_DataPlane_URL"
Write-Output "  To: $AutoRestConfig_DataPlane_Language_FilePath"
Invoke-WebRequest -Uri $AzureQuantum_AutoRestConfig_DataPlane_Language_URL -OutFile $AutoRestConfig_DataPlane_Language_FilePath
Write-Output ""

# For Python, we add a sufix "client" to the DataPlane-client's namespace and package name
# because we want to reserve "azure-quantum" to the convenience layer in QDK
if ( $Language -eq "python" ) {
    (Get-Content -Raw $AutoRestConfig_DataPlane_Language_FilePath) `
        -replace '(?m)^  namespace: .*$', '  namespace: azure.quantum.client' `
        -replace '(?m)^  package-name: .*$', '  package-name: azure-quantum-client' `
        -replace '(?m)^  output-folder: \$\(python-sdks-folder\)/quantum/azure-quantum/azure/quantum$', '  output-folder: $(python-sdks-folder)/quantum/azure-quantum-client/azure/quantum/client' `
        -replace '(?m)^  output-folder: \$\(python-sdks-folder\)/quantum/azure-quantum$', '  output-folder: $(python-sdks-folder)/quantum/azure-quantum-client' `
        | Out-File $AutoRestConfig_DataPlane_Language_FilePath


    $AzureQuantumClient_Folder="$AzureSDK_Folder/quantum/azure-quantum-client/azure/quantum/client"
    $GeneratedClient_Folder="$TempFolder/generated/$Language"
    Remove-Item $GeneratedClient_Folder -Recurse
    Remove-Item $AzureQuantumClient_Folder -Recurse

    autorest $AutoRestConfig_DataPlane_FilePath `
        --verbose `
        --python `
        --package-name="azure-quantum-client" `
        --package-version="0.14.2012" `
        --basic-setup-py `
        --output-folder=$GeneratedClient_Folder `
        --no-namespace-folders=false

    Copy-Item "$GeneratedClient_Folder\quantum_client" $AzureQuantumClient_Folder -Recurse

}
