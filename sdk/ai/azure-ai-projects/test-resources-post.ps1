# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# This script deploys the gpt-realtime model to the Foundry account created by
# test-resources.bicep. It is invoked by the New-TestResources.ps1 script after the Bicep
# template finishes deploying. Model deployments are not expressed directly in the Bicep
# template because they can take several minutes and benefit from retry/wait logic that's
# awkward to express declaratively -- this mirrors the approach used by
# sdk/contentunderstanding/test-resources-post.ps1.
#
# SCOPE NOTE: This only deploys the realtime model needed by the voice-agent live tests
# (tests/agents/test_voice_agent_realtime_live*.py, test_voice_agent_conversations*.py). It does
# not provision anything for this package's broader (already-recorded, cassette-based) test
# suite.

param (
    [hashtable] $DeploymentOutputs,
    [string] $ResourceGroupName
)

$accountName = $DeploymentOutputs['FOUNDRY_VOICE_TEST_ACCOUNT_NAME']
$resourceGroup = $DeploymentOutputs['FOUNDRY_VOICE_TEST_RESOURCE_GROUP_NAME']
$deploymentName = $DeploymentOutputs['FOUNDRY_VOICE_MODEL_NAME']

if (-not $accountName) {
    Write-Error "FOUNDRY_VOICE_TEST_ACCOUNT_NAME (Foundry account name) not found in deployment outputs"
    exit 1
}

if (-not $deploymentName) {
    Write-Error "FOUNDRY_VOICE_MODEL_NAME (model deployment name) not found in deployment outputs"
    exit 1
}

if (-not $resourceGroup) {
    # Fall back to the resource group New-TestResources.ps1 is already operating in.
    $resourceGroup = $ResourceGroupName
}

Write-Host "Deploying model 'gpt-realtime' as deployment '$deploymentName' to account '$accountName' in resource group '$resourceGroup'..."

# NOTE: the exact model version below is a best-effort default and may need to be updated --
# gpt-realtime is a preview model with restricted regional/quota availability, and no other
# package in this repo currently automates its deployment (verified: no existing
# test-resources-post.ps1 anywhere deploys "gpt-realtime"). If this fails with a "model not
# found" or capacity error, check current availability with:
#   az cognitiveservices account list-models --resource-group <rg> --name <account> --output table
# and adjust -ModelVersion/-SkuCapacity/the Bicep template's location parameter accordingly.
$modelVersion = '2025-08-28'
$skuName = 'GlobalStandard'
$skuCapacity = 1

function Deploy-Model {
    param (
        [string] $ResourceGroupName,
        [string] $AccountName,
        [string] $DeploymentName,
        [string] $ModelName,
        [string] $ModelVersion,
        [string] $SkuName,
        [int] $SkuCapacity
    )

    Write-Host "Checking for an existing deployment named '$DeploymentName'..."
    $null = az cognitiveservices account deployment show `
        --resource-group $ResourceGroupName `
        --name $AccountName `
        --deployment-name $DeploymentName `
        2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deployment '$DeploymentName' already exists, skipping creation."
        return $true
    }

    $azArgs = @(
        'cognitiveservices', 'account', 'deployment', 'create',
        '--resource-group', $ResourceGroupName,
        '--name', $AccountName,
        '--deployment-name', $DeploymentName,
        '--model-format', 'OpenAI',
        '--model-name', $ModelName,
        '--model-version', $ModelVersion,
        '--output', 'json'
    )
    if ($SkuName) {
        $azArgs += '--sku-name', $SkuName
    }
    if ($SkuCapacity -gt 0) {
        $azArgs += '--sku-capacity', $SkuCapacity.ToString()
    }

    try {
        $deploymentJson = & az $azArgs 2>&1
        if ($LASTEXITCODE -eq 0) {
            $deployment = $deploymentJson | ConvertFrom-Json
            Write-Host "Successfully created deployment '$DeploymentName' (status: $($deployment.properties.provisioningState))" -ForegroundColor Green
            return $true
        }
        Write-Error "FAILED to deploy '$DeploymentName': $deploymentJson" -ErrorAction Continue
        return $false
    }
    catch {
        Write-Error "FAILED to deploy '$DeploymentName': $_" -ErrorAction Continue
        return $false
    }
}

function Wait-ForDeployment {
    param (
        [string] $ResourceGroupName,
        [string] $AccountName,
        [string] $DeploymentName,
        [int] $MaxWaitMinutes = 15,
        [int] $PollIntervalSeconds = 30
    )

    Write-Host "Waiting for deployment '$DeploymentName' to be ready..."
    $startTime = Get-Date
    $maxWaitTime = $startTime.AddMinutes($MaxWaitMinutes)

    while ((Get-Date) -lt $maxWaitTime) {
        try {
            $deploymentJson = az cognitiveservices account deployment show `
                --resource-group $ResourceGroupName `
                --name $AccountName `
                --deployment-name $DeploymentName `
                --output json 2>&1

            if ($LASTEXITCODE -eq 0) {
                $deployment = $deploymentJson | ConvertFrom-Json
                $provisioningState = $deployment.properties.provisioningState

                if ($provisioningState -eq 'Succeeded') {
                    Write-Host "Deployment '$DeploymentName' is ready (status: $provisioningState)" -ForegroundColor Green
                    return $true
                }
                if ($provisioningState -eq 'Failed') {
                    Write-Error "Deployment '$DeploymentName' failed" -ErrorAction Continue
                    return $false
                }
                Write-Host "Deployment '$DeploymentName' status: $provisioningState (waiting...)"
            }
            else {
                Write-Host "Could not check deployment status, will retry..."
            }
        }
        catch {
            Write-Host "Error checking deployment status: $_, will retry..."
        }

        Start-Sleep -Seconds $PollIntervalSeconds
    }

    Write-Warning "Timeout waiting for deployment '$DeploymentName' to be ready after $MaxWaitMinutes minutes"
    return $false
}

$deployed = Deploy-Model `
    -ResourceGroupName $resourceGroup `
    -AccountName $accountName `
    -DeploymentName $deploymentName `
    -ModelName 'gpt-realtime' `
    -ModelVersion $modelVersion `
    -SkuName $skuName `
    -SkuCapacity $skuCapacity

if ($deployed) {
    $ready = Wait-ForDeployment `
        -ResourceGroupName $resourceGroup `
        -AccountName $accountName `
        -DeploymentName $deploymentName `
        -MaxWaitMinutes 15 `
        -PollIntervalSeconds 30

    if (-not $ready) {
        Write-Error "The '$deploymentName' deployment did not finish provisioning in time. Live voice-agent tests would fail against a not-ready model." -ErrorAction Continue
        exit 1
    }
}
else {
    Write-Error "Could not create the '$deploymentName' model deployment. Live voice-agent tests will fail." -ErrorAction Continue
    exit 1
}
