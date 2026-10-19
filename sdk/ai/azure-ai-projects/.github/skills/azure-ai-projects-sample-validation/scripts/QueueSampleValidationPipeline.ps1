# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$Organization = "azure-sdk",
    [string]$Project = "internal",
    [int]$DefinitionId = 8392,
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

$environmentVariableNames = [System.Collections.Generic.List[string]]::new()
$buildVariables = [ordered]@{}
foreach ($assignment in @($EnvironmentVariable | Where-Object { $null -ne $_ })) {
    $separatorIndex = $assignment.IndexOf("=")
    if ($separatorIndex -le 0) {
        throw "EnvironmentVariable must use NAME=VALUE syntax: '$assignment'"
    }
    $name = $assignment.Substring(0, $separatorIndex)
    if ($name -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") {
        throw "EnvironmentVariable has an invalid name: '$name'"
    }
    if ($buildVariables.Contains($name)) {
        throw "EnvironmentVariable contains duplicate name '$name'."
    }
    $environmentVariableNames.Add($name)
    $buildVariables[$name] = [ordered]@{
        value = $assignment.Substring($separatorIndex + 1)
        isSecret = $true
    }
}

$body = [ordered]@{
    definition = @{ id = $DefinitionId }
    sourceBranch = $SourceBranch
    templateParameters = [ordered]@{
        SamplePattern = $SamplePattern
        TestPattern = if ($TestPattern) { $TestPattern } else { "" }
        EnvironmentVariableNames = @($environmentVariableNames)
    }
    variables = $buildVariables
}
$uri = "https://dev.azure.com/$Organization/$Project/_apis/build/builds?api-version=7.1"
$headers = @{ Authorization = "Bearer $BearerToken" }
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
