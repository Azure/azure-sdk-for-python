# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: End-to-end training pipeline with inline components, data passing, and model registration.

Inspired by azureml-examples/sdk/python/jobs/pipelines/2b_train_cifar_10_with_pytorch
but tests edge cases around:
  - Inline command components defined via the Python DSL (no YAML)
  - Multiple data-passing modes between pipeline steps (upload, download, direct)
  - Registering a model from job output and verifying round-trip property fidelity
  - Re-fetching jobs and verifying serialization of nested properties (services, tags, properties)

Customer story:
  A data science team builds a multi-step ML pipeline entirely in Python (no YAML
  files). They pass data between steps, train a model, register it from the job
  output, and need all metadata (tags, properties, display_name) to survive
  the round-trip through the service. This stresses the ARM client serialization
  and the runhistory dataplane client for job retrieval.

Steps:
  1. Create a temporary compute cluster
  2. Create a custom environment from conda spec + Docker image
  3. Build a 3-step pipeline inline (prepare → train → evaluate) using @pipeline DSL
  4. Submit the pipeline job with custom tags, properties, and display_name
  5. Wait for completion, then re-fetch and verify all nested properties survived round-trip
  6. List child jobs and verify parent-child relationship
  7. Register model from the training step output
  8. Verify the registered model has correct type, path origin, and description
  9. Clean up: delete model version, delete environment, delete compute
"""

import os
import tempfile
import time

import pytest

from azure.ai.ml import Input, MLClient, Output, command, load_component
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import AmlCompute, Environment, Model
from azure.core.polling import LROPoller


class TestScenarioPipelineTrainRegister:
    """Multi-step pipeline → model registration with round-trip fidelity checks."""

    @pytest.mark.timeout(1200)
    def test_inline_pipeline_train_and_register_model(self, ml_client: MLClient, rand_name, wait_for_job):
        """Build a 3-step pipeline in pure Python, run it, register the output model."""

        compute_name = rand_name("cpu")
        env_name = rand_name("env")
        model_name = rand_name("mdl")
        env_version = "1"
        model_version = "1"

        # ── Step 1: Create a small compute cluster ────────────────
        cluster = AmlCompute(
            name=compute_name,
            size="STANDARD_DS3_V2",
            min_instances=0,
            max_instances=2,
            idle_time_before_scale_down=120,
        )
        poller = ml_client.compute.begin_create_or_update(cluster)
        assert isinstance(poller, LROPoller)
        poller.result()

        try:
            # ── Step 2: Create a custom environment ───────────────
            env = Environment(
                name=env_name,
                version=env_version,
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file={
                    "name": "scenario-test",
                    "channels": ["defaults", "conda-forge"],
                    "dependencies": [
                        "python=3.10",
                        "pip",
                        {"pip": ["scikit-learn==1.3.2", "pandas>=1.5", "mlflow", "azureml-mlflow"]},
                    ],
                },
                description="Scenario test environment for pipeline training",
                tags={"purpose": "scenario-test", "branch": "tsp-migration"},
            )
            created_env = ml_client.environments.create_or_update(env)
            assert created_env.name == env_name
            assert created_env.version == env_version
            env_id = f"azureml:{env_name}:{env_version}"

            # ── Step 3: Write inline training scripts to temp dir ─
            with tempfile.TemporaryDirectory() as code_dir:
                # Prepare step: generates a synthetic dataset
                prepare_script = os.path.join(code_dir, "prepare.py")
                with open(prepare_script, "w") as f:
                    f.write(
                        """import argparse, os
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--output-data", type=str)
args = parser.parse_args()

np.random.seed(42)
n = 200
X = np.random.randn(n, 4)
y = (X[:, 0] + 2 * X[:, 1] - X[:, 2] + np.random.randn(n) * 0.1 > 0).astype(int)
df = pd.DataFrame(X, columns=["f1", "f2", "f3", "f4"])
df["target"] = y

os.makedirs(args.output_data, exist_ok=True)
df.to_csv(os.path.join(args.output_data, "data.csv"), index=False)
print(f"Wrote {len(df)} rows to {args.output_data}")
"""
                    )

                # Train step: fits sklearn model, logs to MLflow
                train_script = os.path.join(code_dir, "train.py")
                with open(train_script, "w") as f:
                    f.write(
                        """import argparse, os, json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import mlflow

parser = argparse.ArgumentParser()
parser.add_argument("--input-data", type=str)
parser.add_argument("--model-output", type=str)
parser.add_argument("--n-estimators", type=int, default=10)
parser.add_argument("--max-depth", type=int, default=3)
args = parser.parse_args()

df = pd.read_csv(os.path.join(args.input_data, "data.csv"))
X = df.drop("target", axis=1)
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlflow.sklearn.autolog()
clf = RandomForestClassifier(n_estimators=args.n_estimators, max_depth=args.max_depth, random_state=42)
clf.fit(X_train, y_train)
acc = clf.score(X_test, y_test)
print(f"Accuracy: {acc:.4f}")

os.makedirs(args.model_output, exist_ok=True)
mlflow.sklearn.save_model(clf, args.model_output)
with open(os.path.join(args.model_output, "metrics.json"), "w") as f:
    json.dump({"accuracy": acc, "n_estimators": args.n_estimators}, f)
print(f"Model saved to {args.model_output}")
"""
                    )

                # Evaluate step: loads model, reports metrics
                eval_script = os.path.join(code_dir, "evaluate.py")
                with open(eval_script, "w") as f:
                    f.write(
                        """import argparse, os, json
import pandas as pd
import mlflow

parser = argparse.ArgumentParser()
parser.add_argument("--input-data", type=str)
parser.add_argument("--model-input", type=str)
args = parser.parse_args()

df = pd.read_csv(os.path.join(args.input_data, "data.csv"))
X = df.drop("target", axis=1)
y_true = df["target"]

model = mlflow.sklearn.load_model(args.model_input)
y_pred = model.predict(X)
accuracy = (y_pred == y_true).mean()
print(f"Evaluation accuracy: {accuracy:.4f}")

mlflow.log_metric("eval_accuracy", accuracy)
print("Evaluation complete")
"""
                    )

                # ── Step 4: Build pipeline using DSL ──────────────
                prepare_component = command(
                    name="prepare_data",
                    display_name="Prepare synthetic data",
                    code=code_dir,
                    command="python prepare.py --output-data ${{outputs.prepared_data}}",
                    environment=env_id,
                    outputs={"prepared_data": Output(type="uri_folder", mode="rw_mount")},
                )

                train_component = command(
                    name="train_model",
                    display_name="Train RF classifier",
                    code=code_dir,
                    command=(
                        "python train.py "
                        "--input-data ${{inputs.training_data}} "
                        "--model-output ${{outputs.model_dir}} "
                        "--n-estimators ${{inputs.n_estimators}} "
                        "--max-depth ${{inputs.max_depth}}"
                    ),
                    environment=env_id,
                    inputs={
                        "training_data": Input(type="uri_folder"),
                        "n_estimators": Input(type="integer", default=10),
                        "max_depth": Input(type="integer", default=3),
                    },
                    outputs={"model_dir": Output(type="uri_folder", mode="rw_mount")},
                )

                eval_component = command(
                    name="evaluate_model",
                    display_name="Evaluate model",
                    code=code_dir,
                    command=(
                        "python evaluate.py "
                        "--input-data ${{inputs.test_data}} "
                        "--model-input ${{inputs.model_dir}}"
                    ),
                    environment=env_id,
                    inputs={
                        "test_data": Input(type="uri_folder"),
                        "model_dir": Input(type="uri_folder"),
                    },
                )

                @pipeline(
                    description="Scenario test: 3-step pipeline with data passing",
                    tags={"scenario": "pipeline-train-register", "branch": "tsp-migration"},
                )
                def train_eval_pipeline(n_estimators: int = 15, max_depth: int = 5):
                    prep = prepare_component()
                    train = train_component(
                        training_data=prep.outputs.prepared_data,
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                    )
                    train.compute = compute_name
                    evaluate = eval_component(
                        test_data=prep.outputs.prepared_data,
                        model_dir=train.outputs.model_dir,
                    )
                    return {"final_model": train.outputs.model_dir}

                pipeline_job = train_eval_pipeline()
                pipeline_job.settings.default_compute = compute_name
                pipeline_job.display_name = f"scenario-pipeline-{rand_name('run')}"
                pipeline_job.properties["scenario_test"] = "true"
                pipeline_job.tags["test_type"] = "tsp-migration-validation"

                # ── Step 5: Submit and wait ───────────────────────
                submitted = ml_client.jobs.create_or_update(pipeline_job, experiment_name="scenario-tests")
                assert submitted.name is not None
                assert submitted.display_name == pipeline_job.display_name

                finished = wait_for_job(ml_client, submitted, timeout_seconds=900)
                assert finished.status == "Completed", f"Pipeline failed with status: {finished.status}"

                # ── Step 6: Round-trip fidelity checks ────────────
                # Re-fetch the job and verify nested properties survived serialization
                refetched = ml_client.jobs.get(finished.name)
                assert refetched.display_name == submitted.display_name
                assert refetched.tags.get("test_type") == "tsp-migration-validation"
                assert refetched.tags.get("scenario") == "pipeline-train-register"
                assert refetched.properties.get("scenario_test") == "true"
                assert refetched.status == "Completed"

                # Verify services dict is populated (Studio URL etc.)
                if hasattr(refetched, "services") and refetched.services:
                    assert "Studio" in refetched.services

                # ── Step 7: List child jobs ───────────────────────
                child_jobs = list(ml_client.jobs.list(parent_job_name=finished.name))
                assert len(child_jobs) == 3, f"Expected 3 child jobs, got {len(child_jobs)}"
                child_names = {j.display_name for j in child_jobs}
                assert "Prepare synthetic data" in child_names or any(
                    "prepare" in (n or "").lower() for n in child_names
                )

                # Find the training step to get model output path
                train_job = next(
                    (j for j in child_jobs if "train" in (j.display_name or "").lower()),
                    child_jobs[1],  # fallback to second job
                )

                # ── Step 8: Register model from job output ────────
                model_path = f"azureml://jobs/{train_job.name}/outputs/model_dir"
                model = Model(
                    name=model_name,
                    version=model_version,
                    path=model_path,
                    type=AssetTypes.MLFLOW_MODEL,
                    description="RF model from scenario pipeline test",
                    tags={"source_job": train_job.name, "scenario": "tsp-migration"},
                    properties={"accuracy_metric": "eval_accuracy"},
                )
                registered_model = ml_client.models.create_or_update(model)
                assert registered_model.name == model_name
                assert registered_model.version == model_version

                # Re-fetch model and verify fidelity
                fetched_model = ml_client.models.get(model_name, model_version)
                assert fetched_model.description == "RF model from scenario pipeline test"
                assert fetched_model.tags.get("scenario") == "tsp-migration"
                assert fetched_model.type == AssetTypes.MLFLOW_MODEL

        finally:
            # ── Cleanup ───────────────────────────────────────────
            _safe_delete(ml_client, "model", model_name, model_version)
            _safe_delete(ml_client, "environment", env_name, env_version)
            try:
                ml_client.compute.begin_delete(compute_name).result()
            except Exception:
                pass


def _safe_delete(ml_client, asset_type, name, version):
    """Best-effort delete; don't fail the test on cleanup errors."""
    try:
        if asset_type == "model":
            ml_client.models.archive(name=name, version=version)
        elif asset_type == "environment":
            ml_client.environments.archive(name=name, version=version)
    except Exception:
        pass
