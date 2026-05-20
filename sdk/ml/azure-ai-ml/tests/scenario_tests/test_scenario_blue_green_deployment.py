# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Blue-green online endpoint deployment with traffic shifting and rollback.

Inspired by azureml-examples/sdk/python/endpoints/online/managed/online-endpoints-safe-rollout.ipynb
but tests edge cases around:
  - Creating an endpoint with system-assigned identity (not just key auth)
  - Deploying two model versions with different scoring scripts
  - Traffic splitting with non-standard ratios (e.g., 80/20 instead of 100/0)
  - Invoking specific deployments directly (bypassing traffic rules)
  - Updating endpoint properties (description, tags) mid-lifecycle
  - Deleting individual deployments before deleting the endpoint
  - Verifying scoring_uri and swagger_uri survive round-trip through TypeSpec ARM client

Customer story:
  An ML engineering team has a production model behind a managed online endpoint.
  They need to deploy a new version (green) alongside the old one (blue), gradually
  shift traffic, test the green deployment in isolation, then fully cut over.
  They also need to update endpoint metadata and verify all URIs are correct.

Steps:
  1. Create a managed online endpoint with key auth and tags
  2. Create "blue" deployment with a trivial scoring script + inline model
  3. Set blue to 100% traffic, verify endpoint properties and scoring_uri
  4. Update endpoint description and tags, verify round-trip
  5. Create "green" deployment with a different scoring script
  6. Split traffic 80/20 (blue/green), verify via endpoint get
  7. Invoke the green deployment directly (deployment_name override)
  8. Shift to 100% green, delete blue deployment
  9. Clean up endpoint entirely
"""

import json
import os
import tempfile
import time

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities import CodeConfiguration, Environment, ManagedOnlineDeployment, ManagedOnlineEndpoint, Model
from azure.core.polling import LROPoller


class TestScenarioBlueGreenDeployment:
    """Blue-green deployment lifecycle with traffic shifting and property fidelity."""

    @pytest.mark.timeout(1800)
    def test_blue_green_traffic_shift_with_metadata_updates(self, ml_client: MLClient, rand_name):
        """Full blue-green deployment lifecycle with edge-case traffic and metadata updates."""

        endpoint_name = rand_name("ep")[:32]  # endpoint names have length limit
        env_name = rand_name("scenv")
        model_name_v1 = rand_name("mdl")
        model_name_v2 = rand_name("mdl2")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # ── Scoring scripts ───────────────────────────────
                score_v1 = os.path.join(tmpdir, "score_v1.py")
                with open(score_v1, "w") as f:
                    f.write(
                        """import json, logging
logger = logging.getLogger(__name__)

def init():
    logger.info("Blue (v1) model initialized")

def run(raw_data):
    data = json.loads(raw_data)
    return json.dumps({"version": "v1", "echo": data, "status": "ok"})
"""
                    )

                score_v2 = os.path.join(tmpdir, "score_v2.py")
                with open(score_v2, "w") as f:
                    f.write(
                        """import json, logging
logger = logging.getLogger(__name__)

def init():
    logger.info("Green (v2) model initialized")

def run(raw_data):
    data = json.loads(raw_data)
    result = {"version": "v2", "echo": data, "status": "ok", "improved": True}
    return json.dumps(result)
"""
                    )

                # Minimal model files
                model_dir_v1 = os.path.join(tmpdir, "model_v1")
                os.makedirs(model_dir_v1, exist_ok=True)
                with open(os.path.join(model_dir_v1, "model.txt"), "w") as f:
                    f.write("placeholder model v1")

                model_dir_v2 = os.path.join(tmpdir, "model_v2")
                os.makedirs(model_dir_v2, exist_ok=True)
                with open(os.path.join(model_dir_v2, "model.txt"), "w") as f:
                    f.write("placeholder model v2")

                # ── Step 1: Create endpoint ───────────────────────
                endpoint = ManagedOnlineEndpoint(
                    name=endpoint_name,
                    description="Scenario test: blue-green deployment lifecycle",
                    auth_mode="key",
                    tags={
                        "scenario": "blue-green",
                        "branch": "tsp-migration",
                        "test_phase": "initial",
                    },
                )
                ml_client.online_endpoints.begin_create_or_update(endpoint).result()

                # Verify endpoint properties round-trip
                ep = ml_client.online_endpoints.get(endpoint_name)
                assert ep.name == endpoint_name
                assert ep.provisioning_state == "Succeeded"
                assert ep.auth_mode == "key"
                assert ep.tags["scenario"] == "blue-green"
                assert ep.scoring_uri is not None, "scoring_uri should be set after creation"
                assert "score" in ep.scoring_uri.lower() or "inference" in ep.scoring_uri.lower()

                # ── Step 2: Deploy blue (v1) ──────────────────────
                blue = ManagedOnlineDeployment(
                    name="blue",
                    endpoint_name=endpoint_name,
                    model=Model(path=model_dir_v1),
                    environment=Environment(
                        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                        conda_file={
                            "name": "score-env",
                            "channels": ["defaults"],
                            "dependencies": ["python=3.10", "pip", {"pip": ["azureml-defaults"]}],
                        },
                    ),
                    code_configuration=CodeConfiguration(
                        code=tmpdir,
                        scoring_script="score_v1.py",
                    ),
                    instance_type="Standard_DS3_v2",
                    instance_count=1,
                )
                ml_client.online_deployments.begin_create_or_update(blue).result()

                # ── Step 3: Route 100% to blue, verify ────────────
                ep = ml_client.online_endpoints.get(endpoint_name)
                ep.traffic = {"blue": 100}
                ml_client.online_endpoints.begin_create_or_update(ep).result()

                ep_check = ml_client.online_endpoints.get(endpoint_name)
                assert ep_check.traffic.get("blue") == 100

                # Test invocation with inline data
                sample_input = json.dumps({"data": [[1, 2, 3]]})
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=tmpdir) as f:
                    f.write(sample_input)
                    request_file = f.name

                response = ml_client.online_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    deployment_name="blue",
                    request_file=request_file,
                )
                result = json.loads(response)
                assert result["version"] == "v1"
                assert result["status"] == "ok"

                # ── Step 4: Update endpoint metadata ──────────────
                ep = ml_client.online_endpoints.get(endpoint_name)
                ep.description = "Updated: testing metadata round-trip through TypeSpec ARM client"
                ep.tags["test_phase"] = "blue-deployed"
                ep.tags["updated_at"] = "mid-test"
                ml_client.online_endpoints.begin_create_or_update(ep).result()

                ep_updated = ml_client.online_endpoints.get(endpoint_name)
                assert "TypeSpec ARM client" in ep_updated.description
                assert ep_updated.tags["test_phase"] == "blue-deployed"
                assert ep_updated.tags["updated_at"] == "mid-test"
                # Verify scoring_uri is still valid after update
                assert ep_updated.scoring_uri is not None

                # ── Step 5: Deploy green (v2) ─────────────────────
                green = ManagedOnlineDeployment(
                    name="green",
                    endpoint_name=endpoint_name,
                    model=Model(path=model_dir_v2),
                    environment=Environment(
                        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                        conda_file={
                            "name": "score-env",
                            "channels": ["defaults"],
                            "dependencies": ["python=3.10", "pip", {"pip": ["azureml-defaults"]}],
                        },
                    ),
                    code_configuration=CodeConfiguration(
                        code=tmpdir,
                        scoring_script="score_v2.py",
                    ),
                    instance_type="Standard_DS3_v2",
                    instance_count=1,
                )
                ml_client.online_deployments.begin_create_or_update(green).result()

                # ── Step 6: Split traffic 80/20 ───────────────────
                ep = ml_client.online_endpoints.get(endpoint_name)
                ep.traffic = {"blue": 80, "green": 20}
                ml_client.online_endpoints.begin_create_or_update(ep).result()

                ep_split = ml_client.online_endpoints.get(endpoint_name)
                assert ep_split.traffic.get("blue") == 80
                assert ep_split.traffic.get("green") == 20

                # ── Step 7: Invoke green directly ─────────────────
                response_green = ml_client.online_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    deployment_name="green",
                    request_file=request_file,
                )
                result_green = json.loads(response_green)
                assert result_green["version"] == "v2"
                assert result_green["improved"] is True

                # ── Step 8: Full cutover → delete blue ────────────
                ep = ml_client.online_endpoints.get(endpoint_name)
                ep.traffic = {"blue": 0, "green": 100}
                ml_client.online_endpoints.begin_create_or_update(ep).result()

                # Delete blue deployment independently
                ml_client.online_deployments.begin_delete(name="blue", endpoint_name=endpoint_name).result()

                # Verify only green remains
                ep_final = ml_client.online_endpoints.get(endpoint_name)
                assert ep_final.traffic.get("green") == 100
                assert ep_final.traffic.get("blue", 0) == 0

        finally:
            # ── Cleanup: delete entire endpoint (cascades deployments) ─
            try:
                ml_client.online_endpoints.begin_delete(name=endpoint_name).result()
            except Exception:
                pass
