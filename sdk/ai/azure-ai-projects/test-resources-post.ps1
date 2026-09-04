# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

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

function Get-RequiredOutput {
    param ([string] $Name)

    $value = $DeploymentOutputs[$Name]
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required deployment output '$Name' was not provided."
    }
    return $value
}

function Get-RequiredParameter {
    param ([string] $Name)

    $value = $AdditionalParameters[$Name]
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required additional parameter '$Name' was not provided."
    }
    return $value
}

foreach ($command in @("az", "python")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required command '$command' was not found on PATH."
    }
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

$deploymentJson = & az cognitiveservices account deployment show `
    --subscription $analysisSubscriptionId `
    --resource-group $analysisResourceGroupName `
    --name $analysisAccountName `
    --deployment-name $analysisDeploymentName `
    --only-show-errors `
    --output json
if ($LASTEXITCODE -ne 0) {
    throw "The qualified Agent Insights analysis model deployment could not be read."
}

$deployment = $deploymentJson | ConvertFrom-Json
if (
    $deployment.properties.provisioningState -ne "Succeeded" -or
    $deployment.properties.model.name -ne $analysisModelName -or
    $deployment.properties.model.version -ne $analysisModelVersion -or
    $deployment.sku.name -ne $analysisModelSkuName
) {
    throw "The qualified Agent Insights analysis model deployment does not match the expected model, version, SKU, or provisioning state."
}

$fixtureScript = Join-Path $PSScriptRoot "tests/agent_insights/recording_fixture.py"
if (-not (Test-Path $fixtureScript)) {
    throw "The Agent Insights recording fixture script was not found."
}

Push-Location $PSScriptRoot
try {
    & python -c "import azure.ai.projects; import azure.identity; import azure.monitor.opentelemetry.exporter; import azure.monitor.query; import opentelemetry.sdk"
    if ($LASTEXITCODE -ne 0) {
        throw "Agent Insights fixture dependencies are missing. Install this package in editable mode and install dev_requirements.txt."
    }

    $environmentNames = @(
        "FOUNDRY_PROJECT_ENDPOINT",
        "FOUNDRY_AGENT_NAME",
        "AGENT_INSIGHTS_OTEL_AGENT_ID",
        "AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET"
    )
    $previousEnvironment = @{}
    foreach ($name in $environmentNames) {
        $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    }

    try {
        $env:FOUNDRY_PROJECT_ENDPOINT = Get-RequiredOutput "FOUNDRY_PROJECT_ENDPOINT"
        $env:FOUNDRY_AGENT_NAME = Get-RequiredOutput "FOUNDRY_AGENT_NAME"
        $env:AGENT_INSIGHTS_OTEL_AGENT_ID = Get-RequiredOutput "AGENT_INSIGHTS_OTEL_AGENT_ID"
        $env:AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID = Get-RequiredOutput "AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID"

        if (-not [string]::IsNullOrWhiteSpace($TestApplicationSecret)) {
            if (
                [string]::IsNullOrWhiteSpace($TenantId) -or
                [string]::IsNullOrWhiteSpace($TestApplicationId)
            ) {
                throw "TenantId and TestApplicationId are required when TestApplicationSecret is supplied."
            }
            $env:AZURE_TENANT_ID = $TenantId
            $env:AZURE_CLIENT_ID = $TestApplicationId
            $env:AZURE_CLIENT_SECRET = $TestApplicationSecret
        }

        & python -u $fixtureScript
        if ($LASTEXITCODE -ne 0) {
            throw "The Agent Insights recording fixture failed."
        }
    }
    finally {
        foreach ($name in $environmentNames) {
            [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Agent Insights recording fixture is ready."
