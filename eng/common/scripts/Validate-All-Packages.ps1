[CmdletBinding()]
Param (
  [Parameter(Mandatory=$True)]
  [array]$ArtifactList,
  [Parameter(Mandatory=$True)]
  [string]$ArtifactPath,
  [Parameter(Mandatory=$True)]
  [string]$APIViewUri,
  [Parameter(Mandatory=$True)]
  [string]$APIKey,
  [string]$ConfigFileDir,
  [string]$BuildId,
  [string]$PipelineUrl,
  [string]$Devops_pat = $env:DEVOPS_PAT,
  [bool]$IgnoreFailures = $false
)

Set-StrictMode -Version 3
. (Join-Path $PSScriptRoot common.ps1)
. ${PSScriptRoot}\Helpers\DevOps-WorkItem-Helpers.ps1

if (!$Devops_pat) {
  az account show *> $null
  if (!$?) {
    Write-Host 'Running az login...'
    az login *> $null
  }
}
else {
  # Login using PAT
  LoginToAzureDevops $Devops_pat
}

az extension show -n azure-devops *> $null
if (!$?){
  az extension add --name azure-devops
} else {
  # Force update the extension to the latest version if it was already installed
  # this is needed to ensure we have the authentication issue fixed from earlier versions
  az extension update -n azure-devops *> $null
}

CheckDevOpsAccess

function ProcessPackage($PackageName, $ConfigFileDir)
{
    Write-Host "Artifact path: $($ArtifactPath)"
    Write-Host "Package Name: $($PackageName)"
    Write-Host "Config File directory: $($ConfigFileDir)"

    $pkgPropPath = Join-Path -Path $ConfigFileDir "$PackageName.json"
    if (-Not (Test-Path $pkgPropPath))
    {
        Write-Host " Package property file path $($pkgPropPath) is invalid."
        return $false
    }

    $pkgInfo = Get-Content $pkgPropPath | ConvertFrom-Json
    &$EngCommonScriptsDir/Validate-Package.ps1 `
        -PackageName $PackageName `
        -ArtifactPath $ArtifactPath `
        -APIViewUri $APIViewUri `
        -APIKey $APIKey `
        -BuildId $BuildId `
        -PipelineUrl $PipelineUrl `
        -ConfigFileDir $ConfigFileDir `
        -IgnoreFailures $IgnoreFailures
    if ($LASTEXITCODE -ne 0)
    {
        Write-Host "Failed to validate package $PackageName"
        return $false
    }
    return $true
}

# Check if package config file is present. This file has package version, SDK type etc info.
if (-not $ConfigFileDir)
{
    $ConfigFileDir = Join-Path -Path $ArtifactPath "PackageInfo"
}
$status = $true
foreach ($artifact in $ArtifactList)
{
    Write-Host "Processing $($artifact.name)"
    $pkgStatus = ProcessPackage -PackageName $artifact.name -ConfigFileDir $ConfigFileDir
    if(!$pkgStatus) {
        $status = $false
    }
}

if(!$status)
{
    if (!$IgnoreFailures)
    {
        Write-Error "Failed to validate all packages"
        exit 1
    }
    else
    {
        Write-Host "Ignoring validation failures"
    }
}
else
{
    Write-Host "Validated and updated status in DevOps work item for all packages."
}