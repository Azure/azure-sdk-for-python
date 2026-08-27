#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore pscustomobject

[CmdletBinding()]
param()

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

$script:PostScript = Join-Path $PSScriptRoot '../test-resources-post.ps1'
$script:Failures = 0
$script:Total = 0
$script:ValidJson = @'
{
  "version": 1,
  "accounts": {
    "single-session": {
      "endpoint": "https://single-session.example.com:443/",
      "key": "primary-key-single"
    }
  }
}
'@

function Invoke-PostScript {
    param([AllowEmptyString()][string] $Selector, [AllowEmptyString()][string] $AccountsJson)

    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        $previousSelector = $env:ACCOUNTSELECTOR
        $previousJson = $env:COSMOS_TEST_ACCOUNTS_JSON
        $previousLocal = $env:COSMOS_ACCOUNTS_LOCAL
        $env:ACCOUNTSELECTOR = $Selector
        $env:COSMOS_TEST_ACCOUNTS_JSON = $AccountsJson
        $env:COSMOS_ACCOUNTS_LOCAL = 'true'

        $stdout = & pwsh -NoLogo -NoProfile -NonInteractive -File $script:PostScript `
            -ResourceGroupName 'ignored-by-cosmos-post-script' `
            -DeploymentOutputs '{}' `
            -AdditionalParameters '{}' `
            -CI 2>$stderrFile
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            StdOut   = ($stdout | Out-String)
            StdErr   = (Get-Content -Path $stderrFile -Raw -ErrorAction SilentlyContinue)
        }
    }
    finally {
        $env:ACCOUNTSELECTOR = $previousSelector
        $env:COSMOS_TEST_ACCOUNTS_JSON = $previousJson
        $env:COSMOS_ACCOUNTS_LOCAL = $previousLocal
        Remove-Item -Path $stderrFile -Force -ErrorAction SilentlyContinue
    }
}

function Test-Case {
    param([string] $Name, [scriptblock] $Body)

    $script:Total++
    try {
        & $Body
        Write-Host "  PASS  $Name"
    }
    catch {
        $script:Failures++
        Write-Host "  FAIL  $Name"
        Write-Host "        $($_.Exception.Message)"
    }
}

function Assert-True {
    param([bool] $Condition, [string] $Message)
    if (-not $Condition) { throw $Message }
}

Write-Host 'test-resources-post.ps1'

Test-Case 'keeps provisioned credentials when no selector is set' {
    $result = Invoke-PostScript -Selector '' -AccountsJson ''
    Assert-True ($result.ExitCode -eq 0) "expected exit 0, got $($result.ExitCode): $($result.StdErr)"
    Assert-True ($result.StdOut -match 'keeping the provisioned account credentials') 'expected provisioned-account message'
    Assert-True ($result.StdOut -notmatch 'ACCOUNT_HOST=') 'fixed account variables must not be emitted'
}

Test-Case 'reapplies fixed credentials when a selector is set' {
    $result = Invoke-PostScript -Selector 'single-session' -AccountsJson $script:ValidJson
    Assert-True ($result.ExitCode -eq 0) "expected exit 0, got $($result.ExitCode): $($result.StdErr)"
    Assert-True ($result.StdOut -match 'ACCOUNT_HOST=https://single-session\.example\.com:443/') 'ACCOUNT_HOST not emitted'
    Assert-True ($result.StdOut -match 'ACCOUNT_KEY=primary-key-single') 'ACCOUNT_KEY not emitted'
}

Test-Case 'fails instead of falling back when fixed-account resolution fails' {
    $result = Invoke-PostScript -Selector 'missing' -AccountsJson $script:ValidJson
    Assert-True ($result.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($result.StdErr -match "Account selector 'missing' not found") "unexpected error: $($result.StdErr)"
}

Write-Host ''
if ($script:Failures -gt 0) {
    Write-Host "$($script:Total - $script:Failures)/$($script:Total) passed, $($script:Failures) failed"
    exit 1
}
Write-Host "$($script:Total)/$($script:Total) passed"
exit 0
