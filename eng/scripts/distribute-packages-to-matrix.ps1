<#
.SYNOPSIS
Distributes a set of packages to a platform matrix file by adding computing and adding a TargetingString property
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

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." ".."))
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
                $itemCount = 0

                # this looks very strange to loop over the properties of a PSCustomObject,
                # but this is the only way to actually count. The Count/Length property is
                # NOT available
                foreach($innerProperty in $property.Value.PSObject.Properties) {
                    $itemCount++
                }

                if ($itemCount -gt $highestCount) {
                    $highestCount = $itemCount
                }
            }
            "Object[]" {
                $count = $property.Value.Length
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

    $batches = @()

    for ($i = 0; $i -lt $InputArray.Count; $i += $BatchSize) {
        $batch = $InputArray[$i..[math]::Min($i + $BatchSize - 1, $InputArray.Count - 1)]

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

                if (-not $topLevelPropertyValue.$newSecondLevelName.PSObject.Properties["TargetingString"]) {
                    $topLevelPropertyValue.$newSecondLevelName | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value ""
                }

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

    # we need to ensure the presence of TargetingString in the matrix object
    if ($matrixUpdate) {
        if ($directBatches -or $indirectBatches) {
            if (-not $Matrix.matrix.PSObject.Properties["TargetingString"]) {
                $Matrix.matrix | Add-Member -Force -MemberType NoteProperty -Name TargetingString -Value @()
            }
            else {
                $Matrix.matrix.TargetingString = @()
            }
        }
    }

    # a basic platform matrix has the following:
    # "matrix" -> "PythonVersion" = ["3.6", "3.7", "3.8", "3.9", "3.10"]
    # "include" -> "ConfigName" -> "ActualJobName" -> PythonVersion=3.9
    # so what we need to do is for each batch
        # 1. assign the batch * matrix size to the matrix as "TargetingString", this will evenly distribute the packages to EACH python version non-sparsely
            # So direct packages add their duplicated targetingstring [ "azure-core,azure-storage-blob", "azure-core,azure-storage-blob", "azure-core,azure-storage-blob"]
            # a number of times indicated by the highest matrix multiplier. This forces a non-sparse coverage of this targetingstring batch
            # even in a sparse matrix generation.
            # indirect packages are then merely added as single additional targetingstring values (instead of multipled by the matrix multiplier)
            # which allows them to run on a single platform/python version combination
        # 2. assign the batch to each include with the batch being the value for TargetingString for the include
            # the easiest way to do this is to take a copy of the `Include` object at the beginning of this script,
            # for each batch, assign the batch to the include object, and then add the include object to the matrix object
            # this will have the result of multiplexing our includes, so we will need to update the name there as well
    # any other packages will be added to the matrix as additional targetingstring batches. it'll be sparse in that there won't be full matrix coverage

    foreach($batch in $DirectBatches) {
        $targetingString = ($batch | Select-Object -ExpandProperty Name) -join ","

        # we need to equal the largest multiplier in the matrix. That is USUALLY python version,
        # but in some cases it could be something else (like sdk/cosmos/cosmos-emulator-matrix.json) the multiplier
        # is a different property. We do this because we want to ensure that the matrix is fully covered, even if
        # we are generating the matrix sparsely, we still want full coverage of these targetingStrings
        $targetingStringArray = @($targetingString) * $MatrixMultiplier

        if ($matrixUpdate) {
            $matrix.matrix.TargetingString += $targetingStringArray
        }

        # if there were any include objects, we need to duplicate them exactly and add the targeting string to each
        # this means that the number of includes at the end of this operation will be incoming # of includes * the number of batches
        if ($includeCount -gt 0) {
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

# calculate general targeting information and create our batches prior to updating any matrix
$packageProperties = Get-ChildItem -Recurse "$PackageInfoFolder" *.json `
    | % { Get-Content -Path $_.FullName | ConvertFrom-Json }

$directIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $false }
$indirectIncludedPackages = $packageProperties | Where-Object { $_.IncludedForValidation -eq $true }

# I will assign all the direct included packages first. our goal is to get full coverage of the direct included packages
# then, for the indirect packages, we will add them as sparse TargetingString bundles to the matrix
$directBatches = @()
if ($directIncludedPackages) {
    $directBatches = Split-ArrayIntoBatches -InputArray $directIncludedPackages -BatchSize $BATCHSIZE
}

$indirectBatches = @()
if ($indirectIncludedPackages) {
    $indirectBatches = Split-ArrayIntoBatches -InputArray $indirectIncludedPackages -BatchSize $BATCHSIZE
}

$matrix = Get-Content -Path $PlatformMatrix | ConvertFrom-Json
$matrixLocation = $PlatformMatrix

# handle the case where we discover an import, we need to climb the dependency in that case
if ($matrix.matrix.PSObject.Properties["`$IMPORT"]) {
    $originalMatrix = $matrix
    $originalMatrixLocation = $PlatformMatrix

    # rest of the update will happen to that matrix object
    $matrixLocation = (Join-Path $RepoRoot $matrix.matrix."`$IMPORT")
    $matrix = Get-Content -Path $matrixLocation | ConvertFrom-Json

    # we just need to walk the include objects and update the targeting string for the batches we have before
    # updating in place, then continuing on to update the actual matrix object that we imported
    # there is a clear and present edge case here with nested import. We will not handle that case

    $originalInclude = $originalMatrix.include
    $originalMatrix.include = @()

    # update the include objects for the original matrix that was importing
    Update-Matrix -Matrix $originalMatrix -DirectBatches $directBatches -IndirectBatches $indirectBatches -MatrixMultiplier 1 -IncludeCount $matrix.include.Count -OriginalIncludeObject $originalInclude
    $originalMatrix | ConvertTo-Json -Depth 100 | Set-Content -Path $originalMatrixLocation
}

$matrixMultiplier = Extract-MatrixMultiplier -Matrix $matrix.matrix

$includeCount = 0
$includeObject = $null
$originalInclude = $null
if ($matrix.PSObject.Properties.Name -contains "include") {
    $includeCount = $matrix.include.Count
    $originalInclude = $matrix.include
    $matrix.include = @()
}

Update-Matrix -Matrix $matrix -DirectBatches $directBatches -IndirectBatches $indirectBatches -MatrixMultiplier $matrixMultiplier -IncludeCount $includeCount -OriginalIncludeObject $originalInclude

$matrix | ConvertTo-Json -Depth 100 | Set-Content -Path $matrixLocation
