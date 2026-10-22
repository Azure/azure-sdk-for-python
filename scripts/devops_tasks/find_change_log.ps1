
param (
  $workingDir,
  $version
)
$RELEASE_TITLE_REGEX = "(?<releaseNoteTitle>^\#+.*(?<version>\b\d+\.\d+\.\d+([^0-9\s][^\s:]+)?))"


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
    Write-Host "Versions in change log $changeLogLocation"
    foreach($line in $contents){
      if ($line -match $RELEASE_TITLE_REGEX)
      {   
         Write-Host $line     
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


function VerifyPackages($rootDirectory)
{ 
   #This function verifies version in CHANGELOG.md for a given package
   try
   {
      $historyFiles = Get-ChildItem -Path $rootDirectory -Recurse -Include "CHANGELOG.md"
      if ($historyFiles -eq $null)
      { 
         Write-Host "Change log file is missing for package"
         exit(1)
      }

      #Find current version of package from _version.py and package name from setup.py
      $changeFile = @($historyFiles)[0]
      #Get Version and release notes in each change log files
      $releaseNotes = ExtractReleaseNotes -changeLogLocation $changeFile
      if ($releaseNotes.Count -gt 0)
      {
         #Log package if it doesn't have current version in change log
         if ( $releaseNotes.Contains($version))
         {
            $content = $releaseNotes[$version]
            Write-Host "Change log [$changeFile] is updated with current version $version"
            Write-Host "Release notes for version $version"
            Write-Host "****************************************************************************************************"
            Write-Host $content.ReleaseContent
            Write-Host "****************************************************************************************************"
         }
         else
         {
            Write-Host "Change log [$changeFile] does not have current version $version"
            exit(1)
         }            
      }
   }
   catch
   {
      Write-Host "Error verifying version in change log"
      Write-Host $_.Exception.Message
      exit(1)
   }
   
}


if (($workingDir -eq $null) -or ($version -eq $null))
{
   Write-Host "Invalid arguements. workingDir and version are mandatory arguements"
   exit(1)
}

VerifyPackages -rootDirectory $workingDir

