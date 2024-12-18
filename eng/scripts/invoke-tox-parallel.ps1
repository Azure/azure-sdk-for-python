

<#
.DESCRIPTION
This script is used to dispatch tox in parallel to multiple target packages.

Because the sphinx invocation is IO-bound and do not influence each other, we are doing just simply to speed up
the total runtime.
#>

param(
    $TargetingString,
    $RepoRoot,
    $Check = "sphinx",
    $ServiceDirectory = "",
    $WheelDirectory = ""
)

$pythonScript = Join-Path "$RepoRoot" "scripts" "devops_tasks" "dispatch_tox.py"
$jobs = @()
$packages = $TargetingString -split ","

foreach ($package in $packages) {
    $jobs += Start-Job -ScriptBlock {
        param($Pkg, $ScriptPath, $RepoRoot, $Toxenv, $ServiceParam, $WheelParam)
        $log = Join-Path $RepoRoot "$Toxenv-$Pkg.log"
        Write-Host "& python $ScriptPath $Pkg --toxenv=$Toxenv --service `"$ServiceParam`" -w `"$WheelParam`" --disablecov 2>&1 >> $log"
        & python $ScriptPath $Pkg --toxenv=$Toxenv --service "$ServiceParam" -w "$WheelParam" --disablecov 2>&1 >> $log
        return $LASTEXITCODE
    } -ArgumentList $package, $pythonScript, $RepoRoot, $Check, $ServiceDirectory, $WheelDirectory
}

$jobs | ForEach-Object { $_ | Wait-Job }

$exitCodes = $jobs | ForEach-Object { $_ | Receive-Job }
$nonZeroExit = $exitCodes | Where-Object { $_ -ne 0 }
$jobs | ForEach-Object { $_ | Remove-Job }

Get-ChildItem $RepoRoot -Filter "$Toxenv-*.log" `
    | ForEach-Object {
        Write-Host "Output for $($_.Name)"
        Get-Content $_.FullName
      }

if ($nonZeroExit) {
    Write-Host "One or more scripts failed with a non-zero exit code."
    exit 1
} else {
    Write-Host "All scripts completed successfully."
    exit 0
}
