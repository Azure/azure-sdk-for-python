# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Run with Pester 5: Invoke-Pester -Path eng\scripts\tests\Package-Namespaces.tests.ps1

BeforeAll {
    $scriptsDirectory = Split-Path $PSScriptRoot -Parent
    . (Join-Path $scriptsDirectory "docs" "Docs-ToC.ps1")

    function LogWarning($Message) {
        Write-Warning $Message
    }

    function New-TestWheel {
        param([string]$Path, [string[]]$Entries)

        $archive = [System.IO.Compression.ZipFile]::Open($Path, [System.IO.Compression.ZipArchiveMode]::Create)
        try {
            foreach ($entry in $Entries) {
                $archive.CreateEntry($entry) | Out-Null
            }
        }
        finally {
            $archive.Dispose()
        }
        return $Path
    }
}

Describe "Get-NamespacesFromWhlFile" {
    BeforeEach {
        $library = "namespace-test-$([Guid]::NewGuid().ToString('N'))"
        $version = "1.0.0"
        $wheelDirectory = New-Item (Join-Path $TestDrive $library) -ItemType Directory
        $firstWheel = New-TestWheel (Join-Path $wheelDirectory "test-1.0.0-cp310-win_amd64.whl") @(
            "azure/__init__.py",
            "azure/_internal/__init__.py",
            "test.dist-info/__init__.py",
            "azure/alpha/__init__.py",
            "azure/alpha/child/__init__.py"
        )
        $secondWheel = New-TestWheel (Join-Path $wheelDirectory "test-1.0.0-cp314-manylinux_x86_64.whl") @(
            "azure/zeta/__init__.py"
        )
    }

    AfterEach {
        $remainingDirectories = @(Get-ChildItem ([System.IO.Path]::GetTempPath()) -Directory -Filter "$library$version*")
        try {
            $remainingDirectories.Count | Should -Be 0
        }
        finally {
            foreach ($directory in $remainingDirectories) {
                Remove-Item -LiteralPath $directory.FullName -Recurse -Force
            }
        }
    }

    It "preserves the single-wheel array and primary-namespace discovery rules" {
        $namespaces = Get-NamespacesFromWhlFile $library $version -PythonWhlFile $firstWheel

        ,$namespaces | Should -BeOfType [array]
        $namespaces.Count | Should -Be 1
        $namespaces[0] | Should -BeExactly "azure.alpha"
    }

    It "combines distinct namespaces without mixing extracted wheel contents" {
        $namespaces = Get-NamespacesFromWhlFile $library $version -PythonWhlFile @($firstWheel, $secondWheel)

        $namespaces | Should -Be @("azure.alpha", "azure.zeta")
    }

    It "deduplicates namespaces from multiple platform wheels" {
        $duplicateWheel = New-TestWheel (Join-Path $wheelDirectory "test-1.0.0-cp311-macosx_arm64.whl") @(
            "azure/alpha/__init__.py"
        )
        $namespaces = Get-NamespacesFromWhlFile $library $version -PythonWhlFile @($firstWheel, $duplicateWheel, $secondWheel)

        $namespaces | Should -Be @("azure.alpha", "azure.zeta")
    }

    It "isolates wheels with identical filenames from different directories" {
        $otherDirectory = New-Item (Join-Path $wheelDirectory "other") -ItemType Directory
        $sameNameWheel = New-TestWheel (Join-Path $otherDirectory (Split-Path $firstWheel -Leaf)) @(
            "azure/zeta/__init__.py"
        )
        $namespaces = Get-NamespacesFromWhlFile $library $version -PythonWhlFile @($firstWheel, $sameNameWheel)

        $namespaces | Should -Be @("azure.alpha", "azure.zeta")
    }

    It "does not reuse or remove a preexisting package-version directory" {
        $oldDestination = Join-Path ([System.IO.Path]::GetTempPath()) "$library$version"
        New-Item $oldDestination -ItemType Directory | Out-Null
        $sentinel = Join-Path $oldDestination "sentinel.txt"
        Set-Content $sentinel "unrelated contents"
        try {
            Get-NamespacesFromWhlFile $library $version -PythonWhlFile $firstWheel | Should -Be @("azure.alpha")
            Get-Content $sentinel | Should -BeExactly "unrelated contents"
        }
        finally {
            Remove-Item -LiteralPath $oldDestination -Recurse -Force
        }
    }

    It "warns and returns an empty array for a missing wheel" {
        Mock LogWarning {}
        $missingWheel = Join-Path $wheelDirectory "missing.whl"
        $namespaces = Get-NamespacesFromWhlFile $library $version -PythonWhlFile $missingWheel

        ,$namespaces | Should -BeOfType [array]
        $namespaces.Count | Should -Be 0
        Should -Invoke LogWarning -Times 1 -Exactly -ParameterFilter { $Message -eq "$missingWheel, does not exist." }
    }

    It "preserves the download path and extra index argument" {
        $expectedLibrary = $library
        $expectedVersion = $version
        Mock Get-WhlFile {
            param($Library, $Version, $Destination, $ExtraIndexUrl)
            Copy-Item $firstWheel -Destination $Destination
            return $true
        }
        $namespaces = Get-NamespacesFromWhlFile $library $version "https://example.invalid/simple"

        $namespaces | Should -Be @("azure.alpha")
        Should -Invoke Get-WhlFile -Times 1 -Exactly -ParameterFilter {
            $Library -eq $expectedLibrary -and $Version -eq $expectedVersion -and $ExtraIndexUrl -eq "https://example.invalid/simple"
        }
    }

    It "warns and returns an empty array when the wheel download fails" {
        Mock Get-WhlFile { return $false }
        Mock LogWarning {}
        $namespaces = Get-NamespacesFromWhlFile $library $version

        ,$namespaces | Should -BeOfType [array]
        $namespaces.Count | Should -Be 0
        Should -Invoke LogWarning -Times 1 -Exactly -ParameterFilter {
            $Message -eq "Could not download Whl file for $library $version"
        }
    }

    It "surfaces extraction errors and cleans up temporary files" {
        $invalidWheel = Join-Path $wheelDirectory "invalid.whl"
        Set-Content $invalidWheel "not a zip archive"

        { Get-NamespacesFromWhlFile $library $version -PythonWhlFile @($firstWheel, $invalidWheel) } | Should -Throw
    }
}

Describe "Save-Package-Namespaces-Property.ps1" {
    BeforeAll {
        Import-Module powershell-yaml -ErrorAction Stop
        $fixtureRoot = Join-Path $TestDrive "repo"
        $fixtureScripts = Join-Path $fixtureRoot "eng" "scripts"
        $fixtureCommon = Join-Path $fixtureRoot "eng" "common" "scripts"
        New-Item (Join-Path $fixtureScripts "docs") -ItemType Directory -Force | Out-Null
        New-Item (Join-Path $fixtureCommon "Helpers") -ItemType Directory -Force | Out-Null
        Copy-Item (Join-Path $scriptsDirectory "Save-Package-Namespaces-Property.ps1") $fixtureScripts
        Copy-Item (Join-Path $scriptsDirectory "docs" "Docs-ToC.ps1") (Join-Path $fixtureScripts "docs")
        Copy-Item (Join-Path $scriptsDirectory ".." "common" "scripts" "Helpers" "PSModule-Helpers.ps1") (Join-Path $fixtureCommon "Helpers")
        # Isolate repository discovery and logging; execute the real caller and extractor.
        Set-Content (Join-Path $fixtureCommon "common.ps1") @'
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot ".." ".." "..")
. (Join-Path $RepoRoot "eng" "scripts" "docs" "Docs-ToC.ps1")
function LogError($Message) { Write-Host "ERROR: $Message" }
function LogWarning($Message) { Write-Warning $Message }
'@
        $serviceDirectory = Join-Path $fixtureRoot "sdk" "test"
        New-Item $serviceDirectory -ItemType Directory -Force | Out-Null
        Set-Content (Join-Path $serviceDirectory "ci.yml") @'
extends:
  parameters:
    Artifacts:
      - name: azure-test
'@
        $saveScript = Join-Path $fixtureScripts "Save-Package-Namespaces-Property.ps1"
        $pwsh = (Get-Process -Id $PID).Path
    }

    BeforeEach {
        $stagingDirectory = Join-Path $TestDrive ([Guid]::NewGuid().ToString())
        $wheelDirectory = Join-Path $stagingDirectory "azure-test"
        New-Item $wheelDirectory -ItemType Directory -Force | Out-Null
        $packageInfoDirectory = New-Item (Join-Path $stagingDirectory "PackageInfo") -ItemType Directory
        $packageInfoFile = Join-Path $packageInfoDirectory "azure-test.json"
        @{
            Name = "azure-test"
            Version = "1.0.0"
            DevVersion = ""
            ServiceDirectory = "test"
        } | ConvertTo-Json | Set-Content $packageInfoFile
    }

    It "writes a deduplicated JSON array from all matching wheels" {
        New-TestWheel (Join-Path $wheelDirectory "azure_test-1.0.0-cp310-win_amd64.whl") @("azure/alpha/__init__.py") | Out-Null
        New-TestWheel (Join-Path $wheelDirectory "azure_test-1.0.0-cp311-macosx_arm64.whl") @("azure/alpha/__init__.py") | Out-Null
        New-TestWheel (Join-Path $wheelDirectory "azure_test-1.0.0-cp314-manylinux_x86_64.whl") @("azure/zeta/__init__.py") | Out-Null
        New-TestWheel (Join-Path $wheelDirectory "azure_test-2.0.0-py3-none-any.whl") @("azure/unrelated/__init__.py") | Out-Null

        $output = & $pwsh -NoProfile -File $saveScript -ArtifactStagingDirectory $stagingDirectory 2>&1
        $LASTEXITCODE | Should -Be 0 -Because ($output -join [Environment]::NewLine)
        $packageInfo = Get-Content $packageInfoFile -Raw | ConvertFrom-Json
        ,$packageInfo.Namespaces | Should -BeOfType [array]
        $packageInfo.Namespaces | Should -Be @("azure.alpha", "azure.zeta")
    }

    It "preserves single-wheel output as a JSON array" {
        New-TestWheel (Join-Path $wheelDirectory "azure_test-1.0.0-py3-none-any.whl") @("azure/alpha/__init__.py") | Out-Null

        $output = & $pwsh -NoProfile -File $saveScript -ArtifactStagingDirectory $stagingDirectory 2>&1
        $LASTEXITCODE | Should -Be 0 -Because ($output -join [Environment]::NewLine)
        $packageInfo = Get-Content $packageInfoFile -Raw | ConvertFrom-Json
        ,$packageInfo.Namespaces | Should -BeOfType [array]
        $packageInfo.Namespaces | Should -Be @("azure.alpha")
    }

    It "reports the missing wheel and exits with failure without modifying metadata" {
        $original = Get-Content $packageInfoFile -Raw
        $output = & $pwsh -NoProfile -File $saveScript -ArtifactStagingDirectory $stagingDirectory 2>&1

        $LASTEXITCODE | Should -Be 1
        ($output -join [Environment]::NewLine) | Should -Match "Whl file for, azure-test, was not found"
        Get-Content $packageInfoFile -Raw | Should -BeExactly $original
    }
}
