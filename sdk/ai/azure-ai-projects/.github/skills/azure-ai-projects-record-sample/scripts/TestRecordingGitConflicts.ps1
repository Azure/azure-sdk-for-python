# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$PackageRoot,
    [ValidateSet("main", "feature/azure-ai-projects/vnext")]
    [string]$BaseBranch,
    [string]$AssetsRepositoryPath,
    [switch]$SkipFetch
)

$ErrorActionPreference = "Stop"
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path).FullName
}

function Invoke-Git {
    param(
        [string]$WorkingDirectory,
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $output = @(& git -C $WorkingDirectory @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments -join ' ') failed:`n$($output -join [Environment]::NewLine)"
    }
    [pscustomobject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine).Trim()
    }
}

$repositoryRoot = (Invoke-Git $packageRoot @("rev-parse", "--show-toplevel")).Output
$repositoryRoot = (Get-Item -LiteralPath $repositoryRoot).FullName
$currentBranch = (Invoke-Git $repositoryRoot @("branch", "--show-current")).Output
if (-not $currentBranch) {
    throw "Recording is blocked from a detached HEAD. Switch to a branch and rebase the target first."
}

if (-not $BaseBranch) {
    if ($currentBranch -in @("main", "feature/azure-ai-projects/vnext")) {
        $BaseBranch = $currentBranch
    } else {
        throw "BaseBranch is required for topic branch '$currentBranch'. Choose main or feature/azure-ai-projects/vnext."
    }
}

$remoteExists = (Invoke-Git $repositoryRoot @("remote", "get-url", "origin") -AllowFailure).ExitCode -eq 0
if ($remoteExists -and -not $SkipFetch) {
    $refspec = "+refs/heads/$BaseBranch`:refs/remotes/origin/$BaseBranch"
    $fetch = Invoke-Git $repositoryRoot @("fetch", "--quiet", "origin", $refspec) -AllowFailure
    if ($fetch.ExitCode -ne 0) {
        throw "Unable to refresh origin/$BaseBranch. Recording is blocked because base freshness cannot be verified."
    }
}

$remoteBaseRef = "refs/remotes/origin/$BaseBranch"
$localBaseRef = "refs/heads/$BaseBranch"
if ((Invoke-Git $repositoryRoot @("show-ref", "--verify", "--quiet", $remoteBaseRef) -AllowFailure).ExitCode -eq 0) {
    $baseRef = "origin/$BaseBranch"
} elseif ((Invoke-Git $repositoryRoot @("show-ref", "--verify", "--quiet", $localBaseRef) -AllowFailure).ExitCode -eq 0) {
    $baseRef = $BaseBranch
} else {
    throw "Base branch '$BaseBranch' was not found locally or under origin."
}

$sourceAncestor = Invoke-Git $repositoryRoot @("merge-base", "--is-ancestor", $baseRef, "HEAD") -AllowFailure
if ($sourceAncestor.ExitCode -ne 0) {
    throw "Recording is blocked: HEAD does not contain the latest '$baseRef'. Rebase the target branch, then retry."
}

$relativePackagePath = [System.IO.Path]::GetRelativePath($repositoryRoot, $packageRoot).Replace("\", "/")
$assetsRelativePath = "$relativePackagePath/assets.json"
$localAssetsPath = Join-Path $packageRoot "assets.json"
if (-not (Test-Path -LiteralPath $localAssetsPath -PathType Leaf)) {
    throw "Recording is blocked: local assets.json was not found at '$localAssetsPath'."
}

try {
    $localAssets = Get-Content -LiteralPath $localAssetsPath -Raw | ConvertFrom-Json
    $baseAssetsText = (Invoke-Git $repositoryRoot @("show", "$baseRef`:$assetsRelativePath")).Output
    $baseAssets = $baseAssetsText | ConvertFrom-Json
} catch {
    throw "Recording is blocked: unable to parse local or base assets.json. $($_.Exception.Message)"
}

$localTag = [string]$localAssets.Tag
$baseTag = [string]$baseAssets.Tag
if (-not $localTag -or -not $baseTag) {
    throw "Recording is blocked: local or base assets.json does not contain a Tag."
}

$assetRelationship = "same"
$baseAssetCommit = $null
$localAssetCommit = $null
$baseAssetCommitDate = $null
$localAssetCommitDate = $null
if ($localTag -ne $baseTag) {
    if (-not $AssetsRepositoryPath) {
        $breadcrumbRoot = Join-Path $repositoryRoot ".assets\breadcrumb"
        if (Test-Path -LiteralPath $breadcrumbRoot -PathType Container) {
            $breadcrumb = Get-ChildItem -LiteralPath $breadcrumbRoot -File -Filter "*.breadcrumb" |
                Where-Object { (Get-Content -LiteralPath $_.FullName -Raw).StartsWith("$assetsRelativePath;") } |
                Select-Object -First 1
            if ($breadcrumb) {
                $parts = (Get-Content -LiteralPath $breadcrumb.FullName -Raw).Trim().Split(";")
                if ($parts.Count -ge 2) {
                    $AssetsRepositoryPath = Join-Path (Join-Path $repositoryRoot ".assets") $parts[1]
                }
            }
        }
    }
    if (-not $AssetsRepositoryPath -or -not (Test-Path -LiteralPath (Join-Path $AssetsRepositoryPath ".git"))) {
        throw "Recording is blocked: local assets tag differs from '$baseRef', but the assets Git cache is unavailable for ancestry validation."
    }

    $baseAssetCommitResult = Invoke-Git $AssetsRepositoryPath @("rev-parse", "$baseTag`^{commit}") -AllowFailure
    $localAssetCommitResult = Invoke-Git $AssetsRepositoryPath @("rev-parse", "$localTag`^{commit}") -AllowFailure
    if ($baseAssetCommitResult.ExitCode -ne 0 -or $localAssetCommitResult.ExitCode -ne 0) {
        throw "Recording is blocked: base or local asset tag is unavailable in the assets Git cache."
    }
    $baseAssetCommit = $baseAssetCommitResult.Output
    $localAssetCommit = $localAssetCommitResult.Output
    $assetAncestor = Invoke-Git $AssetsRepositoryPath @(
        "merge-base", "--is-ancestor", $baseAssetCommit, $localAssetCommit
    ) -AllowFailure
    if ($assetAncestor.ExitCode -ne 0) {
        throw "Recording is blocked: local asset tag '$localTag' is not descended from base tag '$baseTag'. Rebase the target branch before recording."
    }
    $assetRelationship = "descendant"
    $baseAssetCommitDate = (Invoke-Git $AssetsRepositoryPath @("show", "-s", "--format=%cI", $baseAssetCommit)).Output
    $localAssetCommitDate = (Invoke-Git $AssetsRepositoryPath @("show", "-s", "--format=%cI", $localAssetCommit)).Output
}

[pscustomobject]@{
    CurrentBranch = $currentBranch
    BaseBranch = $BaseBranch
    BaseRef = $baseRef
    LocalTag = $localTag
    BaseTag = $baseTag
    AssetRelationship = $assetRelationship
    BaseAssetCommit = $baseAssetCommit
    LocalAssetCommit = $localAssetCommit
    BaseAssetCommitDate = $baseAssetCommitDate
    LocalAssetCommitDate = $localAssetCommitDate
    SafeToRecord = $true
}