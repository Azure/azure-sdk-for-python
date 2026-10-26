# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

Describe 'Pinned Pester bootstrap with isolated module commands' {
    It 'handles <Label> without calling a package repository' -TestCases @(
        @{ Label = 'exact cached version'; Cached = @('4.10.1'); HelperVersion = '4.10.1'; Total = 109; Failed = 0; Installs = 0; Reject = $false },
        @{ Label = 'mixed cached versions'; Cached = @('5.7.1', '4.10.1'); HelperVersion = '5.7.1'; Total = 109; Failed = 0; Installs = 0; Reject = $false },
        @{ Label = 'no cached version'; Cached = @(); HelperVersion = '4.10.1'; Total = 109; Failed = 0; Installs = 1; Reject = $false },
        @{ Label = 'incompatible helper version'; Cached = @('5.7.1'); HelperVersion = '5.7.1'; Total = 109; Failed = 0; Installs = 1; Reject = $true },
        @{ Label = 'zero tests'; Cached = @('4.10.1'); HelperVersion = '4.10.1'; Total = 0; Failed = 0; Installs = 0; Reject = $true },
        @{ Label = 'failed tests'; Cached = @('4.10.1'); HelperVersion = '4.10.1'; Total = 109; Failed = 1; Installs = 0; Reject = $true }
    ) {
        param($Label, $Cached, $HelperVersion, $Total, $Failed, $Installs, $Reject)
        $yaml = Get-Content -LiteralPath (Join-Path $PSScriptRoot '../../../tests.yml') -Raw
        # The shared helper is sourced first; isolate the following version-selection/test gate.
        $start = $yaml.IndexOf('                  $pester = Get-Module', [StringComparison]::Ordinal)
        if ($start -lt 0) { throw 'The pipeline Pester version-selection step was not found.' }
        $end = $yaml.IndexOf('                workingDirectory:', $start, [StringComparison]::Ordinal)
        if ($end -le $start) { throw 'The pipeline Pester bootstrap boundary was not found.' }
        $bootstrap = [scriptblock]::Create($yaml.Substring($start, $end - $start))
        $scenario = @{ cached = $Cached; helperVersion = $HelperVersion; total = $Total; failed = $Failed
            installs = 0; imported = $null; testsRun = $false }
        $outcome = & {
            function Get-Module {
                param([switch] $ListAvailable, [string] $Name)
                if (-not $ListAvailable -or $Name -cne 'Pester') { throw 'Unexpected module lookup.' }
                foreach ($version in $scenario.cached) { [pscustomobject]@{ Name = 'Pester'; Version = [version] $version } }
            }
            function Install-ModuleIfNotInstalled {
                param([string] $ModuleName, [string] $Version)
                if ($ModuleName -cne 'Pester' -or $Version -cne '4.10.1') { throw 'Unexpected package request.' }
                $scenario.installs++
                [pscustomobject]@{ Name = 'Pester'; Version = [version] $scenario.helperVersion }
            }
            function Import-Module {
                [CmdletBinding()]
                param([Parameter(ValueFromPipeline)] $InputObject, [switch] $Force)
                process { $scenario.imported = [string] $InputObject.Version }
            }
            function Invoke-Pester {
                param([string] $Script, [switch] $PassThru)
                if ($Script -cne './tests/samples/ci' -or -not $PassThru) { throw 'Unexpected test invocation.' }
                $scenario.testsRun = $true
                [pscustomobject]@{ TotalCount = $scenario.total; FailedCount = $scenario.failed }
            }
            foreach ($name in @('Get-Module', 'Install-ModuleIfNotInstalled', 'Import-Module', 'Invoke-Pester')) {
                if ((Get-Command $name).CommandType -ne 'Function') { throw 'Module command isolation failed.' }
            }
            $failure = $null
            try { & $bootstrap } catch { $failure = $_.Exception.Message }
            [pscustomobject]@{ failure = $failure; installs = $scenario.installs; imported = $scenario.imported; testsRun = $scenario.testsRun }
        }
        $outcome.installs | Should Be $Installs
        [bool] $outcome.failure | Should Be $Reject
        if ($HelperVersion -cne '4.10.1' -and $Cached -notcontains '4.10.1') {
            $outcome.failure | Should Match 'require Pester 4.10.1'
            $outcome.imported | Should BeNullOrEmpty
            $outcome.testsRun | Should Be $false
        } else {
            $outcome.imported | Should Be '4.10.1'
            $outcome.testsRun | Should Be $true
        }
    }
}