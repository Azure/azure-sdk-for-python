# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$Organization = "azure-sdk",
    [string]$Project = "internal",
    [int]$DefinitionId = 8392,
    [int]$PipelineRevision,
    [Parameter(Mandatory = $true)]
    [string]$SourceBranch,
    [Parameter(Mandatory = $true)]
    [string]$SamplePattern,
    [string]$TestPattern,
    [string[]]$EnvironmentVariable,
    [Parameter(Mandatory = $true)]
    [string]$BearerToken,
    [scriptblock]$RequestInvoker
)

$ErrorActionPreference = "Stop"
if (-not $SourceBranch.StartsWith("refs/heads/")) {
    $SourceBranch = "refs/heads/$SourceBranch"
}

$environmentVariables = [ordered]@{}
foreach ($assignment in @($EnvironmentVariable | Where-Object { $null -ne $_ })) {
    $separatorIndex = $assignment.IndexOf("=")
    if ($separatorIndex -le 0) {
        throw "EnvironmentVariable must use NAME=VALUE syntax: '$assignment'"
    }
    $name = $assignment.Substring(0, $separatorIndex)
    if ($name -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") {
        throw "EnvironmentVariable has an invalid name: '$name'"
    }
    if ($environmentVariables.Contains($name)) {
        throw "EnvironmentVariable contains duplicate name '$name'."
    }
    $environmentVariables[$name] = $assignment.Substring($separatorIndex + 1)
}

$headers = @{ Authorization = "Bearer $BearerToken" }
if ($PipelineRevision -le 0) {
    $pipelineUri = "https://dev.azure.com/$Organization/$Project/_apis/pipelines/$DefinitionId`?api-version=7.1"
    $pipeline = Invoke-RestMethod -Method Get -Uri $pipelineUri -Headers $headers
    $PipelineRevision = [int]$pipeline.revision
    if ($PipelineRevision -le 0) {
        throw "Azure DevOps returned an invalid revision for pipeline $DefinitionId."
    }
}

$templateParameters = [ordered]@{
    SamplePattern = $SamplePattern
    TestPattern = if ([string]::IsNullOrWhiteSpace($TestPattern)) { "*" } else { $TestPattern }
}

$body = [ordered]@{
    resources = @{
        repositories = @{
            self = @{ refName = $SourceBranch }
        }
    }
    templateParameters = $templateParameters
    variables = @{
        SAMPLE_ENVIRONMENT_VARIABLES_JSON = [ordered]@{
            value = ($environmentVariables | ConvertTo-Json -Compress)
            isSecret = $true
        }
    }
}
$uri = "https://dev.azure.com/$Organization/$Project/_apis/pipelines/$DefinitionId/runs?pipelineVersion=$PipelineRevision&api-version=7.1"
if (-not $RequestInvoker) {
    $RequestInvoker = {
        param($RequestUri, $RequestHeaders, $RequestBody)
        Invoke-RestMethod -Method Post -Uri $RequestUri -Headers $RequestHeaders `
            -ContentType "application/json" -Body ($RequestBody | ConvertTo-Json -Depth 8 -Compress)
    }
}

$response = & $RequestInvoker $uri $headers $body
if (-not $response -or -not $response.id) {
    throw "Azure DevOps returned an invalid queue response."
}

[pscustomobject]@{
    BuildId = $response.id
    PipelineName = $response.definition.name
    Url = $response._links.web.href
    SourceBranch = $SourceBranch
}
