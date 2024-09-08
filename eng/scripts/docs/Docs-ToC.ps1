# Download the .whl file into the given destination directory.
function Get-WhlFile {
  param(
      [Parameter(Mandatory=$true)] [string]$Library,
      [Parameter(Mandatory=$true)] [string]$Version,
      [Parameter(Mandatory=$true)] [string]$Destination,
      [Parameter(Mandatory=$false)] [string]$ExtraIndexUrl = ""
  )

  $LibArg= "$Library==$Version"
  if ($ExtraIndexUrl) {
    $ExtraIndexArg = "--extra-index-url=$ExtraIndexUrl"
    Write-Host "python -m pip download --quiet --only-binary=:all: --dest $Destination --no-deps $ExtraIndexArg $LibArg"
    python -m pip download --quiet --only-binary=:all: --dest $Destination --no-deps $ExtraIndexArg $LibArg
  } else {
    Write-Host "python -m pip download --quiet --only-binary=:all: --dest $Destination --no-deps $LibArg"
    python -m pip download --quiet --only-binary=:all: --dest $Destination --no-deps $LibArg
  }
  if($LASTEXITCODE -ne 0) {
      return $false
  }
  return $true
}

# Given a library and version, download the .whl file and unpack it to get the namespaces.
# A temp directory is used for the download and unpack which is cleaned up afterwards.
function Get-NamespacesFromWhlFile {
  param(
      [Parameter(Mandatory=$true)] [string]$Library,
      [Parameter(Mandatory=$true)] [string]$Version,
      [Parameter(Mandatory=$false)] [string]$ExtraIndexUrl = "",
      [Parameter(Mandatory=$false)] [string]$PythonWhlFile = $null
  )

  $destination = (Join-Path ([System.IO.Path]::GetTempPath()) "$Library$Version")
  New-Item $destination -ItemType Directory | Out-Null
  $namespaces = @()

  try {

    if ($PythonWhlFile) {
      if (Test-Path $PythonWhlFile -PathType Leaf) {
        Write-Host "Copying $PythonWhlFile to $destination"
        Copy-Item $PythonWhlFile -Destination $destination
      } else {
        LogWarning "$PythonWhlFile, does not exist."
      }
    } else {
      $success = Get-WhlFile $Library $Version $destination $ExtraIndexUrl
      if (-not $success) {
        LogWarning "Could not download Whl file for $Library $Version"
      }
    }
    # Pulling the whl file generates output, make sure it's sent to null so
    # it's not returned as part of this function.
    # Each library gets its own temporary directory. There should only be one whl
    # file in the destination directory
    $whlFile = Get-ChildItem -Path $destination -File -Filter "*.whl" | Select-Object -First 1
    # If we can't download the file or the passed in file doesn't exist then the whlFile
    # won't exist, there's nothing to process and an empty namesapces list will be returned
    if ($whlFile) {
      $unpackDir = Join-Path -Path $destination -ChildPath "$Library-$Version"
      Expand-Archive -Path $whlFile -DestinationPath $unpackDir

      # Look for any directory that contains __init__.py with the following exceptions:
      # 1. *.dist-info directories shouldn't be included in the results.
      # 2. If any subdirectory starts with "_" it's internal and needs to be skipped
      # 3. If there's a root level directory named "azure" with an __init__.py file then
      # needs to be skipped. This doesn't happen with libraries released from the
      # azure-sdk-for-python repository but there are older libraries that are in the
      # docs directories which are/were released outside of the repository where this
      # is true.
      $rootLevelAzureDir = Join-Path -Path $unpackDir -ChildPath "azure"
      $namespaceDirs = Get-ChildItem -Path $unpackDir -Recurse -Filter "__init__.py" |
          Where-Object{$_.DirectoryName -notlike "*.dist-info"} |
          Where-Object{$_.DirectoryName -notlike "*$([IO.Path]::DirectorySeparatorChar)_*" } |
          Where-Object{$_.DirectoryName -ine $rootLevelAzureDir}
      foreach($namespaceDir in $namespaceDirs) {
          # Strip off the root directy, everything left will be subDir1/subDir2/../subDirN.
          # The directory separators will be replaced with periods to compute the
          # namespace
          $partialDir = $namespaceDir.DirectoryName.Replace($unpackDir + $([IO.Path]::DirectorySeparatorChar), "")
          $namespaces += $partialDir.Replace([IO.Path]::DirectorySeparatorChar, ".")
          # Since only the primary namespace is being pulled, break out of the loop after
          # the first one.
          break
      }
    }
  }
  finally {
      # Clean up the temp directory if it was created
      if (Test-Path $destination) {
          Remove-Item $destination -Recurse -Force
      }
  }
  # Make sure this always returns an array
  Write-Output -NoEnumerate $namespaces
}

function GetOnboardingFileForMoniker($docRepoLocation, $moniker) {
  $packageOnboardingFile = 'ci-configs/packages-latest.json'
  if ($moniker -eq 'preview') {
    $packageOnboardingFile = 'ci-configs/packages-preview.json'
  } elseif ($moniker -eq 'legacy') {
    $packageOnboardingFile = 'ci-configs/packages-legacy.json'
  }

  return (Join-Path $docRepoLocation $packageOnboardingFile)
}

function Get-python-OnboardedDocsMsPackagesForMoniker($DocRepoLocation, $moniker) {
  $packageOnboardingFile = GetOnboardingFileForMoniker `
    -docRepoLocation $DocRepoLocation `
    -moniker $moniker

  $onboardedPackages = @{}
  $onboardingSpec = ConvertFrom-Json (Get-Content $packageOnboardingFile -Raw)
  foreach ($spec in $onboardingSpec.packages) {
    if (!($spec.package_info.PSObject.Members.Name -contains "name")) {
      continue
    }
    $packageName = $spec.package_info.name

    $jsonFile = "$DocRepoLocation/metadata/$moniker/$packageName.json"
    if (Test-Path $jsonFile) {
      $onboardedPackages[$packageName] = ConvertFrom-Json (Get-Content $jsonFile -Raw)
    }
    else{
      $onboardedPackages[$packageName] = $null
    }
  }

  return $onboardedPackages
}

function Get-python-OnboardedDocsMsPackages($DocRepoLocation) {
  $packageOnboardingFiles = @(
    "$DocRepoLocation/ci-configs/packages-latest.json",
    "$DocRepoLocation/ci-configs/packages-preview.json",
    "$DocRepoLocation/ci-configs/packages-legacy.json")

  $onboardedPackages = @{}
  foreach ($file in $packageOnboardingFiles) {
    $onboardingSpec = ConvertFrom-Json (Get-Content $file -Raw)
    foreach ($spec in $onboardingSpec.packages) {
      if ($spec.package_info.PSObject.Members.Name -contains "name") {
        $onboardedPackages[$spec.package_info.name] = $null
      } else {
        Write-Warning "Could not find package name: $($spec.package_info)"
      }
    }
  }

  return $onboardedPackages
}

function GetPackageLevelReadme($packageMetadata) {
  # Fallback for package name
  $packageLevelReadmeName = $packageMetadata.Package
  if ($packageLevelReadmeName.StartsWith('azure-')) {
    # Eliminate a preceeding "azure." in the readme filename.
    # "azure-storage-blobs" -> "storage-blobs"
    $packageLevelReadmeName = $packageLevelReadmeName.Substring(6)
  }

  if ($packageMetadata.PSObject.Members.Name -contains "FileMetadata") {
    $readmeMetadata = &$GetDocsMsMetadataForPackageFn -PackageInfo $packageMetadata.FileMetadata
    $packageLevelReadmeName = $readmeMetadata.DocsMsReadMeName
  }
  return $packageLevelReadmeName
}

# This function is called within a loop. To prevent multiple reads of the same
# file data, this uses a script-scoped cache variable.
$script:PackageMetadataJsonLookup = $null
function GetPackageMetadataJsonLookup($docRepoLocation) {
    if ($script:PackageMetadataJsonLookup) {
        return $script:PackageMetadataJsonLookup
    }

    $script:PackageMetadataJsonLookup = @{}
    $packageJsonFiles = Get-ChildItem $docRepoLocation/metadata/ -Filter *.json -Recurse
    foreach ($packageJsonFile in $packageJsonFiles) {
        $packageJson = Get-Content $packageJsonFile -Raw | ConvertFrom-Json -AsHashtable

        if (!$script:PackageMetadataJsonLookup.ContainsKey($packageJson.Name)) {
            $script:PackageMetadataJsonLookup[$packageJson.Name] = @($packageJson)
        } else {
            $script:PackageMetadataJsonLookup[$packageJson.Name] += $packageJson
        }
    }

    return $script:PackageMetadataJsonLookup
}

# Grab the namespaces from the json file
function Get-Toc-Children($package, $docRepoLocation) {
  $packageTable = GetPackageMetadataJsonLookup $docRepoLocation

  $namespaces = @()
  if ($packageTable.ContainsKey($package)) {
      foreach ($entry in $packageTable[$package]) {
          if ($entry.ContainsKey('Namespaces')) {
              $namespaces += $entry['Namespaces']
          }
      }
  }
  # Sort the array and clean out any dupes (there shouldn't be any but better safe than sorry)
  $namespaces = $namespaces | Sort-Object -Unique
  # Ensure that this always returns an array, even if there's one item or 0 items
  Write-Output -NoEnumerate $namespaces
}

function Get-python-PackageLevelReadme($packageMetadata) {
  return GetPackageLevelReadme -packageMetadata $packageMetadata
}

# Defined in common.ps1
# $GetDocsMsTocDataFn = "Get-${Language}-DocsMsTocData"
function Get-python-DocsMsTocData($packageMetadata, $docRepoLocation, $PackageSourceOverride) {
  $packageLevelReadmeName = GetPackageLevelReadme -packageMetadata $packageMetadata
  $packageTocHeader = GetDocsTocDisplayName $packageMetadata

  # Get-Toc-Children always returns an array, even if there's only 1 item or it's empty
  $children = Get-Toc-Children `
    -package $packageMetadata.Package `
    -docRepoLocation $docRepoLocation
    if ($children.Count -eq 0) {
      LogWarning "Did not find the package namespaces for $($packageMetadata.Package)"
    }

  $output = [PSCustomObject]@{
    PackageLevelReadmeHref = "~/docs-ref-services/{moniker}/$packageLevelReadmeName-readme.md"
    PackageTocHeader       = $packageTocHeader
    TocChildren            = $children
  }

  return $output
}

function Get-python-DocsMsTocChildrenForManagementPackages($packageMetadata, $docRepoLocation) {
  return @($packageMetadata.Package)
}

function Get-python-RepositoryLink($packageInfo) {
  return "$PackageRepositoryUri/$($packageInfo.Package)"
}
function Get-python-UpdatedDocsMsToc($toc) {
  $services = $toc[0].items
  for ($i = 0; $i -lt $services.Count; $i++) {

    # Add "ADAL" to "Active Directory" service. This is onboarded through a repo
    # source process that is not obvious in the CI configuration (no package
    # name, only a repo URL)
    if ($services[$i].name -eq 'Active Directory') {
      $services[$i].items += [PSCustomObject]@{
        name  = "adal";
        children = @("adal")
      }
    }
  }

  $functionService =  [PSCustomObject]@{
    name = 'Functions';
    landingPageType = 'Service';
    children = @('azure.functions', 'azure.durable_functions')
  }

  # Add new services which are not onboarded in obvious ways in the CI config.
  # This is done by creating a list of services excluding the ultimate item
  # (i.e. the "Other" service), then appending the new services
  # (e.g. "Functions"), sorting the resulting list, then re-adding the ultimate
  # item to the end. This ensures that the "Other" service is at the bottom as
  # intended.
  $sortableServices = $services[0..($services.Length - 2)] + $functionService
  $toc[0].items = ($sortableServices | Sort-Object -Property name) + $services[-1]

  # PowerShell outputs a single object if the output is an array with only one
  # object. The preceeding comma ensures that the output remains an array for
  # appropriate export formatting. Other formatting (e.g. `@($toc)`) does not
  # produce useful outputs.
  return , $toc
}
