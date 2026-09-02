[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string] $PackageInfoDirectory,

    [Parameter(Mandatory = $true)]
    [string] $PackageInfoPathPrefix
)

$packageInfoFiles = @()

$availablePackageInfoFiles = @(Get-ChildItem -Path $PackageInfoDirectory -Filter '*.json' -File -ErrorAction SilentlyContinue)
if ($availablePackageInfoFiles.Count -eq 0) {
    Write-Host "No packages require a package approval check."
    Write-Host "##vso[task.setvariable variable=PackageApprovalInfoFiles;isOutput=true]"
    Write-Host "##vso[task.setvariable variable=HasPackageApprovalPackages;isOutput=true]False"
    exit 0
}

foreach ($packageInfoFile in $availablePackageInfoFiles) {
    $packageInfo = Get-Content -Raw -Path $packageInfoFile.FullName | ConvertFrom-Json
    if ($packageInfo.SdkType -eq 'mgmt') {
        Write-Host "Package approval is not required for management plane SDKs: $($packageInfo.Name)"
        continue
    }

    $packageInfoFiles += "$PackageInfoPathPrefix/$($packageInfoFile.Name)"
}

$hasPackageApprovalPackages = $packageInfoFiles.Count -gt 0
Write-Host "##vso[task.setvariable variable=PackageApprovalInfoFiles;isOutput=true]$($packageInfoFiles -join "','")"
Write-Host "##vso[task.setvariable variable=HasPackageApprovalPackages;isOutput=true]$hasPackageApprovalPackages"