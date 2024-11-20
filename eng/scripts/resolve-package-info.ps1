param (
    [string] $ParameterTargetingStringSetting,
    [string] $PackagePropertiesFolder,
    [string] $IncludeIndirect = "true"
)

$setting = $ParameterTargetingStringSetting
$targetingString = $ParameterTargetingStringSetting

Write-Host "I see the following for env:BuildTargetingString"
Write-Host $env:BuildTargetingString
Write-Host "I see the following for env:BUILDTARGETINGSTRING"
Write-Host $env:BUILDTARGETINGSTRING

# users of internal service builds will set variable "BuildTargetingString" at runtime
# if they want to artificially filter the discovered packages for the build.
# when azure devops sets the variable, it will make it all capital letters, so we should check that
if ($env:BUILDTARGETINGSTRING) {
    $targetingString = $env:BUILDTARGETINGSTRING
}

if (Test-Path "$PackagePropertiesFolder") {
    if ($IncludeIndirect -eq "true") {
        $packageProperties = Get-ChildItem -Recurse -Force "$PackagePropertiesFolder/*.json" `
            | Where-Object { if ($_.Name.Replace(".json", "") -like "$targetingString") { return $true } else { Remove-Item $_.FullName; return $false; } }
            | ForEach-Object { $_.Name.Replace(".json", "") }
    }
    else {
        $packageProperties = Get-ChildItem -Recurse -Force "$PackagePropertiesFolder/*.json" `
        | Where-Object { (Get-Content -Raw $_ | ConvertFrom-Json).IncludedForValidation -eq $false } `
        | Where-Object { if ($_.Name.Replace(".json", "") -like "$targetingString") { return $true } else { Remove-Item $_.FullName; return $false; } }
        | ForEach-Object { $_.Name.Replace(".json", ""); }
    }

    $setting = $packageProperties -join ","

    # in case we don't expect any packages, we should set the variable to null, which will match NO packages and cause whatever the check
    # is to skip with exit 0 (which is what we want!)
    if (-not $setting) {
        $setting = "null"
    }
}

Write-Host "##vso[task.setvariable variable=TargetingString;]$setting"