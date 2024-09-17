<#
.SYNOPSIS
Distributes a set of packages to a platform matrix file by adding computing and adding a TargetingSTring property
dynamically. If an unexpected situation is encountered, the script will make no changes to the input file.

.DESCRIPTION
Because of the way the platform matrix file is structured, we need to distribute the packages in a way that
honors the Include packages. We have these included this way because want to ensure that these python versions
run on that platform. This script is aware of these additional configurations and will set TargetingString for
them as well.
#>
param(
    [parameter(Mandatory=$true)]
    [string]$PackageInfoFolder,
    [parameter(Mandatory=$true)]
    [string]$PlatformMatrix
)

Set-StrictMode -Version 4
$BATCHSIZE = 8

if (!(Test-Path $PackageInfoFolder)) {
    Write-Error "PackageInfo folder file not found: $PackageInfoFolder"
    exit 1
}

if (!(Test-Path $PlatformMatrix)) {
    Write-Error "Platform matrix file not found: $PlatformMatrix"
    exit 1
}

function Extract-MatrixMultiplier {
    param (
        [Parameter(Mandatory=$true)]
        [PSCustomObject]$Matrix
    )

    $highestCount = 1

    foreach ($property in $Matrix.PSObject.Properties) {
        $type = $property.Value.GetType().Name
        switch ($type) {
            "PSCustomObject" {
                # Write-Host $property.Value
                # Write-Host $property.Value.GetType()
                $itemCount = 0

                # this looks very strange to loop over the properties of a PSCustomObject,
                # but this is the only way to actually count. The Count/Length property is
                # NOT available
                foreach($innerProperty in $property.Value.PSObject.Properties) {
                    # Write-Host "Counting $($innerProperty.Name)"
                    $itemCount++
                }

                if ($itemCount -gt $highestCount) {
                    # Write-Host "Overwriting highest count with $itemCount from $($property.Name)"
                    $highestCount = $itemCount
                }
            }
            "Object[]" {
                $count = $property.Value.Length
                # Write-Host $property.Value
                # Write-Host "Found a Object[] and returning $count from $($property.Name)"
                if ($count -gt $highestCount) {
                    $highestCount = $count
                }
            }
        }
    }

    return $highestCount
}

function Split-ArrayIntoBatches {
    param (
        [Parameter(Mandatory=$true)]
        [object[]]$InputArray,

        [Parameter(Mandatory=$true)]
        [int]$BatchSize
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

function Update-Include {
    param (
        [Parameter(Mandatory=$true)]
        $Matrix,
        [Parameter(Mandatory=$true)]
        $IncludeConfig,
        [Parameter(Mandatory=$true)]
        $TargetingString
    )

    foreach ($configElement in $IncludeConfig) {
        if ($configElement.PSObject.Properties) {
            $topLevelPropertyName = $configElement.PSObject.Properties.Name
            $topLevelPropertyValue = $configElement.PSObject.Properties[$topLevelPropertyName].Value

            if ($topLevelPropertyValue.PSObject.Properties) {
                $secondLevelPropertyName = $topLevelPropertyValue.PSObject.Properties.Name
                $secondLevelPropertyValue = $topLevelPropertyValue.PSObject.Properties[$secondLevelPropertyName].Value

                $newSecondLevelName = "$secondLevelPropertyName" + "$TargetingString"

                $topLevelPropertyValue.PSObject.Properties.Remove($secondLevelPropertyName)
                $topLevelPropertyValue | Add-Member -MemberType NoteProperty -Name $newSecondLevelName -Value $secondLevelPropertyValue

                # add the targeting string property if it doesn't already exist
                if (-not $topLevelPropertyValue.$newSecondLevelName.PSObject.Properties["TargetingString"]) {
                    $topLevelPropertyValue.$newSecondLevelName | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value ""
                }

                # set the targeting string
                $topLevelPropertyValue.$newSecondLevelName.TargetingString = $TargetingString
            }
        }

        $Matrix.include += $configElement
    }
}

function Update-Matrix {
    param (
        [Parameter(Mandatory=$true)]
        $Matrix,

        [Parameter(Mandatory=$true)]
        $DirectBatches,

        [Parameter(Mandatory=$true)]
        $IndirectBatches,

        [Parameter(Mandatory=$true)]
        $MatrixMultiplier,

        [Parameter(Mandatory=$true)]
        $IncludeCount,

        [Parameter(Mandatory=$false)]
        $OriginalIncludeObject
    )

    $matrixUpdate = $true
    if ($Matrix.matrix.PSObject.Properties["`$IMPORT"]) {
        $matrixUpdate = $false
    }

    # a basic platform matrix has the following:
    # "matrix" -> "PythonVersion" = ["3.6", "3.7", "3.8", "3.9", "3.10"]
    # "include" -> "ConfigName" -> "ActualJobName" -> PythonVersion=3.9
    # so what we need to do is for each batch
        # 1. assign the batch * matrix size to the matrix as "TargetingString", this will evenly distribute the packages to EACH python version non-sparsely
        # 2. assign the batch to each include with the batch being the value for TargetingString for the include
            # the easiest way to do this is to take a copy of the `Include` object at the beginning of this script,
            # for each batch, assign the batch to the include object, and then add the include object to the matrix object
            # this will have the result of multiplexing our includes, so we will need to update the name there as well
    foreach($batch in $DirectBatches) {
        $targetingString = ($batch | Select-Object -ExpandProperty Name) -join ","

        # we need to equal the largest multiplier in the matrix. That is USUALLY python version,
        # but in some cases it could be something else (like sdk/cosmos/cosmos-emulator-matrix.json) the multiplier
        # is a different property. We do this because we want to ensure that the matrix is fully covered, even if
        # we are generating the matrix sparsely, we still want full coverage of these targetingStrings
        $targetingStringArray = @($targetingString) * $MatrixMultiplier
        # Write-Host "Returning batch:"
        # foreach($item in $targetingStringArray) {
        #     Write-Host "`t$item"
        # }

        if ($matrixUpdate) {
            $matrix.matrix.TargetingString += $targetingStringArray
        }

        # if there were any include objects, we need to duplicate them exactly and add the targeting string to each
        # this means that the number of includes at the end of this operation will be incoming # of includes * the number of batches
        if ($includeCount -gt 0) {
            # Write-Host "Walking include objects for $targetingString"
            $includeCopy = $OriginalIncludeObject | ConvertTo-Json -Depth 100 | ConvertFrom-Json

            Update-Include -Matrix $matrix -IncludeConfig $includeCopy -TargetingString $targetingString
        }
    }

    foreach($batch in $IndirectBatches) {
        $targetingString = ($batch | Select-Object -ExpandProperty Name) -join ","
        if ($matrixUpdate) {
            $matrix.matrix.TargetingString += @($targetingString)
        }
    }

}

$packageProperties = Get-ChildItem -Recurse "$PackageInfoFolder" *.json `
    | % { Write-Host $_.FullName; Get-Content -Path $_.FullName | ConvertFrom-Json }
$matrix = Get-Content -Path $PlatformMatrix | ConvertFrom-Json

# handle the case where we discover an import, we need to climb the dependency in that case
if ($matrix.matrix.PSObject.Properties["`$IMPORT"]) {
    $matrixUpdate = $false
}

$matrixMultiplier = Extract-MatrixMultiplier -Matrix $matrix.matrix

# Write-Host "Calculated a matrixMultiplier of $matrixMultiplier"
$includeCount = 0
$includeObject = $null
$originalInclude = $null
if ($matrix.PSObject.Properties.Name -contains "include") {
    $includeCount = $matrix.include.Count
    $originalInclude = $matrix.include
    $matrix.include = @()
}

# if there is an IMPORT, we should import that first and use THAT. we have a clear edge case where a doubly-nested include will NOT work.
# TODO: implement grabbing the matrix from the import if it exists

$directIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $false }
$indirectIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $true }

Write-Host "Direct Included Length = $($directIncludedPackages.Length)"
if ($indirectIncludedPackages) {
    Write-Host "IndirectIncludedPackages Included Length = $($indirectIncludedPackages.Length)"
}

# I will assign all the direct included packages first. our goal is to get complete coverage of the direct included packages
# then, for the indirect packages, we will ADD them as extra TargetingString bundles to the matrix.

$directBatches = Split-ArrayIntoBatches -InputArray $directIncludedPackages -BatchSize $BATCHSIZE
if ($indirectIncludedPackages) {
    $indirectBatches = Split-ArrayIntoBatches -InputArray $indirectIncludedPackages -BatchSize $BATCHSIZE
}
else {
    $indirectBatches = @()
}
# Write-Host $directBatches.Length
# Write-Host $directBatches[0].Length
# all directly included packages should have their tests invoked in full, so, lets use a basic storage service discovery. We'll have direct package batches of

# ["azure-storage-blob", "azure-storage-blob-changefeed", "azure-storage-extensions", "azure-storage-file-datalake", "azure-storage-file-share"]
# ["azure-storage-queue"]

# any other packages will be added to the matrix as additional targetingstring batches. it'll be sparse in that there won't be full matrix coverage

if ($directBatches) {
    # we need to ensure the presence of TargetingString in the matrix object
    if (-not $matrix.matrix.PSObject.Properties["TargetingString"]) {
        $matrix.matrix | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value @()
    }
    else {
        $matrix.matrix.TargetingString = @()
    }
}

Update-Matrix -Matrix $matrix -DirectBatches $directBatches -IndirectBatches $indirectBatches -MatrixMultiplier $matrixMultiplier -IncludeCount $includeCount -OriginalIncludeObject $originalInclude

$matrix | ConvertTo-Json -Depth 100 | Set-Content -Path $PlatformMatrix
