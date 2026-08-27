#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

<#
.SYNOPSIS
    Reapplies fixed Cosmos account credentials after the live-test ARM deployment.

.DESCRIPTION
    New-TestResources.ps1 invokes this script after publishing Bicep outputs as pipeline
    variables. Key-auth matrix legs define AccountSelector, so this script resolves their
    fixed account again and overwrites ACCOUNT_HOST / ACCOUNT_KEY. AAD legs do not define
    AccountSelector and retain the provisioned account and tenant-scoped role assignment.

    Do not invoke this file directly. Run New-TestResources.ps1 from the repository root,
    or use pipeline/test-resources-post.tests.ps1 for local validation.
#>
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArguments
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

# Azure Pipelines exposes non-secret matrix variables as uppercase environment variables.
$selector = $env:ACCOUNTSELECTOR
if ([string]::IsNullOrWhiteSpace($selector)) {
    Write-Host 'No fixed Cosmos account selector is set; keeping the provisioned account credentials.'
    return
}

$resolver = Join-Path $PSScriptRoot 'pipeline/resolve-cosmos-test-account.ps1'
$arguments = @(
    '-NoLogo',
    '-NoProfile',
    '-NonInteractive',
    '-File', $resolver,
    '-AccountsJson', $env:COSMOS_TEST_ACCOUNTS_JSON,
    '-Selector', $selector
)

Write-Host "Reapplying fixed Cosmos test account '$selector' after resource deployment."
& pwsh @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Failed to reapply fixed Cosmos test account '$selector' (resolver exit code $LASTEXITCODE)."
}
