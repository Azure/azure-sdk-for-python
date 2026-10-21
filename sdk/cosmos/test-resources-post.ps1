#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore issecret

<#
.SYNOPSIS
    Reapplies fixed Cosmos account credentials after the live-test ARM deployment.

.DESCRIPTION
    New-TestResources.ps1 invokes this script after publishing Bicep outputs as pipeline
    variables. Key-auth matrix legs define AccountSelector and the pre-deployment resolver
    preserves only their selected credentials under COSMOS_FIXED_* names. This script
    rebinds those values to ACCOUNT_HOST / ACCOUNT_KEY using host-stream logging commands
    that survive the deployment task's success-output suppression. AAD legs do not define
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

function Get-RequiredEnvironmentVariable {
    param([string] $Name)

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Fixed account selector '$selector' is set, but $Name is empty. Ensure the fixed-account resolver completed before deployment."
    }
    return $value
}

function Assert-SingleLine {
    param([string] $Name, [string] $Value)

    if ($Value -match '[\r\n]') {
        throw "Fixed account variable $Name contains a line break and cannot be safely exported."
    }
}

function Write-PublicVariable {
    param([string] $Name, [string] $Value)

    Write-Host "##vso[task.setvariable variable=$Name;issecret=false]$Value"
}

function Write-SecretVariable {
    param([string] $Name, [string] $Value)

    Write-Host "##vso[task.setvariable variable=_$Name;issecret=true]$Value"
    Write-Host "##vso[task.setvariable variable=$Name;issecret=false]$Value"
}

$accountHost = Get-RequiredEnvironmentVariable 'COSMOS_FIXED_ACCOUNT_HOST'
$accountKey = Get-RequiredEnvironmentVariable 'COSMOS_FIXED_ACCOUNT_KEY'
$secondaryAccountKey = $env:COSMOS_FIXED_SECONDARY_ACCOUNT_KEY

Assert-SingleLine 'COSMOS_FIXED_ACCOUNT_HOST' $accountHost
Assert-SingleLine 'COSMOS_FIXED_ACCOUNT_KEY' $accountKey
if (-not [string]::IsNullOrWhiteSpace($secondaryAccountKey)) {
    Assert-SingleLine 'COSMOS_FIXED_SECONDARY_ACCOUNT_KEY' $secondaryAccountKey
}

Write-Host "Reapplying fixed Cosmos test account '$selector' after resource deployment."
Write-SecretVariable 'ACCOUNT_HOST' $accountHost
Write-SecretVariable 'ACCOUNT_KEY' $accountKey
if (-not [string]::IsNullOrWhiteSpace($secondaryAccountKey)) {
    Write-SecretVariable 'SECONDARY_ACCOUNT_KEY' $secondaryAccountKey
}

# The final ACCOUNT_* variables are all later tasks need. Clear the plain transport
# variables so the test process receives only its normal selected-account credentials.
Write-PublicVariable 'COSMOS_FIXED_ACCOUNT_HOST' ''
Write-PublicVariable 'COSMOS_FIXED_ACCOUNT_KEY' ''
Write-PublicVariable 'COSMOS_FIXED_SECONDARY_ACCOUNT_KEY' ''
