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

##################
### Step 0: Wait for role assignment to propagate
##################
Write-Host "Sleeping for a bit to give role assignments time to propagate."
Start-Sleep -s 180

##################
### Step 1: Obtain a bearer token used later to authenticate against the DCE.
##################
$scope= [System.Web.HttpUtility]::UrlEncode("https://monitor.azure.com//.default")
$body = "client_id=$clientId&scope=$scope&client_secret=$clientSecret&grant_type=client_credentials";
$headers = @{"Content-Type"="application/x-www-form-urlencoded"};
$uri = "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token"
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
$uri = "$dceEndpoint/dataCollectionRules/$dcrImmutableId/streams/${streamName}?api-version=2021-11-01-preview"
$uri2 = "$dceEndpoint/dataCollectionRules/$dcrImmutableId/streams/${streamName}2?api-version=2021-11-01-preview"

Write-Host "Sending sample data..."
Invoke-RestMethod -Uri $uri -Method "Post" -Body $body -Headers $headers -TimeoutSec 20 -MaximumRetryCount 3
Invoke-RestMethod -Uri $uri2 -Method "Post" -Body $body -Headers $headers -TimeoutSec 20 -MaximumRetryCount 3

##################
### Step 4: Sleep to allow time for data to reflect in the workspace tables.
##################
Write-Host "Sleeping for 300 seconds to allow time for data to reflect in the workspace tables."
Start-Sleep -s 300
