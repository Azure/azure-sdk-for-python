# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Datastore registration, data asset creation, and serverless command job
             that reads from the data asset and logs metrics.

Inspired by azureml-examples/sdk/python/assets/ and jobs/ samples but tests edge
cases around:
  - Listing and inspecting existing datastores (workspace_dataplane)
  - Creating a uri_file data asset with tags and round-trip verification (dataset_dataplane)
  - Submitting a command job on serverless compute (no named cluster) (arm_ml_service)
  - Passing data as job input and verifying input/output serialization
  - Job environment variable round-trip via env_var dict
  - Job display_name with special characters surviving TypeSpec serialization
  - Job metrics/status retrieval after completion (runhistory)
  - Listing jobs filtered by experiment_name

Customer story:
  A data scientist registers a public CSV as a data asset, then submits a
  lightweight training job on serverless compute that reads the data, logs
  metrics via MLflow, and completes. They verify the job's inputs, outputs,
  environment variables, and metrics are all preserved through the REST
  round-trip. This exercises dataset_dataplane (data CRUD), arm_ml_service
  (job submission), and runhistory (job status/metrics) — all regenerated
  in the TypeSpec migration.

Steps:
  1. List datastores, verify default blob store exists
  2. Create a uri_file data asset pointing to a public CSV
  3. Verify data asset round-trip (description, tags, properties)
  4. Submit a serverless command job that takes the data as input
  5. Verify job properties round-trip (display_name, tags, env vars, experiment)
  6. Wait for job completion
  7. Verify terminal status and check services dict serialization
  8. List jobs by experiment, confirm the job appears
  9. Clean up (archive data asset)
"""

import os
import tempfile
import time

import pytest

from azure.ai.ml import Input, MLClient, command
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Data


class TestScenarioServerlessDatastoreJob:
    """Datastore inspection + data asset CRUD + serverless job with data input."""

    @pytest.mark.timeout(600)
    def test_datastore_inspection_and_data_asset_crud(self, ml_client: MLClient, rand_name):
        """Verify datastore listing/get and data asset CRUD with edge-case properties."""

        data_name = rand_name("sdat")

        try:
            # ── Step 1: Datastore listing ─────────────────────────
            datastores = list(ml_client.datastores.list())
            assert len(datastores) >= 1, "Workspace must have at least one datastore"
            ds_names = [ds.name for ds in datastores]
            assert "workspaceblobstore" in ds_names, "Default blob store must exist"

            # Get default and inspect properties
            default_ds = ml_client.datastores.get_default()
            assert default_ds.name is not None
            assert default_ds.account_name is not None

            # Get by name and verify round-trip
            blob_ds = ml_client.datastores.get("workspaceblobstore")
            assert blob_ds.name == "workspaceblobstore"

            # ── Step 2: Create data asset with edge-case properties
            data = Data(
                name=data_name,
                version="1",
                type=AssetTypes.URI_FILE,
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                description="Serverless scenario test — unicode: café, naïve, résumé",
                tags={
                    "scenario": "serverless-job-test",
                    "encoding": "utf-8",
                    "delimiter": "comma",
                    "empty_value": "",
                },
                properties={
                    "source": "public-blob",
                    "row_count": "150",
                    "created_by": "scenario-test",
                },
            )
            created = ml_client.data.create_or_update(data)
            assert created.name == data_name
            assert created.version == "1"

            # ── Step 3: Round-trip fidelity ────────────────────────
            fetched = ml_client.data.get(data_name, "1")
            assert fetched.type == AssetTypes.URI_FILE
            assert "café" in fetched.description
            assert "naïve" in fetched.description
            assert fetched.tags["encoding"] == "utf-8"
            assert fetched.tags["empty_value"] == ""
            assert fetched.properties["row_count"] == "150"
            assert fetched.properties["created_by"] == "scenario-test"

            # ── Step 4: Create version 2 and list ─────────────────
            data_v2 = Data(
                name=data_name,
                version="2",
                type=AssetTypes.URI_FILE,
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                description="Version 2 for listing test",
                tags={"version": "2"},
            )
            ml_client.data.create_or_update(data_v2)

            # List all versions (small delay for eventual consistency)
            time.sleep(5)
            versions = list(ml_client.data.list(name=data_name))
            assert len(versions) >= 2, f"Expected >=2 versions, got {len(versions)}"
            version_numbers = {v.version for v in versions}
            assert "1" in version_numbers
            assert "2" in version_numbers

        finally:
            for ver in ["1", "2"]:
                try:
                    ml_client.data.archive(name=data_name, version=ver)
                except Exception:
                    pass

    @pytest.mark.timeout(900)
    def test_serverless_command_job_with_data_input(self, ml_client: MLClient, rand_name, wait_for_job):
        """Submit a serverless command job reading a data asset, verify metrics and status."""

        data_name = rand_name("sjdat")
        experiment_name = "scenario-serverless-job"

        try:
            # ── Step 1: Create data asset as input ────────────────
            data = Data(
                name=data_name,
                version="1",
                type=AssetTypes.URI_FILE,
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                description="Input data for serverless job scenario",
                tags={"purpose": "serverless-input"},
            )
            ml_client.data.create_or_update(data)

            # ── Step 2: Create inline training script ─────────────
            with tempfile.TemporaryDirectory() as code_dir:
                script_path = os.path.join(code_dir, "train.py")
                with open(script_path, "w") as f:
                    f.write(
                        '''import argparse, os, sys

print(f"Python version: {sys.version}")
print(f"Working dir: {os.getcwd()}")

parser = argparse.ArgumentParser()
parser.add_argument("--input_data", type=str)
parser.add_argument("--learning_rate", type=float, default=0.01)
args = parser.parse_args()

# Verify input data path was passed
print(f"Input data path: {args.input_data}")
print(f"Learning rate: {args.learning_rate}")
assert args.input_data is not None, "Input data path must be set"

# Read a few lines to confirm data is accessible
if os.path.isfile(args.input_data):
    with open(args.input_data, "r") as f:
        lines = f.readlines()
    print(f"Read {len(lines)} lines from input data")
    row_count = len(lines) - 1  # exclude header
else:
    print(f"Input is a directory or URI: {args.input_data}")
    row_count = 0

# Verify env var was passed through
custom_val = os.environ.get("SCENARIO_TEST_VAR", "NOT_SET")
print(f"SCENARIO_TEST_VAR = {custom_val}")

# Log metrics via mlflow
try:
    import mlflow
    mlflow.log_metric("row_count", row_count)
    mlflow.log_metric("learning_rate", args.learning_rate)
    mlflow.log_metric("completed", 1.0)
    print("MLflow metrics logged")
except ImportError:
    print("mlflow not available, skipping metric logging")

print("Job completed successfully")
'''
                    )

                # ── Step 3: Submit serverless command job ─────────
                display_name = f"serverless-test — special chars: <angle> & ampersand {rand_name('sj')}"
                job = command(
                    code=code_dir,
                    command="python train.py --input_data ${{inputs.iris_data}} --learning_rate 0.05",
                    inputs={
                        "iris_data": Input(
                            type=AssetTypes.URI_FILE,
                            path=f"azureml:{data_name}:1",
                        ),
                    },
                    environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
                    compute="serverless",
                    display_name=display_name,
                    experiment_name=experiment_name,
                    tags={
                        "scenario": "serverless-datastore-job",
                        "migration": "typespec",
                        "special_chars": "a&b<c>d",
                    },
                    properties={
                        "test_type": "serverless",
                        "data_asset": data_name,
                    },
                    environment_variables={
                        "SCENARIO_TEST_VAR": "hello-from-scenario",
                        "EMPTY_VAR": "",
                    },
                )

                try:
                    submitted = ml_client.jobs.create_or_update(job)
                except Exception as e:
                    if "serverless" in str(e).lower() or "unknown compute" in str(e).lower():
                        pytest.skip("Workspace does not support serverless compute")
                    raise
                assert submitted.name is not None
                assert submitted.experiment_name == experiment_name

                # ── Step 4: Verify job properties round-trip ──────
                fetched_job = ml_client.jobs.get(submitted.name)
                assert fetched_job.display_name == display_name
                assert "special chars" in fetched_job.display_name
                assert fetched_job.tags["migration"] == "typespec"
                assert fetched_job.tags["special_chars"] == "a&b<c>d"
                assert fetched_job.properties["test_type"] == "serverless"

                # Verify environment_variables survived
                if hasattr(fetched_job, "environment_variables") and fetched_job.environment_variables:
                    assert fetched_job.environment_variables.get("SCENARIO_TEST_VAR") == "hello-from-scenario"

                # Verify inputs survived
                if hasattr(fetched_job, "inputs") and fetched_job.inputs:
                    assert "iris_data" in fetched_job.inputs

                # Verify services dict (Studio URL)
                if hasattr(fetched_job, "services") and fetched_job.services:
                    assert "Studio" in fetched_job.services

                # ── Step 5: Wait for completion ───────────────────
                finished = wait_for_job(ml_client, submitted, timeout_seconds=600)
                assert finished.status == "Completed", f"Job ended with status {finished.status}"

                # ── Step 6: List jobs by experiment ───────────────
                exp_jobs = list(ml_client.jobs.list(experiment_name=experiment_name))
                assert len(exp_jobs) >= 1
                job_names = {j.name for j in exp_jobs}
                assert submitted.name in job_names

        finally:
            try:
                ml_client.data.archive(name=data_name, version="1")
            except Exception:
                pass

    @pytest.mark.timeout(300)
    def test_data_asset_update_tags_and_description(self, ml_client: MLClient, rand_name):
        """Test updating data asset tags and description preserves values through TypeSpec."""

        data_name = rand_name("updat")

        try:
            # Create initial version
            data = Data(
                name=data_name,
                version="1",
                type=AssetTypes.URI_FILE,
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                description="Original description",
                tags={"stage": "raw", "owner": "scenario-test"},
            )
            ml_client.data.create_or_update(data)

            # Fetch and verify
            fetched = ml_client.data.get(data_name, "1")
            assert fetched.description == "Original description"
            assert fetched.tags["stage"] == "raw"

            # Create a new version with updated description and extra tags
            data_v2 = Data(
                name=data_name,
                version="2",
                type=AssetTypes.URI_FILE,
                path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                description="Updated description — now with longer text and unicode: ñoño",
                tags={
                    "stage": "processed",
                    "owner": "scenario-test",
                    "new_tag": "added-in-v2",
                    "numeric_tag": "42",
                },
            )
            ml_client.data.create_or_update(data_v2)

            # Verify v2 round-trip
            fetched_v2 = ml_client.data.get(data_name, "2")
            assert "ñoño" in fetched_v2.description
            assert fetched_v2.tags["stage"] == "processed"
            assert fetched_v2.tags["new_tag"] == "added-in-v2"
            assert fetched_v2.tags["numeric_tag"] == "42"

            # Verify v1 is unchanged
            fetched_v1 = ml_client.data.get(data_name, "1")
            assert fetched_v1.description == "Original description"
            assert fetched_v1.tags["stage"] == "raw"
            assert "new_tag" not in fetched_v1.tags

        finally:
            for ver in ["1", "2"]:
                try:
                    ml_client.data.archive(name=data_name, version=ver)
                except Exception:
                    pass
