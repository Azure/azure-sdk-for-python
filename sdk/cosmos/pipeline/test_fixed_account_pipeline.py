# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Offline contracts for fixed-account routing; requires PyYAML and PowerShell."""

import json
import os
from pathlib import Path
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[3]
RESOURCE_GATE = "${{ if not(parameters.DisableAzureResourceCreation) }}"
FIXED_GATE = "${{ if eq(matrixType, 'fixed') }}"


def load_yaml(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def mappings(value, ancestors=()):
    if isinstance(value, dict):
        yield value, ancestors
        for key, child in value.items():
            yield from mappings(child, (*ancestors, key))
    elif isinstance(value, list):
        for child in value:
            yield from mappings(child, ancestors)


def template_call(document, suffix):
    return next(
        (node, ancestors)
        for node, ancestors in mappings(document)
        if node.get("template", "").endswith(suffix)
    )


class FixedAccountPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = load_yaml("sdk/cosmos/tests.yml")["extends"]["parameters"]
        cls.stage = load_yaml("eng/pipelines/templates/stages/archetype-sdk-tests.yml")
        cls.job = load_yaml("eng/pipelines/templates/jobs/live.tests.yml")
        cls.build = load_yaml("eng/pipelines/templates/steps/build-test.yml")

    def test_fixed_matrix_routes_to_non_provisioning_jobs_only(self):
        defaults = {p["name"]: p.get("default") for p in self.stage["parameters"]}
        self.assertEqual([], defaults["FixedAccountMatrixConfigs"])
        self.assertEqual([], defaults["FixedAccountPreSteps"])
        generator, ancestors = template_call(self.stage, "generate-job-matrix.yml")
        self.assertIn("${{ each matrixType in split('provisioned,fixed', ',') }}", ancestors)
        self.assertIn(
            "${{ if or(eq(matrixType, 'provisioned'), ne(length(parameters.FixedAccountMatrixConfigs), 0)) }}",
            ancestors,
        )
        params = generator["parameters"]
        self.assertEqual(
            "generate_fixed_account_job_matrix", params[FIXED_GATE]["GenerateJobName"]
        )
        self.assertEqual(
            [{FIXED_GATE: ["${{ parameters.FixedAccountMatrixConfigs }}"]},
             {"${{ else }}": ["${{ parameters.MatrixConfigs }}", "${{ parameters.AdditionalMatrixConfigs }}"]}],
            params["MatrixConfigs"],
        )
        forwarded = params["AdditionalParameters"]
        self.assertEqual("${{ eq(matrixType, 'fixed') }}", forwarded["DisableAzureResourceCreation"])
        self.assertEqual(
            "${{ and(parameters.UseFederatedAuth, ne(matrixType, 'fixed')) }}",
            forwarded["UseFederatedAuth"],
        )
        self.assertIn(
            {FIXED_GATE: ["${{ parameters.FixedAccountPreSteps }}"]}, forwarded["PreSteps"]
        )
        self.assertNotIn("PreSteps", self.pipeline)
        self.assertNotIn("UseFederatedAuth", self.pipeline)
        self.assertTrue(defaults["UseFederatedAuth"])

    def test_all_resource_setup_deployment_and_cleanup_are_compile_time_gated(self):
        defaults = {p["name"]: p.get("default") for p in self.job["parameters"]}
        self.assertFalse(defaults["DisableAzureResourceCreation"])
        resource_templates = []
        for node, ancestors in mappings(self.job["jobs"][0]["steps"]):
            if "/TestResources/" in node.get("template", ""):
                self.assertIn(RESOURCE_GATE, ancestors)
                resource_templates.append(Path(node["template"]).name)
            self.assertFalse(node.get("task", "").startswith("Azure"))
        self.assertCountEqual(
            ["build-test-resource-config.yml", "deploy-test-resources.yml", "remove-test-resources.yml"],
            resource_templates,
        )
        deploy, _ = template_call(self.job, "deploy-test-resources.yml")
        cleanup, _ = template_call(self.job, "remove-test-resources.yml")
        self.assertEqual("${{ parameters.PersistOidcToken }}", deploy["parameters"]["PersistOidcToken"])
        for call in (deploy, cleanup):
            self.assertEqual("${{ parameters.UseFederatedAuth }}", call["parameters"]["UseFederatedAuth"])

    def test_tests_are_not_gated_on_deployment_or_service_connection(self):
        build, ancestors = template_call(self.job, "/steps/build-test.yml")
        self.assertNotIn(RESOURCE_GATE, ancestors)
        self.assertNotIn("condition", build)
        self.assertEqual("${{ parameters.UseFederatedAuth }}", build["parameters"]["UseFederatedAuth"])
        run, ancestors = next(
            (node, ancestors) for node, ancestors in mappings(self.build)
            if node.get("displayName") == "Run Tests"
        )
        self.assertIn("${{ else }}", ancestors)
        self.assertIn("python eng/scripts/dispatch_checks.py", run["pwsh"])
        self.assertNotIn("condition", run)
        self.assertNotIn("task", run)
        self.assertNotIn("CI_HAS_DEPLOYED_RESOURCES", json.dumps([self.stage, self.job, self.build]))

    def test_only_fixed_jobs_resolve_credentials_and_missing_selector_fails(self):
        resolver_call = self.pipeline["FixedAccountPreSteps"][0]
        self.assertEqual("/sdk/cosmos/pipeline/resolve-test-account-steps.yml", resolver_call["template"])
        self.assertEqual("$(AccountSelector)", resolver_call["parameters"]["AccountSelector"])
        resolver = load_yaml(resolver_call["template"].lstrip("/"))["steps"][0]
        self.assertEqual("./sdk/cosmos/pipeline/resolve-cosmos-test-account.ps1\n", resolver["pwsh"])
        self.assertNotIn("condition", resolver)
        self.assertEqual(
            {
                "COSMOS_TEST_ACCOUNTS_JSON": "$(${{ parameters.AccountsJsonVar }})",
                "COSMOS_ACCOUNT_SELECTOR": "${{ parameters.AccountSelector }}",
            },
            resolver["env"],
        )
        self.assertNotIn("COSMOS_TEST_ACCOUNTS_JSON", json.dumps(self.pipeline.get("EnvVars", {})))
        self.assertFalse((ROOT / "sdk/cosmos/test-resources-post.ps1").exists())

    def test_generated_matrices_cover_all_existing_lanes_without_overlap(self):
        generated = {}
        for kind, key in (("fixed", "FixedAccountMatrixConfigs"), ("provisioned", "MatrixConfigs")):
            config = self.pipeline[key][0]
            result = subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
                 ". ./eng/common/scripts/job-matrix/job-matrix-functions.ps1; "
                 "$config = GetMatrixConfigFromFile (Get-Content $env:MATRIX_CONFIG -Raw); "
                 "$matrix = GenerateMatrix -config $config -selectFromMatrixType all -skipEnvironmentVariables; "
                 "(SerializePipelineMatrix $matrix).compressed"],
                cwd=ROOT, env={**os.environ, "MATRIX_CONFIG": config["Path"]},
                capture_output=True, text=True, check=True, timeout=60,
            )
            self.assertEqual("all", config["Selection"])
            self.assertTrue(config["GenerateVMJobs"])
            generated[kind] = json.loads(result.stdout)
        fixed, provisioned = generated["fixed"], generated["provisioned"]
        self.assertEqual(12, len(fixed))
        self.assertEqual(8, len(provisioned))
        self.assertFalse(fixed.keys() & provisioned.keys())
        self.assertEqual(
            {"env:LINUXPOOL", "env:WINDOWSPOOL", "env:MACPOOL"},
            {leg["Pool"] for leg in fixed.values()},
        )
        for leg in fixed.values():
            self.assertTrue(leg["AccountSelector"])
            self.assertNotEqual("aad", leg.get("COSMOS_TEST_DATA_AUTH_MODE"))
            if leg["TestMarkArgument"] in ("cosmosCircuitBreaker", "cosmosCircuitBreakerMultiRegion"):
                self.assertEqual("True", leg["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"])
        for leg in provisioned.values():
            self.assertNotIn("AccountSelector", leg)
            if leg["TestMarkArgument"] != "cosmosGSI":
                self.assertEqual("aad", leg["COSMOS_TEST_DATA_AUTH_MODE"])
        self.assertEqual(7, sum(leg.get("COSMOS_TEST_DATA_AUTH_MODE") == "aad" for leg in provisioned.values()))


if __name__ == "__main__":
    unittest.main()
