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

function Get-python-DocsMsTocData($packageMetadata, $docRepoLocation) {
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


  $packageTocHeader = $packageMetadata.Package
  if ($packageMetadata.DisplayName) {
    $packageTocHeader = $packageMetadata.DisplayName
  }
  $output = [PSCustomObject]@{
    PackageLevelReadmeHref = "~/docs-ref-services/{moniker}/$packageLevelReadmeName-readme.md"
    PackageTocHeader       = $packageTocHeader
    TocChildren            = @($packageMetadata.Package)
  }

  return $output
}

function Get-python-DocsMsTocChildrenForManagementPackages($packageMetadata, $docRepoLocation) {
  return @($packageMetadata.Package)
}

function addManagementPackage($serviceEntry, $packageName) {
  for ($i = 0; $i -lt $serviceEntry.items.Count; $i++) {
    if ($serviceEntry.items[$i].name -eq "Management") {
      $serviceEntry.items[$i].children += @($packageName)
      return $serviceEntry
    }
  }

  $serviceEntry.items += [PSCustomObject]@{
    name  = "Management";
    landingPageType = 'Service';
    children = @($packageName)
  }

  return $serviceEntry
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

    # azure-mgmt-mixedreality is not onboarded in an obvious manner, it is
    # onboarded using a URL to a specific dist.
    if ($services[$i].name -eq 'Mixed Reality') {
      $services[$i] = addManagementPackage $services[$i] 'azure-mgmt-mixedreality'
    }

    # Retired package
    if ($services[$i].name -eq 'Container Registry') {
      $services[$i] = addManagementPackage $services[$i] 'azure-mgmt-containerregistry'
    }
  }

  $functionService =  [PSCustomObject]@{
    name = 'Functions';
    landingPageType = 'Service';
    children = @('azure-functions', 'azure-functions-durable')
  }

  # The network service is not onboarded into the regular Python build because
  # it takes many hours to build.
  $networkService = [PSCustomObject]@{
    name = 'Network';
    href = "~/docs-ref-services/{moniker}/network.md";
    items = @([PSCustomObject]@{
      name = 'Management';
      landingPageType = 'Service';
      children = @('azure-mgmt-network')
    })
  }

  # Add new services which are not onboarded in obvious ways in the CI config.
  # This is done by creating a list of services excluding the ultimate item
  # (i.e. the "Other" service), then appending the new services
  # (e.g. "Functions"), sorting the resulting list, then re-adding the ultimate
  # item to the end. This ensures that the "Other" service is at the bottom as
  # intended.
  $sortableServices = $services[0..($services.Length - 2)] + $functionService + $networkService
  $toc[0].items = ($sortableServices | Sort-Object -Property name) + $services[-1]

  # PowerShell outputs a single object if the output is an array with only one
  # object. The preceeding comma ensures that the output remains an array for
  # appropriate export formatting. Other formatting (e.g. `@($toc)`) does not
  # produce useful outputs.
  return , $toc
}