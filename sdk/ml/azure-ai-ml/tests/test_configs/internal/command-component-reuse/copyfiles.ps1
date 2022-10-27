 param (
    [Parameter(Mandatory=$true)][string]$inputdir,
    [Parameter(Mandatory=$true)][string]$outputdir,
    [Parameter(Mandatory=$true)][string[]]$copyfilelist
 )

Write-Host "SystemLog: Input directory: " $inputdir
Write-Host "SystemLog: Output directory:" $outputdir
Write-Host "SystemLog: List of files to copy: " $copyfilelist
$filelist = [array] $copyfilelist.split(',')
Write-Host "SystemLog: Copying " $filelist.length " files from " $inputdir " to " $outputdir


foreach ($f in $filelist){
    $fi = Join-Path $inputdir $f
    Copy-Item $fi -Destination $outputdir
    Write-Host "SystemLog: Copied file " $fi
}


Write-Host "SystemLog: Successfully copied files.":