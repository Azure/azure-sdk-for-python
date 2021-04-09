  
#Requires -Version 6.0
# This script is intended to update docs.ms CI configuration (currently supports Java, Python, C#, JS) in nightly build
# For details on calling, check `docindex.yml`. 

# In this script, we will do the following business logic.
# 1. Filter out the packages from release csv file by `New=true`, `Hide!=true`
# 2. Compare current package list with the csv packages, and keep them in sync. Leave other packages as they are.
# 3. Update the tarage packages back to CI config files. 
param (
  [Parameter(Mandatory = $true)]
  $DocRepoLocation, # the location of the cloned doc repo

  [Parameter(Mandatory = $true)]
  $Configs, # The configuration elements informing important locations within the cloned doc repo

  [Parameter(Mandatory = $false)]
  $ScriptRepository = "eng/common/scripts"# The eng/common script path
)

. (Join-Path $ScriptRepository common.ps1)

$docLoc = ($Configs | ConvertFrom-Json).targets

if ($UpdateDocCIFn -and (Test-Path "Function:$UpdateDocCIFn"))
{
  &$UpdateDocCIFn -ciRepo $DocRepoLocation -locationInDocRepo $docLoc
}
else
{
  LogWarning "The function for '$UpdateDocCIFn' was not found.`
  Make sure it is present in eng/scripts/Language-Settings.ps1 and referenced in eng/common/scripts/common.ps1.`
  See https://github.com/Azure/azure-sdk-tools/blob/master/doc/common/common_engsys.md#code-structure"
}