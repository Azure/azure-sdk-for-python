<#
.SYNOPSIS
Given an artifact staging directory and the artifacts list, loop through all artifacts
that docs that aren't skipping docs creation and add the namespace to the PackageInfo
json file.

.DESCRIPTION
Given an artifact staging directory and the artifacts list, loop through all artifacts
that docs that aren't skipping docs creation and add the namespace to the PackageInfo
json file. This is done using the .whl file from the build.

.PARAMETER ArtifactStagingDirectory
The root directory of the staged artifacts. The PackageInfo files will be in the
PackageInfo subdirectory. The whl files are going to be in the subdirectory which
is the same as the artifact's name but artifact name in the file's name will have
 underscores instead of dashes.

.PARAMETER RepoRoot
The root of the directory. This will be used in combination with the paths of of
the properties within each PackageInfo file to determine the full path to other relevant
metadata...like ci.yml for instance.
#>
[CmdletBinding()]
Param (
    [Parameter(Mandatory = $True)]
    [string] $ArtifactStagingDirectory
)
.  (Join-Path $PSScriptRoot ".." common scripts Helpers PSModule-Helpers.ps1)
Install-ModuleIfNotInstalled "powershell-yaml" "0.4.1" | Import-Module

. (Join-Path $PSScriptRoot ".." common scripts common.ps1)

function ShouldPublish ($ServiceDirectory, $PackageName) {
    $ciYmlPath = Join-Path $ServiceDirectory "ci.yml"

    Write-Host $PackageName

    if (Test-Path $ciYmlPath)
    {
        Write-Host $ciYmlPath
        $ciYml = ConvertFrom-Yaml (Get-Content $ciYmlPath -Raw)

        if ($ciYml.extends -and $ciYml.extends.parameters -and $ciYml.extends.parameters.Artifacts) {
            $packagesBuildingDocs = $ciYml.extends.parameters.Artifacts `
                | Where-Object { -not ($_["skipPublishDocMs"] -eq $true) }
                | Select-Object -ExpandProperty name

            if ($packagesBuildingDocs -contains $PackageName)
            {
                Write-Host $packagesBuildingDocs
                return $true
            }
            else {
                return $false
            }
        }
    }
}

Write-Host "ArtifactStagingDirectory=$ArtifactStagingDirectory"
if (-not (Test-Path -Path $ArtifactStagingDirectory)) {
    LogError "ArtifactStagingDirectory '$ArtifactStagingDirectory' does not exist."
    exit 1
}

$packageInfoDirectory = Join-Path $ArtifactStagingDirectory "PackageInfo"
$foundError = $false
$artifacts = Get-ChildItem -Path $packageInfoDirectory -File -Filter "*.json"
$artifacts | Format-Table -Property Name | Out-String | Write-Host

if (-not $artifacts) {
    Write-Host "Artifacts list is empty, nothing to process. This can happen if skipPublishDocMs is set to true for all libraries being built."
    exit 0
}

# by this point, the PackageInfo folder will have a json file for each artifact
# we simply need to read each file, get the appropriate metadata, and add the namespaces if necessary
foreach($packageInfoFile in $artifacts) {
    # Get the version from the packageInfo file
    Write-Host "processing $($packageInfoFile.FullName)"
    $packageInfo = ConvertFrom-Json (Get-Content $packageInfoFile -Raw)
    $version = $packageInfo.Version
    # If the dev version is set, use that. This will be set for nightly builds
    if ($packageInfo.DevVersion) {
      $version = $packageInfo.DevVersion
    }

    if (-not (ShouldPublish -ServiceDirectory (Join-Path $RepoRoot "sdk" $packageInfo.ServiceDirectory) -PackageName $packageInfo.Name)) {
        Write-Host "Skipping publishing docs for $($packageInfo.Name)"
        continue
    }


    # From the $packageInfo piece together the path to the javadoc jar file
    $WhlDir = Join-Path $ArtifactStagingDirectory $packageInfo.Name
    $WhlName = $packageInfo.Name.Replace("-","_")
    $WhlFile = Get-ChildItem -Path $WhlDir -File -Filter "$whlName-$version*.whl"

    if (!(Test-Path $WhlFile -PathType Leaf)) {
        LogError "Whl file for, $($packageInfo.Name), was not found in $WhlDir. Please ensure that a .whl file is being produced for the library."
        $foundError = $true
        continue
    }
    $namespaces = Get-NamespacesFromWhlFile $packageInfo.Name $version -PythonWhlFile $WhlFile
    if ($namespaces.Count -gt 0) {
        Write-Host "Adding/Updating Namespaces property with the following namespaces:"
        $namespaces | Write-Host
        if ($packageInfo.PSobject.Properties.Name -contains "Namespaces") {
            Write-Host "Contains Namespaces property, updating"
            $packageInfo.Namespaces = $namespaces
        }
        else {
            Write-Host "Adding Namespaces property"
            $packageInfo = $packageInfo | Add-Member -MemberType NoteProperty -Name Namespaces -Value $namespaces -PassThru
        }
        $packageInfoJson = ConvertTo-Json -InputObject $packageInfo -Depth 100
        Write-Host "The updated packageInfo for $packageInfoFile is:"
        Write-Host "$packageInfoJson"
        Set-Content `
            -Path $packageInfoFile `
            -Value $packageInfoJson
    } else {
        LogError "Unable to determine namespaces for $($packageInfo.Name). Please ensure that skipPublishDocMs isn't incorrectly set to true."
        $foundError = $true
    }
}

if ($foundError) {
    exit 1
}
exit 0