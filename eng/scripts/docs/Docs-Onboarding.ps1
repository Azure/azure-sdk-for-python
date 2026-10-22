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

# The package info format required by py2docfx to verify a single library.
# The format can be found at https://github.com/MicrosoftDocs/azure-docs-sdk-python/blob/main/ci-configs/packages-latest.json
# which is a file that contains all of package_info objects. For verifying a single library
# the same format is used but there's only a single package_info object in the packages list.
# This is an example:
# {
#   "packages": [
#       {
#           "package_info": {
#             "name": "azure-core",
#             "install_type": "pypi",
#             "prefer_source_distribution": "true",
#             "version": "==1.29.6a20231207001",
#             "extra_index_url": "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"
#           },
#           "exclude_path": [
#             "test*",
#             "example*",
#             "sample*",
#             "doc*"
#           ]
#         }
#       ]
#   }
# The above example contains the common settings for Python track 2 libraries.
# There are a few things of note:
# 1. install_type can be something other than pypi. source_code or dist_file are two examples of this
#    but those are for track 1 or libraries released by other teams and not through our engineering system.
# 2. extra_index_url only needs to exist on the object if PackageSourceOverride is set
# 3. The reason this needs to be done using a json file instead of just a command line is because py2docfx
#    doesn't handle the autodoc_default_options on the command line.
function Get-SinglePackageJsonForDocsValidation($PackageInfo, $PackageSourceOverride)
{

  $packageArr = @()
  $packageSpec = [ordered]@{
      package_info = [ordered]@{
          name = $PackageInfo.Name
          install_type = 'pypi'
          prefer_source_distribution = 'true'
          version = "==$($PackageInfo.Version)"
      }
      exclude_path = @("test*","example*","sample*","doc*")
  }
  if ($PackageSourceOverride) {
      $packageSpec['package_info']['extra_index_url'] = $PackageSourceOverride
  }
  # Data-plane packages (not mgmt packages, and not manually added '00`packages)
  # should document inherited members
  if ($PackageInfo.Name -notlike 'azure-mgmt-*' -and $PackageInfo.Name -notlike '*-00-*') {
      $packageSpec['extension_config'] = @{ 'autodoc_default_options' = @{ 'inherited-members' = 1 } }
  }
  $packageArr += $packageSpec

  # "packages" must be an array of packages even if there's only a single package in it.
  # There are other top level elements, required_packages, target_repo etc. that aren't
  # required for validation of a single package.
  $docsConfigPackage = [ordered]@{
      packages = $packageArr
  }

  # Return the JSon string
  return $docsConfigPackage | ConvertTo-Json -Depth 10
}

# Defined in common.ps1 as:
# $ValidateDocsMsPackagesFn = "Validate-${Language}-DocMsPackages"
function Validate-Python-DocMsPackages($PackageInfo, $PackageInfos, $PackageSourceOverride, $DocValidationImageId)
{
  # While eng/common/scripts/Update-DocsMsMetadata.ps1 is still passing a single packageInfo, process as a batch
  if (!$PackageInfos) {
    $PackageInfos =  @($PackageInfo)
  }

  # Adding these for diagnostics purposes so we know which version of python is being
  # executed and dumping all the pip packages for this install of python
  Write-Host "Executing: which python"
  $whichOutput = which python 2>&1
  $whichOutput | ForEach-Object { Write-Host $_ }
  Write-Host "`n"

  Write-Host "Executing: python -m pip freeze --all"
  $pipFreezeOutput = python -m pip freeze --all 2>&1
  $pipFreezeOutput | ForEach-Object { Write-Host $_ }
  Write-Host "`n"

  $tempDirs = @()
  $allSucceeded = $true
  try {
    foreach ($packageInfo in $PackageInfos) {
      # Some packages won't have a version and this is the case when they're being onboarded manually
      # and there's no version, only a repository and a SHA. In that case package we skip traditional
      # package validation since the library doesn't exist yet outside of source and there's nothing
      # the verification tools can do with this.
      if ($packageInfo.Version -eq 'IGNORE') {
        continue
      }

      # Create a temporary directory. The json file being passed to py2docfx will be in the root and
      # the docs will be generated to a docsOutput subdirectory.
      $outputRoot = New-Item `
      -ItemType Directory `
      -Path (Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName()))

      $tempDirs += $outputRoot

      # Create the JSON file
      $outputJsonFile = New-Item `
      -ItemType File `
      -Path (Join-Path $outputRoot ($packageInfo.Name + ".json"))

      ## Write out the json file and echo the contents
      $JsonString = Get-SinglePackageJsonForDocsValidation $packageInfo $PackageSourceOverride
      $JsonString | Out-File $outputJsonFile
      Write-Host "$JsonString"

      # Create the docs output subdirectory. This is where the tool will generate its docs
      $outputDocsDir = New-Item `
      -ItemType Directory `
      -Path (Join-Path $outputRoot "docsOutput")

      # Force the python output to be unbuffered so we see more than just the warnings.
      Write-Host "Executing: python -u -m py2docfx --param-file-path $outputJsonFile -o $outputDocsDir"
      $pyOutput = python -u -m py2docfx --param-file-path $outputJsonFile -o $outputDocsDir 2>&1
      $pyOutput | ForEach-Object { Write-Host $_ }
      Write-Host "`n"
      if ($LASTEXITCODE -ne 0) {
        LogWarning "py2docfx command failed, see output above."
        $allSucceeded = $false
      }
    }
  }
  finally {
    # Clean up any temp directories
    foreach ($tempDir in $tempDirs)
    {
      Remove-Item -Force -Recurse $tempDir | Out-Null
    }
  }
  return $allSucceeded
}
