# Overides the project file and CHANGELOG.md for the template project using the next publishable version
# This is to help with testing the release pipeline.
. "${PSScriptRoot}\..\common\scripts\common.ps1"
$latestTags = git tag -l "azure-template_*"
$semVars = @()

$versionFile = "${PSScriptRoot}\..\..\sdk\template\azure-template\azure\template\_version.py"
$changeLogFile = "${PSScriptRoot}\..\..\sdk\template\azure-template\CHANGELOG.md"

Foreach ($tags in $latestTags)
{
  $semVars += $tags.Replace("azure-template_", "")
}

$semVarsSorted = [AzureEngSemanticVersion]::SortVersionStrings($semVars)
LogDebug "Last Published Version $($semVarsSorted[0])"

$newVersion = [AzureEngSemanticVersion]::ParsePythonVersionString($semVarsSorted[0])
$newVersion.IncrementAndSetToPrerelease()
LogDebug "Version to publish [ $($newVersion.ToString()) ]"

$versionFileContent = Get-Content -Path $versionFile
$newVersionFile = @()

Foreach ($line in $versionFileContent)
{
    if($line.StartsWith("VERSION"))
    {
        $line = 'VERSION = "{0}"' -F $newVersion.ToString()
    }
    $newVersionFile += $line
}

Set-Content -Path $versionFile -Value $newVersionFile
Set-Content -Path $changeLogFile -Value @"
# Release History
## $($newVersion.ToString()) ($(Get-Date -f "yyyy-MM-dd"))
- Test Release Pipeline
"@
