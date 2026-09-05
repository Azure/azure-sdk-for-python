# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# Run this hook through New-TestResources.ps1 so the Az context is authenticated.

[CmdletBinding()]
param (
    [hashtable] $DeploymentOutputs,
    [string] $ResourceGroupName,
    [string] $TenantId,
    [string] $TestApplicationId,
    [string] $TestApplicationSecret,
    [hashtable] $AdditionalParameters = @{},
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArguments
)

$ErrorActionPreference = "Stop"

function Get-RequiredParameter {
    param ([string] $Name)

    $value = $AdditionalParameters[$Name]
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required additional parameter '$Name' was not provided."
    }
    return $value
}

$analysisSubscriptionId = Get-RequiredParameter "analysisModelSubscriptionId"
$analysisResourceGroupName = Get-RequiredParameter "analysisModelResourceGroupName"
$analysisAccountName = Get-RequiredParameter "analysisModelAccountName"
$analysisDeploymentName = if ($AdditionalParameters["analysisModelDeploymentName"]) {
    $AdditionalParameters["analysisModelDeploymentName"]
} else {
    "gpt-5.4"
}
$analysisModelName = if ($AdditionalParameters["analysisModelName"]) {
    $AdditionalParameters["analysisModelName"]
} else {
    "gpt-5.4"
}
$analysisModelVersion = if ($AdditionalParameters["analysisModelVersion"]) {
    $AdditionalParameters["analysisModelVersion"]
} else {
    "2026-03-05"
}
$analysisModelSkuName = if ($AdditionalParameters["analysisModelSkuName"]) {
    $AdditionalParameters["analysisModelSkuName"]
} else {
    "GlobalStandard"
}

$deploymentPath = (
    "/subscriptions/$analysisSubscriptionId" +
    "/resourceGroups/$analysisResourceGroupName" +
    "/providers/Microsoft.CognitiveServices/accounts/$analysisAccountName" +
    "/deployments/$analysisDeploymentName" +
    "?api-version=2025-06-01"
)
$deploymentResponse = Invoke-AzRestMethod -Method GET -Path $deploymentPath
if ($deploymentResponse.StatusCode -ne 200) {
    throw "The qualified Agent Insights analysis model deployment could not be read."
}

$deployment = $deploymentResponse.Content | ConvertFrom-Json
if (
    $deployment.properties.provisioningState -ne "Succeeded" -or
    $deployment.properties.model.name -ne $analysisModelName -or
    $deployment.properties.model.version -ne $analysisModelVersion -or
    $deployment.sku.name -ne $analysisModelSkuName
) {
    throw "The qualified Agent Insights analysis model deployment does not match the expected model, version, SKU, or provisioning state."
}

# Trace seeding runs separately after the package test dependencies are installed.
Write-Host "Agent Insights analysis model deployment is ready."
