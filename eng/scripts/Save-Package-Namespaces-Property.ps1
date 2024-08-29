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

.PARAMETER ArtifactsList
The list of artifacts to gather namespaces for, this is only done for libraries that are
producing docs.
-ArtifactsList ('${{ convertToJson(parameters.Artifacts) }}' | ConvertFrom-Json)
#>
[CmdletBinding()]
Param (
    [Parameter(Mandatory = $True)]
    [string] $ArtifactStagingDirectory,
    [Parameter(Mandatory=$true)]
    [array] $ArtifactsList
)

$ArtifactsList = $ArtifactsList | Where-Object -Not "skipPublishDocMs"

. (Join-Path $PSScriptRoot ".." common scripts common.ps1)

if (-not $ArtifactsList) {
    Write-Host "ArtifactsList is empty, nothing to process. This can happen if skipPublishDocMs is set to true for all libraries being built."
    exit 0
}

Write-Host "ArtifactStagingDirectory=$ArtifactStagingDirectory"
if (-not (Test-Path -Path $ArtifactStagingDirectory)) {
    LogError "ArtifactStagingDirectory '$ArtifactStagingDirectory' does not exist."
    exit 1
}

Write-Host ""
Write-Host "ArtifactsList:"
$ArtifactsList | Format-Table -Property Name | Out-String | Write-Host

$packageInfoDirectory = Join-Path $ArtifactStagingDirectory "PackageInfo"

$foundError = $false
# At this point the packageInfo files should have been already been created.
# The only thing being done here is adding or updating namespaces for libraries
# that will be producing docs.
foreach($artifact in $ArtifactsList) {
    # Get the version from the packageInfo file
    $packageInfoFile = Join-Path $packageInfoDirectory "$($artifact.Name).json"
    Write-Host "processing $($packageInfoFile.FullName)"
    $packageInfo = ConvertFrom-Json (Get-Content $packageInfoFile -Raw)
    $version = $packageInfo.Version
    # If the dev version is set, use that. This will be set for nightly builds
    if ($packageInfo.DevVersion) {
      $version = $packageInfo.DevVersion
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