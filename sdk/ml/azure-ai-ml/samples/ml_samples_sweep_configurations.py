# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_sweep_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure hyperparameter sweep jobs.
USAGE:
    python ml_samples_sweep_configurations.py

"""

import os


class SweepConfigurationOptions(object):
    def ml_sweep_config(self):
        from azure.identity import DefaultAzureCredential

        from azure.ai.ml import MLClient

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")

        cpu_cluster = ml_client.compute.get("cpu-cluster")

        from azure.ai.ml.entities import Environment

        job_env = Environment(
            name="my-env",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        )
        job_env = ml_client.environments.create_or_update(job_env)

        # [START configure_sweep_job_choice_loguniform]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        from azure.ai.ml.sweep import Choice, LogUniform

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        job_for_sweep = job(
            kernel=LogUniform(min_value=-6, max_value=-1),
            penalty=Choice([0.9, 0.18, 0.36, 0.72]),
        )

        # [END configure_sweep_job_choice_loguniform]

        # [START configure_sweep_job_uniform]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        from azure.ai.ml.sweep import Uniform

        job_for_sweep = job(
            kernel=Uniform(min_value=0.0005, max_value=0.005),
            penalty=Uniform(min_value=0.9, max_value=0.99),
        )
        # [END configure_sweep_job_uniform]

        # [START configure_sweep_job_bandit_policy]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        from azure.ai.ml.sweep import Uniform

        job_for_sweep = job(
            kernel=Uniform(min_value=0.0005, max_value=0.005),
            penalty=Uniform(min_value=0.9, max_value=0.99),
        )

        from azure.ai.ml.sweep import BanditPolicy

        sweep_job = job_for_sweep.sweep(
            sampling_algorithm="random",
            primary_metric="best_val_acc",
            goal="Maximize",
            max_total_trials=8,
            max_concurrent_trials=4,
            early_termination_policy=BanditPolicy(slack_factor=0.15, evaluation_interval=1, delay_evaluation=10),
        )
        # [END configure_sweep_job_bandit_policy]

        # [START configure_sweep_job_median_stopping_policy]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        from azure.ai.ml.sweep import MedianStoppingPolicy, Uniform

        job_for_sweep = job(
            kernel=Uniform(min_value=0.0005, max_value=0.005),
            penalty=Uniform(min_value=0.9, max_value=0.99),
        )

        sweep_job = job_for_sweep.sweep(
            sampling_algorithm="random",
            primary_metric="best_val_acc",
            goal="Maximize",
            max_total_trials=8,
            max_concurrent_trials=4,
            early_termination_policy=MedianStoppingPolicy(delay_evaluation=5, evaluation_interval=2),
        )
        # [END configure_sweep_job_median_stopping_policy]

        # [START configure_sweep_job_bayesian_sampling_algorithm]
        from azure.ai.ml.entities import CommandJob
        from azure.ai.ml.sweep import BayesianSamplingAlgorithm, Objective, SweepJob, SweepJobLimits

        command_job = CommandJob(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        sweep = SweepJob(
            sampling_algorithm=BayesianSamplingAlgorithm(),
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"file": "top_level.csv", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
            objective=Objective(goal="maximize", primary_metric="accuracy"),
        )
        # [END configure_sweep_job_bayesian_sampling_algorithm]

        # [START configure_sweep_job_grid_sampling_algorithm]
        from azure.ai.ml.entities import CommandJob
        from azure.ai.ml.sweep import GridSamplingAlgorithm, SweepJob, SweepJobLimits

        command_job = CommandJob(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        sweep = SweepJob(
            sampling_algorithm=GridSamplingAlgorithm(),
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"file": "top_level.csv", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
        )
        # [END configure_sweep_job_grid_sampling_algorithm]

        # [START configure_sweep_job_random_sampling_algorithm]
        from azure.ai.ml.entities import CommandJob
        from azure.ai.ml.sweep import RandomSamplingAlgorithm, SweepJob, SweepJobLimits

        command_job = CommandJob(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        sweep = SweepJob(
            sampling_algorithm=RandomSamplingAlgorithm(seed=999, rule="sobol", logbase="e"),
            trial=command_job,
            search_space={"ss": Choice(type="choice", values=[{"space1": True}, {"space2": True}])},
            inputs={"input1": {"file": "top_level.csv", "mode": "ro_mount"}},
            compute="top_level",
            limits=SweepJobLimits(trial_timeout=600),
        )
        # [END configure_sweep_job_random_sampling_algorithm]

        # [START configure_sweep_job_truncation_selection_policy]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        from azure.ai.ml.sweep import QUniform, TruncationSelectionPolicy, Uniform

        job_for_sweep = job(
            kernel=Uniform(min_value=0.0005, max_value=0.005),
            penalty=QUniform(min_value=0.05, max_value=0.75, q=1),
        )

        sweep_job = job_for_sweep.sweep(
            sampling_algorithm="random",
            primary_metric="best_val_acc",
            goal="Maximize",
            max_total_trials=8,
            max_concurrent_trials=4,
            early_termination_policy=TruncationSelectionPolicy(delay_evaluation=5, evaluation_interval=2),
        )
        # [END configure_sweep_job_truncation_selection_policy]

        # [START configure_sweep_job_randint_normal]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        from azure.ai.ml.sweep import Normal, Randint

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        job_for_sweep = job(
            penalty=Randint(upper=5),
            kernel=Normal(mu=2.0, sigma=1.0),
        )

        # [END configure_sweep_job_randint_normal]

        # [START configure_sweep_job_lognormal_qlognormal]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        from azure.ai.ml.sweep import LogNormal, QLogNormal

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        job_for_sweep = job(
            kernel=LogNormal(mu=0.0, sigma=1.0),
            penalty=QLogNormal(mu=5.0, sigma=2.0),
        )

        # [END configure_sweep_job_lognormal_qlognormal]

        # [START configure_sweep_job_qloguniform_qnormal]
        from azure.ai.ml import command

        job = command(
            inputs=dict(kernel="linear", penalty=1.0),
            compute=cpu_cluster,
            environment=f"{job_env.name}:{job_env.version}",
            code="./scripts",
            command="python scripts/train.py --kernel $kernel --penalty $penalty",
            experiment_name="sklearn-iris-flowers",
        )

        from azure.ai.ml.sweep import QLogUniform, QNormal

        # we can reuse an existing Command Job as a function that we can apply inputs to for the sweep configurations
        job_for_sweep = job(
            penalty=QNormal(mu=2.0, sigma=1.0, q=1),
            kernel=QLogUniform(min_value=1.0, max_value=5.0),
        )

        # [END configure_sweep_job_qloguniform_qnormal]


if __name__ == "__main__":
    sample = SweepConfigurationOptions()
    sample.ml_sweep_config()
