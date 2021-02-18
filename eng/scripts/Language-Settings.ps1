$Language = "python"
$LanguageDisplayName = "Python"
$PackageRepository = "PyPI"
$packagePattern = "*.zip"
$MetadataUri = "https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/python-packages.csv"
$BlobStorageUrl = "https://azuresdkdocs.blob.core.windows.net/%24web?restype=container&comp=list&prefix=python%2F&delimiter=%2F"

function Get-python-PackageInfoFromRepo  ($pkgPath, $serviceDirectoryName, $artifactName)
{  
  $packageName = $artifactName.Replace('_', '-')
  $pkgDirName = Split-Path $pkgPath -Leaf
  if ($pkgDirName -ne $packageName)
  {
    # Common code triggers this function against each directory but we can skip if it doesn't match package name
    return $null
  }

  $setupPyPath = Join-Path $pkgPath "setup.py"

  if (Test-Path $setupPyPath)
  {
    # Get PackageName and Version Info from SetUp.py
    $packageNameFromSetupPy = $null
    $namespaceNameFromSetupPy = $null
    $versionFromSetupPy = $null
    $versionFileSubDir = $null
    $requiresCorePkg = $False
    $nameAndVersionInfo = Select-String -Path $setupPyPath -Pattern '^\s+version=.+,$', '^\s+name=.+,$', '^PACKAGE_NAME\s=.+$', '^NAMESPACE_NAME\s=.+$', '^package_folder_path\s=.+$'-Raw

    #Write-Host "nameandversion $nameAndVersionInfo"

    if ($null -ne $nameAndVersionInfo)
    {
      foreach ($info in $nameAndVersionInfo)
      {
        if ($info -match "PACKAGE_NAME =")
        {
          $packageNameFromSetupPy = $info.Replace("'",'"').Split('"')[1]
        }
        if ($info -match "version=")
        {
          $versionFromSetupPy = $info.Replace("'",'"').Split('"')[1]
        }
        if ($info -match "NAMESPACE_NAME =")
        {
          $namespaceNameFromSetupPy = $info.Replace("'",'"').Split('"')[1]
        }
        if ($null -eq $packageNameFromSetupPy -and $info -match "name=")
        {
          $packageNameFromSetupPy = $info.Replace("'",'"').Split('"')[1]
        }
        if ($info -match 'package_folder_path = \".+\"')
        {
          $versionFileSubDir = $info.Replace("'",'"').Split('"')[1]
        }
      }

      #Write-Host "Package Name $packageNameFromSetupPy" -ForegroundColor Green
      #Write-Host "Package Version $versionFromSetupPy" -ForegroundColor Green

      $installRequiresInfo = (Get-Content -Path $setupPyPath -Raw | Select-String -Pattern '(?s)\sinstall_requires=.*?],').Matches.Value

      if (($installRequiresInfo -match "azure-core") -or ($installRequiresInfo -match "azure-mgmt-core"))
      {
        $requiresCorePkg = $True
      }
    }
    $ParsedVersion = [AzureEngSemanticVersion]::ParsePythonVersionString($versionFromSetupPy)

    if ($null -eq $ParsedVersion)
    {
      $versionFilePath = Join-Path $pkgPath ($packageName.Replace('-', '/')) "_version.py"
      if (!(Test-Path $versionFilePath))
      {
        $versionFilePath = Join-Path $pkgPath ($packageName.Replace('-', '/')) "version.py"
      }
      if (!(Test-Path $versionFilePath) -and ($null -ne $namespaceNameFromSetupPy))
      {
        $versionFilePath = Join-Path $pkgPath ($namespaceNameFromSetupPy.Replace('.', '/')) "_version.py"
      }
      if (!(Test-Path $versionFilePath) -and ($null -ne $versionFileSubDir))
      {
        $versionFilePath = Join-Path $pkgPath $versionFileSubDir "_version.py"
      }
      if (Test-Path $versionFilePath)
      {
        #Write-Host "Version File $versionFilePath" -ForegroundColor Yellow
        $versionFromFile = (Select-String -Path $versionFilePath -Pattern '^VERSION\s=\s.+' -Raw).Replace("'", '"').Split('"')[1]
        $parsedVersion = [AzureEngSemanticVersion]::ParsePythonVersionString($versionFromFile)

        if (($null -ne $versionFromFile) -and ($null -eq $parsedVersion))
        {
          LogWarning "Retirieved version [ $versionFromFile ] for [ $packageName ] is invalid"
        }

        if ($null -ne $ParsedVersion)
        {
          $versionFromSetupPy = $versionFromFile
        }
      }
    }

    #Write-Host "Package Version $versionFromSetupPy" -ForegroundColor Blue
    #Write-Host "IsNewSDK $requiresCorePkg" -ForegroundColor Blue

    if ($packageNameFromSetupPy -eq $packageName)
    {
      if ($null -eq $parsedVersion)
      {
        LogWarning "Failed to get version for [ $packageName ]"
      }
      $pkgProp = [PackageProps]::new($packageName, $parsedVersion.RawVersion, $pkgPath, $serviceDirectoryName)
      $pkgProp.IsNewSdk = $requiresCorePkg
      $pkgProp.ArtifactName = $packageName
      return $pkgProp
    }
  }
  LogWarning "Failed to retrieve Package Properties for [ $packageName ]"
  return $null
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
  GenerateDocfxTocContent -tocContent $tocContent -lang "Python"
}

# Updates a python CI configuration json.
# For "latest", the version attribute is cleared, as default behavior is to pull latest "non-preview".
# For "preview", we update to >= the target releasing package version.
function Update-python-CIConfig($pkgs, $ciRepo, $locationInDocRepo, $monikerId=$null)
{
  $pkgJsonLoc = (Join-Path -Path $ciRepo -ChildPath $locationInDocRepo)

  if (-not (Test-Path $pkgJsonLoc)) {
    Write-Error "Unable to locate package json at location $pkgJsonLoc, exiting."
    exit(1)
  }

  $allJson  = Get-Content $pkgJsonLoc | ConvertFrom-Json
  $visibleInCI = @{}

  for ($i=0; $i -lt $allJson.packages.Length; $i++) {
    $pkgDef = $allJson.packages[$i]

    if ($pkgDef.package_info.name) {
      $visibleInCI[$pkgDef.package_info.name] = $i
    }
  }

  foreach ($releasingPkg in $pkgs) {
    if ($visibleInCI.ContainsKey($releasingPkg.PackageId)) {
      $packagesIndex = $visibleInCI[$releasingPkg.PackageId]
      $existingPackageDef = $allJson.packages[$packagesIndex]

      if ($releasingPkg.IsPrerelease) {
        if (-not $existingPackageDef.package_info.version) {
          $existingPackageDef.package_info | Add-Member -NotePropertyName version -NotePropertyValue ""
        }

        $existingPackageDef.package_info.version = ">=$($releasingPkg.PackageVersion)"
      }
      else {
        if ($def.version) {
          $def.PSObject.Properties.Remove('version')  
        }
      }
    }
    else {
      $newItem = New-Object PSObject -Property @{ 
          package_info = New-Object PSObject -Property @{ 
            prefer_source_distribution = "true"
            install_type = "pypi"
            name=$releasingPkg.PackageId
          }
          exclude_path = @("test*","example*","sample*","doc*")
        }
      $allJson.packages += $newItem
    }
  }

  $jsonContent = $allJson | ConvertTo-Json -Depth 10 | % {$_ -replace "(?m)  (?<=^(?:  )*)", "  " }

  Set-Content -Path $pkgJsonLoc -Value $jsonContent
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

  $packageName = $artifactName + "-"
  Write-Host "Searching for $($packageName) wheel in artifact path $($artifactDir)"
  $files = Get-ChildItem "${artifactDir}" | Where-Object -FilterScript {$_.Name.StartsWith($packageName) -and $_.Name.EndsWith(".whl")}
  if (!$files)
  {
    Write-Host "$($artifactDir) does not have wheel package for $($packageName)"
    return $null
  }
  elseif($files.Count -ne 1)
  {
    Write-Host "$($artifactDir) should contain only one published wheel package for $($packageName)"
    Write-Host "No of Packages $($files.Count)"
    return $null
  }

  $packages = @{
    $files[0].Name = $files[0].FullName
  }
  return $packages
}

function SetPackageVersion ($PackageName, $Version, $ServiceDirectory, $ReleaseDate, $BuildType=$null, $GroupId=$null)
{
  if($null -eq $ReleaseDate)
  {
    $ReleaseDate = Get-Date -Format "yyyy-MM-dd"
  }
  pip install -r "$EngDir/versioning/requirements.txt" -q -I
  python "$EngDir/versioning/version_set.py" --package-name $PackageName --new-version $Version --service $ServiceDirectory --release-date $ReleaseDate
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
