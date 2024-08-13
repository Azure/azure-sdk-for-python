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

$packageProperties = Get-ChildItem -Recurse "$PackageInfoFolder" *.json
$platformMatrixFile = Get-Content -Path $PlatformMatrix | ConvertFrom-Json

# determine batch dize
$versionCount = $matrix.matrix.PythonVersion.Count
$includeCount = $matrix.include.Count
$batchCount = $versionCount + $includeCount
if ($batchCount -eq 0) {
    Write-Error "No batches detected, skipping without updating platform matrix file $PlatformMatrix"
    exit 0
}
$batchSize = $packageProperties.Count % $batchCount
$batches = @{}
for ($i = 0; $i -lt $batchCount; $i++) {
    $batches[$i] = @()
}

# what situations can we have with the calculated batch size of 6? (number of platforms + include)
# 1. < 6 packages we simply exit. default distribution will be fine
# 2. >= 6 packages we rotate and assign 1 to each batch until all work is exhausted
if ($packageProperties.Count -lt $batchCount) {
    Write-Error "Not enough packages to distribute to all batches, skipping without updating platform matrix file $PlatformMatrix"
    exit 0
}

$batchCounter = 0
$batchValues = @()

# regular case is when we have more packages than batches
if ($packageProperties.Count -ge $batchCount) {
    for ($i = 0; $i -lt $packageProperties.Count; $i++) {
        $batches[$batchCounter] += $packageProperties[$i].Name.Replace(".json", "")
        $batchCounter = ($batchCounter + 1) % $batchCount
    }
}
# the case where we have fewer packages than batches, we instead walk the batches
# and assign packages to them, even if we end up assigning the same package twice
# that's ok, we just don't want to have dead platforms
else {
    for ($i = 0; $i -lt $batchCount; $i++) {
        $batches[$i] += $packageProperties[$i % $packageProperties.Count].Name.Replace(".json", "")
    }
}

# simplify the batches down
foreach($key in $batches.Keys) {
    $batchValues += $batches[$key] -join ","
}

# set the values for the matrix
$platformMatrixFile.matrix.TargetingString = $batchValues[0..($versionCount - 1)]

# set the values for include
$platformMatrixFile.include[0].CoverageConfig.ubuntu2004_39_coverage.TargetingString = $batchValues[$versionCount]
$platformMatrixFile.include[1].Config.Ubuntu2004_312.TargetingString = $batchValues[$versionCount+1]

$platformMatrixFile | ConvertTo-Json -Depth 100 | Set-Content -Path $PlatformMatrix
