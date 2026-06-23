# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic entity builders for the golden smoke suite.

Every builder MUST be fully deterministic: fixed names, no random suffixes, no timestamps. The same
inputs must produce byte-identical wire on every run and on every branch, so that any diff against a
golden is purely a serialization change, never input noise.

Field coverage is intentionally rich (inputs/outputs/distribution/identity/resources/limits/services/
queue_settings/tags/properties/environment_variables) because the migration wraps each of those nested
children, and a regression typically hides in exactly one child.
"""
from azure.ai.ml import Input, Output, MpiDistribution
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._job.finetuning import FineTuningTaskTypes
from azure.ai.ml.entities import CommandJob, Environment, JobSchedule, SparkJob
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job import AzureOpenAIFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml.entities._job.import_job import ImportJob, DatabaseImportSource
from azure.ai.ml.entities._job.job_limits import CommandJobLimits, SweepJobLimits
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.early_termination_policy import BanditPolicy
from azure.ai.ml.entities._job.sweep.search_space import Choice, Uniform
from azure.ai.ml.entities._schedule.trigger import CronTrigger
from azure.ai.ml.sweep import SweepJob


def build_command_job_full():
    """A richly-populated CommandJob exercising every migrated nested child.

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-job",
        display_name="smoke-command-job-display",
        description="smoke serialization command job",
        experiment_name="smoke-experiment",
        command="echo ${{inputs.uri}} ${{inputs.folder}} ${{inputs.data_asset}} && echo done",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        environment_variables={"ENV1": "VAL1", "ENV2": "VAL2"},
        compute="smoke-compute",
        tags={"tag1": "value1", "tag2": "value2"},
        properties={"prop1": "value1"},
        inputs={
            "uri": Input(
                type=AssetTypes.URI_FILE,
                path="azureml://datastores/workspaceblobstore/paths/python/data.csv",
            ),
            "folder": Input(
                type=AssetTypes.URI_FOLDER,
                path="azureml://datastores/workspaceblobstore/paths/python/",
                mode="ro_mount",
            ),
            "data_asset": Input(path="smoke-data:1"),
        },
        outputs={
            "model_output": Output(type=AssetTypes.URI_FOLDER),
        },
        distribution=MpiDistribution(process_count_per_instance=2),
        resources=JobResourceConfiguration(
            instance_count=2,
            instance_type="STANDARD_DS3_V2",
            locations=["westus", "eastus"],
        ),
        limits=CommandJobLimits(timeout=600),
        queue_settings=QueueSettings(job_tier="standard"),
    )


def build_sweep_job_full():
    """A SweepJob exercising search_space, objective, BanditPolicy, limits and a command trial.

    :return: A deterministic SweepJob entity.
    :rtype: ~azure.ai.ml.sweep.SweepJob
    """
    trial = CommandJob(
        command="python train.py --lr ${{search_space.learning_rate}} --bs ${{search_space.batch_size}}",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        inputs={
            "data": Input(
                type=AssetTypes.URI_FILE,
                path="azureml://datastores/workspaceblobstore/paths/python/data.csv",
            ),
        },
    )
    return SweepJob(
        name="smoke-sweep-job",
        display_name="smoke-sweep-job-display",
        description="smoke serialization sweep job",
        experiment_name="smoke-experiment",
        compute="smoke-compute",
        tags={"tag1": "value1"},
        properties={"prop1": "value1"},
        sampling_algorithm="random",
        search_space={
            "learning_rate": Uniform(min_value=0.001, max_value=0.1),
            "batch_size": Choice(values=[16, 32, 64]),
        },
        objective=Objective(goal="maximize", primary_metric="accuracy"),
        early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.1, delay_evaluation=5),
        limits=SweepJobLimits(
            max_total_trials=10,
            max_concurrent_trials=2,
            timeout=3600,
            trial_timeout=600,
        ),
        queue_settings=QueueSettings(job_tier="standard"),
        trial=trial,
    )


# Registry of (golden_name -> builder) for the smoke suite, grouped by entity area.
COMMAND_JOB_BUILDERS = {
    "command_job_full": build_command_job_full,
}

SWEEP_JOB_BUILDERS = {
    "sweep_job_full": build_sweep_job_full,
}


def build_spark_job_full():
    """A SparkJob exercising entry, conf, inputs/outputs and a resource configuration.

    :return: A deterministic SparkJob entity.
    :rtype: ~azure.ai.ml.entities.SparkJob
    """
    return SparkJob(
        name="smoke-spark-job",
        display_name="smoke-spark-job-display",
        description="smoke serialization spark job",
        experiment_name="smoke-experiment",
        code="./src",
        entry={"file": "main.py"},
        driver_cores=1,
        driver_memory="2g",
        executor_cores=2,
        executor_memory="2g",
        executor_instances=2,
        inputs={
            "data": Input(
                type=AssetTypes.URI_FILE,
                path="azureml://datastores/workspaceblobstore/paths/python/data.csv",
                mode="direct",
            ),
        },
        outputs={
            "output": Output(type=AssetTypes.URI_FOLDER, mode="direct"),
        },
        args="--input ${{inputs.data}} --output ${{outputs.output}}",
        tags={"tag1": "value1"},
        resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.4.0"),
    )


SPARK_JOB_BUILDERS = {
    "spark_job_full": build_spark_job_full,
}


def build_import_job_full():
    """An ImportJob exercising a database source and an output.

    :return: A deterministic ImportJob entity.
    :rtype: ~azure.ai.ml.entities._job.import_job.ImportJob
    """
    return ImportJob(
        name="smoke-import-job",
        display_name="smoke-import-job-display",
        description="smoke serialization import job",
        experiment_name="smoke-experiment",
        compute="smoke-compute",
        source=DatabaseImportSource(
            type="azuresqldb",
            connection="azureml:my_username_password",
            query="SELECT * FROM my_table",
        ),
        output=Output(
            type=AssetTypes.MLTABLE,
            path="azureml://datastores/workspaceblobstore/paths/imported/",
        ),
    )


IMPORT_JOB_BUILDERS = {
    "import_job_full": build_import_job_full,
}


def build_schedule_full():
    """A JobSchedule wrapping a command job with a CronTrigger.

    This is the inverse-tree case: a msrest schedule envelope embeds the job definition. On a
    migration branch the embedded job is an arm-hybrid child, so this guards the schedule embed-site.

    :return: A deterministic JobSchedule entity.
    :rtype: ~azure.ai.ml.entities.JobSchedule
    """
    job = CommandJob(
        command="echo scheduled",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
    )
    return JobSchedule(
        name="smoke-schedule",
        display_name="smoke-schedule-display",
        description="smoke serialization schedule",
        tags={"tag1": "value1"},
        properties={"prop1": "value1"},
        trigger=CronTrigger(
            expression="15 10 * * 1",
            start_time="2026-01-01T00:00:00",
            end_time="2026-12-31T00:00:00",
            time_zone="UTC",
        ),
        create_job=job,
    )


SCHEDULE_BUILDERS = {
    "schedule_full": build_schedule_full,
}


def build_custom_finetuning_full():
    """A CustomModelFineTuningJob exercising training/validation data, model, outputs and queue settings.

    NOTE: this entity is KNOWN to have a pre-existing serialize break (custom finetuning outputs/
    queue_settings) that is present identically on main and on the migration branch. The test using
    this builder is marked ``xfail`` and will auto-pass (xpass) once the break is fixed.

    :return: A deterministic CustomModelFineTuningJob entity.
    :rtype: ~azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job.CustomModelFineTuningJob
    """
    return CustomModelFineTuningJob(
        name="smoke-custom-finetuning",
        display_name="smoke-custom-finetuning-display",
        experiment_name="smoke-experiment",
        task=FineTuningTaskTypes.TEXT_COMPLETION,
        training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.csv"),
        validation_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/test.csv"),
        model=Input(
            type=AssetTypes.MLFLOW_MODEL,
            path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9",
        ),
        hyperparameters={"learning_rate": "0.001"},
        tags={"tag1": "value1"},
        properties={"prop1": "value1"},
        outputs={"registered_model": Output(type="mlflow_model", name="smoke-finetune-registered")},
        queue_settings=QueueSettings(job_tier="standard"),
    )


FINETUNING_BUILDERS = {
    "custom_finetuning_full": build_custom_finetuning_full,
}


def build_aoai_finetuning_full():
    """An AzureOpenAIFineTuningJob exercising training/validation data, model, outputs and hyperparameters.

    The Azure OpenAI path keeps its own (v2024-01-01-preview) msrest envelope, so this case guards that
    its nested inputs/outputs stay msrest and serialize as a consistent tree.

    :return: A deterministic AzureOpenAIFineTuningJob entity.
    :rtype: ~azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job.AzureOpenAIFineTuningJob
    """
    return AzureOpenAIFineTuningJob(
        name="smoke-aoai-finetuning",
        display_name="smoke-aoai-finetuning-display",
        experiment_name="smoke-experiment",
        task=FineTuningTaskTypes.TEXT_COMPLETION,
        training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.jsonl"),
        validation_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/validation.jsonl"),
        model=Input(
            type=AssetTypes.CUSTOM_MODEL,
            path="azureml://registries/azure-openai/models/gpt-4/versions/1",
        ),
        hyperparameters=AzureOpenAIHyperparameters(n_epochs=2, batch_size=4, learning_rate_multiplier=0.5),
        tags={"tag1": "value1"},
        properties={"prop1": "value1"},
        outputs={"registered_model": Output(type="mlflow_model", name="smoke-aoai-registered")},
    )


AOAI_FINETUNING_BUILDERS = {
    "aoai_finetuning_full": build_aoai_finetuning_full,
}
