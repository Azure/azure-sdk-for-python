[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string] $PackageInfoDirectory,

    [Parameter(Mandatory = $true)]
    [string] $ArtifactsJson,

    [Parameter(Mandatory = $true)]
    [string] $PackageInfoPathPrefix
)

$artifacts = @($ArtifactsJson | ConvertFrom-Json)
$packageInfoFiles = @()

foreach ($artifact in $artifacts) {
    $packageInfoPath = Join-Path $PackageInfoDirectory "$($artifact.name).json"
    if (!(Test-Path -Path $packageInfoPath -PathType Leaf)) {
        throw "PackageInfo file was not found: $packageInfoPath"
    }

    $packageInfo = Get-Content -Raw -Path $packageInfoPath | ConvertFrom-Json
    if ($packageInfo.SdkType -eq 'mgmt') {
        Write-Host "Package approval is not required for management plane SDKs: $($packageInfo.Name)"
        continue
    }

    $packageInfoFiles += "$PackageInfoPathPrefix/$($artifact.name).json"
}

$hasPackageApprovalPackages = $packageInfoFiles.Count -gt 0
Write-Host "##vso[task.setvariable variable=PackageApprovalInfoFiles;isOutput=true]$($packageInfoFiles -join "','")"
Write-Host "##vso[task.setvariable variable=HasPackageApprovalPackages;isOutput=true]$hasPackageApprovalPackages"