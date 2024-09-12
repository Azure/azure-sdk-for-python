<#
.SYNOPSIS
Distributes a set of packages to a platform matrix file by adding TargetingString property dynamically.
If an unexpected situation is encountered, the script will make no changes to the input file.

.DESCRIPTION
Because of the way the platform matrix file is structured, we need to distribute the packages in a way that
honors the Include packages. We have these included this way because want to ensure that these python versions
run on that platform. This is aware of these additional configurations and will set TargetingString for them as well.
#>
param(
    [parameter(Mandatory=$true)]
    [string]$PackageInfoFolder,
    [parameter(Mandatory=$true)]
    [string]$PlatformMatrix
)

Set-StrictMode -Version 4

if (!(Test-Path $PackageInfoFolder)) {
    Write-Error "PackageInfo folder file not found: $PackageInfoFolder"
    exit 1
}

if (!(Test-Path $PlatformMatrix)) {
    Write-Error "Platform matrix file not found: $PlatformMatrix"
    exit 1
}

$packageProperties = Get-ChildItem -Recurse "$PackageInfoFolder" *.json | % { Get-Content -Path $_.FullName | ConvertFrom-Json }
$matrix = Get-Content -Path $PlatformMatrix | ConvertFrom-Json

$versionCount = $matrix.matrix.PythonVersion.Count
$includeCount = 0
if ($matrix.PSObject.Properties.Name -contains "include") {
    $includeCount = $matrix.include.Count
}
$batchCount = $versionCount + $includeCount
if ($batchCount -eq 0) {
    Write-Error "No batches detected, skipping without updating platform matrix file $PlatformMatrix"
    exit 1
}

$batchSize = 5

# batches is a hashtable because you cannot instantiate an array of empty arrays
# the add method will merely invoke and silently NOT add a new item
# using a hashtable bypasses this limitation
$batches = @{}
for ($i = 0; $i -lt $batchCount; $i++) {
    $batches[$i] = @()
}

$batchCounter = 0
$batchValues = @()

# if there is an IMPORT, we should import that first and use THAT. we have a clear edge case where a nested include will NOT work.
# I am accepting that in interests of making this work with all our platform matrix json files throughout the repo
# TODO: implement grabbing the matrix from the import if it exists

$directIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $false }
$indirectIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $true }

# for python, for fast tests, I want the sets of packages to be broken up into sets of five.

# I will assign all the direct included packages first. our goal is to get complete coverage of the direct included packages
# then, for the indirect packages, we will ADD them as extra TargetingString bundles to the matrix.
# this means that these "extra" packages will never run on any platform that's not present in INCLUDE, but frankly
# that's nbd IMO

# all directly included packages should have their tests invoked in full, so we just need to generate the batches, multiplex them times the number of packages,
# and evenly assign them to the batches + direct to "include" members



# # regular case is when we have more packages than batches
# if ($packageProperties.Count -ge $batchCount) {
#     for ($i = 0; $i -lt $packageProperties.Count; $i++) {
#         Write-Host "Assigning package $($packageProperties[$i].Name) to batch $batchCounter"
#         $batches[$batchCounter] += $packageProperties[$i].Name.Replace(".json", "")
#         $batchCounter = ($batchCounter + 1) % $batchCount
#     }
# }
# # the case where we have fewer packages than batches, we instead walk the batches
# # and assign packages to them, even if we end up assigning the same package twice
# # that's ok, we just don't want to have dead platforms running no tests
# else {
#     for ($i = 0; $i -lt $batchCount; $i++) {
#         $batches[$i] += $packageProperties[$i % $packageProperties.Count].Name.Replace(".json", "")
#     }
# }

# # simplify the batches down to single values that will be added to the matrix
# foreach($key in $batches.Keys) {
#     $batchValues += $batches[$key] -join ","
# }

# # set the values for include
# $matrix.include[0].CoverageConfig.ubuntu2004_39_coverage | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value $batchValues[0]
# $matrix.include[1].Config.Ubuntu2004_312 | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value $batchValues[1]

# # set the values for the matrix
# $matrix.matrix | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value $batchValues[2..($batchValues.Length-1)]

# $matrix | ConvertTo-Json -Depth 100 | Set-Content -Path $PlatformMatrix
