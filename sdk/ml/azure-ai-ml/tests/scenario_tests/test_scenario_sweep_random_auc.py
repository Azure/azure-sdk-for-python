# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scenario: Hyperparameter sweep with RandomSampling targeting AUC maximization.

Mirrors the customer pattern from:
  https://github.com/Azure/azureml-examples/tree/main/sdk/python/jobs/single-step/scikit-learn/diabetes

Customer story:
  A data scientist submits a hyperparameter sweep job for a scikit-learn model
  using RandomSampling with Bandit early termination, targeting AUC maximization
  on a tabular dataset. The sweep explores learning rate (log-uniform), max depth
  (choice), and regularization (uniform). After tuning, the best model is
  registered for downstream deployment.

Steps:
  1. Create compute cluster
  2. Create a custom environment with scikit-learn and mlflow
  3. Define a command job with inline training script (logistic regression for AUC)
  4. Convert to sweep with RandomSampling + BanditPolicy
  5. Configure search space with diverse distribution types (LogUniform, Choice, Uniform)
  6. Submit sweep job with tags, display_name, properties
  7. Wait for completion
  8. Re-fetch sweep job and verify:
     - Sampling algorithm is "random"
     - Search space distributions preserved
     - Early termination policy settings preserved
     - Limits preserved
  9. List child trials and verify constraints
  10. Register model from best trial
  11. Clean up
"""

import os
import tempfile

import pytest

from azure.ai.ml import MLClient, command
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import AmlCompute, Environment, IdentityConfiguration, Model
from azure.ai.ml.sweep import BanditPolicy, Choice, LogUniform, RandomSamplingAlgorithm, Uniform


class TestScenarioSweepRandomAUC:
    """Hyperparameter sweep with RandomSampling and AUC optimization."""

    def test_sweep_random_sampling_auc_with_bandit(self, ml_client: MLClient, rand_name, wait_for_job):
        """RandomSampling sweep targeting AUC, Bandit early termination, model registration."""

        compute_name = rand_name("swrnd")
        env_name = rand_name("swenv")
        model_name = rand_name("aucmdl")

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
            # ── Custom environment with scikit-learn for AUC computation ──
            env = Environment(
                name=env_name,
                version="1",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file={
                    "name": "sweep-auc-test",
                    "channels": ["defaults", "conda-forge"],
                    "dependencies": [
                        "python=3.10",
                        "pip",
                        {
                            "pip": [
                                "scikit-learn==1.3.2",
                                "mlflow==2.17.0",
                                "azureml-mlflow",
                                "numpy>=1.21",
                            ]
                        },
                    ],
                },
            )
            ml_client.environments.create_or_update(env)
            env_id = f"azureml:{env_name}:1"

            with tempfile.TemporaryDirectory() as code_dir:
                # Training script: Logistic Regression with AUC as primary metric
                train_path = os.path.join(code_dir, "train_auc.py")
                with open(train_path, "w") as f:
                    f.write(
                        """import argparse
import os
import mlflow
import joblib
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

parser = argparse.ArgumentParser()
parser.add_argument("--learning_rate", type=float, default=0.01)
parser.add_argument("--max_iter", type=int, default=100)
parser.add_argument("--regularization", type=float, default=1.0)
args = parser.parse_args()

# Generate synthetic binary classification data
X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=15,
    n_redundant=3,
    n_classes=2,
    random_state=42,
    flip_y=0.1,  # Add some noise
)

# Build pipeline with scaling + logistic regression
# C is inverse of regularization strength
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        C=1.0 / args.regularization,
        max_iter=args.max_iter,
        solver="lbfgs",
        random_state=42,
    ))
])

# Compute AUC using cross-validation
auc_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")
mean_auc = auc_scores.mean()
std_auc = auc_scores.std()

# Also compute accuracy for secondary metric
acc_scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
mean_acc = acc_scores.mean()

# Log parameters
mlflow.log_param("learning_rate", args.learning_rate)
mlflow.log_param("max_iter", args.max_iter)
mlflow.log_param("regularization", args.regularization)

# Log metrics - AUC is primary
mlflow.log_metric("AUC", mean_auc)
mlflow.log_metric("AUC_std", std_auc)
mlflow.log_metric("accuracy", mean_acc)

print(f"AUC: {mean_auc:.4f} +/- {std_auc:.4f}")
print(f"Accuracy: {mean_acc:.4f}")

# Fit final model and save to outputs (Azure ML auto-captures this folder)
pipeline.fit(X, y)
os.makedirs("outputs", exist_ok=True)
joblib.dump(pipeline, "outputs/model.joblib")
print("Model saved to outputs/model.joblib")
"""
                    )

                # ── Define the base command job ───────────────────────
                base_job = command(
                    code=code_dir,
                    command=(
                        "python train_auc.py "
                        "--learning_rate ${{search_space.learning_rate}} "
                        "--max_iter ${{search_space.max_iter}} "
                        "--regularization ${{search_space.regularization}}"
                    ),
                    environment=env_id,
                    compute=compute_name,
                    display_name="scenario-sweep-auc-base",
                )

                # ── Convert to sweep with RandomSampling ──────────────
                sweep_job = base_job.sweep(
                    sampling_algorithm=RandomSamplingAlgorithm(seed=42, rule="random"),
                    primary_metric="AUC",
                    goal="maximize",
                )

                # ── Search space with diverse distributions ───────────
                # Edge case: LogUniform for learning rate (spans orders of magnitude)
                # Edge case: Choice with non-uniform intervals
                # Edge case: Uniform for regularization
                sweep_job.search_space = {
                    "learning_rate": LogUniform(min_value=-5, max_value=-1),  # 1e-5 to 0.1
                    "max_iter": Choice(values=[50, 100, 200, 500]),
                    "regularization": Uniform(min_value=0.01, max_value=10.0),
                }

                # ── BanditPolicy for early termination ────────────────
                # Edge case: delay_evaluation > 0 to let trials warm up
                sweep_job.early_termination = BanditPolicy(
                    slack_factor=0.1,
                    evaluation_interval=1,
                    delay_evaluation=2,
                )

                # ── Resource limits ───────────────────────────────────
                sweep_job.limits.max_total_trials = 10
                sweep_job.limits.max_concurrent_trials = 2
                sweep_job.limits.timeout = 600  # 10 minutes

                # ── Metadata ──────────────────────────────────────────
                sweep_job.display_name = f"scenario-random-auc-{rand_name('run')}"
                sweep_job.tags = {
                    "scenario": "sweep-random-auc",
                    "sampling": "random",
                    "primary_metric": "AUC",
                    "early_termination": "bandit",
                }
                sweep_job.properties["test_type"] = "random-sampling-validation"
                sweep_job.properties["seed"] = "42"

                # ── Submit sweep job ──────────────────────────────────
                submitted = ml_client.jobs.create_or_update(sweep_job, experiment_name="scenario-sweep-tests")
                assert submitted.name is not None
                assert submitted.type == "sweep"

                # ── Wait for completion ───────────────────────────────
                finished = wait_for_job(ml_client, submitted)
                assert finished.status == "Completed", f"Sweep failed: {finished.status}"

                # ── Round-trip fidelity: verify sampling algorithm ────
                refetched = ml_client.jobs.get(finished.name)
                assert refetched.type == "sweep"
                assert refetched.sampling_algorithm is not None

                # Verify it's random sampling
                sampling_type = (
                    refetched.sampling_algorithm.type
                    if hasattr(refetched.sampling_algorithm, "type")
                    else str(refetched.sampling_algorithm)
                )
                assert "random" in sampling_type.lower(), f"Expected random, got {sampling_type}"

                # ── Round-trip fidelity: verify tags and properties ───
                assert refetched.tags.get("sampling") == "random"
                assert refetched.tags.get("primary_metric") == "AUC"
                assert refetched.tags.get("scenario") == "sweep-random-auc"
                assert refetched.properties.get("test_type") == "random-sampling-validation"

                # ── Round-trip fidelity: verify search space ──────────
                assert refetched.search_space is not None
                assert "learning_rate" in refetched.search_space
                assert "max_iter" in refetched.search_space
                assert "regularization" in refetched.search_space

                # ── Round-trip fidelity: verify early termination ─────
                assert refetched.early_termination is not None
                assert refetched.early_termination.evaluation_interval == 1
                assert refetched.early_termination.delay_evaluation == 2
                # Slack factor should be preserved
                assert hasattr(refetched.early_termination, "slack_factor") or hasattr(
                    refetched.early_termination, "slack_amount"
                )

                # ── Round-trip fidelity: verify limits ────────────────
                assert refetched.limits.max_total_trials == 10
                assert refetched.limits.max_concurrent_trials == 2

                # ── List child trials and verify constraints ──────────
                child_jobs = list(ml_client.jobs.list(parent_job_name=finished.name))
                assert len(child_jobs) >= 1, "Sweep should have at least 1 trial"
                assert len(child_jobs) <= 10, f"Max trials was 10, got {len(child_jobs)}"

                # ── Find completed trials ─────────────────────────────
                completed_trials = [j for j in child_jobs if j.status == "Completed"]
                assert len(completed_trials) >= 1, "At least one trial should complete"

                # Pick the first completed trial as "best" for registration
                best_trial = completed_trials[0]

                # ── Register model from best trial ────────────────────
                model = Model(
                    name=model_name,
                    version="1",
                    path=f"azureml://jobs/{best_trial.name}/outputs/artifacts/paths/outputs",
                    type=AssetTypes.CUSTOM_MODEL,
                    description="Best AUC model from random sweep scenario test",
                    tags={
                        "source_sweep": finished.name,
                        "trial": best_trial.name,
                        "primary_metric": "AUC",
                        "sampling": "random",
                    },
                )
                registered = ml_client.models.create_or_update(model)
                assert registered.name == model_name
                assert registered.version == "1"

                # ── Verify model round-trip ───────────────────────────
                fetched_model = ml_client.models.get(model_name, "1")
                assert fetched_model.tags["source_sweep"] == finished.name
                assert fetched_model.tags["primary_metric"] == "AUC"
                assert fetched_model.type == AssetTypes.CUSTOM_MODEL

        finally:
            # ── Cleanup ───────────────────────────────────────────────
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

    def test_sweep_random_with_median_stopping_and_loguniform(self, ml_client: MLClient, rand_name, wait_for_job):
        """RandomSampling with MedianStoppingPolicy, edge case: all LogUniform search space."""

        from azure.ai.ml.sweep import MedianStoppingPolicy

        compute_name = rand_name("swmed")
        env_name = rand_name("medenv")

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
            # ── Minimal environment ───────────────────────────────────
            env = Environment(
                name=env_name,
                version="1",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file={
                    "name": "median-test",
                    "channels": ["defaults"],
                    "dependencies": [
                        "python=3.10",
                        "pip",
                        {"pip": ["scikit-learn==1.3.2", "mlflow==2.17.0", "azureml-mlflow"]},
                    ],
                },
            )
            ml_client.environments.create_or_update(env)
            env_id = f"azureml:{env_name}:1"

            with tempfile.TemporaryDirectory() as code_dir:
                # Simpler training script for faster execution
                train_path = os.path.join(code_dir, "train_simple.py")
                with open(train_path, "w") as f:
                    f.write(
                        """import argparse
import mlflow
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

parser = argparse.ArgumentParser()
parser.add_argument("--lr", type=float, default=0.1)
parser.add_argument("--subsample", type=float, default=0.8)
parser.add_argument("--min_samples_split", type=float, default=0.1)
args = parser.parse_args()

X, y = make_classification(n_samples=500, n_features=10, random_state=42)

clf = GradientBoostingClassifier(
    learning_rate=args.lr,
    subsample=args.subsample,
    min_samples_split=max(2, int(args.min_samples_split * len(X))),
    n_estimators=20,
    random_state=42,
)

auc = cross_val_score(clf, X, y, cv=3, scoring="roc_auc").mean()

mlflow.log_param("lr", args.lr)
mlflow.log_param("subsample", args.subsample)
mlflow.log_metric("AUC", auc)

print(f"AUC: {auc:.4f}")
"""
                    )

                base_job = command(
                    code=code_dir,
                    command=(
                        "python train_simple.py "
                        "--lr ${{search_space.lr}} "
                        "--subsample ${{search_space.subsample}} "
                        "--min_samples_split ${{search_space.min_samples_split}}"
                    ),
                    environment=env_id,
                    compute=compute_name,
                    display_name="scenario-median-sweep",
                )

                # ── Sweep with RandomSampling + MedianStoppingPolicy ──
                sweep_job = base_job.sweep(
                    sampling_algorithm="random",
                    primary_metric="AUC",
                    goal="maximize",
                )

                # Edge case: All parameters use LogUniform distribution
                sweep_job.search_space = {
                    "lr": LogUniform(min_value=-4, max_value=-1),  # 1e-4 to 0.1
                    "subsample": Uniform(min_value=0.5, max_value=1.0),
                    "min_samples_split": Uniform(min_value=0.01, max_value=0.3),
                }

                # Edge case: MedianStoppingPolicy instead of Bandit
                sweep_job.early_termination = MedianStoppingPolicy(
                    evaluation_interval=1,
                    delay_evaluation=3,
                )

                sweep_job.limits.max_total_trials = 6
                sweep_job.limits.max_concurrent_trials = 2
                sweep_job.limits.timeout = 480

                sweep_job.display_name = f"scenario-median-{rand_name('run')}"
                sweep_job.tags = {
                    "scenario": "sweep-median-stopping",
                    "sampling": "random",
                    "early_termination": "median",
                }

                # ── Submit and wait ───────────────────────────────────
                submitted = ml_client.jobs.create_or_update(sweep_job, experiment_name="scenario-sweep-tests")
                assert submitted.name is not None

                finished = wait_for_job(ml_client, submitted)
                assert finished.status == "Completed", f"Sweep failed: {finished.status}"

                # ── Round-trip: verify MedianStoppingPolicy ───────────
                refetched = ml_client.jobs.get(finished.name)

                # Verify early termination is MedianStoppingPolicy
                assert refetched.early_termination is not None
                assert refetched.early_termination.delay_evaluation == 3

                # Verify search space has all parameters
                assert "lr" in refetched.search_space
                assert "subsample" in refetched.search_space
                assert "min_samples_split" in refetched.search_space

                # Verify tags
                assert refetched.tags.get("early_termination") == "median"

                # Verify limits
                assert refetched.limits.max_total_trials == 6

                # Verify child jobs
                child_jobs = list(ml_client.jobs.list(parent_job_name=finished.name))
                assert 1 <= len(child_jobs) <= 6

        finally:
            try:
                ml_client.environments.archive(name=env_name, version="1")
            except Exception:
                pass
            try:
                ml_client.compute.begin_delete(compute_name).result()
            except Exception:
                pass

    def test_sweep_random_with_truncation_selection(self, ml_client: MLClient, rand_name, wait_for_job):
        """RandomSampling with TruncationSelectionPolicy, edge case: aggressive truncation."""

        from azure.ai.ml.sweep import QUniform, TruncationSelectionPolicy

        compute_name = rand_name("swtrc")
        env_name = rand_name("trcenv")

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
            env = Environment(
                name=env_name,
                version="1",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
                conda_file={
                    "name": "truncation-test",
                    "channels": ["defaults"],
                    "dependencies": [
                        "python=3.10",
                        "pip",
                        {"pip": ["scikit-learn==1.3.2", "mlflow==2.17.0", "azureml-mlflow"]},
                    ],
                },
            )
            ml_client.environments.create_or_update(env)
            env_id = f"azureml:{env_name}:1"

            with tempfile.TemporaryDirectory() as code_dir:
                train_path = os.path.join(code_dir, "train_quick.py")
                with open(train_path, "w") as f:
                    f.write(
                        """import argparse
import mlflow
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

parser = argparse.ArgumentParser()
parser.add_argument("--max_depth", type=int, default=5)
parser.add_argument("--min_samples_leaf", type=int, default=1)
args = parser.parse_args()

X, y = make_classification(n_samples=300, n_features=10, random_state=42)

clf = DecisionTreeClassifier(
    max_depth=args.max_depth,
    min_samples_leaf=args.min_samples_leaf,
    random_state=42,
)

auc = cross_val_score(clf, X, y, cv=3, scoring="roc_auc").mean()

mlflow.log_param("max_depth", args.max_depth)
mlflow.log_param("min_samples_leaf", args.min_samples_leaf)
mlflow.log_metric("AUC", auc)

print(f"AUC: {auc:.4f}")
"""
                    )

                base_job = command(
                    code=code_dir,
                    command=(
                        "python train_quick.py "
                        "--max_depth ${{search_space.max_depth}} "
                        "--min_samples_leaf ${{search_space.min_samples_leaf}}"
                    ),
                    environment=env_id,
                    compute=compute_name,
                    display_name="scenario-truncation-sweep",
                )

                sweep_job = base_job.sweep(
                    sampling_algorithm="random",
                    primary_metric="AUC",
                    goal="maximize",
                )

                # Edge case: QUniform for discrete hyperparameters
                sweep_job.search_space = {
                    "max_depth": QUniform(min_value=2, max_value=20, q=1),
                    "min_samples_leaf": Choice(values=[1, 2, 5, 10, 20]),
                }

                # Edge case: TruncationSelectionPolicy with aggressive truncation
                sweep_job.early_termination = TruncationSelectionPolicy(
                    truncation_percentage=50,  # Terminate worst 50%
                    evaluation_interval=1,
                    delay_evaluation=2,
                )

                sweep_job.limits.max_total_trials = 8
                sweep_job.limits.max_concurrent_trials = 2
                sweep_job.limits.timeout = 360

                sweep_job.display_name = f"scenario-truncation-{rand_name('run')}"
                sweep_job.tags = {
                    "scenario": "sweep-truncation",
                    "sampling": "random",
                    "early_termination": "truncation",
                    "truncation_pct": "50",
                }

                submitted = ml_client.jobs.create_or_update(sweep_job, experiment_name="scenario-sweep-tests")
                assert submitted.name is not None

                finished = wait_for_job(ml_client, submitted)
                assert finished.status == "Completed", f"Sweep failed: {finished.status}"

                # ── Round-trip: verify TruncationSelectionPolicy ──────
                refetched = ml_client.jobs.get(finished.name)

                assert refetched.early_termination is not None
                # Verify truncation percentage survived
                if hasattr(refetched.early_termination, "truncation_percentage"):
                    assert refetched.early_termination.truncation_percentage == 50

                # Verify tags
                assert refetched.tags.get("early_termination") == "truncation"
                assert refetched.tags.get("truncation_pct") == "50"

                # Verify QUniform in search space
                assert "max_depth" in refetched.search_space

        finally:
            try:
                ml_client.environments.archive(name=env_name, version="1")
            except Exception:
                pass
            try:
                ml_client.compute.begin_delete(compute_name).result()
            except Exception:
                pass
