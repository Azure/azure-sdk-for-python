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
 
function Get-python-PackageLevelReadme($packageMetadata) {  
  return GetPackageLevelReadme -packageMetadata $packageMetadata
}

function Get-python-DocsMsTocData($packageMetadata, $docRepoLocation) {
  $packageLevelReadmeName = GetPackageLevelReadme -packageMetadata $packageMetadata

  $packageTocHeader = GetDocsTocDisplayName $packageMetadata
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
