<#
.SYNOPSIS
Saves package properties from source into JSON files

.DESCRIPTION
Saves package properties in source of a given service directory to JSON files.
JSON files are named in the form <package name>.json or <artifact name>.json if
an artifact name property is available in the package properties.

Can optionally add a dev version property which can be used logic for daily 
builds.

In cases of collisions where track 2 packages (IsNewSdk = true) have the same 
filename as track 1 packages (e.g. same artifact name or package name), the
track 2 package properties will be written.

.PARAMETER inputDiffJson
The file containing the result of an invocatio of Generate-PR-Diff.ps1 for a PR. Needed to determine which services have changed.

.PARAMETER outDirectory
Output location (generally a package artifact directory in DevOps) for JSON 
files

.PARAMETER addDevVersion
Reads the version out of the source and adds a DevVersion property to the 
package properties JSON file. If the package properties JSON file already 
exists, read the Version property from the existing package properties JSON file
and set that as the Version property for the new output. This has the effect of
"adding" a DevVersion property to the file which could be different from the 
Verison property in that file.
#>

[CmdletBinding()]
Param (
  [Parameter(Mandatory=$True)]
  [string] $inputDiffJson,
  [Parameter(Mandatory=$True)]
  [string] $outDirectory
)

$inputDiff = Get-Content $inputDiffJson | ConvertFrom-Json

$changedServices = $inputDiff.ChangedServices

if ($changedServices -eq $null -or $changedServices.Count -eq 0) {
    Write-Host "No services have changed. Exiting."
    exit 0
}
else {
    Write-Host "Services that have changed: $changedServices"
}

# todo, handle exit 1 on Save-Package-Properties.ps1 failure
foreach ($service in $changedServices) {
  & $PSScriptRoot/Save-Package-Properties.ps1 -ServiceDirectory $service -OutDirectory $outDirectory
}
