# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$Organization = "azure-sdk",
    [string]$Project = "internal",
    [Parameter(Mandatory = $true)]
    [int]$BuildId,
    [Parameter(Mandatory = $true)]
    [string]$BearerToken,
    [int]$PollIntervalSeconds = 15,
    [int]$TimeoutMinutes = 120,
    [scriptblock]$StatusInvoker
)

$ErrorActionPreference = "Stop"
if (-not $StatusInvoker) {
    $StatusInvoker = {
        param($StatusUri, $Headers)
        Invoke-RestMethod -Method Get -Uri $StatusUri -Headers $Headers
    }
}

$statusUri = "https://dev.azure.com/$Organization/$Project/_apis/build/builds/$BuildId`?api-version=7.1"
$headers = @{ Authorization = "Bearer $BearerToken" }
$deadline = [DateTimeOffset]::UtcNow.AddMinutes($TimeoutMinutes)
$waitHandle = [System.Threading.ManualResetEventSlim]::new($false)
try {
    while ($true) {
        $build = & $StatusInvoker $statusUri $headers
        if ($build.status -eq "completed") {
            $url = $build._links.web.href
            if ($build.result -ne "succeeded") {
                throw "Azure DevOps pipeline $BuildId completed with result '$($build.result)'. $url"
            }
            return [pscustomobject]@{
                BuildId = $BuildId
                Status = $build.status
                Result = $build.result
                Url = $url
            }
        }
        if ([DateTimeOffset]::UtcNow -ge $deadline) {
            throw "Timed out waiting for Azure DevOps pipeline $BuildId after $TimeoutMinutes minutes."
        }
        $waitHandle.Wait([TimeSpan]::FromSeconds($PollIntervalSeconds))
    }
} finally {
    $waitHandle.Dispose()
}
