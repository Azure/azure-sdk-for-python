. "$PSScriptRoot/Docs-ToC.ps1"

# $SetDocsPackageOnboarding = "Set-${Language}-DocsPackageOnboarding"
function Set-python-DocsPackageOnboarding($moniker, $metadata, $docRepoLocation, $packageSourceOverride) { 
    $onboardingFile = GetOnboardingFileForMoniker $docRepoLocation $moniker

    $onboardingSpec = Get-Content $onboardingFile -Raw | ConvertFrom-Json -AsHashtable

    $packagesToOnboard = @()
    foreach ($package in $metadata) {
        $packageSpec = [ordered]@{
            package_info = [ordered]@{
                name                       = $package.Name
                install_type               = 'pypi'
                prefer_source_distribution = 'true'
                version                    = "==$($package.Version)"
            }
            exclude_path = @("test*", "example*", "sample*", "doc*")
        }

        # Data-plane packages (not mgmt packages, and not manually added '00`
        # packages) should document inherited members
        if ($package.Name -notlike 'azure-mgmt-*' -and $package.Name -notlike '*-00-*') {
            $packageSpec['extension_config'] = @{ 'autodoc_default_options' = @{ 'inherited-members' = 1 } }
        }

        if ($packageSourceOverride) {
            $packageSpec['package_info']['extra_index_url'] = $packageSourceOverride
        }

        if ($package.ContainsKey('DocsCiConfigProperties')) {
            $overrides = $package['DocsCiConfigProperties']
            
            # Merge properties from package_info object (duplicate values will)
            # be overwritten
            if ($overrides.ContainsKey('package_info')) {
                foreach ($key in $overrides['package_info'].Keys) {
                    $packageSpec['package_info'][$key] = $overrides['package_info'][$key]
                }
            }

            # Directly override other keys like exlcude_path
            foreach ($key in $overrides.Keys) { 
                if ($key -in @('package_info')) {
                    # Skip over keys that have already been processed
                    continue
                }

                $packageSpec[$key] = $overrides[$key]
            }
        }

        $packagesToOnboard += $packageSpec
    }

    $onboardingSpec['packages'] = $packagesToOnboard

    Set-Content `
        -Path $onboardingFile `
        -Value ($onboardingSpec | ConvertTo-Json -Depth 100)
}

# $GetDocsPackagesAlreadyOnboarded = "Get-${Language}-DocsPackagesAlreadyOnboarded"
function Get-python-DocsPackagesAlreadyOnboarded($docRepoLocation, $moniker) {
    return &$GetOnboardedDocsMsPackagesForMonikerFn `
        -DocRepoLocation $docRepoLocation `
        -moniker $moniker
}



function ValidatePackage {
    Param(
        [Parameter(Mandatory = $true)]
        [string]$packageName,
        [Parameter(Mandatory = $true)]
        [string]$packageVersion,
        [Parameter(Mandatory = $false)]
        [string]$PackageSourceOverride,
        [Parameter(Mandatory = $false)]
        [string]$DocValidationImageId
    )
    $installValidationFolder = Join-Path ([System.IO.Path]::GetTempPath()) "validation"
    if (!(Test-Path $installValidationFolder)) {
        New-Item -ItemType Directory -Force -Path $installValidationFolder | Out-Null
    }
    # Add more validation by replicating as much of the docs CI process as
    # possible
    # https://github.com/Azure/azure-sdk-for-python/issues/20109
    $result = $true
    if (!$DocValidationImageId) {
        Write-Host "Validating using pip command directly on $packageName."
        $result = FallbackValidation -packageName "$packageName" -packageVersion "$packageVersion" -workingDirectory $installValidationFolder -PackageSourceOverride $PackageSourceOverride
    }
    else {
        Write-Host "Validating using $DocValidationImageId on $packageName."
        $result = DockerValidation -packageName "$packageName" -packageVersion "$packageVersion" `
            -PackageSourceOverride $PackageSourceOverride -DocValidationImageId $DocValidationImageId -workingDirectory $installValidationFolder
    }

    return $result
}
function DockerValidation {
    Param(
        [Parameter(Mandatory = $true)]
        [string]$packageName,
        [Parameter(Mandatory = $true)]
        [string]$packageVersion,
        [Parameter(Mandatory = $false)]
        [string]$PackageSourceOverride,
        [Parameter(Mandatory = $false)]
        [string]$DocValidationImageId,
        [Parameter(Mandatory = $false)]
        [string]$workingDirectory
    )
    if ($PackageSourceOverride) {
        Write-Host "docker run -v ${workingDirectory}:/workdir/out -e TARGET_PACKAGE=$packageName -e TARGET_VERSION=$packageVersion -e EXTRA_INDEX_URL=$PackageSourceOverride -t $DocValidationImageId"
        $commandLine = docker run -v "${workingDirectory}:/workdir/out" -e TARGET_PACKAGE=$packageName -e TARGET_VERSION=$packageVersion `
            -e EXTRA_INDEX_URL=$PackageSourceOverride -t $DocValidationImageId 2>&1
    }
    else {
        Write-Host "docker run -v ${workingDirectory}:/workdir/out -e TARGET_PACKAGE=$packageName -e TARGET_VERSION=$packageVersion -t $DocValidationImageId"
        $commandLine = docker run -v "${workingDirectory}:/workdir/out" `
            -e TARGET_PACKAGE=$packageName -e TARGET_VERSION=$packageVersion -t $DocValidationImageId 2>&1
    }
    # The docker exit codes: https://docs.docker.com/engine/reference/run/#exit-status
    # If the docker failed because of docker itself instead of the application,
    # we should skip the validation and keep the packages.

    if ($LASTEXITCODE -eq 125 -Or $LASTEXITCODE -eq 126 -Or $LASTEXITCODE -eq 127) {
        $commandLine | ForEach-Object { Write-Debug $_ }
        LogWarning "The `docker` command does not work with exit code $LASTEXITCODE. Fall back to npm install $packageName directly."
        FallbackValidation -packageName "$packageName" -packageVersion "$packageVersion" -workingDirectory $workingDirectory -PackageSourceOverride $PackageSourceOverride
    }
    elseif ($LASTEXITCODE -ne 0) {
        $commandLine | ForEach-Object { Write-Debug $_ }
        LogWarning "Package $packageName ref docs validation failed."
        return $false
    }
    return $true
}

function FallbackValidation {
    Param(
        [Parameter(Mandatory = $true)]
        [string]$packageName,
        [Parameter(Mandatory = $true)]
        [string]$packageVersion,
        [Parameter(Mandatory = $true)]
        [string]$workingDirectory,
        [Parameter(Mandatory = $false)]
        [string]$PackageSourceOverride
    )
    $installTargetFolder = Join-Path $workingDirectory $packageName
    New-Item -ItemType Directory -Force -Path $installTargetFolder | Out-Null
    $packageExpression = "$packageName$packageVersion"
    try {
        $pipInstallOutput = ""
        if ($PackageSourceOverride) {
            Write-Host "python -m pip install $packageExpression --no-cache-dir --target $installTargetFolder --extra-index-url=$PackageSourceOverride"
            $pipInstallOutput = python -m pip `
                install `
                $packageExpression `
                --no-cache-dir `
                --target $installTargetFolder `
                --extra-index-url=$PackageSourceOverride 2>&1
        }
        else {
            Write-Host "python -m pip install $packageExpression --no-cache-dir --target $installTargetFolder"
            $pipInstallOutput = python -m pip `
                install `
                $packageExpression `
                --no-cache-dir `
                --target $installTargetFolder 2>&1
        }
        if ($LASTEXITCODE -ne 0) {
            LogWarning "python -m pip install failed for $packageExpression"
            Write-Host $pipInstallOutput
            return $false
        }
    }
    catch {
        LogWarning "python -m pip install failed for $packageExpression with exception"
        LogWarning $_.Exception
        LogWarning $_.Exception.StackTrace
        return $false
    }

    return $true
}

# Defined in common.ps1 as:
# $ValidateDocsMsPackagesFn = "Validate-${Language}-DocMsPackages"
function Validate-Python-DocMsPackages ($PackageInfo, $PackageInfos, $PackageSourceOverride, $DocValidationImageId) {
    # While eng/common/scripts/Update-DocsMsMetadata.ps1 is still passing a single packageInfo, process as a batch
    if (!$PackageInfos) {
        $PackageInfos = @($PackageInfo)
    }

    $allSucceeded = $true
    foreach ($item in $PackageInfos) {
        # If the Version is IGNORE that means it's a source install and those aren't run through ValidatePackage
        if ($item.Version -eq 'IGNORE') {
            continue
        }

        $result = ValidatePackage `
            -packageName $item.Name `
            -packageVersion "==$($item.Version)" `
            -PackageSourceOverride $PackageSourceOverride `
            -DocValidationImageId $DocValidationImageId

        if (!$result) {
            $allSucceeded = $false
        }
    }

    return $allSucceeded
}
