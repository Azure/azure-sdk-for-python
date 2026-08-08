#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore issecret pscustomobject unscrubbed

<#
.SYNOPSIS
    Tests for resolve-cosmos-test-account.ps1.

.DESCRIPTION
    Port of the Java repo's resolve-cosmos-test-account.tests.sh, covering the same cases plus
    two Python-specific ones (see "circuit breaker" and "line break" below).

    Deliberately plain PowerShell rather than Pester so it runs anywhere pwsh does with no
    module install, matching the zero-dependency posture of the resolver itself.

.EXAMPLE
    pwsh ./resolve-cosmos-test-account.tests.ps1
#>
[CmdletBinding()]
param()

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

$script:Resolver = Join-Path $PSScriptRoot 'resolve-cosmos-test-account.ps1'
$script:Failures = 0
$script:Total = 0

$script:ValidJson = @'
{
  "version": 1,
  "accounts": {
    "single-session": {
      "endpoint": "https://sdkci-single-session.documents.azure.com:443/",
      "key": "primary-key-single",
      "regions": ["Central US"],
      "consistency": "Session",
      "multiWrite": false
    },
    "multimaster-multiregion-session": {
      "endpoint": "https://sdkci-multimaster-multiregion-session.documents.azure.com:443/",
      "key": "primary-key-mm",
      "secondaryKey": "secondary-key-mm",
      "regions": ["Central US", "East US 2"],
      "consistency": "Session",
      "multiWrite": true
    }
  }
}
'@

function Invoke-Resolver {
    param([string] $Json, [string] $Selector)

    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        $arguments = @(
            '-NoLogo', '-NoProfile', '-NonInteractive',
            '-File', $script:Resolver,
            '-AccountsJson', $Json,
            '-Selector', $Selector,
            '-Local'
        )
        $stdout = & pwsh @arguments 2>$stderrFile
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            StdOut   = ($stdout | Out-String)
            StdErr   = (Get-Content -Path $stderrFile -Raw -ErrorAction SilentlyContinue)
        }
    }
    finally {
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

Write-Host "resolve-cosmos-test-account.ps1"

Test-Case 'resolves endpoint and key for a valid selector' {
    $r = Invoke-Resolver -Json $script:ValidJson -Selector 'single-session'
    Assert-True ($r.ExitCode -eq 0) "expected exit 0, got $($r.ExitCode): $($r.StdErr)"
    Assert-True ($r.StdOut -match 'ACCOUNT_HOST=https://sdkci-single-session\.documents\.azure\.com:443/') 'ACCOUNT_HOST not emitted'
    Assert-True ($r.StdOut -match 'ACCOUNT_KEY=primary-key-single') 'ACCOUNT_KEY not emitted'
}

Test-Case 'emits SECONDARY_ACCOUNT_KEY only when the account defines one' {
    $withSecondary = Invoke-Resolver -Json $script:ValidJson -Selector 'multimaster-multiregion-session'
    Assert-True ($withSecondary.StdOut -match 'SECONDARY_ACCOUNT_KEY=secondary-key-mm') 'SECONDARY_ACCOUNT_KEY not emitted when present'

    $withoutSecondary = Invoke-Resolver -Json $script:ValidJson -Selector 'single-session'
    Assert-True ($withoutSecondary.StdOut -notmatch 'SECONDARY_ACCOUNT_KEY') 'SECONDARY_ACCOUNT_KEY emitted when absent'
}

# Python-specific: the circuit breaker flag is a client-side SDK setting owned by
# live-platform-matrix.json, not an account property. If the resolver ever emitted it, it would
# clobber the per-leg value and silently change what the circuit-breaker lane actually tests.
Test-Case 'does not emit matrix-owned settings (circuit breaker, consistency, preferred locations)' {
    $r = Invoke-Resolver -Json $script:ValidJson -Selector 'multimaster-multiregion-session'
    Assert-True ($r.StdOut -notmatch 'AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER') 'circuit breaker flag must stay matrix-controlled'
    Assert-True ($r.StdOut -notmatch 'ACCOUNT_CONSISTENCY') 'consistency must stay matrix-controlled'
    Assert-True ($r.StdOut -notmatch 'PREFERRED_LOCATIONS') 'preferred locations must stay matrix-controlled'
}

Test-Case 'fails when the accounts JSON is empty' {
    $r = Invoke-Resolver -Json '' -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'is empty') "unexpected error: $($r.StdErr)"
}

Test-Case 'fails when the selector is empty' {
    $r = Invoke-Resolver -Json $script:ValidJson -Selector ''
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'selector is empty') "unexpected error: $($r.StdErr)"
}

Test-Case 'fails when the accounts JSON is not valid JSON' {
    $r = Invoke-Resolver -Json 'not json at all' -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'not valid JSON') "unexpected error: $($r.StdErr)"
}

Test-Case 'rejects an unsupported schema version' {
    $json = '{"version": 2, "accounts": {"single-session": {"endpoint": "https://x.documents.azure.com:443/", "key": "k"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'Unsupported or missing schema version') "unexpected error: $($r.StdErr)"
}

Test-Case 'rejects a missing schema version' {
    $json = '{"accounts": {"single-session": {"endpoint": "https://x.documents.azure.com:443/", "key": "k"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'Unsupported or missing schema version') "unexpected error: $($r.StdErr)"
}

Test-Case 'lists the available selectors when the requested one is missing' {
    $r = Invoke-Resolver -Json $script:ValidJson -Selector 'does-not-exist'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match "Account selector 'does-not-exist' not found") "unexpected error: $($r.StdErr)"
    Assert-True ($r.StdErr -match 'single-session') 'error should list the available selectors'
}

# A case-insensitive match would let a matrix typo silently bind a leg to the wrong account,
# which is exactly the class of bug this whole design is meant to make impossible.
Test-Case 'selector matching is case-sensitive' {
    $r = Invoke-Resolver -Json $script:ValidJson -Selector 'Single-Session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit for a case mismatch'
    Assert-True ($r.StdErr -match 'not found') "unexpected error: $($r.StdErr)"
}

Test-Case 'requires endpoint' {
    $json = '{"version": 1, "accounts": {"single-session": {"key": "k"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match "missing required 'endpoint'") "unexpected error: $($r.StdErr)"
}

Test-Case 'requires key' {
    $json = '{"version": 1, "accounts": {"single-session": {"endpoint": "https://x.documents.azure.com:443/"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match "missing required 'key'") "unexpected error: $($r.StdErr)"
}

Test-Case 'requires an https endpoint' {
    $json = '{"version": 1, "accounts": {"single-session": {"endpoint": "http://x.documents.azure.com:443/", "key": "k"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'must start with https://') "unexpected error: $($r.StdErr)"
}

# Azure DevOps logging commands are line-oriented, so a newline in a key would truncate the
# variable and print the remainder of the secret to the log as unscrubbed plain text.
Test-Case 'rejects a key containing a line break' {
    $json = '{"version": 1, "accounts": {"single-session": {"endpoint": "https://x.documents.azure.com:443/", "key": "line1\nline2"}}}'
    $r = Invoke-Resolver -Json $json -Selector 'single-session'
    Assert-True ($r.ExitCode -ne 0) 'expected non-zero exit'
    Assert-True ($r.StdErr -match 'line break') "unexpected error: $($r.StdErr)"
}

Test-Case 'emits ADO logging commands, using the double-set convention for secrets' {
    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        $arguments = @(
            '-NoLogo', '-NoProfile', '-NonInteractive',
            '-File', $script:Resolver,
            '-AccountsJson', $script:ValidJson,
            '-Selector', 'multimaster-multiregion-session'
        )
        $stdout = (& pwsh @arguments 2>$stderrFile | Out-String)
        Assert-True ($LASTEXITCODE -eq 0) "expected exit 0, got $LASTEXITCODE"
        Assert-True ($stdout -match '\#\#vso\[task\.setvariable variable=ACCOUNT_HOST;issecret=false\]') 'ACCOUNT_HOST must be public'
        Assert-True ($stdout -match '\#\#vso\[task\.setvariable variable=_ACCOUNT_KEY;issecret=true\]') 'ACCOUNT_KEY must be registered with the log scrubber'
        Assert-True ($stdout -match '\#\#vso\[task\.setvariable variable=ACCOUNT_KEY;issecret=false\]') 'ACCOUNT_KEY must also be set plainly so it reaches the test task env'
        Assert-True ($stdout -notmatch 'key=primary-key-mm') 'the summary line must not echo the key'
    }
    finally {
        Remove-Item -Path $stderrFile -Force -ErrorAction SilentlyContinue
    }
}

Test-Case 'reads its inputs from the environment when parameters are omitted' {
    $stderrFile = [System.IO.Path]::GetTempFileName()
    try {
        $previousJson = $env:COSMOS_TEST_ACCOUNTS_JSON
        $previousSelector = $env:COSMOS_ACCOUNT_SELECTOR
        $previousLocal = $env:COSMOS_ACCOUNTS_LOCAL
        $env:COSMOS_TEST_ACCOUNTS_JSON = $script:ValidJson
        $env:COSMOS_ACCOUNT_SELECTOR = 'single-session'
        $env:COSMOS_ACCOUNTS_LOCAL = 'true'

        $stdout = (& pwsh -NoLogo -NoProfile -NonInteractive -File $script:Resolver 2>$stderrFile | Out-String)
        Assert-True ($LASTEXITCODE -eq 0) "expected exit 0, got $LASTEXITCODE"
        Assert-True ($stdout -match 'ACCOUNT_KEY=primary-key-single') 'env-provided inputs were not used'
    }
    finally {
        $env:COSMOS_TEST_ACCOUNTS_JSON = $previousJson
        $env:COSMOS_ACCOUNT_SELECTOR = $previousSelector
        $env:COSMOS_ACCOUNTS_LOCAL = $previousLocal
        Remove-Item -Path $stderrFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ''
if ($script:Failures -gt 0) {
    Write-Host "$($script:Total - $script:Failures)/$($script:Total) passed, $($script:Failures) failed"
    exit 1
}
Write-Host "$($script:Total)/$($script:Total) passed"
exit 0
