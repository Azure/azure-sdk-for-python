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
from azure.ai.ml import Input, Output, MpiDistribution, PyTorchDistribution, TensorFlowDistribution
from azure.ai.ml import command
from datetime import datetime
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._job.finetuning import FineTuningTaskTypes
from azure.ai.ml.entities import (
    AmlTokenConfiguration,
    CommandJob,
    JobSchedule,
    ManagedIdentityConfiguration,
    PipelineJob,
    PipelineJobSettings,
    SparkJob,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job import AzureOpenAIFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml.entities._job.import_job import ImportJob, DatabaseImportSource, FileImportSource
from azure.ai.ml.entities._job.job_limits import CommandJobLimits, SweepJobLimits
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.early_termination_policy import (
    BanditPolicy,
    MedianStoppingPolicy,
    TruncationSelectionPolicy,
)
from azure.ai.ml.entities._job.sweep.search_space import Choice, LogUniform, QUniform, Randint, Uniform
from azure.ai.ml.entities._schedule.trigger import CronTrigger, RecurrencePattern, RecurrenceTrigger
from azure.ai.ml.entities._data_import.data_import import DataImport
from azure.ai.ml.entities._data_import.schedule import ImportDataSchedule
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
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


def build_command_job_minimal():
    """A CommandJob with only the required fields (guards optional-omission defaults).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-minimal",
        command="echo hello",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
    )


def build_command_job_serverless():
    """A CommandJob with no named compute (serverless path omits computeId).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-serverless",
        command="echo serverless",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        resources=JobResourceConfiguration(instance_type="STANDARD_DS3_V2", instance_count=1),
    )


def build_command_job_aml_token():
    """A CommandJob whose identity is an AmlToken (guards the identity child wrap).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-aml-token",
        command="echo token",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        identity=AmlTokenConfiguration(),
    )


def build_command_job_user_identity():
    """A CommandJob whose identity is a UserIdentity (guards the token-header isinstance gate).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-user-identity",
        command="echo user",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        identity=UserIdentityConfiguration(),
    )


def build_command_job_managed_identity():
    """A CommandJob whose identity is a ManagedIdentity (guards the identity child wrap).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-managed-identity",
        command="echo managed",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        identity=ManagedIdentityConfiguration(),
    )


def build_command_job_local_compute():
    """A CommandJob on local compute (guards the LOCAL_COMPUTE_PROPERTY resources injection).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-local",
        command="echo local",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="local",
    )


def build_command_job_docker_args_list():
    """A CommandJob with list-form docker_args (routes to the 2025-01 resources model).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-docker-args",
        command="echo docker",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        resources=JobResourceConfiguration(
            instance_count=1,
            docker_args=["--shm-size=1g", "--ipc=host"],
        ),
    )


def build_command_job_pytorch():
    """A CommandJob with a PyTorch distribution (guards the distribution child wrap, non-Mpi).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-pytorch",
        command="python train.py",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        distribution=PyTorchDistribution(process_count_per_instance=4),
        resources=JobResourceConfiguration(instance_count=2),
    )


def build_command_job_tensorflow():
    """A CommandJob with a TensorFlow distribution (guards the distribution child wrap, non-Mpi).

    :return: A deterministic CommandJob entity.
    :rtype: ~azure.ai.ml.entities.CommandJob
    """
    return CommandJob(
        name="smoke-command-tensorflow",
        command="python train.py",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        distribution=TensorFlowDistribution(worker_count=2, parameter_server_count=1),
        resources=JobResourceConfiguration(instance_count=2),
    )


COMMAND_JOB_BUILDERS.update(
    {
        "command_job_minimal": build_command_job_minimal,
        "command_job_serverless": build_command_job_serverless,
        "command_job_aml_token": build_command_job_aml_token,
        "command_job_user_identity": build_command_job_user_identity,
        "command_job_managed_identity": build_command_job_managed_identity,
        "command_job_local_compute": build_command_job_local_compute,
        "command_job_docker_args_list": build_command_job_docker_args_list,
        "command_job_pytorch": build_command_job_pytorch,
        "command_job_tensorflow": build_command_job_tensorflow,
    }
)

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


def build_sweep_job_median_policy():
    """A SweepJob with a MedianStoppingPolicy and grid sampling (variation of termination + sampling).

    :return: A deterministic SweepJob entity.
    :rtype: ~azure.ai.ml.sweep.SweepJob
    """
    trial = CommandJob(
        command="python train.py --lr ${{search_space.learning_rate}}",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
    )
    return SweepJob(
        name="smoke-sweep-median",
        experiment_name="smoke-experiment",
        compute="smoke-compute",
        sampling_algorithm="grid",
        search_space={"learning_rate": Choice(values=[0.01, 0.1])},
        objective=Objective(goal="minimize", primary_metric="loss"),
        early_termination=MedianStoppingPolicy(evaluation_interval=1, delay_evaluation=5),
        limits=SweepJobLimits(max_total_trials=4, max_concurrent_trials=2),
        trial=trial,
    )


def build_sweep_job_truncation_policy():
    """A SweepJob with a TruncationSelectionPolicy and Bayesian sampling + varied search-space types.

    :return: A deterministic SweepJob entity.
    :rtype: ~azure.ai.ml.sweep.SweepJob
    """
    trial = CommandJob(
        command="python train.py --lr ${{search_space.lr}} --units ${{search_space.units}}",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
    )
    return SweepJob(
        name="smoke-sweep-truncation",
        experiment_name="smoke-experiment",
        compute="smoke-compute",
        sampling_algorithm="bayesian",
        search_space={
            "lr": LogUniform(min_value=-6, max_value=-1),
            "units": Randint(upper=128),
            "dropout": QUniform(min_value=0.0, max_value=0.5, q=1),
        },
        objective=Objective(goal="maximize", primary_metric="accuracy"),
        early_termination=TruncationSelectionPolicy(
            truncation_percentage=20, evaluation_interval=2, delay_evaluation=5
        ),
        limits=SweepJobLimits(max_total_trials=8, max_concurrent_trials=4),
        trial=trial,
    )


SWEEP_JOB_BUILDERS.update(
    {
        "sweep_job_median_policy": build_sweep_job_median_policy,
        "sweep_job_truncation_policy": build_sweep_job_truncation_policy,
    }
)


def build_spark_job_dynamic_allocation():
    """A SparkJob with dynamic allocation enabled and an AmlToken identity (variation of resources).

    :return: A deterministic SparkJob entity.
    :rtype: ~azure.ai.ml.entities.SparkJob
    """
    return SparkJob(
        name="smoke-spark-dynamic",
        experiment_name="smoke-experiment",
        code="./src",
        entry={"file": "main.py"},
        driver_cores=2,
        driver_memory="4g",
        executor_cores=2,
        executor_memory="4g",
        dynamic_allocation_enabled=True,
        dynamic_allocation_min_executors=1,
        dynamic_allocation_max_executors=4,
        identity=AmlTokenConfiguration(),
        resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.4.0"),
    )


SPARK_JOB_BUILDERS.update(
    {
        "spark_job_dynamic_allocation": build_spark_job_dynamic_allocation,
    }
)


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


def build_import_job_file_source():
    """An ImportJob with a FileImportSource (variation of the import source type).

    :return: A deterministic ImportJob entity.
    :rtype: ~azure.ai.ml.entities._job.import_job.ImportJob
    """
    return ImportJob(
        name="smoke-import-file",
        display_name="smoke-import-file-display",
        experiment_name="smoke-experiment",
        compute="smoke-compute",
        source=FileImportSource(
            type="s3",
            path="s3://my-bucket/my-folder/",
        ),
        output=Output(
            type=AssetTypes.URI_FOLDER,
            path="azureml://datastores/workspaceblobstore/paths/imported-files/",
        ),
    )


IMPORT_JOB_BUILDERS.update(
    {
        "import_job_file_source": build_import_job_file_source,
    }
)


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


def build_schedule_recurrence_spark():
    """A JobSchedule wrapping a spark job with a RecurrenceTrigger (variation of trigger + embedded job).

    :return: A deterministic JobSchedule entity.
    :rtype: ~azure.ai.ml.entities.JobSchedule
    """
    job = SparkJob(
        entry={"file": "main.py"},
        code="./src",
        driver_cores=1,
        driver_memory="2g",
        executor_cores=2,
        executor_memory="2g",
        executor_instances=2,
        compute="smoke-spark-compute",
    )
    return JobSchedule(
        name="smoke-schedule-recurrence",
        display_name="smoke-schedule-recurrence-display",
        trigger=RecurrenceTrigger(
            frequency="week",
            interval=1,
            schedule=RecurrencePattern(hours=[10], minutes=[15], week_days=["monday", "wednesday"]),
            start_time="2026-01-01T00:00:00",
            time_zone="UTC",
        ),
        create_job=job,
    )


SCHEDULE_BUILDERS.update(
    {
        "schedule_recurrence_spark": build_schedule_recurrence_spark,
    }
)


def build_schedule_cron_datetime():
    """A JobSchedule whose CronTrigger uses ``datetime`` start/end times (not strings).

    The YAML/schema layer parses trigger times into ``datetime`` objects; arm and msrest format those
    differently on the wire (ISO ``...T...Z`` vs ``%Y-%m-%d %H:%M:%S``). String-only builders miss this,
    so this case exercises the datetime path explicitly.

    :return: A deterministic JobSchedule entity.
    :rtype: ~azure.ai.ml.entities.JobSchedule
    """
    job = CommandJob(
        command="echo scheduled",
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
    )
    return JobSchedule(
        name="smoke-schedule-cron-datetime",
        display_name="smoke-schedule-cron-datetime-display",
        trigger=CronTrigger(
            expression="15 10 * * 1",
            start_time=datetime(2026, 1, 1, 0, 0, 0),
            end_time=datetime(2026, 12, 31, 0, 0, 0),
            time_zone="UTC",
        ),
        create_job=job,
    )


SCHEDULE_BUILDERS.update(
    {
        "schedule_cron_datetime": build_schedule_cron_datetime,
    }
)


def build_schedule_pipeline():
    """A JobSchedule wrapping a PipelineJob with a CronTrigger.

    PipelineJob routes to the v2024_01 msrest client, so its job_definition is a msrest model that must
    be converted to a wire dict before embedding in the arm schedule envelope; this guards that branch
    (which is distinct from the Command (arm) and Spark (v2023_04 msrest) branches).

    :return: A deterministic JobSchedule entity.
    :rtype: ~azure.ai.ml.entities.JobSchedule
    """
    node = command(
        name="node1",
        command="echo ${{inputs.x}}",
        environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        compute="smoke-compute",
        inputs={"x": 1},
    )
    pipeline_job = PipelineJob(
        jobs={"node1": node},
        settings=PipelineJobSettings(default_compute="smoke-compute"),
    )
    return JobSchedule(
        name="smoke-schedule-pipeline",
        display_name="smoke-schedule-pipeline-display",
        trigger=CronTrigger(
            expression="15 10 * * 1",
            start_time="2026-01-01T00:00:00",
            time_zone="UTC",
        ),
        create_job=pipeline_job,
    )


SCHEDULE_BUILDERS.update(
    {
        "schedule_pipeline": build_schedule_pipeline,
    }
)


def build_import_data_schedule_database():
    """An ImportDataSchedule wrapping a database DataImport with a CronTrigger.

    ImportDataAction/DataImport are absent from arm_ml_service, so the schedule envelope is arm but the
    action is emitted as a JSON-direct wire dict. This case guards that mixed envelope (arm Schedule +
    plain-dict action + arm trigger) which a wire-broken migration crashes on at serialize time.

    :return: A deterministic ImportDataSchedule entity.
    :rtype: ~azure.ai.ml.entities._data_import.schedule.ImportDataSchedule
    """
    import_data = DataImport(
        name="smoke-azuresqldb-asset",
        path="azureml://datastores/workspaceblobstore/paths/{name}",
        source=Database(connection="azureml:smoke_connection", query="select * from region"),
    )
    return ImportDataSchedule(
        name="smoke-import-schedule-db",
        display_name="smoke-import-schedule-db-display",
        import_data=import_data,
        trigger=CronTrigger(
            expression="15 10 * * 1",
            start_time="2026-01-01T00:00:00",
            end_time="2026-12-31T00:00:00",
            time_zone="UTC",
        ),
    )


def build_import_data_schedule_file_system():
    """An ImportDataSchedule wrapping a file-system DataImport with a RecurrenceTrigger.

    :return: A deterministic ImportDataSchedule entity.
    :rtype: ~azure.ai.ml.entities._data_import.schedule.ImportDataSchedule
    """
    import_data = DataImport(
        name="smoke-s3-asset",
        path="azureml://datastores/workspaceblobstore/paths/{name}",
        source=FileSystem(connection="azureml:smoke_s3_connection", path="test1/*"),
    )
    return ImportDataSchedule(
        name="smoke-import-schedule-fs",
        display_name="smoke-import-schedule-fs-display",
        import_data=import_data,
        trigger=RecurrenceTrigger(
            frequency="week",
            interval=1,
            schedule=RecurrencePattern(hours=[10], minutes=[15], week_days=["monday", "wednesday"]),
            start_time="2026-01-01T00:00:00",
            time_zone="UTC",
        ),
    )


SCHEDULE_BUILDERS.update(
    {
        "import_data_schedule_database": build_import_data_schedule_database,
        "import_data_schedule_file_system": build_import_data_schedule_file_system,
    }
)


def build_custom_finetuning_full():
    """A CustomModelFineTuningJob exercising training/validation data, model, outputs and queue settings.

    The custom-model path builds an arm_ml_service hybrid envelope, so its outputs/resources/
    queue_settings children are wrapped to hybrid; this case guards that whole tree.

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


def build_custom_finetuning_minimal():
    """A CustomModelFineTuningJob with only required fields (no outputs/queue_settings/resources).

    Guards the arm-hybrid envelope when the optional children are absent (None-omission defaults).

    :return: A deterministic CustomModelFineTuningJob entity.
    :rtype: ~azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job.CustomModelFineTuningJob
    """
    return CustomModelFineTuningJob(
        name="smoke-custom-finetuning-minimal",
        experiment_name="smoke-experiment",
        task=FineTuningTaskTypes.TEXT_COMPLETION,
        training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.csv"),
        model=Input(
            type=AssetTypes.MLFLOW_MODEL,
            path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9",
        ),
    )


FINETUNING_BUILDERS = {
    "custom_finetuning_full": build_custom_finetuning_full,
    "custom_finetuning_minimal": build_custom_finetuning_minimal,
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


def build_aoai_finetuning_minimal():
    """An AzureOpenAIFineTuningJob with only required fields (no hyperparameters/outputs).

    Guards the v2024_01 msrest tree when optional children are absent.

    :return: A deterministic AzureOpenAIFineTuningJob entity.
    :rtype: ~azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job.AzureOpenAIFineTuningJob
    """
    return AzureOpenAIFineTuningJob(
        name="smoke-aoai-finetuning-minimal",
        experiment_name="smoke-experiment",
        task=FineTuningTaskTypes.TEXT_COMPLETION,
        training_data=Input(type=AssetTypes.URI_FILE, path="https://foo/bar/train.jsonl"),
        model=Input(
            type=AssetTypes.CUSTOM_MODEL,
            path="azureml://registries/azure-openai/models/gpt-4/versions/1",
        ),
    )


AOAI_FINETUNING_BUILDERS.update(
    {
        "aoai_finetuning_minimal": build_aoai_finetuning_minimal,
    }
)
