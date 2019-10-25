
param (
  $workingDir,
  $service
)
$RELEASE_TITLE_REGEX = "(?<releaseNoteTitle>^\#+.*(?<version>\b\d+\.\d+\.\d+([^0-9\s][^\s:]+)?))"
$VERSION_REGEX = "(?<version>\b\d+\.\d+\.\d+([^0-9\s][^\s:""']+)?)"
$PACKAGE_NAME = "^PACKAGE_NAME\s*=\s*[\'""](?<name>\b[^\'""]*)[\'""]"

function ExtractReleaseNotes($changeLogLocation)
{
  $releaseNotes = @{}
  $contentArrays = @{}
  if ($changeLogLocation.Length -eq 0)
  {
    return $releaseNotes
  }

  try {
    $contents = Get-Content $changeLogLocation

    # walk the document, finding where the version specifiers are and creating lists
    $version = ""
    foreach($line in $contents){
      if ($line -match $RELEASE_TITLE_REGEX)
      {
        $version = $matches["version"]
        $contentArrays[$version] = @()
      }

      $contentArrays[$version] += $line
    }

    # resolve each of discovered version specifier string arrays into real content
    foreach($key in $contentArrays.Keys)
    {
      $releaseNotes[$key] = New-Object PSObject -Property @{
        ReleaseVersion = $key
        ReleaseContent = $contentArrays[$key] -join [Environment]::NewLine
      }
    }
  }
  catch
  {
    Write-Host "Error parsing $changeLogLocation."
    Write-Host $_.Exception.Message
  }

  return $releaseNotes
}

function shouldSkipPackage($pkgName)
{
  #Inlcude any package name that needs to be excluded from verifying current version in change log
  $excludedPkgs = @('azure-sdk-for-python','azure-sdk-tools','azure-servicemanagement-legacy')

  return $excludedPkgs.Contains($pkgName) -or ($pkgName.Contains('-mgmt-')) -or ($pkgName.Contains('-nspkg'))
}

function ParseFile($fileName, $regex, $groupName, $directory)
{
  #This is helper function to parse a file to find given regex
  #Currently this is used to parse _version.py and setup.py to get version and package name
  #Validate all arguements
  if(($fileName -eq $null) -or
     ($regex -eq $null) -or
     ($groupName -eq $null) -or
     ($directory -eq $null))
  {
     Write-Host "Invalid arguements to parse file"
     Write-Host "fileName: $fileName, regex: $regex, groupName: $groupName, directory: $directory"
     return $null
  }

  try
  {
     #Find files with given name
     $files = @(Get-ChildItem -Path $directory -Recurse -Include $fileName)
     if (($files -eq $null) -or ($files.Count -eq 0))
     {
        Write-Host "No files found with name $fileName in path [$directory]"
        return $null
     }

     $file = $files[0]
     $contents = Get-Content $file
     foreach($line in $contents)
     {
        if ($line -match $regex)
        {
           $value = $matches[$groupName]
           return $value
        }
     }

  }
  catch
  {
     Write-Host "Exception when parsing $fileName in path $directory"     
  }
  
  Write-Host "Regex $regex did not find any match in file $fileName"
  return $null
}

function GetPackageDetails($historyFile)
{ 
  #This function return current version and package name for a given history.md file
  $pkgDir = Join-Path -Path $historyFile.Directory.FullName -ChildPath "\azure*"
  #This function returns package name and current version for a given change.log
  try
  {
     $version = ParseFile -fileName "_version.py" -regex $VERSION_REGEX -groupName "version" -directory $pkgDir
     if($version -eq $null)
     {
        Write-Host "Current version info is not available in path $pkgDir"
        return $null
     }
     
     $pkgRootDir = $historyFile.Directory.FullName
     $pkgName = ParseFile -fileName "setup.py" -regex $PACKAGE_NAME -groupName "name" -directory $historyFile.Directory.FullName
     if($pkgName -eq $null)
     {
        Write-Host "Current version info is not available in path $pkgRootDir"
        return $null
     }
     
     return New-Object PSObject -Property @{
       Name = $pkgName
       Version = $version
     }

  }
  catch
  {
     Write-Host "Exception when retrieving version from _version_py in $pkgDir"
     return $null
  }
}

function GetHistoryFilePaths($rootDirectory)
{
  #This function returns package name and version for packages within current working directory
  if ($rootDirectory -eq $null)
  {
     Write-Host "Root directory to search for history.md is empty"
     return $null
  }

  try
  {
     #Get all history.md file locations  
     $historyFiles = Get-ChildItem -Path $rootDirectory -Recurse -Include "history.md"
     return $historyFiles
  }
  catch
  {
     Write-Host 'Failed to find history.md file for service $service'
     return $null
  }  
}

function VerifyPackages($rootDirectory)
{ 
  #This function identifies all packages with history.md file for a given service and verify version in release notes
  $ChangeMissingPkgs = @{}
  $historyFiles = GetHistoryFilePaths -rootDirectory $rootDirectory
  if ($historyFiles -eq $null)
  { 
     Write-Host "history.md file is missing in root directory $rootDirectory"
     return $changeMissingPkgs
  }

  #Find current version of package from _version.py and package name from setup.py
  foreach($changeFile in $historyFiles)
  {
     #Get Version and release notes in each change log files
     $releaseNotes = ExtractReleaseNotes -changeLogLocation $changeFile
     if ($releaseNotes.Count -gt 0)
     {
        #Get package name and version from setup.py and _version.py for current change.log's package
        $pkg = GetPackageDetails -historyFile $changeFile
        if($pkg -ne $null)
        {
           $version = $pkg.Version
           $name = $pkg.Name

           #Check if this package needs to be skipped
           $shouldSkip = ShouldSkipPackage - pkgName $name
           if ($shouldSkip)
           {
              Write-Host "Package $name is skipped verifying change log"
              continue
           }     
           
           #Log package if it doesn't have current version in history.md
           if ( -not($releaseNotes.Contains($version)))
           {
              Write-Host "Change log in path $name doesn't have current version $version"
              $ChangeMissingPkgs[$name] = $version
           }            
        }       
     }     
  }

  return $ChangeMissingPkgs
}

$serviceRootDir = $workingDir +"\sdk\"+$service
$ChangeMissingPkgs = VerifyPackages -rootDirectory $serviceRootDir
if ( $ChangeMissingPkgs.Count -gt 0)
{
   foreach($pkgName in $ChangeMissingPkgs.Keys)
   {
      $value = $changeMissingPkgs.item($pkgName)
      Write-Host "Package $pkgName doesn't have change log for version $value"
   }
   exit(1)
}
else
{
   Write-Host "Change log is updated with current version for $service"
}
