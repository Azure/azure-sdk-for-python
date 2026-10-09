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

    # Protect the existing safety contract from checked-in YAML, not historical
    # objects: shallow CI and source-only copies must run every assertion.
    It 'keeps feed and approval overrides opt-in and preserves both template artifacts' {
        foreach ($name in @('ReleaseToDevOpsOnly', 'AutoApproveRelease')) {
            $parameter = @($entry.parameters | Where-Object name -eq $name)
            $parameter.Count | Should -Be 1
            $parameter[0].type | Should -BeExactly 'boolean'
            $parameter[0].default | Should -BeFalse
        }
        $entry.extends.template | Should -BeExactly '../../eng/pipelines/templates/stages/archetype-sdk-client.yml'
        $entry.extends.parameters.Contains('PublicFeed') | Should -BeFalse
        $entry.extends.parameters.Contains('PublicPublishEnvironment') | Should -BeFalse
        $entry.extends.parameters['${{ if eq(parameters.ReleaseToDevOpsOnly, ''true'') }}'].PublicFeed | Should -BeExactly 'public/storage-staging'
        $entry.extends.parameters['${{ if eq(parameters.AutoApproveRelease, ''true'') }}'].PublicPublishEnvironment | Should -BeExactly 'none'
        $artifacts = @($entry.extends.parameters.Artifacts)
        $artifacts.Count | Should -Be 2
        $artifacts[0].name | Should -BeExactly 'azure-template'
        $artifacts[0].safeName | Should -BeExactly 'azuretemplate'
        $artifacts[0].Contains('signBinaries') | Should -BeFalse
        $artifacts[1].name | Should -BeExactly 'azure-template-two'
        $artifacts[1].safeName | Should -BeExactly 'azuretemplatetwo'
        $artifacts[1].signBinaries | Should -BeTrue
        $artifacts[1].skipPublishDocGithubIo | Should -BeTrue
        $artifacts[1].skipPublishDocMs | Should -BeTrue
        @($entry.trigger.branches.include) -join '|' | Should -BeExactly 'main|hotfix/*|release/*|restapi*'
        @($entry.trigger.paths.include) -join '|' | Should -BeExactly 'sdk/template/|scripts/|eng/common/'
    }

    It 'keeps client build dependencies, artifact eligibility and non-template defaults' {
        @(Find-YamlMap $client template 'archetype-python-release.yml').Count | Should -Be 1
        $clientRelay.parameters.DependsOn | Should -BeExactly 'Build'
        $clientRelay.parameters.Artifacts | Should -BeExactly '${{ parameters.Artifacts }}'
        $clientRelay.parameters.ArtifactName | Should -BeExactly 'packages_extended'
        $clientRelay.parameters.Contains('TestPipeline') | Should -BeFalse
        $clientRelay.parameters[$templateGuard].TestPipeline | Should -BeTrue
        foreach ($name in @('ServiceDirectory', 'PublicFeed', 'PublicPublishEnvironment', 'DevFeedName')) {
            $clientRelay.parameters[$name] | Should -BeExactly ('${{ parameters.' + $name + ' }}')
        }
        foreach ($contract in @(
            @{ Name = 'PublicFeed'; Default = 'PyPi' },
            @{ Name = 'PublicPublishEnvironment'; Default = 'package-publish' },
            @{ Name = 'TestPipeline'; Default = $false }
        )) {
            $parameter = @($client.parameters | Where-Object name -eq $contract.Name)
            $parameter.Count | Should -Be 1
            $parameter[0].default | Should -Be $contract.Default
            $release.parameters[$contract.Name] | Should -Be $contract.Default
            $parameter = @($artifact.parameters | Where-Object name -eq $contract.Name)
            $parameter.Count | Should -Be 1
            $parameter[0].default | Should -Be $contract.Default
        }
        $build = @(Find-YamlMap $client stage Build)
        $build.Count | Should -Be 1
        $build[0].condition | Should -BeExactly 'not(and(eq(${{ parameters.SkipPrValidation }}, true), eq(variables[''Build.Reason''], ''Manual'')))'
    }

    It 'keeps internal release eligibility and the auto-release prepare build dependency' {
        $releaseGate = '${{ if and(eq(variables[''System.TeamProject''], ''internal''), or(in(variables[''Build.Reason''], ''Manual'', ''''), and(eq(variables[''Build.Reason''], ''IndividualCI''), eq(variables[''Build.SourceBranch''], ''refs/heads/main'')))) }}'
        $guarded = @($release.stages | Where-Object { $_.Contains($releaseGate) })
        $guarded.Count | Should -Be 1
        $nodes = $guarded[0][$releaseGate]
        $loop = @($nodes | Where-Object { $_.Contains('${{ each artifact in parameters.Artifacts }}') })
        $loop.Count | Should -Be 1
        @(Find-YamlMap $loop[0]['${{ each artifact in parameters.Artifacts }}'] template '/eng/pipelines/templates/stages/release-artifact.yml').Count | Should -Be 1
        $prepareGuard = @($nodes | Where-Object { $_.Contains($autoGuard) })
        $prepareGuard.Count | Should -Be 1
        $prepare = @($prepareGuard[0][$autoGuard])
        $prepare.Count | Should -Be 1
        $prepare[0].template | Should -BeExactly '/eng/common/pipelines/templates/stages/archetype-auto-release-prepare.yml'
        @($prepare[0].parameters.DependsOn) | Should -Be @('${{ parameters.DependsOn }}')
        $prepare[0].parameters.Artifacts | Should -BeExactly '${{ parameters.Artifacts }}'
        $prepare[0].parameters.Condition | Should -BeExactly 'and(succeeded(), ne(variables[''SetDevVersion''], ''true''), ne(variables[''Skip.Release''], ''true''), ne(variables[''Build.Repository.Name''], ''Azure/azure-sdk-for-python-pr''))'
        @($stage.dependsOn).Count | Should -Be 2
        @($stage.dependsOn[1].Keys) | Should -Be @($autoGuard)
        @(Find-YamlMap $release template '/eng/common/pipelines/templates/stages/archetype-auto-release-prepare.yml').Count | Should -Be 1
    }

    It 'keeps all signed and unsigned manual and automatic release skip gates' {
        $safe = 'ne(variables[''SetDevVersion''], ''true''), ne(variables[''Skip.Release''], ''true''), ne(variables[''Build.Repository.Name''], ''Azure/azure-sdk-for-python-pr'')'
        $eligible = 'eq(dependencies.AutoReleasePrepare.outputs[''ResolveAutoReleasePackages.resolve.ReleaseArtifact_${{ parameters.Artifact.safeName }}''], ''true'')'
        $targeted = 'eq(dependencies.${{ parameters.SignedArtifactTargetingStage }}.outputs[''ResolveTargeting.resolve.ArtifactTargeted''], ''true'')'
        $stage['${{ if and(eq(variables[''Build.Reason''], ''IndividualCI''), eq(variables[''Build.SourceBranch''], ''refs/heads/main''), ne(parameters.SignedArtifactTargetingStage, '''')) }}'].condition | Should -BeExactly "and(succeeded(), $eligible, $targeted, $safe)"
        $stage['${{ elseif and(eq(variables[''Build.Reason''], ''IndividualCI''), eq(variables[''Build.SourceBranch''], ''refs/heads/main'')) }}'].condition | Should -BeExactly "and(succeeded(), $eligible, $safe)"
        $stage['${{ elseif ne(parameters.SignedArtifactTargetingStage, '''') }}'].condition | Should -BeExactly "and(succeeded(), $targeted, $safe)"
        $stage['${{ else }}'].condition | Should -BeExactly "and(succeeded(), $safe)"
        $signingGate = '${{ if and(eq(variables[''System.TeamProject''], ''internal''), ne(variables[''Build.Reason''], ''PullRequest'')) }}'
        $signing = @($release.stages | Where-Object { $_.Contains($signingGate) })
        $signing.Count | Should -Be 1
        $signingLoop = $signing[0][$signingGate][0]['${{ each artifact in parameters.Artifacts }}']
        $sign = @($signingLoop[0]['${{ if eq(artifact.signBinaries, true) }}'])
        $sign.Count | Should -Be 1
        $sign[0].template | Should -BeExactly '/eng/pipelines/templates/stages/sign-binaries.yml'
        $sign[0].parameters.Artifact | Should -BeExactly '${{ artifact }}'
        $sign[0].parameters.DependsOn | Should -BeExactly '${{ parameters.DependsOn }}'
        $unsigned = $artifactRelay.parameters['${{ else }}']
        $unsigned.Contains('SignedArtifactTargetingStage') | Should -BeFalse
        $parameter = @($artifact.parameters | Where-Object name -eq SignedArtifactTargetingStage)
        $parameter.Count | Should -Be 1
        $parameter[0].default | Should -BeExactly ''
    }

    It 'keeps signed and unsigned integration routing and the dev-feed skip gate' {
        $guard = @($release.stages | Where-Object { $_.Contains('${{ if eq(variables[''System.TeamProject''], ''internal'') }}') })
        $guard.Count | Should -Be 1
        $integration = @(Find-YamlMap $guard[0]['${{ if eq(variables[''System.TeamProject''], ''internal'') }}'] stage Integration)
        $integration.Count | Should -Be 1
        $integration[0].condition | Should -BeExactly 'succeededOrFailed(''${{parameters.DependsOn}}'')'
        $integration[0].dependsOn[0] | Should -BeExactly '${{ parameters.DependsOn }}'
        $notPr = '${{ if ne(variables[''Build.Reason''], ''PullRequest'') }}'
        $signedDependencies = $integration[0].dependsOn[1][$notPr][0]['${{ each artifact in parameters.Artifacts }}'][0]['${{ if eq(artifact.signBinaries, true) }}']
        @($signedDependencies) | Should -Be @('Sign_${{ artifact.safeName }}')
        $publish = @(Find-YamlMap $integration[0] job PublishPackages)
        $publish.Count | Should -Be 1
        $publish[0].condition | Should -BeExactly 'or(eq(variables[''SetDevVersion''], ''true''), and(eq(variables[''Build.Reason''],''Schedule''), eq(variables[''System.TeamProject''], ''internal'')))'
        $loop = @($publish[0].steps | Where-Object { $_.Contains('${{ each artifact in parameters.Artifacts }}') })
        $loop.Count | Should -Be 1
        $alpha = @(Find-YamlMap $loop[0]['${{ each artifact in parameters.Artifacts }}'][0]['${{if ne(artifact.skipPublishDevFeed, ''true'')}}'] template '/eng/pipelines/templates/steps/publish-alpha-package.yml')
        $alpha.Count | Should -Be 1
        $alpha[0].parameters['${{ if and(eq(artifact.signBinaries, true), ne(variables[''Build.Reason''], ''PullRequest'')) }}'].PackagePath | Should -BeExactly '$(Pipeline.Workspace)/packages_${{ artifact.safeName }}_signed/${{ artifact.name }}'
        $alpha[0].parameters['${{ else }}'].PackagePath | Should -BeExactly '$(Pipeline.Workspace)/${{ parameters.ArtifactName }}/${{ artifact.name }}'
        $downloads = @($publish[0].steps | Where-Object { $_.Contains($notPr) })
        $downloads.Count | Should -Be 1
        $signedDownload = $downloads[0][$notPr][0]['${{ each artifact in parameters.Artifacts }}'][0]['${{ if eq(artifact.signBinaries, true) }}'][0]
        $signedDownload.artifact | Should -BeExactly 'packages_${{ artifact.safeName }}_signed'
        $signedDownload.continueOnError | Should -BeTrue
    }

    It 'keeps publication artifact inputs, approval environments and downstream skip gates' {
        $publishGuard = @($stage.jobs | Where-Object { $_.Contains('${{if ne(parameters.Artifact.skipPublishPackage, ''true'')}}') })
        $publishGuard.Count | Should -Be 1
        $publish = @(Find-YamlMap $publishGuard[0]['${{if ne(parameters.Artifact.skipPublishPackage, ''true'')}}'] deployment PublishPackage)
        $publish.Count | Should -Be 1
        $publish[0].Contains('environment') | Should -BeFalse
        $publish[0].templateContext.type | Should -BeExactly 'releaseJob'
        $publish[0].templateContext.isProduction | Should -BeTrue
        $inputs = @($publish[0].templateContext.inputs)
        $inputs.Count | Should -Be 2
        $inputs[0].artifactName | Should -BeExactly 'release_artifact'
        $inputs[1].artifactName | Should -BeExactly '${{ parameters.ArtifactName }}'
        $inputs[1].targetPath | Should -BeExactly '$(Pipeline.Workspace)/${{ parameters.ArtifactName }}'
        $steps = $publish[0].strategy.runOnce.deploy.steps
        $public = @($steps | Where-Object { $_.Contains('${{ if eq(parameters.PublicFeed, ''PyPi'') }}') })
        $public.Count | Should -Be 1
        @(Find-YamlMap $public[0]['${{ if eq(parameters.PublicFeed, ''PyPi'') }}'] template '/eng/pipelines/templates/steps/esrp-publish.yml')[0].parameters.targetFolder | Should -BeExactly '$(Pipeline.Workspace)/esrp-release/${{parameters.ArtifactName}}/${{parameters.Artifact.name}}'
        $private = @($steps | Where-Object { $_.Contains('${{ if ne(parameters.PublicFeed, ''PyPi'') }}') })
        $private.Count | Should -Be 1
        @(Find-YamlMap $private[0]['${{ if ne(parameters.PublicFeed, ''PyPi'') }}'] task 'TwineAuthenticate@0')[0].inputs.artifactFeeds | Should -BeExactly '${{parameters.PublicFeed}}'
        @(Find-YamlMap $artifact job TagRepository)[0].condition | Should -BeExactly 'and(succeeded(), ne(variables[''Skip.TagRepository''], ''true''))'
        @(Find-YamlMap $artifact job UpdatePackageVersion)[0].condition | Should -BeExactly 'and(succeeded(), ne(variables[''Skip.UpdatePackageVersion''], ''true''))'
        foreach ($contract in @(
            @{ Gate = '${{if ne(parameters.Artifact.skipPublishDocGithubIo, ''true'')}}'; Job = 'PublishGitHubIODocs' },
            @{ Gate = '${{if ne(parameters.Artifact.skipPublishDocMs, ''true'')}}'; Job = 'PublishDocs' }
        )) {
            $guarded = @($stage.jobs | Where-Object { $_.Contains($contract.Gate) })
            $guarded.Count | Should -Be 1
            $job = @(Find-YamlMap $guarded[0][$contract.Gate] job $contract.Job)
            $job.Count | Should -Be 1
            $job[0].dependsOn | Should -BeExactly 'PublishPackage'
            ($job[0].condition -replace '\s', '') | Should -BeExactly 'and(succeeded(),ne(variables[''Skip.PublishDocs''],''true''),ne(variables[''Build.Repository.Name''],''Azure/azure-sdk-for-python-pr''))'
        }
        $arh = @(Find-YamlMap $artifact displayName 'Mark Package Released')
        $arh.Count | Should -Be 1
        ($arh[0].condition -replace '\s', '') | Should -BeExactly 'and(succeeded(),ne(variables[''IsManagementPackage''],''true''),not(and(eq(variables[''Skip.MarkPackageReleased''],''true''),eq(variables[''IsRequesterAuthorizedToSkipApiReview''],''true''))))'
    }

    It 'keeps non-template completion arguments and the shared completion skip gate explicit' {
        $completion.parameters.ConfigFileDir | Should -BeExactly '$(Pipeline.Workspace)/${{parameters.ArtifactName}}/PackageInfo'
        $completion.parameters.PackageArtifactName | Should -BeExactly '${{parameters.Artifact.name}}'
        $common = ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root 'eng/common/pipelines/templates/steps/mark-release-completion.yml') -Raw)
        @($common.parameters.Keys | Sort-Object) | Should -Be @('ConfigFileDir', 'PackageArtifactName', 'SourceRootPath')
        $common.parameters.ConfigFileDir | Should -BeExactly ''
        $common.parameters.PackageArtifactName | Should -BeExactly ''
        $common.parameters.SourceRootPath | Should -BeExactly '$(Build.SourcesDirectory)'
        $mark = @(Find-YamlMap $common task 'AzureCLI@2')
        $mark.Count | Should -Be 1
        $mark[0].condition | Should -BeExactly 'and(succeeded(), ne(variables[''Skip.MarkReleaseCompletion''], ''true''))'
        $mark[0].continueOnError | Should -BeTrue
        $mark[0].inputs.scriptPath | Should -BeExactly '${{ parameters.SourceRootPath }}/eng/common/scripts/Mark-ReleasePlanCompletion.ps1'
        $mark[0].inputs.arguments.Trim() | Should -BeExactly '-PackageInfoFilePath ''${{ parameters.ConfigFileDir }}/${{ parameters.PackageArtifactName }}.json'' -AzsdkExePath ''$(AZSDK)'''
        $common = ConvertFrom-Yaml (Get-Content -LiteralPath (Join-Path $root 'eng/common/pipelines/templates/stages/archetype-auto-release-prepare.yml') -Raw)
        $prepare = @(Find-YamlMap $common stage AutoReleasePrepare)
        $prepare.Count | Should -Be 1
        $prepare[0].dependsOn | Should -BeExactly '${{ parameters.DependsOn }}'
        $prepare[0].condition | Should -BeExactly '${{ parameters.Condition }}'
        $resolve = @(Find-YamlMap $prepare[0] job ResolveAutoReleasePackages)
        $resolve.Count | Should -Be 1
        @(Find-YamlMap $resolve[0] name resolve).Count | Should -Be 1
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
