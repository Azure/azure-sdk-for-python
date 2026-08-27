#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore issecret pscustomobject

[CmdletBinding()]
param()

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

$script:PostScript = Join-Path $PSScriptRoot '../test-resources-post.ps1'
$script:Failures = 0
$script:Total = 0

function Invoke-PostScript {
    param(
        [AllowEmptyString()][string] $Selector,
        [AllowEmptyString()][string] $AccountHost,
        [AllowEmptyString()][string] $AccountKey,
        [AllowEmptyString()][string] $SecondaryAccountKey = ''
    )

    $stderrFile = [System.IO.Path]::GetTempFileName()
    $callerFile = Join-Path ([System.IO.Path]::GetTempPath()) "cosmos-post-caller-$([guid]::NewGuid()).ps1"
    try {
        $previousSelector = $env:ACCOUNTSELECTOR
        $previousHost = $env:COSMOS_FIXED_ACCOUNT_HOST
        $previousKey = $env:COSMOS_FIXED_ACCOUNT_KEY
        $previousSecondaryKey = $env:COSMOS_FIXED_SECONDARY_ACCOUNT_KEY
        $previousJson = $env:COSMOS_TEST_ACCOUNTS_JSON
        $env:ACCOUNTSELECTOR = $Selector
        $env:COSMOS_FIXED_ACCOUNT_HOST = $AccountHost
        $env:COSMOS_FIXED_ACCOUNT_KEY = $AccountKey
        $env:COSMOS_FIXED_SECONDARY_ACCOUNT_KEY = $SecondaryAccountKey
        $env:COSMOS_TEST_ACCOUNTS_JSON = 'the-post-hook-must-not-read-the-aggregate-secret'

        # Model the production caller exactly: New-TestResources.ps1 invokes the post
        # script in-process while deploy-test-resources.yml discards its success stream.
        $escapedPostScript = $script:PostScript.Replace("'", "''")
        @"
`$ErrorActionPreference = 'Stop'
& '$escapedPostScript' -ResourceGroupName 'ignored-by-cosmos-post-script' -DeploymentOutputs '{}' -AdditionalParameters '{}' -CI | Out-Null
"@ | Set-Content -LiteralPath $callerFile -Encoding utf8

        $stdout = & pwsh -NoLogo -NoProfile -NonInteractive -File $callerFile 2>$stderrFile
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            StdOut   = ($stdout | Out-String)
            StdErr   = (Get-Content -Path $stderrFile -Raw -ErrorAction SilentlyContinue)
        }
    }
    finally {
        $env:ACCOUNTSELECTOR = $previousSelector
        $env:COSMOS_FIXED_ACCOUNT_HOST = $previousHost
        $env:COSMOS_FIXED_ACCOUNT_KEY = $previousKey
        $env:COSMOS_FIXED_SECONDARY_ACCOUNT_KEY = $previousSecondaryKey
        $env:COSMOS_TEST_ACCOUNTS_JSON = $previousJson
        Remove-Item -Path $stderrFile -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $callerFile -Force -ErrorAction SilentlyContinue
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
    $result = Invoke-PostScript -Selector '' -AccountHost '' -AccountKey ''
    Assert-True ($result.ExitCode -eq 0) "expected exit 0, got $($result.ExitCode): $($result.StdErr)"
    Assert-True ($result.StdOut -match 'keeping the provisioned account credentials') 'expected provisioned-account message'
    Assert-True ($result.StdOut -notmatch 'variable=ACCOUNT_HOST;') 'fixed account variables must not be emitted'
}

Test-Case 'reapplies selected credentials through the production Out-Null caller' {
    $result = Invoke-PostScript `
        -Selector 'single-session' `
        -AccountHost 'https://single-session.example.com:443/' `
        -AccountKey 'primary-key-single'
    Assert-True ($result.ExitCode -eq 0) "expected exit 0, got $($result.ExitCode): $($result.StdErr)"
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=_ACCOUNT_HOST;issecret=true\]https://single-session\.example\.com:443/') 'ACCOUNT_HOST was not registered as a secret'
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=ACCOUNT_HOST;issecret=false\]https://single-session\.example\.com:443/') 'ACCOUNT_HOST logging command did not survive Out-Null'
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=_ACCOUNT_KEY;issecret=true\]primary-key-single') 'ACCOUNT_KEY was not registered as a secret'
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=ACCOUNT_KEY;issecret=false\]primary-key-single') 'ACCOUNT_KEY logging command did not survive Out-Null'
    Assert-True ($result.StdOut -match '(?m)^\#\#vso\[task\.setvariable variable=COSMOS_FIXED_ACCOUNT_KEY;issecret=false\]\r?$') 'plain key transport variable was not cleared'
}

Test-Case 'reapplies an optional selected secondary key' {
    $result = Invoke-PostScript `
        -Selector 'single-session' `
        -AccountHost 'https://single-session.example.com:443/' `
        -AccountKey 'primary-key-single' `
        -SecondaryAccountKey 'secondary-key-single'
    Assert-True ($result.ExitCode -eq 0) "expected exit 0, got $($result.ExitCode): $($result.StdErr)"
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=_SECONDARY_ACCOUNT_KEY;issecret=true\]secondary-key-single') 'secondary key was not registered as a secret'
    Assert-True ($result.StdOut -match '\#\#vso\[task\.setvariable variable=SECONDARY_ACCOUNT_KEY;issecret=false\]secondary-key-single') 'secondary key logging command did not survive Out-Null'
    Assert-True ($result.StdOut -match '(?m)^\#\#vso\[task\.setvariable variable=COSMOS_FIXED_SECONDARY_ACCOUNT_KEY;issecret=false\]\r?$') 'plain secondary key transport variable was not cleared'
}

Test-Case 'fails instead of falling back when selected credentials are missing' {
    $result = Invoke-PostScript `
        -Selector 'single-session' `
        -AccountHost 'https://single-session.example.com:443/' `
        -AccountKey ''
    Assert-True ($result.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($result.StdErr -match 'COSMOS_FIXED_ACCOUNT_KEY is empty') "unexpected error: $($result.StdErr)"
}

Write-Host ''
if ($script:Failures -gt 0) {
    Write-Host "$($script:Total - $script:Failures)/$($script:Total) passed, $($script:Failures) failed"
    exit 1
}
Write-Host "$($script:Total)/$($script:Total) passed"
exit 0
