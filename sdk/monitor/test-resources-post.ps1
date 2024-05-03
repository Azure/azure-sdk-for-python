# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# IMPORTANT: Do not invoke this file directly. Please instead run eng/New-TestResources.ps1 from the repository root.

param (
    [hashtable] $DeploymentOutputs
)

# Outputs from the Bicep deployment passed in from New-TestResources
$tenantId = $DeploymentOutputs['MONITOR_TENANT_ID']
$clientId = $DeploymentOutputs['MONITOR_CLIENT_ID']
$clientSecret = $DeploymentOutputs['MONITOR_CLIENT_SECRET']
$dcrImmutableId = $DeploymentOutputs['AZURE_MONITOR_DCR_ID']
$dceEndpoint = $DeploymentOutputs['AZURE_MONITOR_DCE']
$streamName = $DeploymentOutputs['AZURE_MONITOR_STREAM_NAME']
$environment = $DeploymentOutputs['MONITOR_ENVIRONMENT']
$authorityHost = $DeploymentOutputs['AZURE_AUTHORITY_HOST']

##################
### Step 0: Wait for role assignment to propagate
##################
Write-Host "Sleeping for a bit to give role assignments time to propagate."
Start-Sleep -s 180

##################
### Step 1: Obtain a bearer token used later to authenticate against the DCE.
##################
# Audience Mappings
$audienceMappings = @{
    "AzureCloud" = "https://monitor.azure.com";
    "AzureUSGovernment" = "https://monitor.azure.us";
    "AzureChinaCloud" = "https://monitor.azure.cn";
}

$audience = $audienceMappings[$environment]

$scope= [System.Web.HttpUtility]::UrlEncode("$audience/.default")
$body = "client_id=$clientId&scope=$scope&client_secret=$clientSecret&grant_type=client_credentials";
$headers = @{"Content-Type"="application/x-www-form-urlencoded"};
$uri = "$authorityHost/$tenantId/oauth2/v2.0/token"
$bearerToken = (Invoke-RestMethod -Uri $uri -Method "Post" -Body $body -Headers $headers).access_token

##################
### Step 2: Load up some sample data.
##################
$currentTime = Get-Date ([datetime]::UtcNow) -Format O
$staticData = @"
[
{
    "Time": "$currentTime",
    "Computer": "Computer1",
    "AdditionalContext": {
        "testContextKey": 1,
        "CounterName": "AppMetric1"
    }
},
{
    "Time": "$currentTime",
    "Computer": "Computer2",
    "AdditionalContext": {
        "testContextKey": 2,
        "CounterName": "AppMetric1"
    }
},
{
    "Time": "$currentTime",
    "Computer": "Computer3",
    "AdditionalContext": {
        "testContextKey": 3,
        "CounterName": "AppMetric1"
    }
}
]
"@;

##################
### Step 3: Populate tables in both the primary and secondary Log Analytics workspaces.
##################
$body = $staticData;
$headers = @{"Authorization"="Bearer $bearerToken";"Content-Type"="application/json"};
$uri = "$dceEndpoint/dataCollectionRules/$dcrImmutableId/streams/${streamName}?api-version=2023-01-01"
$uri2 = "$dceEndpoint/dataCollectionRules/$dcrImmutableId/streams/${streamName}2?api-version=2023-01-01"

Write-Host "Sending sample data..."
Invoke-RestMethod -Uri $uri -Method "Post" -Body $body -Headers $headers -TimeoutSec 40 -MaximumRetryCount 3
Invoke-RestMethod -Uri $uri2 -Method "Post" -Body $body -Headers $headers -TimeoutSec 40 -MaximumRetryCount 3

##################
### Step 4: Sleep to allow time for data to reflect in the workspace tables.
##################
Write-Host "Sleeping for 300 seconds to allow time for data to reflect in the workspace tables."
Start-Sleep -s 300
