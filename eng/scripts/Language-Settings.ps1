$Language = "python"
$Lang = "python"
$PackageRepository = "PyPI"
$packagePattern = "*.zip"
$MetadataUri = "https://raw.githubusercontent.com/Azure/azure-sdk/master/_data/releases/latest/python-packages.csv"

function Get-python-PackageInfoFromRepo ($pkgPath, $serviceName, $pkgName)
{
  $pkgName = $pkgName.Replace('_', '-')
  if (Test-Path (Join-Path $pkgPath "setup.py"))
  {
    $setupLocation = $pkgPath.Replace('\', '/')
    Push-Location $RepoRoot
    $setupProps = (python -c "import sys; import os; sys.path.append(os.path.join('scripts', 'devops_tasks')); from common_tasks import parse_setup; obj=parse_setup('$setupLocation'); print('{0},{1}'.format(obj[0], obj[1]));") -split ","
    Pop-Location
    if (($setupProps -ne $null) -and ($setupProps[0] -eq $pkgName))
    {
      return [PackageProps]::new($setupProps[0], $setupProps[1], $pkgPath, $serviceName)
    }
  }
  return $null
}

# Returns the pypi publish status of a package id and version.
function IsPythonPackageVersionPublished($pkgId, $pkgVersion)
{
  try 
  {
    $existingVersion = (Invoke-RestMethod -MaximumRetryCount 3 -Method "Get" -Uri "https://pypi.org/pypi/$pkgId/$pkgVersion/json").info.version
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
function Get-python-PackageInfoFromPackageFile($pkg, $workingDirectory)
{
  $pkg.Basename -match $SDIST_PACKAGE_REGEX | Out-Null

  $pkgId = $matches["package"]
  $pkgVersion = $matches["versionstring"]

  $workFolder = "$workingDirectory$($pkg.Basename)"
  $origFolder = Get-Location
  $releaseNotes = ""
  $readmeContent = ""

  New-Item -ItemType Directory -Force -Path $workFolder
  Expand-Archive -Path $pkg -DestinationPath $workFolder

  $changeLogLoc = @(Get-ChildItem -Path $workFolder -Recurse -Include "CHANGELOG.md")[0]
  if ($changeLogLoc)
  {
    $releaseNotes = Get-ChangeLogEntryAsString -ChangeLogLocation $changeLogLoc -VersionString $pkgVersion
  }

  $readmeContentLoc = @(Get-ChildItem -Path $workFolder -Recurse -Include "README.md") | Select-Object -Last 1

  if ($readmeContentLoc)
  {
    $readmeContent = Get-Content -Raw $readmeContentLoc
  }

  Remove-Item $workFolder -Force -Recurse -ErrorAction SilentlyContinue

  return New-Object PSObject -Property @{
    PackageId = $pkgId
    PackageVersion = $pkgVersion
    Deployable = $forceCreate -or !(IsPythonPackageVersionPublished -pkgId $pkgId -pkgVersion $pkgVersion)
    ReleaseNotes = $releaseNotes
    ReadmeContent = $readmeContent
  }
}

# Stage and Upload Docs to blob Storage
function Publish-python-GithubIODocs()
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

    Upload-Blobs -DocDir $UnzippedDocumentationPath -PkgName $PkgName -DocVersion $Version
  }
}