# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

. (Join-Path $PSScriptRoot '../scripts/IdentityNaming.ps1')

Describe 'Literal MI resource placeholder contract' {
    BeforeEach {
        Mock Invoke-RestMethod { throw 'Naming must not access the network.' }
    }

    It 'expands the original pattern without changing any existing names' {
        $naming = Resolve-IdentityNamePattern -IdentityNamePattern 'mi-azsdk-sample-{resource}-wus3'
        $naming.ContainsKey('location') | Should Be $false
        $naming.ContainsKey('identityResourceGroup') | Should Be $false
        $naming.names.Count | Should Be 4
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $naming.names[$purpose] | Should BeExactly "mi-azsdk-sample-$purpose-wus3"
        }
        Assert-MockCalled Invoke-RestMethod -Times 0 -Exactly -Scope It
    }

    It 'accepts any valid prefix and suffix without deriving a region or group: <Pattern>' -TestCases @(
        @{ Pattern = 'custom_{resource}_blue' }, @{ Pattern = '{resource}-Team-A' },
        @{ Pattern = 'MI-{resource}' }, @{ Pattern = '{resource}' }, @{ Pattern = 'foo{resource}bar' }
    ) {
        param($Pattern)
        $naming = Resolve-IdentityNamePattern -IdentityNamePattern $Pattern
        $naming.names.Count | Should Be 4
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $naming.names[$purpose] | Should BeExactly $Pattern.Replace('{resource}', $purpose)
        }
        $naming.ContainsKey('location') | Should Be $false
    }

    It 'converts only the terminal resource role in an older concrete project name' {
        ConvertTo-IdentityNamePattern -ProjectIdentityName mi-azsdk-unit-project-project-uksouth |
            Should BeExactly 'mi-azsdk-unit-project-{resource}-uksouth'
        ConvertTo-IdentityNamePattern -ProjectIdentityName mi-azsdk-sample-project-wus3 |
            Should BeExactly 'mi-azsdk-sample-{resource}-wus3'
    }

    It 'rejects malformed or executable patterns without evaluating them: <Label>' -TestCases @(
        @{ Label = 'null'; Pattern = $null }, @{ Label = 'empty'; Pattern = '' },
        @{ Label = 'missing placeholder'; Pattern = 'mi-azsdk-unit-project-uksouth' },
        @{ Label = 'multiple'; Pattern = 'mi-azsdk-unit-{resource}-{resource}-uksouth' },
        @{ Label = 'wrong case'; Pattern = 'mi-azsdk-unit-{Resource}-uksouth' },
        @{ Label = 'unknown placeholder'; Pattern = 'mi-azsdk-{set}-{resource}-uksouth' },
        @{ Label = 'PowerShell'; Pattern = 'mi-azsdk-unit-{resource}-$(throw "unsafe")' },
        @{ Label = 'format string'; Pattern = 'mi-azsdk-unit-{0}-{resource}-uksouth' },
        @{ Label = 'newline'; Pattern = "mi-azsdk-unit-{resource}-uksouth`n" },
        @{ Label = 'path'; Pattern = '../mi-azsdk-unit-{resource}-uksouth' },
        @{ Label = 'oversized name'; Pattern = (('a' * 124) + '{resource}') }
    ) {
        param($Label, $Pattern)
        { Resolve-IdentityNamePattern -IdentityNamePattern $Pattern } | Should Throw 'MI name pattern'
        Assert-MockCalled Invoke-RestMethod -Times 0 -Exactly -Scope It
    }
}