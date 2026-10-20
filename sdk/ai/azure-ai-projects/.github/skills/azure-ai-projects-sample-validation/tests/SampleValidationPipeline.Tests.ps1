# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$pipelinePath = Join-Path $packageRoot "tests.yml"

Describe "azure-ai-projects sample validation pipeline" {
    It "parses with the expected manual runtime parameter contract" {
        $pythonScript = @'
import json
from pathlib import Path
import sys

import yaml


data = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(
    json.dumps(
        {
            "trigger": data.get("trigger"),
            "pr": data.get("pr"),
            "parameters": [parameter["name"] for parameter in data["parameters"]],
            "sampleDisplayName": data["parameters"][0].get("displayName"),
            "sampleDefault": data["parameters"][0].get("default"),
            "testDisplayName": data["parameters"][1].get("displayName"),
            "testDefault": data["parameters"][1].get("default"),
            "template": data["extends"]["template"],
        }
    )
)
'@
        $output = @($pythonScript | & $paths.PythonExecutable - $pipelinePath)
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to parse tests.yml."
        }
        $actual = $output -join [Environment]::NewLine | ConvertFrom-Json

        $actual.trigger | Should Be "none"
        $actual.pr | Should Be "none"
        ($actual.parameters -join ",") | Should Be "SamplePattern,TestPattern"
        $actual.sampleDisplayName | Should Be 'Sample pattern (example: samples\hosted_agents\sample_*.py)'
        $actual.sampleDefault | Should Be 'samples/**/*.py'
        $actual.testDisplayName | Should Be 'Test pattern (required: enter * for all, or e.g. *remote_build*)'
        $actual.testDefault | Should BeNullOrEmpty
        $actual.template | Should Be "/eng/pipelines/templates/stages/1es-redirect.yml"
    }

    It "uses secret variable transport and the renamed validation runner" {
        $content = Get-Content -LiteralPath $pipelinePath -Raw
        $content | Should Match "AZURE_TEST_ATTACH_SAMPLE_LOGS: 'true'"
        $content | Should Match 'SAMPLE_ENVIRONMENT_VARIABLES_JSON: \$\(SAMPLE_ENVIRONMENT_VARIABLES_JSON\)'
        $content | Should Match "Push-Location sdk/ai/azure-ai-projects"
        $content | Should Match '\$\(PIP_EXE\) install -e \. -r dev_requirements\.txt'
        $content | Should Match '(?m)^\s*azureSubscription: azure-sdk-tests\r?$'
        $content | Should Match "azure-ai-projects-sample-validation/scripts/InvokeSampleValidation.ps1"
        $content | Should Not Match 'HideEnvironmentValues'
        $content | Should Match 'publishRunAttachments: true'
        $oldSkillName = "azure-ai-projects-record" + "-sample"
        $oldRunnerName = "InvokeSample" + "Test.ps1"
        $content | Should Not Match "$oldSkillName|$oldRunnerName"
    }
}
