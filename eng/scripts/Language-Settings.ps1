$Language = "python"
$LanguageDisplayName = "Python"
$PackageRepository = "PyPI"
$packagePattern = "*.zip"
$MetadataUri = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
$BlobStorageUrl = "https://azuresdkdocs.blob.core.windows.net/%24web?restype=container&comp=list&prefix=python%2F&delimiter=%2F"

function Get-AllPackageInfoFromRepo ($serviceDirectory)
{
  $allPackageProps = @()
  $searchPath = "sdk"
  if ($serviceDirectory)
  {
    $searchPath = Join-Path sdk ${serviceDirectory}
  }

  $allPkgPropLines = $null
  try
  {
    Push-Location $RepoRoot
    pip install packaging==20.4 setuptools==44.1.1 -q -I
    $allPkgPropLines = python (Join-path eng scripts get_package_properties.py) -s $searchPath
  }
  catch
  {
    # This is soft error and failure is expected for python metapackages
    LogError "Failed to get all package properties"
  }
  finally
  {
    Pop-Location
  }

  foreach ($line in $allPkgPropLines)
  {
    $pkgInfo = ($line -Split " ")
    $packageName = $pkgInfo[0]
    $packageVersion = $pkgInfo[1]
    $isNewSdk = ($pkgInfo[2] -eq "True")
    $pkgDirectoryPath = $pkgInfo[3]
    $serviceDirectoryName = Split-Path (Split-Path -Path $pkgDirectoryPath -Parent) -Leaf
    if ($packageName -match "mgmt")
    {
      $sdkType = "mgmt"
    }
    else
    {
      $sdkType = "client"
    }
    $pkgProp = [PackageProps]::new($packageName, $packageVersion, $pkgDirectoryPath, $serviceDirectoryName)
    $pkgProp.IsNewSdk = $isNewSdk
    $pkgProp.SdkType = $sdkType
    $pkgProp.ArtifactName = $packageName
    $allPackageProps += $pkgProp
  }
  return $allPackageProps
}

# Returns the pypi publish status of a package id and version.
function IsPythonPackageVersionPublished($pkgId, $pkgVersion)
{
  try
  {
    $existingVersion = (Invoke-RestMethod -MaximumRetryCount 3 -RetryIntervalSec 10 -Method "Get" -uri "https://pypi.org/pypi/$pkgId/$pkgVersion/json").info.version
    # if existingVersion exists, then it's already been published
    return $True
  }
  catch
  {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $statusDescription = $_.Exception.Response.StatusDescription

    # if this is 404ing, then this pkg has never been published before
    if ($statusCode -eq 404)
    {
      return $False
    }
    Write-Host "PyPI Invocation failed:"
    Write-Host "StatusCode:" $statusCode
    Write-Host "StatusDescription:" $statusDescription
    exit(1)
  }
}

# Parse out package publishing information given a python sdist of ZIP format.
function Get-python-PackageInfoFromPackageFile ($pkg, $workingDirectory)
{
  $pkg.Basename -match $SDIST_PACKAGE_REGEX | Out-Null

  $pkgId = $matches["package"]
  $docsReadMeName = $pkgId -replace "^azure-" , ""
  $pkgVersion = $matches["versionstring"]

  $workFolder = "$workingDirectory$($pkg.Basename)"
  $origFolder = Get-Location
  $releaseNotes = ""
  $readmeContent = ""

  New-Item -ItemType Directory -Force -Path $workFolder
  Expand-Archive -Path $pkg -DestinationPath $workFolder

  $changeLogLoc = @(Get-ChildItem -Path $workFolder -Recurse -Include "CHANGELOG.md")[0]
  if ($changeLogLoc) {
    $releaseNotes = Get-ChangeLogEntryAsString -ChangeLogLocation $changeLogLoc -VersionString $pkgVersion
  }

  $readmeContentLoc = @(Get-ChildItem -Path $workFolder -Recurse -Include "README.md") | Select-Object -Last 1

  if ($readmeContentLoc) {
    $readmeContent = Get-Content -Raw $readmeContentLoc
  }

  Remove-Item $workFolder -Force  -Recurse -ErrorAction SilentlyContinue

  return New-Object PSObject -Property @{
    PackageId      = $pkgId
    PackageVersion = $pkgVersion
    ReleaseTag     = "$($pkgId)_$($pkgVersion)"
    Deployable     = $forceCreate -or !(IsPythonPackageVersionPublished -pkgId $pkgId -pkgVersion $pkgVersion)
    ReleaseNotes   = $releaseNotes
    ReadmeContent  = $readmeContent
    DocsReadMeName = $docsReadMeName
  }
}

# Stage and Upload Docs to blob Storage
function Publish-python-GithubIODocs ($DocLocation, $PublicArtifactLocation)
{
  $PublishedDocs = Get-ChildItem "$DocLocation" | Where-Object -FilterScript {$_.Name.EndsWith(".zip")}

  foreach ($Item in $PublishedDocs)
  {
    $PkgName = $Item.BaseName
    $ZippedDocumentationPath = Join-Path -Path $DocLocation -ChildPath $Item.Name
    $UnzippedDocumentationPath = Join-Path -Path $DocLocation -ChildPath $PkgName
    $VersionFileLocation = Join-Path -Path $UnzippedDocumentationPath -ChildPath "version.txt"

    Expand-Archive -Force -Path $ZippedDocumentationPath -DestinationPath $UnzippedDocumentationPath

    $Version = $(Get-Content $VersionFileLocation).Trim()

    Write-Host "Discovered Package Name: $PkgName"
    Write-Host "Discovered Package Version: $Version"
    Write-Host "Directory for Upload: $UnzippedDocumentationPath"
    $releaseTag = RetrieveReleaseTag $PublicArtifactLocation
    Upload-Blobs -DocDir $UnzippedDocumentationPath -PkgName $PkgName -DocVersion $Version -ReleaseTag $releaseTag
  }
}

function Get-python-GithubIoDocIndex()
{
  # Update the main.js and docfx.json language content
  UpdateDocIndexFiles -appTitleLang Python
  # Fetch out all package metadata from csv file.
  $metadata = Get-CSVMetadata -MetadataUri $MetadataUri
  # Get the artifacts name from blob storage
  $artifacts =  Get-BlobStorage-Artifacts -blobStorageUrl $BlobStorageUrl -blobDirectoryRegex "^python/(.*)/$" -blobArtifactsReplacement '$1'
  # Build up the artifact to service name mapping for GithubIo toc.
  $tocContent = Get-TocMapping -metadata $metadata -artifacts $artifacts
  # Generate yml/md toc files and build site.
  GenerateDocfxTocContent -tocContent $tocContent -lang "Python" -campaignId "UA-62780441-36"
}

function ValidatePackage($packageName, $packageVersion, $workingDirectory) {
  $packageExpression = "$packageName$packageVersion"
  Write-Host "Validating $packageExpression"

  $installTargetFolder = Join-Path $workingDirectory $packageName
  New-Item -ItemType Directory -Force -Path $installTargetFolder | Out-Null

  # Add more validation by replicating as much of the docs CI process as
  # possible
  # https://github.com/Azure/azure-sdk-for-python/issues/20109
  try {
    $pipInstallOutput = ""
    $extraIndexUrl = " --extra-index-url=$PackageSourceOverride"
    if ($PackageSourceOverride) {
      Write-Host "pip install $packageExpression --no-cache-dir --target $installTargetFolder --extra-index-url=$PackageSourceOverride"
      $pipInstallOutput = pip `
        install `
        $packageExpression `
        --no-cache-dir `
        --target $installTargetFolder `
        --extra-index-url=$PackageSourceOverride 2>&1
    }
    else {
      Write-Host "pip install $packageExpression --no-cache-dir --target $installTargetFolder"
      $pipInstallOutput = pip `
        install `
        $packageExpression `
        --no-cache-dir `
        --target $installTargetFolder 2>&1
    }
    if ($LASTEXITCODE -ne 0) {
      LogWarning "pip install failed for $packageExpression"
      Write-Host $pipInstallOutput
      return $false
    }
  } catch {
    LogWarning "pip install failed for $packageExpression with exception"
    LogWarning $_.Exception
    LogWarning $_.Exception.StackTrace
    return $false
  }

  return $true
}

$PackageExclusions = @{
  'azure-mgmt-videoanalyzer' = 'Unsupported doc directives: https://github.com/Azure/azure-sdk-for-python/issues/21563';
  'azure-mgmt-quota' = 'Unsupported doc directives: https://github.com/Azure/azure-sdk-for-python/issues/21366';
  'azure-mgmt-webpubsub' = 'Unsupported doc directives https://github.com/Azure/azure-sdk-for-python/issues/21346';
  'azure-mgmt-apimanagement' = 'Unsupported doc directives https://github.com/Azure/azure-sdk-for-python/issues/18084';
  'azure-mgmt-reservations' = 'Unsupported doc directives https://github.com/Azure/azure-sdk-for-python/issues/18077';
  'azure-mgmt-signalr' = 'Unsupported doc directives https://github.com/Azure/azure-sdk-for-python/issues/18085';
  'azure-mgmt-mixedreality' = 'Missing version info https://github.com/Azure/azure-sdk-for-python/issues/18457';
  'azure-monitor-query' = 'Unsupported doc directives https://github.com/Azure/azure-sdk-for-python/issues/19417';
  'azure-mgmt-network' = 'Manual process used to build';
}

function Update-python-DocsMsPackages($DocsRepoLocation, $DocsMetadata) {
  Write-Host "Excluded packages:"
  foreach ($excludedPackage in $PackageExclusions.Keys) {
    Write-Host "  $excludedPackage - $($PackageExclusions[$excludedPackage])"
  }

  $FilteredMetadata = $DocsMetadata.Where({ !($PackageExclusions.ContainsKey($_.Package)) })

  UpdateDocsMsPackages `
    (Join-Path $DocsRepoLocation 'ci-configs/packages-preview.json') `
    'preview' `
    $FilteredMetadata

  UpdateDocsMsPackages `
    (Join-Path $DocsRepoLocation 'ci-configs/packages-latest.json') `
    'latest' `
    $FilteredMetadata
}

function UpdateDocsMsPackages($DocConfigFile, $Mode, $DocsMetadata) {
  Write-Host "Updating configuration: $DocConfigFile with mode: $Mode"
  $packageConfig = Get-Content $DocConfigFile -Raw | ConvertFrom-Json

  $installValidationFolder = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
  New-Item -ItemType Directory -Force -Path $installValidationFolder | Out-Null


  $outputPackages = @()
  foreach ($package in $packageConfig.packages) {
    $packageName = $package.package_info.name
    if (!$packageName) { 
      Write-Host "Keeping package with no name: $($package.package_info)"
      $outputPackages += $package
      continue
    }

    if ($package.package_info.install_type -ne 'pypi') { 
      Write-Host "Keeping package with install_type not 'pypi': $($package.package_info.name)"
      $outputPackages += $package
      continue
    }

    # Do not filter by GA/Preview status because we want differentiate between
    # tracked and non-tracked packages
    $matchingPublishedPackageArray = $DocsMetadata.Where( { $_.Package -eq $packageName })

    # If this package does not match any published packages keep it in the list.
    # This handles packages which are not tracked in metadata but still need to
    # be built in Docs CI.
    if ($matchingPublishedPackageArray.Count -eq 0) {
      Write-Host "Keep non-tracked package: $packageName"
      $outputPackages += $package
      continue
    }

    if ($matchingPublishedPackageArray.Count -gt 1) { 
      LogWarning "Found more than one matching published package in metadata for $packageName; only updating first entry"
    }
    $matchingPublishedPackage = $matchingPublishedPackageArray[0]

    if ($Mode -eq 'preview' -and !$matchingPublishedPackage.VersionPreview.Trim()) { 
      # If we are in preview mode and the package does not have a superseding
      # preview version, remove the package from the list. 
      Write-Host "Remove superseded preview package: $packageName"
      continue
    }

    if ($Mode -eq 'latest' -and !$matchingPublishedPackage.VersionGA.Trim()) { 
      LogWarning "Metadata is missing GA version for GA package $packageName. Keeping existing package."
      $outputPackages += $package
      continue
    }

    $packageVersion = "==$($matchingPublishedPackage.VersionGA)"
    if ($Mode -eq 'preview') {
      if (!$matchingPublishedPackage.VersionPreview.Trim()) { 
        LogWarning "Metadata is missing preview version for preview package $packageName. Keeping existing package."
        $outputPackages += $package
        continue
      }
      $packageVersion = "==$($matchingPublishedPackage.VersionPreview)"
    }

    # If upgrading the package, run basic sanity checks against the package
    if ($package.package_info.version -ne $packageVersion) {
      Write-Host "New version detected for $packageName ($packageVersion)"
      if (!(ValidatePackage -packageName $packageName -packageVersion $packageVersion -workingDirectory $installValidationFolder)) {
        LogWarning "Package is not valid: $packageName. Keeping old version."
        $outputPackages += $package
        continue
      }

      $package.package_info = Add-Member `
        -InputObject $package.package_info `
        -MemberType NoteProperty `
        -Name 'version' `
        -Value $packageVersion `
        -PassThru `
        -Force 
      if ($PackageSourceOverride) {
        $package.package_info = Add-Member `
          -InputObject $package.package_info `
          -MemberType NoteProperty `
          -Name 'extra_index_url' `
          -Value $PackageSourceOverride `
          -PassThru `
          -Force 
      }
    }

    Write-Host "Keeping tracked package: $packageName."
    $outputPackages += $package
  }

  $outputPackagesHash = @{}
  foreach ($package in $outputPackages) {
    # In some cases there is no $package.package_info.name, only hash if the 
    # name is set.
    if ($package.package_info.name) { 
      $outputPackagesHash[$package.package_info.name] = $true
    }
  }

  $remainingPackages = @() 
  if ($Mode -eq 'preview') { 
    $remainingPackages = $DocsMetadata.Where({
      $_.VersionPreview.Trim() -and !$outputPackagesHash.ContainsKey($_.Package)
    })
  } else {
    $remainingPackages = $DocsMetadata.Where({
      $_.VersionGA.Trim() -and !$outputPackagesHash.ContainsKey($_.Package)
    })
  }

  # Add packages that exist in the metadata but are not onboarded in docs config
  foreach ($package in $remainingPackages) {
    $packageName = $package.Package
    $packageVersion = "==$($package.VersionGA)"
    if ($Mode -eq 'preview') {
      $packageVersion = "==$($package.VersionPreview)"
    }
    if (!(ValidatePackage -packageName $packageName -packageVersion $packageVersion -workingDirectory $installValidationFolder)) {
      LogWarning "Package is not valid: $packageName. Cannot onboard."
      continue
    }

    Write-Host "Add new package from metadata: $packageName"
    if ($PackageSourceOverride) {
      $package = [ordered]@{
        package_info = [ordered]@{
          name = $packageName;
          install_type = 'pypi';
          prefer_source_distribution = 'true';
          version = $packageVersion;
          extra_index_url = $PackageSourceOverride
        };
        exclude_path = @("test*","example*","sample*","doc*");
      }
    }
    else {
      $package = [ordered]@{
          package_info = [ordered]@{
            name = $packageName;
            install_type = 'pypi';
            prefer_source_distribution = 'true';
            version = $packageVersion;
          };
          exclude_path = @("test*","example*","sample*","doc*");
      }
    }
    $outputPackages += $package
  }

  $packageConfig.packages = $outputPackages
  $packageConfig | ConvertTo-Json -Depth 100 | Set-Content $DocConfigFile
  Write-Host "Onboarding configuration written to: $DocConfigFile"
}

# function is used to auto generate API View
function Find-python-Artifacts-For-Apireview($artifactDir, $artifactName)
{
  # Find wheel file in given artifact directory
  # Make sure to pick only package with given artifact name
  # Skip auto API review creation for management packages
  if ($artifactName -match "mgmt")
  {
    Write-Host "Skipping automatic API review for management artifact $($artifactName)"
    return $null
  }

  $whlDirectory = (Join-Path -Path $artifactDir -ChildPath $artifactName.Replace("_","-"))

  Write-Host "Searching for $($artifactName) wheel in artifact path $($whlDirectory)"
  $files = Get-ChildItem $whlDirectory | ? {$_.Name.EndsWith(".whl")}
  if (!$files)
  {
    Write-Host "$whlDirectory does not have wheel package for $($artifactName)"
    return $null
  }
  elseif($files.Count -ne 1)
  {
    Write-Host "$whlDirectory should contain only one published wheel package for $($artifactName)"
    Write-Host "No of Packages $($files.Count)"
    return $null
  }

  $packages = @{
    $files[0].Name = $files[0].FullName
  }
  return $packages
}

function SetPackageVersion ($PackageName, $Version, $ServiceDirectory, $ReleaseDate, $ReplaceLatestEntryTitle)
{
  if($null -eq $ReleaseDate)
  {
    $ReleaseDate = Get-Date -Format "yyyy-MM-dd"
  }
  pip install -r "$EngDir/versioning/requirements.txt" -q -I
  python "$EngDir/versioning/version_set.py" --package-name $PackageName --new-version $Version `
  --service $ServiceDirectory --release-date $ReleaseDate --replace-latest-entry-title $ReplaceLatestEntryTitle
}

function GetExistingPackageVersions ($PackageName, $GroupId=$null)
{
  try
  {
    $existingVersion = Invoke-RestMethod -Method GET -Uri "https://pypi.python.org/pypi/${PackageName}/json"
    return ($existingVersion.releases | Get-Member -MemberType NoteProperty).Name
  }
  catch
  {
    LogError "Failed to retrieve package versions. `n$_"
    return $null
  }
}

function Get-python-DocsMsMetadataForPackage($PackageInfo) { 
  $readmeName = $PackageInfo.Name.ToLower()
  Write-Host "Docs.ms Readme name: $($readmeName)"

  # Readme names (which are used in the URL) should not include redundant terms
  # when viewed in URL form. For example: 
  # https://docs.microsoft.com/en-us/dotnet/api/overview/azure/storage-blobs-readme
  # Note how the end of the URL doesn't look like:
  # ".../azure/azure-storage-blobs-readme" 

  # This logic eliminates a preceeding "azure." in the readme filename.
  # "azure-storage-blobs" -> "storage-blobs"
  if ($readmeName.StartsWith('azure-')) {
    $readmeName = $readmeName.Substring(6)
  }

  New-Object PSObject -Property @{
    DocsMsReadMeName = $readmeName
    LatestReadMeLocation  = 'docs-ref-services/latest'
    PreviewReadMeLocation = 'docs-ref-services/preview'
    Suffix = ''
  }
}
