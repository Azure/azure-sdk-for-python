. "$PSScriptRoot/Docs-ToC.ps1"

# $SetDocsPackageOnboarding = "Set-${Language}-DocsPackageOnboarding"
function Set-python-DocsPackageOnboarding($moniker, $metadata, $docRepoLocation, $packageSourceOverride) { 
    $onboardingFile = GetOnboardingFileForMoniker $docRepoLocation $moniker

    $onboardingSpec = Get-Content $onboardingFile -Raw | ConvertFrom-Json -AsHashtable

    $packagesToOnboard = @()
    foreach ($package in $metadata) {
        $packageSpec = [ordered]@{
            package_info = [ordered]@{
                name = $package.Name
                install_type = 'pypi'
                prefer_source_distribution = 'true'
                version = "==$($package.Version)"
            }
            exclude_path = @("test*","example*","sample*","doc*")
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
