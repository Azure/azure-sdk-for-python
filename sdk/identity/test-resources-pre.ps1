# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# IMPORTANT: Do not invoke this file directly. Please instead run eng/New-TestResources.ps1 from the repository root.
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param (
    # Captures any arguments from eng/New-TestResources.ps1 not declared here (no parameter errors).
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArguments,

    [Parameter()]
    [string] $Location = '',

    [Parameter()]
    [ValidatePattern('^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')]
    [string] $TestApplicationId,

    [Parameter()]
    [string] $TestApplicationSecret,

    [Parameter()]
    [ValidatePattern('^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')]
    [string] $SubscriptionId,

    [Parameter()]
    [hashtable] $AdditionalParameters = @{},

    [Parameter(ParameterSetName = 'Provisioner', Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $TenantId
)

$ProvisionLiveResources = $AdditionalParameters['ProvisionLiveResources']
Write-Host "ProvisionLiveResources: $ProvisionLiveResources"
if ($CI -and !$ProvisionLiveResources) {
    Write-Host "Skipping test resource pre-provisioning."
    return
}
$templateFileParameters['provisionLiveResources'] = $true

Import-Module -Name $PSScriptRoot/../../eng/common/scripts/X509Certificate2 -Verbose

ssh-keygen -t rsa -b 4096 -f $PSScriptRoot/sshKey -N '' -C ''
$sshKey = Get-Content $PSScriptRoot/sshKey.pub

$templateFileParameters['sshPubKey'] = $sshKey

Write-Host "Sleeping for a bit to ensure service principal is ready."
Start-Sleep -s 45

# Install this specific version of the Azure CLI to avoid https://github.com/Azure/azure-cli/issues/28358.
pip install azure-cli=="2.56.0"

$az_version = az version
Write-Host "Azure CLI version: $az_version"
az login --service-principal -u $TestApplicationId -p $TestApplicationSecret --tenant $TenantId
az account set --subscription $SubscriptionId
$versions = az aks get-versions -l westus -o json | ConvertFrom-Json
Write-Host "AKS versions: $($versions | ConvertTo-Json -Depth 100)"
$patchVersions = $versions.values | Where-Object { $_.isPreview -eq $null } | Select-Object -ExpandProperty patchVersions
Write-Host "AKS patch versions: $($patchVersions | ConvertTo-Json -Depth 100)"
$latestAksVersion = $patchVersions | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name | Sort-Object -Descending | Select-Object -First 1
Write-Host "Latest AKS version: $latestAksVersion"
$templateFileParameters['latestAksVersion'] = $latestAksVersion
