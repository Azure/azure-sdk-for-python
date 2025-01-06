$Language = "python"
$LanguageDisplayName = "Python"
$PackageRepository = "PyPI"
$packagePattern = "*.tar.gz"
$MetadataUri = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
$GithubUri = "https://github.com/Azure/azure-sdk-for-python"
$PackageRepositoryUri = "https://pypi.org/project"

."$PSScriptRoot/docs/Docs-ToC.ps1"
."$PSScriptRoot/docs/Docs-Onboarding.ps1"

function Get-python-AdditionalValidationPackagesFromPackageSet {
  param(
    [Parameter(Mandatory=$true)]
    $LocatedPackages,
    [Parameter(Mandatory=$true)]
    $diffObj,
    [Parameter(Mandatory=$true)]
    $AllPkgProps
  )
  $additionalValidationPackages = @()
  $uniqueResultSet = @()

  function isOther($fileName) {
    $startsWithPrefixes = @(".config", ".devcontainer", ".github", ".vscode", "common", "conda", "doc", "eng", "scripts")

    $startsWith = $false
    foreach ($prefix in $startsWithPrefixes) {
      if ($fileName.StartsWith($prefix)) {
        $startsWith = $true
      }
    }

    return $startsWith
  }

  # this section will identify the list of packages that we should treat as
  # "directly" changed for a given service level change. While that doesn't
  # directly change a package within the service, I do believe we should directly include all
  # packages WITHIN that service. This is because the service level file changes are likely to
  # have an impact on the packages within that service.
  $changedServices = @()
  if ($diffObj.ChangedFiles) {
    foreach($file in $diffObj.ChangedFiles) {
      $pathComponents = $file -split "/"
      # handle changes only in sdk/<service>/<file>/<extension>
      if ($pathComponents.Length -eq 3 -and $pathComponents[0] -eq "sdk") {
        $changedServices += $pathComponents[1]
      }

      # handle any changes under sdk/<file>.<extension>
      if ($pathComponents.Length -eq 2 -and $pathComponents[0] -eq "sdk") {
        $changedServices += "template"
      }
    }
    foreach ($changedService in $changedServices) {
      $additionalPackages = $AllPkgProps | Where-Object { $_.ServiceDirectory -eq $changedService }

      foreach ($pkg in $additionalPackages) {
        if ($uniqueResultSet -notcontains $pkg -and $LocatedPackages -notcontains $pkg) {
          # notice the lack of setting IncludedForValidation to true. This is because these "changed services"
          # are specifically where a file within the service, but not an individual package within that service has changed.
          # we want this package to be fully validated
          $uniqueResultSet += $pkg
        }
      }
    }
  }

  $toolChanged = @()
  $othersChanged = @()
  $engChanged = @()

  if ($diffObj.ChangedFiles) {
    $toolChanged = $diffObj.ChangedFiles | Where-Object { $_.StartsWith("tool")}
    $engChanged = $diffObj.ChangedFiles | Where-Object { $_.StartsWith("eng")}
    $othersChanged = $diffObj.ChangedFiles | Where-Object { isOther($_) }
  }

  $changedServices = $changedServices | Get-Unique

  if ($toolChanged) {
    $additionalPackages = @(
      "azure-storage-blob",
      "azure-servicebus",
      "azure-eventhub",
      "azure-data-table",
      "azure-appconfig",
      "azure-keyvault-keys",
      "azure-identity",
      "azure-mgmt-core",
      "azure-core-experimental",
      "azure-core-tracing-opentelemetry",
      "azure-core-tracing-opencensus",
      # "azure-cosmos", leave removed until we resolve what to do with the emulator tests
      "azure-ai-documentintelligence",
      "azure-ai-ml",
      "azure-ai-inference",
      "azure-ai-textanalytics",
      "azure-ai-doctranslation",
      "azure-mgmt-compute",
      "azure-communication-chat",
      "azure-communication-identity"
    ) | ForEach-Object { $me=$_; $AllPkgProps | Where-Object { $_.Name -eq $me } | Select-Object -First 1 }

    $additionalValidationPackages += $additionalPackages
  }

  if ($engChanged -or $othersChanged) {
    $additionalPackages = @(
      "azure-template",
      "azure-core"
    ) | ForEach-Object { $me=$_; $AllPkgProps | Where-Object { $_.Name -eq $me } | Select-Object -First 1 }

    $additionalValidationPackages += $additionalPackages
  }


  foreach ($pkg in $additionalValidationPackages) {
    if ($uniqueResultSet -notcontains $pkg -and $LocatedPackages -notcontains $pkg) {
      $pkg.IncludedForValidation = $true
      $uniqueResultSet += $pkg
    }
  }

  Write-Host "Returning additional packages for validation: $($uniqueResultSet.Count)"
  foreach ($pkg in $uniqueResultSet) {
    Write-Host "  - $($pkg.Name)"
  }

  return $uniqueResultSet
}

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
    $null = python -m pip install "./tools/azure-sdk-tools[build]" -q -I
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

    $additionalValidationPackages = $pkgInfo[4] -Split ","

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
    $pkgProp.AdditionalValidationPackages = $additionalValidationPackages
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

# Parse out package publishing information given a python sdist of tar.gz format.
function Get-python-PackageInfoFromPackageFile ($pkg, $workingDirectory)
{
  $pkg.Basename -match $SDIST_PACKAGE_REGEX | Out-Null

  $pkgId = $matches["package"]
  $pkgId = $pkgId.Replace("_","-")
  $docsReadMeName = $pkgId -replace "^azure-" , ""

  $pkgVersion = $matches["versionstring"]

  $workFolder = "$workingDirectory$($pkg.Basename)"
  $origFolder = Get-Location
  $releaseNotes = ""
  $readmeContent = ""

  New-Item -ItemType Directory -Force -Path $workFolder
  Write-Host "tar -zxvf $pkg -C $workFolder"
  tar -zxvf $pkg -C $workFolder

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

# This is the GetDocsMsDevLanguageSpecificPackageInfoFn implementation
# Defined in common.ps1 as:
# $GetDocsMsDevLanguageSpecificPackageInfoFn = "Get-${Language}-DocsMsDevLanguageSpecificPackageInfo"
function Get-python-DocsMsDevLanguageSpecificPackageInfo($packageInfo, $packageSourceOverride) {
  # If the default namespace isn't in the package info then it needs to be added
  # Can't check if (!$packageInfo.Namespaces) in strict mode because Namespaces won't exist
  # at all.
  if (!($packageInfo | Get-Member Namespaces)) {
    # If the Version is INGORE that means it's a source install and those
    # ones need to be done by hand
    if ($packageInfo.Version -ine "IGNORE") {
      $version = $packageInfo.Version
      # If the dev version is set, use that
      if ($packageInfo.DevVersion) {
        $version = $packageInfo.DevVersion
      }
      $namespaces = Get-NamespacesFromWhlFile $packageInfo.Name $version $packageSourceOverride
      if ($namespaces.Count -gt 0) {
        $packageInfo | Add-Member -Type NoteProperty -Name "Namespaces" -Value $namespaces
      } else {
        LogWarning "Unable to find namespaces for $($packageInfo.Name):$version, using the package name."
        $tempNamespaces = @()
        $tempNamespaces += $packageInfo.Name
        $packageInfo | Add-Member -Type NoteProperty -Name "Namespaces" -Value $tempNamespaces
      }
    }
  }
  return $packageInfo
}

# Stage and Upload Docs to blob Storage
function Publish-python-GithubIODocs ($DocLocation, $PublicArtifactLocation)
{
  $PublishedDocs = Get-ChildItem "$DocLocation" | Where-Object -FilterScript {$_.Name.EndsWith(".tar.gz")}

  foreach ($Item in $PublishedDocs)
  {
    $PkgName = $Item.BaseName.Replace(".tar", "")
    $ZippedDocumentationPath = Join-Path -Path $DocLocation -ChildPath $Item.Name
    $UnzippedDocumentationPath = Join-Path -Path $DocLocation -ChildPath $PkgName
    $VersionFileLocation = Join-Path -Path $UnzippedDocumentationPath -ChildPath "version.txt"

    if (!(Test-Path $UnzippedDocumentationPath)) {
      New-Item -Path $UnzippedDocumentationPath -ItemType Directory
    }

    Write-Host "tar -zxvf $ZippedDocumentationPath -C $UnzippedDocumentationPath"
    tar -zxvf $ZippedDocumentationPath -C $UnzippedDocumentationPath

    if ($LASTEXITCODE -ne 0) {
      Write-Error "tar failed with exit code $LASTEXITCODE."
      exit $LASTEXITCODE
    }

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
  $artifacts = Get-BlobStorage-Artifacts `
    -blobDirectoryRegex "^python/(.*)/$" `
    -blobArtifactsReplacement '$1' `
    -storageAccountName 'azuresdkdocs' `
    -storageContainerName '$web' `
    -storagePrefix 'python/'
  # Build up the artifact to service name mapping for GithubIo toc.
  $tocContent = Get-TocMapping -metadata $metadata -artifacts $artifacts
  # Generate yml/md toc files and build site.
  GenerateDocfxTocContent -tocContent $tocContent -lang "Python" -campaignId "UA-62780441-36"
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

  $packageName = $artifactName.Replace("_","-")
  $whlDirectory = (Join-Path -Path $artifactDir -ChildPath $packageName)

  Write-Host "Searching for $($artifactName) wheel in artifact path $($whlDirectory)"
  $files = @(Get-ChildItem $whlDirectory | ? {$_.Name.EndsWith(".whl")})
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

  # Python requires pregenerated token file in addition to wheel to generate API review.
  # Make sure that token file exists in same path as wheel file.
  $tokenFile = Join-Path -Path $whlDirectory -ChildPath "${packageName}_${Language}.json"
  if (!(Test-Path $tokenFile))
  {
    Write-Host "API review token file for $($tokenFile) does not exist in path $($whlDirectory). Skipping API review for $packageName"
    return $null
  }
  else
  {
    Write-Host "Found API review token file for $($tokenFile)"
  }

  $packages = @{
    $files[0].Name = $files[0].FullName
  }
  return $packages
}

function SetPackageVersion ($PackageName, $Version, $ServiceDirectory, $ReleaseDate, $ReplaceLatestEntryTitle=$True)
{
  if($null -eq $ReleaseDate)
  {
    $ReleaseDate = Get-Date -Format "yyyy-MM-dd"
  }
  python -m pip install "$RepoRoot/tools/azure-sdk-tools[build]" -q -I
  sdk_set_version --package-name $PackageName --new-version $Version `
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
    if ($_.Exception.Response.StatusCode -ne 404)
    {
      LogError "Failed to retrieve package versions for ${PackageName}. $($_.Exception.Message)"
    }
    return $null
  }
}

# Defined in common.ps1 as:
# GetDocsMsMetadataForPackageFn = Get-${Language}-DocsMsMetadataForPackage
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
    LegacyReadMeLocation  = 'docs-ref-services/legacy'
    Suffix = ''
  }
}

function Import-Dev-Cert-python
{
  Write-Host "Python no longer requires an out of proc trust methodology." `
    "The variables SSL_CERT_DIR, SSL_CERT_FILE, and REQUESTS_CA_BUNDLE are now dynamically set in proxy_startup.py"
}

function Get-python-EmitterName() {
  return "@azure-tools/typespec-python"
}

function Get-python-EmitterAdditionalOptions([string]$projectDirectory) {
  return "--option @azure-tools/typespec-python.emitter-output-dir=$projectDirectory/"
}

function Get-python-DirectoriesForGeneration () {
  return Get-ChildItem "$RepoRoot/sdk" -Directory
  | Get-ChildItem -Directory
  | Where-Object { $_ -notmatch "-mgmt-" }
  | Where-Object { (Test-Path "$_/tsp-location.yaml") }
  # TODO: Reenable swagger generation when tox generate supports arbitrary generator versions
  # -or (Test-Path "$_/swagger/README.md")
}

function Update-python-GeneratedSdks([string]$PackageDirectoriesFile) {
  $packageDirectories = Get-Content $PackageDirectoriesFile | ConvertFrom-Json

  $directoriesWithErrors = @()

  foreach ($directory in $packageDirectories) {
    Push-Location $RepoRoot/sdk/$directory
    try {
      Write-Host "`n`n======================================================================"
      Write-Host "Generating project under directory 'sdk/$directory'" -ForegroundColor Yellow
      Write-Host "======================================================================`n"

      $toxConfigPath = Resolve-Path "$RepoRoot/eng/tox/tox.ini"
      Invoke-LoggedCommand "tox run -e generate -c `"$toxConfigPath`" --root ."
    }
    catch {
      Write-Host "##[error]Error generating project under directory $directory"
      Write-Host $_.Exception.Message
      $directoriesWithErrors += $directory
    }
    finally {
      Pop-Location
    }
  }

  if($directoriesWithErrors.Count -gt 0) {
    Write-Host "##[error]Generation errors found in $($directoriesWithErrors.Count) directories:"

    foreach ($directory in $directoriesWithErrors) {
      Write-Host "  $directory"
    }

    exit 1
  }
}