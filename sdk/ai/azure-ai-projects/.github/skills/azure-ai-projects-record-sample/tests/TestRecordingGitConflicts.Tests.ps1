# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

function Invoke-TestGit {
    param([string]$Root, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $output = @(& git -C $Root @Arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $($output -join [Environment]::NewLine)"
    }
    ($output -join [Environment]::NewLine).Trim()
}

function Initialize-TestRepository {
    param([string]$Root)
    New-Item -ItemType Directory -Path $Root -Force | Out-Null
    Invoke-TestGit $Root init --initial-branch=main | Out-Null
    Invoke-TestGit $Root config user.email test@example.com | Out-Null
    Invoke-TestGit $Root config user.name "Recording Guard Tests" | Out-Null
}

function Write-TestAssetsFile {
    param([string]$PackageRoot, [string]$Tag)
    [ordered]@{
        AssetsRepo = "Test/assets"
        AssetsRepoPrefixPath = "python"
        TagPrefix = "python/ai/azure-ai-projects"
        Tag = $Tag
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PackageRoot "assets.json") -Encoding UTF8
}

function New-GuardRepositories {
    param([string]$Root)

    $sourceRoot = Join-Path $Root "source"
    $packageRoot = Join-Path $sourceRoot "sdk\ai\azure-ai-projects"
    $assetsRoot = Join-Path $Root "assets"
    Initialize-TestRepository $sourceRoot
    New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null
    Write-TestAssetsFile $packageRoot "asset-base"
    Invoke-TestGit $sourceRoot add . | Out-Null
    Invoke-TestGit $sourceRoot commit -m "base assets" | Out-Null

    Initialize-TestRepository $assetsRoot
    "base" | Set-Content -LiteralPath (Join-Path $assetsRoot "recording.txt") -Encoding UTF8
    Invoke-TestGit $assetsRoot add . | Out-Null
    Invoke-TestGit $assetsRoot commit -m "base recording" | Out-Null
    Invoke-TestGit $assetsRoot tag asset-base | Out-Null

    [pscustomobject]@{
        SourceRoot = $sourceRoot
        PackageRoot = $packageRoot
        AssetsRoot = $assetsRoot
    }
}

Describe "TestRecordingGitConflicts.ps1" {
    It "allows recording on a current base branch with the same asset tag" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "equal-base")
        $actual = & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot -BaseBranch main `
            -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch

        $actual.SafeToRecord | Should Be $true
        $actual.AssetRelationship | Should Be "same"
    }

    It "allows a topic branch rebased onto the base with the same asset tag" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "topic-equal")
        Invoke-TestGit $repos.SourceRoot checkout -b topic | Out-Null
        "topic" | Set-Content -LiteralPath (Join-Path $repos.SourceRoot "topic.txt") -Encoding UTF8
        Invoke-TestGit $repos.SourceRoot add . | Out-Null
        Invoke-TestGit $repos.SourceRoot commit -m "topic work" | Out-Null

        $actual = & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot -BaseBranch main `
            -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch

        $actual.SafeToRecord | Should Be $true
        $actual.AssetRelationship | Should Be "same"
    }

    It "allows a descendant local asset tag on the base branch" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "asset-descendant")
        "new" | Set-Content -LiteralPath (Join-Path $repos.AssetsRoot "recording.txt") -Encoding UTF8
        Invoke-TestGit $repos.AssetsRoot add . | Out-Null
        Invoke-TestGit $repos.AssetsRoot commit -m "new recording" | Out-Null
        Invoke-TestGit $repos.AssetsRoot tag asset-new | Out-Null
        Write-TestAssetsFile $repos.PackageRoot "asset-new"

        $actual = & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot -BaseBranch main `
            -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch

        $actual.SafeToRecord | Should Be $true
        $actual.AssetRelationship | Should Be "descendant"
        $actual.BaseAssetCommitDate | Should Not BeNullOrEmpty
        $actual.LocalAssetCommitDate | Should Not BeNullOrEmpty
    }

    It "blocks a divergent local asset tag" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "asset-divergent")
        Invoke-TestGit $repos.AssetsRoot checkout --orphan divergent | Out-Null
        Invoke-TestGit $repos.AssetsRoot rm -rf . | Out-Null
        "divergent" | Set-Content -LiteralPath (Join-Path $repos.AssetsRoot "recording.txt") -Encoding UTF8
        Invoke-TestGit $repos.AssetsRoot add . | Out-Null
        Invoke-TestGit $repos.AssetsRoot commit -m "divergent recording" | Out-Null
        Invoke-TestGit $repos.AssetsRoot tag asset-divergent | Out-Null
        Write-TestAssetsFile $repos.PackageRoot "asset-divergent"
        $caught = $null
        try {
            & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot -BaseBranch main `
                -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch
        } catch { $caught = $_ }

        $caught.Exception.Message | Should Match "not descended from base tag"
    }

    It "blocks a topic branch that does not contain the selected base" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "stale-topic")
        Invoke-TestGit $repos.SourceRoot checkout -b topic | Out-Null
        "topic" | Set-Content -LiteralPath (Join-Path $repos.SourceRoot "topic.txt") -Encoding UTF8
        Invoke-TestGit $repos.SourceRoot add . | Out-Null
        Invoke-TestGit $repos.SourceRoot commit -m "topic work" | Out-Null
        Invoke-TestGit $repos.SourceRoot checkout main | Out-Null
        "new base" | Set-Content -LiteralPath (Join-Path $repos.SourceRoot "base.txt") -Encoding UTF8
        Invoke-TestGit $repos.SourceRoot add . | Out-Null
        Invoke-TestGit $repos.SourceRoot commit -m "advance base" | Out-Null
        Invoke-TestGit $repos.SourceRoot checkout topic | Out-Null
        $caught = $null
        try {
            & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot -BaseBranch main `
                -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch
        } catch { $caught = $_ }

        $caught.Exception.Message | Should Match "does not contain the latest 'main'"
    }

    It "requires explicit base selection on a topic branch" {
        $repos = New-GuardRepositories (Join-Path $TestDrive "missing-base")
        Invoke-TestGit $repos.SourceRoot checkout -b topic | Out-Null
        $caught = $null
        try {
            & $paths.RecordingConflictCheck -PackageRoot $repos.PackageRoot `
                -AssetsRepositoryPath $repos.AssetsRoot -SkipFetch
        } catch { $caught = $_ }

        $caught.Exception.Message | Should Match "BaseBranch is required"
    }
}