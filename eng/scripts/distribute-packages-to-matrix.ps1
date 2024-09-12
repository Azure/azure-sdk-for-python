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


function Split-ArrayIntoBatches {
    param (
        [Parameter(Mandatory=$true)]
        [object[]]$InputArray,

        [int]$BatchSize = 5
    )

    # Initialize an empty array to hold the batches
    $batches = @()

    # Loop through the input array in increments of the batch size
    for ($i = 0; $i -lt $InputArray.Count; $i += $BatchSize) {
        # Create a batch containing up to $BatchSize elements
        $batch = $InputArray[$i..[math]::Min($i + $BatchSize - 1, $InputArray.Count - 1)]

        # Add the batch to the list of batches
        $batches += ,$batch
    }

    return ,$batches
}

$packageProperties = Get-ChildItem -Recurse "$PackageInfoFolder" *.json | % { Get-Content -Path $_.FullName | ConvertFrom-Json }
$matrix = Get-Content -Path $PlatformMatrix | ConvertFrom-Json

$versionCount = $matrix.matrix.PythonVersion.Count
$includeCount = 0
$includeObject = $null
if ($matrix.PSObject.Properties.Name -contains "include") {
    $includeCount = $matrix.include.Count
    $originalInclude = $matrix.include
    # todo: reenable this
    $matrix.include = @()
    Write-Host "Original include type " + $originalInclude.GetType()
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

Write-Host "Direct Included Length = $($directIncludedPackages.Length)"
Write-Host "IndirectIncludedPackages Included Length = $($indirectIncludedPackages.Length)"

# for python, for fast tests, I want the sets of packages to be broken up into sets of five.

# I will assign all the direct included packages first. our goal is to get complete coverage of the direct included packages
# then, for the indirect packages, we will ADD them as extra TargetingString bundles to the matrix.
# this means that these "extra" packages will never run on any platform that's not present in INCLUDE, but frankly
# that's nbd IMO

$directBatches = Split-ArrayIntoBatches -InputArray $directIncludedPackages -BatchSize $batchSize
Write-Host $directBatches.Length
Write-Host $directBatches[0].Length
# all directly included packages should have their tests invoked in full, so, lets use a basic storage service discovery. We'll have direct package batches of

# ["azure-storage-blob", "azure-storage-blob-changefeed", "azure-storage-extensions", "azure-storage-file-datalake", "azure-storage-file-share"]
# ["azure-storage-queue"]

# any other packages will be added to the matrix as additional targetingstring batches. it'll be sparse in that there won't be full matrix coverage

# a basic platform matrix has the following:
# "matrix" -> "PythonVersion" = ["3.6", "3.7", "3.8", "3.9", "3.10"]
# "include" -> "ConfigName" -> "ActualJobName" -> PythonVersion=3.9
# so what we need to do is for each batch
    # 1. assign the batch * matrix size to the matrix as "TargetingString"
    # 2. assign the batch to each include with the batch being the value for TargetingString for the include
        # the easiest way to do this is to take a copy of the `Include` object at the beginning of this script,
        # for each batch, assign the batch to the include object, and then add the include object to the matrix object
        # this will have the result of multiplexing our includes, so we will need to update the name there

if ($directBatches) {
    # we need to ensure the presence of TargetingString in the matrix object
    if (-not $matrix.matrix.PSObject.Properties["TargetingString"]) {
        $matrix.matrix | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value @()
    }
    else {
        $matrix.matrix.TargetingString = @()
    }
}

foreach($batch in $directBatches) {
    $targetingString = ($batch | Select-Object -ExpandProperty Name) -join ","

    # we need to equal the number of python versions in the matrix (to ensure we get complete coverage)
    # so we need to multiply the targeting string by the number of python versions, that'll ensure that
    # across all python versions we see the same packages
    $targetingStringArray = @($targetingString) * $versionCount
    Write-Host "Returning batch:"
    foreach($item in $targetingStringArray) {
        Write-Host "`t$item"
    }

    $matrix.matrix.TargetingString += $targetingStringArray

    # if there were any include objects, we need to duplicate them exactly and add the targeting string to each
    # this means that the number of includes at the end of this operation will be incoming # of includes * the number of batches
    if ($includeCount -gt 0) {
        Write-Host "Walking include objects for $targetingString"
        $includeCopy = $originalInclude | ConvertTo-Json -Depth 100 | ConvertFrom-Json
        foreach ($configElement in $includeCopy) {
            if ($configElement.PSObject.Properties) {
                # an include looks like this
                # access by <ConfigName>.<ActualJobName>[ConfigElement]
                # {
                #     "CoverageConfig": {
                #         "ubuntu2004_39_coverage": {
                #         "OSVmImage": "env:LINUXVMIMAGE",
                #         "Pool": "env:LINUXPOOL",
                #         "PythonVersion": "3.9",
                #         "CoverageArg": "",
                #         "TestSamples": "false"
                #         }
                #     }
                # }
                $topLevelPropertyName = $configElement.PSObject.Properties.Name
                $topLevelPropertyValue = $configElement.PSObject.Properties[$topLevelPropertyName].Value

                if ($topLevelPropertyValue.PSObject.Properties) {

                    $secondLevelPropertyName = $topLevelPropertyValue.PSObject.Properties.Name
                    $secondLevelPropertyValue = $topLevelPropertyValue.PSObject.Properties[$secondLevelPropertyName].Value

                    Write-Host "Top-level: $topLevelPropertyName"
                    Write-Host "Second-level: $secondLevelPropertyName"

                    # Example of updating the second-level property name (optional)
                    # This will rename the property `ubuntu2004_39_coverage` to something else
                    $newSecondLevelName = "$secondLevelPropertyName" + "$targetingString"

                    $topLevelPropertyValue.PSObject.Properties.Remove($secondLevelPropertyName)
                    $topLevelPropertyValue | Add-Member -MemberType NoteProperty -Name $newSecondLevelName -Value $secondLevelPropertyValue

                    # add the targeting string property if it doesn't already exist
                    if (-not $topLevelPropertyValue.$newSecondLevelName.PSObject.Properties["TargetingString"]) {
                        $topLevelPropertyValue.$newSecondLevelName | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value @()
                    }

                    # set the targeting string
                    $topLevelPropertyValue.$newSecondLevelName.TargetingString = $targetingString
                }
            }

            $matrix.include += $configElement
        }
    }
}

$matrix | ConvertTo-Json -Depth 100

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

$matrix | ConvertTo-Json -Depth 100 | Set-Content -Path $PlatformMatrix
