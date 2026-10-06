# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Parsed YAML contracts for template-only release-completion correlation.
# Requires Pester 5 and powershell-yaml; no Python runtime or cloud access.
# Run Invoke-Pester -Path this file. This does not expand Azure Pipelines templates.

BeforeAll {
    Set-StrictMode -Version 4
    $ErrorActionPreference = 'Stop'
    Import-Module powershell-yaml -ErrorAction Stop
    $root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
    $baseline = '9dfa85db8189054119f842ca8a48415cdb218abf'
    $paths = @(
        'sdk/template/ci.yml',
        'eng/pipelines/templates/stages/archetype-sdk-client.yml',
        'eng/pipelines/templates/stages/archetype-python-release.yml',
        'eng/pipelines/templates/stages/release-artifact.yml'
    )
    $documents = @($paths | ForEach-Object {
        ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root $_) -Raw)
    })
    $entry, $client, $release, $artifact = $documents
    $idExpression = '${{ parameters.ReleasePlanId }}'
    $templateGuard = '${{ if eq(parameters.ServiceDirectory, ''template'') }}'
    $autoGuard = '${{ if and(eq(variables[''Build.Reason''], ''IndividualCI''), eq(variables[''Build.SourceBranch''], ''refs/heads/main'')) }}'
    $bindingGuard = '${{ if and(eq(parameters.ServiceDirectory, ''template''), eq(variables[''Build.Reason''], ''IndividualCI''), eq(variables[''Build.SourceBranch''], ''refs/heads/main'')) }}'

    function Find-YamlMap {
        param([object]$Node, [string]$Key, [string]$Value)
        if ($Node -is [System.Collections.IDictionary]) {
            if ($Node.Contains($Key) -and $Node[$Key] -eq $Value) {
                ,$Node
            }
            foreach ($child in $Node.Values) {
                Find-YamlMap -Node $child -Key $Key -Value $Value
            }
        } elseif ($Node -is [System.Collections.IList]) {
            foreach ($child in $Node) {
                Find-YamlMap -Node $child -Key $Key -Value $Value
            }
        }
    }

    function ConvertTo-CanonicalNode {
        param([object]$Node)
        if ($Node -is [System.Collections.IDictionary]) {
            $result = [ordered]@{}
            foreach ($key in @($Node.Keys | Sort-Object)) {
                $result[$key] = ConvertTo-CanonicalNode $Node[$key]
            }
            return $result
        }
        if ($Node -is [System.Collections.IList]) {
            $result = @($Node | ForEach-Object { ConvertTo-CanonicalNode $_ })
            Write-Output -NoEnumerate $result
            return
        }
        return $Node
    }

    function Get-BaselineYaml {
        param([string]$Path)
        # Do not allow a partial clone to fetch objects during local contract validation.
        $previous = $env:GIT_NO_LAZY_FETCH
        try {
            $env:GIT_NO_LAZY_FETCH = '1'
            $text = git -C $root show "${baseline}:$Path"
            if ($LASTEXITCODE -ne 0) { throw "Baseline unavailable: $Path" }
            return ConvertFrom-Yaml ($text -join "`n")
        } finally {
            $env:GIT_NO_LAZY_FETCH = $previous
        }
    }

    $clientRelay = @(Find-YamlMap $client template 'archetype-python-release.yml')[0]
    $artifactRelay = @(Find-YamlMap $release template '/eng/pipelines/templates/stages/release-artifact.yml')[0]
    $stage = $artifact.stages[0]
    $completion = @(Find-YamlMap $artifact template '/eng/common/pipelines/templates/steps/mark-release-completion.yml')[0]
}

Describe 'Python template completion correlation' {
    It 'declares optional string IDs without numeric conversion at every boundary' {
        foreach ($document in @($entry, $client, $artifact)) {
            $parameter = @($document.parameters | Where-Object { $_.name -eq 'ReleasePlanId' })
            $parameter.Count | Should -Be 1
            $parameter[0].type | Should -BeExactly 'string'
            $parameter[0].default | Should -BeOfType ([string])
            $parameter[0].default | Should -BeExactly '0'
        }
        # Preserve this template's existing mapping-style parameter declaration.
        $release.parameters.ReleasePlanId | Should -BeOfType ([string])
        $release.parameters.ReleasePlanId | Should -BeExactly '0'
    }

    It 'relays the raw ID through entry, client and per-artifact release' {
        $entry.extends.parameters.ServiceDirectory | Should -BeExactly 'template'
        foreach ($relay in @($entry.extends, $clientRelay, $artifactRelay)) {
            $relay.parameters.ReleasePlanId | Should -BeExactly $idExpression
        }
    }

    It 'adds completion arguments only behind the template service guard' {
        $completion.parameters.Contains('ReleasePlanId') | Should -BeFalse
        $completion.parameters.Contains('SdkPullRequest') | Should -BeFalse
        @($completion.parameters.Keys | Sort-Object) | Should -Be @($templateGuard, 'ConfigFileDir', 'PackageArtifactName' | Sort-Object)
        $pilot = $completion.parameters[$templateGuard]
        @($pilot.Keys | Sort-Object) | Should -Be @($autoGuard, 'ReleasePlanId' | Sort-Object)
        $pilot.ReleasePlanId | Should -BeExactly $idExpression
        @($pilot[$autoGuard].Keys) | Should -Be @('SdkPullRequest')
        $pilot[$autoGuard].SdkPullRequest | Should -BeExactly '$(AutoReleaseSdkPullRequestUrl)'
    }

    It 'binds the PR output at release-stage scope only for template IndividualCI main' {
        $binding = @($stage.variables | Where-Object { $_.Contains($bindingGuard) })
        $binding.Count | Should -Be 1
        $binding[0][$bindingGuard].Count | Should -Be 1
        $binding[0][$bindingGuard][0].name | Should -BeExactly 'AutoReleaseSdkPullRequestUrl'
        $binding[0][$bindingGuard][0].value | Should -BeExactly '$[ stageDependencies.AutoReleasePrepare.ResolveAutoReleasePackages.outputs[''resolve.AutoReleaseSdkPullRequestUrl''] ]'
        @(Find-YamlMap $stage.jobs name AutoReleaseSdkPullRequestUrl).Count | Should -Be 0
        $stage.dependsOn[1][$autoGuard] | Should -Be @('AutoReleasePrepare')
    }

    It 'preserves signed and unsigned artifact sources and dependencies' {
        $signed = $artifactRelay.parameters['${{ if eq(artifact.signBinaries, true) }}']
        $signed.ArtifactName | Should -BeExactly 'packages_${{ artifact.safeName }}_signed'
        $signed.DependsOn | Should -BeExactly 'Sign_${{ artifact.safeName }}'
        $signed.SignedArtifactTargetingStage | Should -BeExactly 'Sign_${{ artifact.safeName }}'
        $unsigned = $artifactRelay.parameters['${{ else }}']
        $unsigned.ArtifactName | Should -BeExactly '${{ parameters.ArtifactName }}'
        $unsigned.DependsOn | Should -BeExactly '${{ parameters.DependsOn }}'
        $stage.dependsOn[0] | Should -BeExactly '${{ parameters.DependsOn }}'
    }

    It 'preserves completion ordering and manual versus auto publication environments' {
        $job = @(Find-YamlMap $artifact job MarkPackageReleaseCompletion)[0]
        $job.dependsOn | Should -BeExactly 'PublishPackage'
        $publish = @(Find-YamlMap $artifact deployment PublishPackage)[0]
        $publish[$autoGuard].environment | Should -BeExactly 'none'
        $publish['${{ else }}'].environment | Should -BeExactly '${{ parameters.PublicPublishEnvironment }}'
        $publish.dependsOn | Should -BeExactly 'TagRepository'
        $publish.condition | Should -BeExactly 'and(succeeded(), ne(variables[''Skip.PublishPackage''], ''true''))'
    }

    It 'leaves the entire parsed <Path> baseline unchanged after removing only pilot additions' -TestCases @(
        @{ Path = 'sdk/template/ci.yml'; Kind = 'entry' },
        @{ Path = 'eng/pipelines/templates/stages/archetype-sdk-client.yml'; Kind = 'client' },
        @{ Path = 'eng/pipelines/templates/stages/archetype-python-release.yml'; Kind = 'release' },
        @{ Path = 'eng/pipelines/templates/stages/release-artifact.yml'; Kind = 'artifact' }
    ) {
        param([string]$Path, [string]$Kind)
        $actual = ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root $Path) -Raw)
        if ($Kind -eq 'release') {
            $actual.parameters.Remove('ReleasePlanId')
        } else {
            $actual.parameters = @($actual.parameters | Where-Object { $_.name -ne 'ReleasePlanId' })
        }
        switch ($Kind) {
            entry { $actual.extends.parameters.Remove('ReleasePlanId') }
            client { @(Find-YamlMap $actual template 'archetype-python-release.yml')[0].parameters.Remove('ReleasePlanId') }
            release { @(Find-YamlMap $actual template '/eng/pipelines/templates/stages/release-artifact.yml')[0].parameters.Remove('ReleasePlanId') }
            artifact {
                $actual.stages[0].variables = @($actual.stages[0].variables | Where-Object { -not $_.Contains($bindingGuard) })
                @(Find-YamlMap $actual template '/eng/common/pipelines/templates/steps/mark-release-completion.yml')[0].parameters.Remove($templateGuard)
            }
        }
        $expectedJson = ConvertTo-CanonicalNode (Get-BaselineYaml $Path) | ConvertTo-Json -Depth 100 -Compress
        $actualJson = ConvertTo-CanonicalNode $actual | ConvertTo-Json -Depth 100 -Compress
        # Protect all gates, eligibility, signing, integration, docs and ARH management workaround.
        $actualJson | Should -BeExactly $expectedJson
    }

    It 'keeps non-template completion identical to baseline with no extra arguments' {
        $parameters = (ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root $paths[3]) -Raw)).stages[0]
        $parameters = @(Find-YamlMap $parameters template '/eng/common/pipelines/templates/steps/mark-release-completion.yml')[0].parameters
        $parameters.Remove($templateGuard)
        @($parameters.Keys | Sort-Object) | Should -Be @('ConfigFileDir', 'PackageArtifactName')
        $old = @(Find-YamlMap (Get-BaselineYaml $paths[3]) template '/eng/common/pipelines/templates/steps/mark-release-completion.yml')[0].parameters
        (ConvertTo-CanonicalNode $parameters | ConvertTo-Json -Compress) | Should -BeExactly (ConvertTo-CanonicalNode $old | ConvertTo-Json -Compress)
    }

    It 'does not modify common completion or automatic preparation pending upstream sync' {
        foreach ($path in @(
            'eng/common/pipelines/templates/steps/mark-release-completion.yml',
            'eng/common/pipelines/templates/stages/archetype-auto-release-prepare.yml'
        )) {
            $current = ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root $path) -Raw)
            (ConvertTo-CanonicalNode $current | ConvertTo-Json -Depth 100 -Compress) | Should -BeExactly (ConvertTo-CanonicalNode (Get-BaselineYaml $path) | ConvertTo-Json -Depth 100 -Compress)
        }
    }

    It 'preserves raw string <Id> for downstream validation on both paths' -TestCases @(
        @{ Id = '0' }, @{ Id = '35307' }, @{ Id = '2147483647' }, @{ Id = '100.6' }
    ) {
        param([string]$Id)
        $value = (ConvertFrom-Yaml "ReleasePlanId: '$Id'").ReleasePlanId
        foreach ($relay in @($entry.extends, $clientRelay, $artifactRelay)) {
            $relay.parameters.ReleasePlanId | Should -BeExactly $idExpression
            $value | Should -BeOfType ([string])
            $value | Should -BeExactly $Id
        }
        $completion.parameters[$templateGuard].ReleasePlanId.Replace($idExpression, $value) | Should -BeExactly $Id
        $completion.parameters[$templateGuard][$autoGuard].SdkPullRequest | Should -BeExactly '$(AutoReleaseSdkPullRequestUrl)'
    }
}
