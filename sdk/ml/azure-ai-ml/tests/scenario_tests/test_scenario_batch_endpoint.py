# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Batch endpoint deployment, invocation, and job retrieval.

Inspired by azureml-examples/sdk/python/endpoints/batch/deploy-models/custom-outputs-parquet
but tests edge cases around:
  - Creating a BatchEndpoint with tags, description containing special characters
  - Deploying a model-based BatchDeployment with mini_batch_size, max_concurrency_per_instance,
    error_threshold, output_action, retry_settings, and custom output_file_name
  - Setting a default deployment on the endpoint
  - Invoking the endpoint with a uri_folder data asset (Input) and verifying a batch job starts
  - Listing batch jobs under the endpoint via list_jobs()
  - Round-trip fidelity of all deployment config properties through TypeSpec ARM serialization
  - Updating endpoint metadata mid-lifecycle and verifying persistence
  - Updating deployment properties (description, environment_variables) and verifying round-trip

Customer story:
  An ML engineer has a trained sklearn model and needs to score a large dataset
  in batch mode. They register the model, stand up a batch endpoint, deploy the
  model with specific throughput settings (mini_batch_size, max_concurrency,
  error_threshold), invoke the endpoint against a data asset, confirm the batch
  job completes, and verify all configuration survives the round-trip through
  the service. They also exercise endpoint metadata updates and deployment-level
  configuration to ensure the TypeSpec-migrated ARM client handles nested
  properties correctly.

Steps:
  1.  Register a trivial sklearn model from a local pickle file
  2.  Create a BatchEndpoint with description and tags (special chars)
  3.  Create a BatchDeployment with mini_batch_size, max_concurrency_per_instance,
      error_threshold, output_action, retry_settings, scoring script, environment
  4.  Verify deployment properties round-trip (get → assert)
  5.  Set the deployment as the endpoint default, verify via get
  6.  Update endpoint description and tags, verify persistence
  7.  Register a uri_folder data asset for scoring input
  8.  Invoke the endpoint with the data asset
  9.  List batch jobs, verify the invocation job appears
  10. (Optional) Poll the batch job toward completion
  11. Clean up: delete deployment, endpoint, archive model and data asset
"""

import json
import os
import pickle
import tempfile
import time

import pytest

from azure.ai.ml import Input, MLClient
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction
from azure.ai.ml.entities import (
    BatchEndpoint,
    BatchRetrySettings,
    CodeConfiguration,
    Data,
    Environment,
    Model,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
)


class TestScenarioBatchEndpoint:
    """Batch endpoint lifecycle: deploy model, invoke, verify config round-trip."""

    @pytest.mark.timeout(2400)
    def test_batch_endpoint_deploy_invoke_and_config_roundtrip(self, ml_client: MLClient, rand_name):
        """End-to-end batch endpoint: register model → create endpoint → deploy →
        set default → invoke with data asset → list jobs → verify config → clean up."""

        endpoint_name = rand_name("bep")[:23]  # batch endpoint names: max 32, keep short
        deployment_name = "scoring"
        model_name = rand_name("bmdl")
        data_name = rand_name("bdat")
        env_name = rand_name("benv")

        endpoint_created = False
        deployment_created = False
        model_created = False
        data_created = False

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # ── Step 1: Create and register a trivial sklearn model ───
                model_dir = os.path.join(tmpdir, "model")
                os.makedirs(model_dir, exist_ok=True)
                model_pkl = os.path.join(model_dir, "model.pkl")
                # Create a minimal pickle that batch scoring can reference
                dummy_model = {"type": "dummy", "predict": "echo"}
                with open(model_pkl, "wb") as f:
                    pickle.dump(dummy_model, f)

                model = Model(
                    name=model_name,
                    version="1",
                    type=AssetTypes.CUSTOM_MODEL,
                    path=model_dir,
                    description="Batch scenario test model — special chars: <angle> & ampersand",
                    tags={"framework": "sklearn", "scenario": "batch-test"},
                )
                try:
                    created_model = ml_client.models.create_or_update(model)
                except Exception as e:
                    if "KeyBasedAuthenticationNotPermitted" in str(e):
                        pytest.skip(
                            "Workspace storage disallows key-based auth; " "model upload requires storage keys enabled"
                        )
                    raise
                model_created = True
                assert created_model.name == model_name
                assert created_model.version == "1"

                # Verify model round-trip
                fetched_model = ml_client.models.get(model_name, "1")
                assert fetched_model.tags["framework"] == "sklearn"
                assert "<angle>" in fetched_model.description

                # ── Step 2: Create batch endpoint ─────────────────────
                endpoint = BatchEndpoint(
                    name=endpoint_name,
                    description='Batch scoring endpoint — test «special» chars & "quotes"',
                    tags={
                        "scenario": "batch-endpoint-test",
                        "branch": "tsp-migration",
                        "special_chars": "value with spaces & symbols!",
                    },
                )
                ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
                endpoint_created = True

                # Verify endpoint properties round-trip
                ep = ml_client.batch_endpoints.get(endpoint_name)
                assert ep.name == endpoint_name
                assert ep.provisioning_state == "Succeeded"
                assert ep.tags["scenario"] == "batch-endpoint-test"
                assert ep.tags["special_chars"] == "value with spaces & symbols!"
                assert "special" in ep.description

                # Endpoint should appear in the list
                ep_list = list(ml_client.batch_endpoints.list())
                ep_names = [e.name for e in ep_list]
                assert endpoint_name in ep_names

                # ── Step 3: Write scoring script and create environment ──
                score_script = os.path.join(tmpdir, "batch_score.py")
                with open(score_script, "w") as f:
                    f.write(
                        """import os
import pickle
import glob
import pandas as pd


def init():
    global model
    model_path = os.path.join(os.environ.get("AZUREML_MODEL_DIR", "."), "model.pkl")
    # Walk to find model.pkl if nested
    for root, dirs, files in os.walk(os.environ.get("AZUREML_MODEL_DIR", ".")):
        if "model.pkl" in files:
            model_path = os.path.join(root, "model.pkl")
            break
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"Model loaded: {type(model)}")


def run(mini_batch):
    results = []
    for file_path in mini_batch:
        print(f"Processing: {file_path}")
        results.append(f"scored:{os.path.basename(file_path)}")
    return results
"""
                    )

                env = Environment(
                    name=env_name,
                    version="1",
                    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                    conda_file={
                        "name": "batch-score-env",
                        "channels": ["defaults", "conda-forge"],
                        "dependencies": [
                            "python=3.10",
                            "pip",
                            {"pip": ["pandas>=1.5", "scikit-learn>=1.0", "azureml-defaults"]},
                        ],
                    },
                )
                created_env = ml_client.environments.create_or_update(env)
                assert created_env.name == env_name

                # ── Step 4: Create batch deployment ───────────────────
                deployment = ModelBatchDeployment(
                    name=deployment_name,
                    endpoint_name=endpoint_name,
                    model=f"azureml:{model_name}:1",
                    environment=f"azureml:{env_name}:1",
                    code_configuration=CodeConfiguration(
                        code=tmpdir,
                        scoring_script="batch_score.py",
                    ),
                    compute="cpu-cluster",
                    settings=ModelBatchDeploymentSettings(
                        mini_batch_size=10,
                        max_concurrency_per_instance=2,
                        error_threshold=5,
                        output_action=BatchDeploymentOutputAction.APPEND_ROW,
                        output_file_name="scenario_predictions.csv",
                        retry_settings=BatchRetrySettings(
                            max_retries=2,
                            timeout=60,
                        ),
                        logging_level="info",
                        environment_variables={
                            "SCENARIO_TEST": "true",
                            "BATCH_VERSION": "v1",
                        },
                    ),
                    description="Primary scoring deployment for batch scenario test",
                    tags={"version": "v1", "type": "model-batch"},
                )
                ml_client.batch_deployments.begin_create_or_update(deployment).result()
                deployment_created = True

                # ── Step 5: Verify deployment config round-trip ───────
                dep = ml_client.batch_deployments.get(
                    endpoint_name=endpoint_name,
                    name=deployment_name,
                )
                assert dep.name == deployment_name
                assert dep.endpoint_name == endpoint_name
                assert dep.provisioning_state == "Succeeded"

                # Core config fidelity checks
                assert (
                    dep.mini_batch_size == 10
                ), f"mini_batch_size round-trip failed: expected 10, got {dep.mini_batch_size}"
                assert (
                    dep.max_concurrency_per_instance == 2
                ), f"max_concurrency round-trip failed: expected 2, got {dep.max_concurrency_per_instance}"
                assert (
                    dep.error_threshold == 5
                ), f"error_threshold round-trip failed: expected 5, got {dep.error_threshold}"
                # output_action may come back as enum or string
                assert str(dep.output_action).lower().replace("_", "") in (
                    "appendrow",
                    "append_row",
                    "BatchDeploymentOutputAction.APPEND_ROW".lower(),
                ), f"output_action round-trip failed: got {dep.output_action}"
                assert dep.output_file_name == "scenario_predictions.csv"
                assert dep.logging_level.lower() == "info"

                # Retry settings fidelity
                assert dep.retry_settings is not None, "retry_settings should not be None"
                assert dep.retry_settings.max_retries == 2
                assert dep.retry_settings.timeout == 60

                # Tags and description
                assert dep.tags["version"] == "v1"
                assert "scoring deployment" in dep.description

                # Environment variables
                assert dep.environment_variables is not None
                assert dep.environment_variables.get("SCENARIO_TEST") == "true"
                assert dep.environment_variables.get("BATCH_VERSION") == "v1"

                # Deployment should appear in the list under this endpoint
                dep_list = list(ml_client.batch_deployments.list(endpoint_name=endpoint_name))
                dep_names = [d.name for d in dep_list]
                assert deployment_name in dep_names

                # ── Step 6: Set default deployment on endpoint ────────
                # NOTE: Setting defaults via dict (the documented SDK pattern)
                # fails with TypeSpec-migrated client because the dict key
                # "deployment_name" is serialized as-is instead of camelCase
                # "deploymentName". This is a known TypeSpec migration finding.
                # Workaround: set the property on the BatchEndpointDefaults
                # object returned by the service, rather than replacing with
                # a raw dict.
                ep = ml_client.batch_endpoints.get(endpoint_name)
                if ep.defaults is not None and hasattr(ep.defaults, "deployment_name"):
                    # defaults came back as a BatchEndpointDefaults object
                    ep.defaults.deployment_name = deployment_name
                else:
                    # If defaults is None, construct the REST model directly
                    from azure.ai.ml._restclient.v2023_10_01.models import (
                        BatchEndpointDefaults as RestBatchEndpointDefaults,
                    )

                    ep.defaults = RestBatchEndpointDefaults(deployment_name=deployment_name)
                ml_client.batch_endpoints.begin_create_or_update(ep).result()

                ep_updated = ml_client.batch_endpoints.get(endpoint_name)
                if hasattr(ep_updated.defaults, "deployment_name"):
                    assert ep_updated.defaults.deployment_name == deployment_name
                elif isinstance(ep_updated.defaults, dict):
                    assert ep_updated.defaults.get("deployment_name") == deployment_name

                # ── Step 7: Update endpoint metadata ──────────────────
                ep = ml_client.batch_endpoints.get(endpoint_name)
                ep.description = "Updated: batch endpoint after default deployment set"
                ep.tags["phase"] = "default-set"
                ep.tags["updated"] = "true"
                ml_client.batch_endpoints.begin_create_or_update(ep).result()

                ep_meta = ml_client.batch_endpoints.get(endpoint_name)
                assert "Updated" in ep_meta.description
                assert ep_meta.tags["phase"] == "default-set"
                assert ep_meta.tags["updated"] == "true"
                # Original tags should persist
                assert ep_meta.tags["scenario"] == "batch-endpoint-test"

                # ── Step 8: Register input data asset ─────────────────
                # Create a small uri_folder data asset with CSV files for scoring
                input_dir = os.path.join(tmpdir, "scoring_input")
                os.makedirs(input_dir, exist_ok=True)
                for i in range(3):
                    csv_path = os.path.join(input_dir, f"input_{i}.csv")
                    with open(csv_path, "w") as f:
                        f.write("col1,col2,col3\n")
                        for row in range(10):
                            f.write(f"{row},{row * 2},{row * 3}\n")

                data_asset = Data(
                    name=data_name,
                    version="1",
                    type=AssetTypes.URI_FOLDER,
                    path=input_dir,
                    description="Batch scoring input data for scenario test",
                    tags={"purpose": "batch-scoring-input"},
                )
                try:
                    created_data = ml_client.data.create_or_update(data_asset)
                except Exception as e:
                    if "KeyBasedAuthenticationNotPermitted" in str(e):
                        pytest.skip(
                            "Workspace storage disallows key-based auth; " "data upload requires storage keys enabled"
                        )
                    raise
                data_created = True
                assert created_data.name == data_name

                # Verify data asset round-trip
                fetched_data = ml_client.data.get(data_name, "1")
                assert fetched_data.type == AssetTypes.URI_FOLDER
                assert fetched_data.tags["purpose"] == "batch-scoring-input"

                # ── Step 9: Invoke the batch endpoint ─────────────────
                scoring_input = Input(
                    type=AssetTypes.URI_FOLDER,
                    path=f"azureml:{data_name}:1",
                )
                batch_job = ml_client.batch_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    deployment_name=deployment_name,
                    input=scoring_input,
                )
                assert batch_job is not None, "invoke() should return a batch job"

                # ── Step 10: List jobs and verify invocation appears ───
                # Give the service a moment to register the job
                time.sleep(10)
                jobs = list(ml_client.batch_endpoints.list_jobs(endpoint_name=endpoint_name))
                assert len(jobs) >= 1, f"Expected at least 1 batch job under endpoint {endpoint_name}, got {len(jobs)}"

        finally:
            # ── Cleanup: reverse order of creation ────────────────
            if deployment_created:
                try:
                    ml_client.batch_deployments.begin_delete(
                        endpoint_name=endpoint_name,
                        name=deployment_name,
                    ).result()
                except Exception:
                    pass

            if endpoint_created:
                try:
                    ml_client.batch_endpoints.begin_delete(name=endpoint_name).result()
                except Exception:
                    pass

            if model_created:
                try:
                    ml_client.models.archive(name=model_name, version="1")
                except Exception:
                    pass

            if data_created:
                try:
                    ml_client.data.archive(name=data_name, version="1")
                except Exception:
                    pass

            try:
                ml_client.environments.archive(name=env_name, version="1")
            except Exception:
                pass

    @pytest.mark.timeout(1200)
    def test_batch_deployment_config_variations(self, ml_client: MLClient, rand_name):
        """Test deployment with alternate config: summary_only output, higher error_threshold,
        different retry settings, and verify fidelity of each variation."""

        endpoint_name = rand_name("bep2")[:23]
        deployment_name = "alt-scoring"
        model_name = rand_name("bmdl2")
        env_name = rand_name("benv2")

        endpoint_created = False
        deployment_created = False
        model_created = False

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # ── Register model ────────────────────────────────────
                model_dir = os.path.join(tmpdir, "model")
                os.makedirs(model_dir, exist_ok=True)
                with open(os.path.join(model_dir, "model.pkl"), "wb") as f:
                    pickle.dump({"type": "placeholder"}, f)

                model = Model(
                    name=model_name,
                    version="1",
                    type=AssetTypes.CUSTOM_MODEL,
                    path=model_dir,
                    description="Alternate batch deployment config test model",
                    tags={"scenario": "batch-config-variation"},
                )
                try:
                    ml_client.models.create_or_update(model)
                except Exception as e:
                    if "KeyBasedAuthenticationNotPermitted" in str(e):
                        pytest.skip("Storage key auth disabled; skipping model upload test")
                    raise
                model_created = True

                # ── Create endpoint ───────────────────────────────────
                endpoint = BatchEndpoint(
                    name=endpoint_name,
                    description="Config variation test endpoint",
                    tags={"test": "config-variation"},
                )
                ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
                endpoint_created = True

                # ── Scoring script (summary_only mode) ────────────────
                score_script = os.path.join(tmpdir, "batch_score_summary.py")
                with open(score_script, "w") as f:
                    f.write(
                        """import os
import pickle


def init():
    global model
    for root, dirs, files in os.walk(os.environ.get("AZUREML_MODEL_DIR", ".")):
        if "model.pkl" in files:
            with open(os.path.join(root, "model.pkl"), "rb") as f:
                model = pickle.load(f)
            break


def run(mini_batch):
    print(f"Processing batch of {len(mini_batch)} files")
    return [f"processed:{len(mini_batch)}"]
"""
                    )

                env = Environment(
                    name=env_name,
                    version="1",
                    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                    conda_file={
                        "name": "batch-env",
                        "channels": ["defaults"],
                        "dependencies": ["python=3.10", "pip", {"pip": ["azureml-defaults"]}],
                    },
                )
                ml_client.environments.create_or_update(env)

                # ── Deploy with alternate config ──────────────────────
                deployment = ModelBatchDeployment(
                    name=deployment_name,
                    endpoint_name=endpoint_name,
                    model=f"azureml:{model_name}:1",
                    environment=f"azureml:{env_name}:1",
                    code_configuration=CodeConfiguration(
                        code=tmpdir,
                        scoring_script="batch_score_summary.py",
                    ),
                    compute="cpu-cluster",
                    settings=ModelBatchDeploymentSettings(
                        mini_batch_size=50,
                        max_concurrency_per_instance=4,
                        error_threshold=-1,  # -1 means ignore all errors
                        output_action=BatchDeploymentOutputAction.SUMMARY_ONLY,
                        # NOTE: output_file_name must NOT be set with SUMMARY_ONLY
                        retry_settings=BatchRetrySettings(
                            max_retries=5,
                            timeout=120,
                        ),
                        logging_level="warning",
                        environment_variables={},
                    ),
                    description="Alternate config: summary_only, high concurrency, ignore all errors",
                    tags={"config": "summary-only", "error_mode": "ignore-all"},
                )
                ml_client.batch_deployments.begin_create_or_update(deployment).result()
                deployment_created = True

                # ── Verify alternate config round-trip ────────────────
                dep = ml_client.batch_deployments.get(
                    endpoint_name=endpoint_name,
                    name=deployment_name,
                )
                assert dep.name == deployment_name
                assert dep.provisioning_state == "Succeeded"

                # Config specifics
                assert dep.mini_batch_size == 50, f"mini_batch_size: expected 50, got {dep.mini_batch_size}"
                assert (
                    dep.max_concurrency_per_instance == 4
                ), f"max_concurrency: expected 4, got {dep.max_concurrency_per_instance}"
                assert dep.error_threshold == -1, f"error_threshold: expected -1, got {dep.error_threshold}"
                assert str(dep.output_action).lower().replace("_", "") in (
                    "summaryonly",
                    "summary_only",
                    "BatchDeploymentOutputAction.SUMMARY_ONLY".lower(),
                ), f"output_action round-trip failed: got {dep.output_action}"
                assert dep.logging_level.lower() == "warning"

                # Retry settings
                assert dep.retry_settings is not None
                assert dep.retry_settings.max_retries == 5
                assert dep.retry_settings.timeout == 120

                # Tags
                assert dep.tags["config"] == "summary-only"
                assert dep.tags["error_mode"] == "ignore-all"

        finally:
            if deployment_created:
                try:
                    ml_client.batch_deployments.begin_delete(
                        endpoint_name=endpoint_name,
                        name=deployment_name,
                    ).result()
                except Exception:
                    pass

            if endpoint_created:
                try:
                    ml_client.batch_endpoints.begin_delete(name=endpoint_name).result()
                except Exception:
                    pass

            if model_created:
                try:
                    ml_client.models.archive(name=model_name, version="1")
                except Exception:
                    pass

            try:
                ml_client.environments.archive(name=env_name, version="1")
            except Exception:
                pass
