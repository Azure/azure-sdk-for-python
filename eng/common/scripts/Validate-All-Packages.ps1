[CmdletBinding()]
Param (
  [Parameter(Mandatory=$True)]
  [array] $ArtifactList,
  [Parameter(Mandatory=$True)]
  [string] $ArtifactPath,
  [Parameter(Mandatory=$True)]
  [string] $APIViewUri,
  [Parameter(Mandatory=$True)]
  [string] $APIKey,
  [string] $ConfigFileDir,
  [string] $BuildId,
  [string] $PipelineUrl,
  [bool] $IgnoreFailures = $false
)

Set-StrictMode -Version 3
. (Join-Path $PSScriptRoot common.ps1)

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