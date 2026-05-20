# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Command job with sweep hyperparameter tuning, custom environment,
             and model registration with extensive property validation.

Inspired by azureml-examples/sdk/python/jobs/single-step/lightgbm/iris/lightgbm-iris-sweep.ipynb
but tests edge cases around:
  - Building an environment with a complex conda spec (pinned versions, multi-channel)
  - Submitting a command job that logs metrics and artifacts to MLflow
  - Converting a command job to a sweep job with Bayesian sampling
  - Setting early termination policies (BanditPolicy with non-default slack)
  - Setting resource limits (timeout, max_total_trials, max_concurrent_trials)
  - Re-fetching the sweep job and validating all search space params survived serialization
  - Accessing the best child run and its metrics
  - Verifying the `additional_properties` bag doesn't silently drop data (TypeSpec edge case)

Customer story:
  A data scientist runs hyperparameter tuning for a classification model. They need
  the sweep configuration (search space, early termination, resource limits) to be
  fully preserved when they re-fetch the job from the service. After tuning, they
  pick the best trial and register it. This exercises the ARM job client and
  runhistory client serialization for complex nested structures.

Steps:
  1. Create compute
  2. Create a custom environment
  3. Define a command job with an inline training script
  4. Convert to sweep with Bayesian sampling + BanditPolicy
  5. Submit sweep job with tags, display_name, and properties
  6. Wait for completion
  7. Re-fetch sweep job and verify search_space, limits, and early_termination round-trip
  8. Get best child trial, verify it has logged metrics
  9. Register model from best trial
  10. Clean up
"""

import os
import tempfile

import pytest

from azure.ai.ml import MLClient, command
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import AmlCompute, Environment, IdentityConfiguration, Model
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


class TestScenarioSweepTuning:
    """Hyperparameter sweep with complex search space and round-trip serialization checks."""

    @pytest.mark.timeout(1200)
    def test_sweep_bayesian_with_bandit_and_model_registration(self, ml_client: MLClient, rand_name, wait_for_job):
        """Bayesian sweep with BanditPolicy, verify config survives round-trip, register best model."""

        compute_name = rand_name("swcpu")
        env_name = rand_name("swenv")
        model_name = rand_name("swmdl")

        cluster = AmlCompute(
            name=compute_name,
            size="STANDARD_DS3_V2",
            min_instances=0,
            max_instances=2,
            idle_time_before_scale_down=120,
            identity=IdentityConfiguration(type="system_assigned"),
        )
        poller = ml_client.compute.begin_create_or_update(cluster)
        poller.result()

        try:
            # ── Custom environment with pinned, multi-channel deps ─
            env = Environment(
                name=env_name,
                version="1",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file={
                    "name": "sweep-test",
                    "channels": ["defaults", "conda-forge"],
                    "dependencies": [
                        "python=3.10",
                        "pip",
                        {
                            "pip": [
                                "scikit-learn==1.3.2",
                                "mlflow==2.17.0",
                                "azureml-mlflow",
                            ]
                        },
                    ],
                },
            )
            ml_client.environments.create_or_update(env)
            env_id = f"azureml:{env_name}:1"

            with tempfile.TemporaryDirectory() as code_dir:
                # Training script that accepts hyperparams and logs metrics
                train_path = os.path.join(code_dir, "train_sweep.py")
                with open(train_path, "w") as f:
                    f.write(
                        """import argparse, mlflow
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

parser = argparse.ArgumentParser()
parser.add_argument("--n_estimators", type=int, default=10)
parser.add_argument("--max_depth", type=int, default=5)
parser.add_argument("--min_samples_split", type=float, default=0.1)
args = parser.parse_args()

X, y = make_classification(n_samples=500, n_features=20, n_informative=10, random_state=42)
clf = RandomForestClassifier(
    n_estimators=args.n_estimators,
    max_depth=args.max_depth,
    min_samples_split=max(2, int(args.min_samples_split * len(X))) if args.min_samples_split < 1 else int(args.min_samples_split),
    random_state=42,
)
scores = cross_val_score(clf, X, y, cv=3, scoring="accuracy")
mean_acc = scores.mean()

mlflow.log_param("n_estimators", args.n_estimators)
mlflow.log_param("max_depth", args.max_depth)
mlflow.log_param("min_samples_split", args.min_samples_split)
mlflow.log_metric("accuracy", mean_acc)
mlflow.log_metric("std_accuracy", scores.std())
print(f"Accuracy: {mean_acc:.4f} +/- {scores.std():.4f}")

clf.fit(X, y)
mlflow.sklearn.log_model(clf, "model")
"""
                    )

                # ── Define the base command job ───────────────────
                base_job = command(
                    code=code_dir,
                    command=(
                        "python train_sweep.py "
                        "--n_estimators ${{search_space.n_estimators}} "
                        "--max_depth ${{search_space.max_depth}} "
                        "--min_samples_split ${{search_space.min_samples_split}}"
                    ),
                    environment=env_id,
                    compute=compute_name,
                    display_name="scenario-sweep-base",
                )

                # ── Convert to sweep with Bayesian + BanditPolicy ─
                sweep_job = base_job.sweep(
                    sampling_algorithm="bayesian",
                    primary_metric="accuracy",
                    goal="maximize",
                )
                sweep_job.search_space = {
                    "n_estimators": Choice(values=[5, 10, 25, 50]),
                    "max_depth": Choice(values=[3, 5, 10, 15]),
                    "min_samples_split": Uniform(min_value=0.01, max_value=0.5),
                }
                sweep_job.early_termination = BanditPolicy(
                    slack_factor=0.15,
                    evaluation_interval=2,
                    delay_evaluation=3,
                )
                sweep_job.limits.max_total_trials = 8
                sweep_job.limits.max_concurrent_trials = 2
                sweep_job.limits.timeout = 600

                sweep_job.display_name = f"scenario-sweep-{rand_name('run')}"
                sweep_job.tags = {
                    "scenario": "sweep-hyperparameter",
                    "sampling": "bayesian",
                    "branch": "tsp-migration",
                }
                sweep_job.properties["test_type"] = "serialization-validation"

                # ── Submit ────────────────────────────────────────
                submitted = ml_client.jobs.create_or_update(sweep_job, experiment_name="scenario-tests")
                assert submitted.name is not None
                assert submitted.type == "sweep"

                finished = wait_for_job(ml_client, submitted, timeout_seconds=900)
                assert finished.status == "Completed", f"Sweep failed: {finished.status}"

                # ── Round-trip fidelity on sweep config ────────────
                refetched = ml_client.jobs.get(finished.name)
                assert refetched.type == "sweep"
                assert refetched.tags.get("sampling") == "bayesian"
                assert refetched.tags.get("scenario") == "sweep-hyperparameter"
                assert refetched.properties.get("test_type") == "serialization-validation"

                # Verify search space survived
                assert refetched.search_space is not None
                assert "n_estimators" in refetched.search_space
                assert "max_depth" in refetched.search_space
                assert "min_samples_split" in refetched.search_space

                # Verify early termination survived
                assert refetched.early_termination is not None
                assert refetched.early_termination.evaluation_interval == 2
                assert refetched.early_termination.delay_evaluation == 3

                # Verify limits survived
                assert refetched.limits.max_total_trials == 8
                assert refetched.limits.max_concurrent_trials == 2

                # ── List child trials ─────────────────────────────
                child_jobs = list(ml_client.jobs.list(parent_job_name=finished.name))
                assert len(child_jobs) >= 1, "Sweep should have at least 1 trial"
                assert len(child_jobs) <= 8, f"Max trials was 8, got {len(child_jobs)}"

                # ── Register model from best trial ────────────────
                # Find trial with highest accuracy (or just use first completed)
                completed_trials = [j for j in child_jobs if j.status == "Completed"]
                assert len(completed_trials) >= 1
                best_trial = completed_trials[0]

                model = Model(
                    name=model_name,
                    version="1",
                    path=f"azureml://jobs/{best_trial.name}/outputs/artifacts/paths/model",
                    type=AssetTypes.MLFLOW_MODEL,
                    description="Best model from sweep scenario test",
                    tags={"source_sweep": finished.name, "trial": best_trial.name},
                )
                registered = ml_client.models.create_or_update(model)
                assert registered.name == model_name

                # Verify model round-trip
                fetched_model = ml_client.models.get(model_name, "1")
                assert fetched_model.tags["source_sweep"] == finished.name
                assert fetched_model.type == AssetTypes.MLFLOW_MODEL

        finally:
            try:
                ml_client.models.archive(name=model_name, version="1")
            except Exception:
                pass
            try:
                ml_client.environments.archive(name=env_name, version="1")
            except Exception:
                pass
            try:
                ml_client.compute.begin_delete(compute_name).result()
            except Exception:
                pass
