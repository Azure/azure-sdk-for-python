# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# This script is used to set up test resources for the Azure Health Data Services de-identification service.

# It is invoked by the https://github.com/Azure/azure-sdk-for-net/blob/main/eng/New-TestResources.ps1
# script after the ARM template, defined in https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/storage/test-resources.json,
# is finished being deployed. The ARM template is responsible for creating the storage account and permissions needed for live tests.

param (
    [hashtable] $DeploymentOutputs,
    [string] $TenantId,
    [string] $TestApplicationId
)

# Retrieve the connection string from environment variables
$resourceGroup = $DeploymentOutputs['HEALTHDATAAISERVICES_RESOURCE_GROUP']
$storageAccountName = $DeploymentOutputs['HEALTHDATAAISERVICES_STORAGE_ACCOUNT_NAME']
$containerName = $DeploymentOutputs['HEALTHDATAAISERVICES_STORAGE_CONTAINER_NAME']

# Set the local folder path to upload
$localFolderPath = "$PSScriptRoot\tests\data\example_patient_1"

# Check if the connection string is present
if ([string]::IsNullOrWhiteSpace($storageAccountName)) {
    Write-Host "Error: Azure Storage Name string not found in environment variables."
    exit 1
}

# Retries a script block with exponential backoff until it succeeds or the time budget is exhausted.
# Role assignments and network ACL changes can take minutes to propagate after deployment.
function Invoke-WithRetry {
    param (
        [Parameter(Mandatory = $true)]
        [scriptblock] $ScriptBlock,
        [Parameter(Mandatory = $true)]
        [string] $Operation,
        [int] $MaxTotalSeconds = 300,
        [int] $InitialDelaySeconds = 5,
        [int] $MaxDelaySeconds = 60
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $delay = $InitialDelaySeconds
    $attempt = 0
    while ($true) {
        $attempt++
        try {
            $result = & $ScriptBlock
            if ($attempt -gt 1) {
                Write-Host "$Operation succeeded on attempt $attempt after $([int]$stopwatch.Elapsed.TotalSeconds)s."
            }
            return $result
        }
        catch {
            $lastError = $_
            $elapsed = $stopwatch.Elapsed.TotalSeconds
            if ($elapsed + $delay -gt $MaxTotalSeconds) {
                throw "$Operation failed after $attempt attempt(s) over $([int]$elapsed)s. This usually means the storage role assignment or network ACL change has not propagated. Last error: $($lastError.Exception.Message)"
            }
            Write-Host "$Operation failed (attempt $attempt, $([int]$elapsed)s elapsed): $($lastError.Exception.Message). Retrying in ${delay}s."
            Start-Sleep -Seconds $delay
            $delay = [Math]::Min($delay * 2, $MaxDelaySeconds)
        }
    }
}

# Load the Azure Storage module
Import-Module Az.Storage

# Connect to the storage account
$storageContext = New-AzStorageContext -StorageAccountName $storageAccountName -UseConnectedAccount

# FIXME Remove once vpn team fixes the network acl issue
$networkRuleSet = New-Object -TypeName Microsoft.Azure.Commands.Management.Storage.Models.PSNetworkRuleSet
$networkRuleSet.DefaultAction = "Allow"
Set-AzStorageAccount -ResourceGroupName $resourceGroup -Name $storageAccountName -NetworkRuleSet $networkRuleSet -ErrorAction Stop
$sinceNetworkRuleUpdate = [System.Diagnostics.Stopwatch]::StartNew()

# Wait until the container is reachable through the data plane (RBAC + network ACL propagated)
Invoke-WithRetry -Operation "Accessing container '$containerName'" -ScriptBlock {
    Get-AzStorageContainer -Name $containerName -Context $storageContext -ErrorAction Stop
}

# Upload the folder and its contents to the container
# Gets last folder name + filename. example_patient_1/doctor_dictation.txt
Get-ChildItem -Path $localFolderPath -Recurse -File | ForEach-Object {
    $filePath = $_.FullName
    $folderName = Split-Path -Path (Split-Path -Path $filePath -Parent) -Leaf
    $blobName = Split-Path -Path $filePath -Leaf
    $destinationBlob = $blobName -replace ":", ""

    $destinationBlob = "$folderName/$destinationBlob"
    Write-Host "Uploading file '$destinationBlob'"
    Invoke-WithRetry -Operation "Uploading blob '$destinationBlob'" -ScriptBlock {
        Set-AzStorageBlobContent -File $filePath -Container $containerName -Blob $destinationBlob -Context $storageContext -Force -ErrorAction Stop
    }
}

Write-Host "Folder '$localFolderPath' uploaded to container '$containerName' successfully."

# Our own access proves the test principal's RBAC and the network rule, but not the DeID service's managed
# identity role assignment. Keep a minimum wait after the network rule update for it to propagate.
$minimumWaitSeconds = 30
$remainingSeconds = [int][Math]::Ceiling($minimumWaitSeconds - $sinceNetworkRuleUpdate.Elapsed.TotalSeconds)
if ($remainingSeconds -gt 0) {
    Write-Host "Waiting ${remainingSeconds}s more so at least ${minimumWaitSeconds}s pass after the network rule update for role assignments to propagate."
    Start-Sleep -Seconds $remainingSeconds
}
