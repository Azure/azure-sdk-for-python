$Language = "python"
$LanguageDisplayName = "Python"
$PackageRepository = "PyPI"
$packagePattern = "*.tar.gz"
$MetadataUri = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
$GithubUri = "https://github.com/Azure/azure-sdk-for-python"
$PackageRepositoryUri = "https://pypi.org/project"

."$PSScriptRoot/docs/Docs-ToC.ps1"
."$PSScriptRoot/docs/Docs-Onboarding.ps1"

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

# Parse out package publishing information given a python sdist of tar.gz format.
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
  Write-Host "Python Trust Methodology"

  $pathToScript = Resolve-Path (Join-Path -Path $PSScriptRoot -ChildPath "../../scripts/devops_tasks/trust_proxy_cert.py")
  python -m pip install requests
  python $pathToScript
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
#    doesn't handle the autodoc_default_options on the
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
  #
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

      # Because this would be running on a lab image, a virtual environment shouldn't be required
      Write-Host "Executing: python -m py2docfx --param-file-path $outputJsonFile -o $outputDocsDir --no-venv-required"
      #$py2docfxOutput = python -m py2docfx --param-file-path $outputJsonFile -o $outputDocsDir --no-venv-required 2>&1
      python -m py2docfx --param-file-path $outputJsonFile -o $outputDocsDir --no-venv-required
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