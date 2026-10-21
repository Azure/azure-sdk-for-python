# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'TestHelpers.ps1')
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$python = Join-Path $packageRoot '.venv/Scripts/python.exe'

Describe 'Separated profile pipeline and skill contracts' {
    It 'parses the shared endpoint stage with explicit variable-group and secret mappings' {
        $inspect = @'
from pathlib import Path
import json
import sys
import yaml

stage = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
master = yaml.safe_load(Path(sys.argv[2]).read_text(encoding="utf-8"))
job = stage["stages"][0]["jobs"][0]
live = next(s for s in job["steps"] if s.get("task") == "AzurePowerShell@5")
print(json.dumps({
    "stageParameters": [p["name"] for p in stage["parameters"]],
    "groups": [v["group"] for v in stage["stages"][0]["variables"]],
    "liveEnv": list(live["env"]), "connection": live["inputs"]["azureSubscription"],
    "masterTrigger": master["trigger"], "masterPr": master["pr"],
    "masterParameters": master.get("parameters", []), "masterSchedules": master.get("schedules", []),
    "masterTemplate": master["extends"]["template"]
}))
'@
        $output = @($inspect | & $python - (Join-Path $packageRoot 'pipelines/test-profile-project.yml') (Join-Path $packageRoot 'tests-projects-master.yml'))
        if ($LASTEXITCODE -ne 0) { throw 'New pipeline YAML did not parse.' }
        $actual = $output -join "`n" | ConvertFrom-Json
        ($actual.stageParameters -join ',') | Should Be 'ExpectedEndpointHash,RegistryVariableGroup,ProjectVariableGroup,ValueVariables'
        ($actual.groups -join ',') | Should Be '${{ parameters.RegistryVariableGroup }},${{ parameters.ProjectVariableGroup }}'
        $actual.connection | Should Be 'azure-sdk-tests'
        ($actual.liveEnv -contains '${{ each name in parameters.ValueVariables }}') | Should Be $true
        $actual.masterTrigger | Should Be 'none'
        $actual.masterPr | Should Be 'none'
        $actual.masterParameters.Count | Should Be 0
        $actual.masterSchedules.Count | Should Be 0
        $actual.masterTemplate | Should Be '/eng/pipelines/templates/stages/1es-redirect.yml'
    }

    It 'never substitutes secret values during template expansion or uses a runtime-selected variable group' {
        $content = Get-Content -LiteralPath (Join-Path $packageRoot 'pipelines/test-profile-project.yml') -Raw
        $content | Should Match "format\('SAMPLE_PROFILE_VALUE_\{0\}', name\)"
        $content | Should Match 'SAMPLE_TEST_PROFILE_IDS: \$\(SAMPLE_TEST_PROFILE_IDS\)'
        $content | Should Not Match 'convertToJson\(variables|group: \$\('
        $content | Should Match 'PublishTestResults@2'
        $content | Should Match 'publishRunAttachments: true'
        $content | Should Match 'condition: always\(\)'
    }

    It 'offers independent Add/Update/Skip profiles only after confirmed ADO completion' {
        $content = Get-Content -LiteralPath (Join-Path $packageRoot '.github/skills/azure-ai-projects-sample-validation/SKILL.md') -Raw
        $content | Should Match 'confirmed \*\*completed\*\*'
        $content | Should Match 'Add new test profile'
        $content | Should Match 'Update existing test profile'
        $content | Should Match 'Respect Skip'
        $content | Should Match 'one independent profile per exact TestId'
        $content | Should Match 'without running tests first'
    }

    It 'has valid example metadata with no pipeline coupling or prior-build requirement' {
        $content = Get-Content -LiteralPath (Join-Path $skillRoot 'assets/profile.example.json') -Raw
        $testProfile = $content | ConvertFrom-Json
        $null = Assert-TestProfile $testProfile
        $content | Should Not Match 'DefinitionId|SourceBuildId|https://|"Value"\s*:'
        $skill = Get-Content -LiteralPath (Join-Path $skillRoot 'SKILL.md') -Raw
        $skill | Should Match '(?m)^name: azure-ai-projects-test-profiles\r?$'
        $skill | Should Match 'without running'
        (Test-Path -LiteralPath (Join-Path $skillRoot 'references/setup.md')) | Should Be $true
    }
}