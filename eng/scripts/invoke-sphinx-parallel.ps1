

<#
.DESCRIPTION
This script is used to dispatch tox in parallel to multiple target packages.

Because the sphinx invocation is IO-bound and do not influence each other, we are doing just simply to speed up
the total runtime.
#>

param(
    $TargetingString,
    $RepoRoot,
    $ServiceDirectory = "",
    $WheelDirectory = ""
)

$pythonScript = Join-Path "$RepoRoot" "scripts" "devops_tasks" "dispatch_tox.py"
$jobs = @()
$packages = $TargetingString -split ","
$optionalParams = ""

if ($ServiceDirectory) {
    $optionalParams += "--service=$ServiceDirectory"
}

if ($WheelDirectory) {
    $optionalParams += " --wheel_dir=$WheelDirectory"
}

foreach ($package in $packages) {
    $jobs += Start-Job -ScriptBlock {
        param($Pkg, $ScriptPath, $RepoRoot, $Params)
        $log = Join-Path $RepoRoot "sphinx-$Pkg.log"
        Write-Host "& python $ScriptPath $Pkg --toxenv=sphinx $Params --disablecov 2>&1 >> $log"
        & python $ScriptPath $Pkg --toxenv=sphinx $Params --disablecov 2>&1 >> $log
        return $LASTEXITCODE
    } -ArgumentList $package, $pythonScript, $RepoRoot, $optionalParams
}

$jobs | ForEach-Object { $_ | Wait-Job }

$exitCodes = $jobs | ForEach-Object { $_ | Receive-Job }
$nonZeroExit = $exitCodes | Where-Object { $_ -ne 0 }
$jobs | ForEach-Object { $_ | Remove-Job }

if ($nonZeroExit) {
    Write-Host "One or more scripts failed with a non-zero exit code."
    Get-ChildItem $RepoRoot -Filter "sphinx-*.log" | ForEach-Object { Get-Content $_.FullName }
    exit 1
} else {
    Write-Host "All scripts completed successfully."
    Get-ChildItem $RepoRoot -Filter "sphinx-*.log" | ForEach-Object { Get-Content $_.FullName }
    exit 0
}
