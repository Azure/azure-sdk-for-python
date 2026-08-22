#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore issecret psobject

<#
.SYNOPSIS
    Resolves a single fixed Cosmos live-test account from the one JSON secret and exports
    ACCOUNT_HOST / ACCOUNT_KEY (and optional SECONDARY_ACCOUNT_KEY) for the test run.

.DESCRIPTION
    This is the PowerShell counterpart of the Java repo's sdk/cosmos/pipeline/resolve-cosmos-test-account.sh
    and reads the exact same secret, in the same schema, with the same validation rules.

    It is PowerShell rather than bash+jq on purpose: unlike Java, the Python Cosmos live matrix
    (sdk/cosmos/live-platform-matrix.json) runs legs on windows-2022 and macos images as well as
    Linux, and neither bash nor jq can be relied on there. `pwsh` is present on all three hosted
    images and ConvertFrom-Json removes the jq dependency entirely.

    Only ACCOUNT_HOST / ACCOUNT_KEY (+ optional SECONDARY_ACCOUNT_KEY) are emitted. Account
    consistency, preferred locations and AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER are deliberately NOT
    emitted here: those are per-leg concerns owned by live-platform-matrix.json, and emitting them
    would clobber the matrix values.

.PARAMETER AccountsJson
    Raw JSON matching live-test-accounts.schema.json (the value of the
    sub-config-cosmos-azure-cloud-test-resources variable). Defaults to $env:COSMOS_TEST_ACCOUNTS_JSON.

.PARAMETER Selector
    Logical account name to select, e.g. multimaster-multiregion-session.
    Defaults to $env:COSMOS_ACCOUNT_SELECTOR.

.PARAMETER Local
    Print NAME=VALUE to stdout instead of emitting Azure DevOps ##vso logging commands.
    Used by the tests and for local troubleshooting. Also honours
    $env:COSMOS_ACCOUNTS_LOCAL -eq 'true'.

.OUTPUTS
    Azure DevOps logging commands on stdout (or NAME=VALUE lines under -Local).

.NOTES
    Exit codes: 0 on success, 1 on any validation failure.
#>
[CmdletBinding()]
param(
    [string] $AccountsJson = $env:COSMOS_TEST_ACCOUNTS_JSON,
    [string] $Selector = $env:COSMOS_ACCOUNT_SELECTOR,
    [switch] $Local
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

if (-not $Local -and $env:COSMOS_ACCOUNTS_LOCAL -eq 'true') {
    $Local = [switch]::Present
}

function Write-Failure {
    param([string] $Message)
    Write-Error "ERROR: $Message" -ErrorAction Continue
    exit 1
}

# Azure DevOps logging commands are line-oriented, so a value containing a newline would
# truncate the variable and spill the remainder into the log as plain text. For a key that
# would mean leaking secret material past the scrubber, so reject it outright.
function Assert-SingleLine {
    param([string] $Name, [string] $Value)
    if ($Value -match '[\r\n]') {
        Write-Failure "Account '$Selector' field '$Name' contains a line break, which cannot be safely exported as a pipeline variable."
    }
}

function Write-PublicVariable {
    param([string] $Name, [string] $Value)
    if ($Local) {
        Write-Output "$Name=$Value"
    }
    else {
        Write-Host "##vso[task.setvariable variable=$Name;issecret=false]$Value"
    }
}

# Emit a secret using the azure-sdk double-set convention (the same one
# eng/common/TestResources/TestResources-Helpers.ps1 uses when it publishes ARM outputs):
# register the literal value as a secret under _NAME so the log scrubber masks it
# everywhere, AND set a plain NAME so it still auto-exports as an environment variable to
# the test task. Marking a variable issecret=true alone would suppress that propagation and
# the tests would see no key at all.
function Write-SecretVariable {
    param([string] $Name, [string] $Value)
    if ($Local) {
        Write-Output "$Name=$Value"
    }
    else {
        Write-Host "##vso[task.setvariable variable=_$Name;issecret=true]$Value"
        Write-Host "##vso[task.setvariable variable=$Name;issecret=false]$Value"
    }
}

if ([string]::IsNullOrWhiteSpace($AccountsJson)) {
    Write-Failure "Accounts JSON is empty. Wire the sub-config-cosmos-azure-cloud-test-resources secret to COSMOS_TEST_ACCOUNTS_JSON."
}
if ([string]::IsNullOrWhiteSpace($Selector)) {
    Write-Failure "Account selector is empty. Set COSMOS_ACCOUNT_SELECTOR to a logical account name."
}

try {
    $config = $AccountsJson | ConvertFrom-Json
}
catch {
    Write-Failure "Accounts JSON is not valid JSON: $($_.Exception.Message)"
}

if ($null -eq $config -or $config -isnot [psobject]) {
    Write-Failure "Accounts JSON must be a JSON object."
}

$configProperties = @($config.PSObject.Properties.Name)

$version = if ($configProperties -contains 'version') { $config.version } else { $null }
if ("$version" -ne '1') {
    Write-Failure "Unsupported or missing schema version '$version' (parser supports: 1)."
}

if ($configProperties -notcontains 'accounts' -or $null -eq $config.accounts) {
    Write-Failure "Accounts JSON has no 'accounts' object."
}

# Match the selector case-sensitively, like the jq `has()` the Java resolver uses, so a leg
# never silently binds to a different account than the one its matrix entry names.
$accountProperty = @($config.accounts.PSObject.Properties | Where-Object { $_.Name -ceq $Selector })
if ($accountProperty.Count -ne 1) {
    $available = ($config.accounts.PSObject.Properties.Name | Sort-Object) -join ', '
    if ([string]::IsNullOrWhiteSpace($available)) { $available = '<none>' }
    Write-Failure "Account selector '$Selector' not found. Available: $available"
}

$account = $accountProperty[0].Value
if ($null -eq $account -or $account -isnot [psobject]) {
    Write-Failure "Account '$Selector' is not an object."
}

$accountProperties = @($account.PSObject.Properties.Name)
function Get-AccountField {
    param([string] $Name)
    if ($accountProperties -contains $Name) {
        $value = $account.$Name
        if ($value -is [string]) { return $value }
        if ($null -ne $value) { return "$value" }
    }
    return ''
}

$endpoint = Get-AccountField 'endpoint'
$key = Get-AccountField 'key'
$secondaryKey = Get-AccountField 'secondaryKey'

if ([string]::IsNullOrWhiteSpace($endpoint)) {
    Write-Failure "Account '$Selector' is missing required 'endpoint'."
}
if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Failure "Account '$Selector' is missing required 'key'."
}
if (-not $endpoint.StartsWith('https://', [System.StringComparison]::Ordinal)) {
    Write-Failure "Account '$Selector' endpoint must start with https:// (got '$endpoint')."
}

Assert-SingleLine 'endpoint' $endpoint
Assert-SingleLine 'key' $key

Write-PublicVariable 'ACCOUNT_HOST' $endpoint
Write-SecretVariable 'ACCOUNT_KEY' $key
if (-not [string]::IsNullOrWhiteSpace($secondaryKey)) {
    Assert-SingleLine 'secondaryKey' $secondaryKey
    Write-SecretVariable 'SECONDARY_ACCOUNT_KEY' $secondaryKey
}

# Masked, secret-free summary for the build log.
Write-Host "Resolved Cosmos test account '$Selector': endpoint=$endpoint key=***"
exit 0
