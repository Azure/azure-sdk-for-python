param (
    [string] $ParameterTargetingStringSetting,
    [string] $PackagePropertiesFolder,
    [bool] $IncludeIndirect = $true
)

$setting = $ParameterTargetingStringSetting
$targetingString = $ParameterTargetingStringSetting

# users of internal service builds will set variable "BuildTargetingString" at runtime
# if they want to artificially filter the discovered packages for the build.
# when azure devops sets the variable, it will make it all capital letters, so we should check that
if ($env:BUILDTARGETINGSTRING) {
    $targetingString = $env:BUILDTARGETINGSTRING
}

Write-Host "The resolved targeting string within the script is `"$targetingString`""

if (Test-Path "$PackagePropertiesFolder") {
    $packageProperties = Get-ChildItem -Recurse -Force "$PackagePropertiesFolder/*.json" `

    if (-not $IncludeIndirect) {
        $packageProperties = Get-ChildItem -Recurse -Force "$PackagePropertiesFolder/*.json" `
            | Where-Object {
                $includedForValidation = (Get-Content -Raw $_ | ConvertFrom-Json).IncludedForValidation
                if ($includedForValidation -eq $true) {
                    Remove-Item $_.FullName; $false
                } else { $true }
            }
    }

    $packageProperties = $packageProperties
        | Where-Object { if ($_.Name.Replace(".json", "") -like "$targetingString") { return $true } else { Remove-Item $_.FullName; return $false; } }
        | ForEach-Object { $_.Name.Replace(".json", "") }

    $setting = $packageProperties -join ","

    # in case we don't expect any packages, we should set the variable to null, which will match NO packages and cause whatever the check
    # is to skip with exit 0 (which is what we want!)
    if (-not $setting) {
        $setting = "null"
    }
}

Write-Host "##vso[task.setvariable variable=TargetingString;]$setting"
