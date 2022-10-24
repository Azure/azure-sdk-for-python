from pathlib import Path

import pydash

from azure.ai.ml import Input
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict

ADLS_DATA_STORE_NAME = "workspaceblobstore"  # "searchdm_partner_c09"
ADF_NAME = "cpu-cluster"  # "adftest"
DATA_VERSION = "2"

PARAMETERS_TO_TEST = [
    # which of them are available for other components?
    (
        "tests/test_configs/internal/command-component-ls/ls_command_component.yaml",
        {},
        {
            "compute": "cpu-cluster",  # runsettings.target
            "environment": None,  # runsettings.environment
            # TODO: "resources.priority": 5,  # runsettings.priority  # JobResourceConfiguration doesn't have priority
            "limits.timeout": 300,  # runsettings.timeout_seconds
            "resources.instance_type": "1Gi",  # runsettings.resource_layout.instance_type
            "resources.instance_count": 2,  # runsettings.resource_layout.instance_count/node_count
            "resources.shm_size": "4g",  # runsettings.docker_configuration.shm_size
            "resources.docker_args": "--cpus=2 --memory=1GB",  # runsettings.docker_configuration.docker_args
            # runsettings.docker_configuration.user_docker/shared_volumes are removed
            # https://github.com/Azure/azureml_run_specification/blob/master/specs/docker_run_config.md
        },
        {
            "default_compute": "cpu-cluster",
            "default_datastore": None,
        },
    ),  # Command
    (
        "tests/test_configs/internal/distribution-component/component_spec.yaml",  # Distributed
        {
            "input_path": Input(type=AssetTypes.MLTABLE, path="mltable_imdb_reviews_train@latest"),
        },
        {
            "compute": "cpu-cluster",  # runsettings.target
            "environment": None,  # runsettings.environment
            "limits.timeout": 300,  # runsettings.timeout_seconds
            "resources.instance_type": "1Gi",  # runsettings.resource_layout.instance_type
            "resources.instance_count": 2,  # runsettings.resource_layout.instance_count/node_count
            "distribution.process_count_per_instance": 2,  # runsettings.resource_layout.process_count_per_node
            "resources.shm_size": "1Gi",  # runsettings.docker_configuration.shm_size
            "resources.docker_args": "--cpus=2 --memory=1GB",  # runsettings.docker_configuration.docker_args
        },
        {
            "default_compute": "cpu-cluster",
            "default_datastore": None,
        },
    ),
    (
        "tests/test_configs/internal/batch_inference/batch_score.yaml",  # Parallel
        {
            "model_path": Input(type=AssetTypes.MLTABLE, path="mltable_mnist_model@latest"),
            "images_to_score": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest"),
        },
        {
            "resources.instance_count": 1,  # runsettings.parallel.node_count
            "max_concurrency_per_instance": 2,  # runsettings.parallel.max_concurrency_per_instance
            "error_threshold": 5,  # runsettings.parallel.error_threshold
            "mini_batch_size": 2,  # runsettings.parallel.mini_batch_size
            "logging_level": "DEBUG",  # runsettings.parallel.logging_level
            "retry_settings.timeout": 300,  # runsettings.parallel.run_invocation_timeout
            "retry_settings.max_retries": 2,  # runsettings.parallel.run_max_try
            # runsettings.parallel.partition_keys/version are not exposed
        },
        {
            "default_compute": "cpu-cluster",
            "default_datastore": None,
        },
    ),
    (
        "tests/test_configs/internal/scope-component/component_spec.yaml",
        {
            "TextData": Input(
                type=AssetTypes.MLTABLE,
                path="mltable_Adls_Tsv@latest",
            ),
            "ExtractionClause": "column1:string, column2:int",
        },
        {
            "adla_account_name": "adla_account_name",  # runsettings.adla_account_name
            "scope_param": "-tokens 50",  # runsettings.scope.scope_param
            "custom_job_name_suffix": "component_sdk_test",  # runsettings.scope.custom_job_name_suffix
            "priority": 800,  # runsettings.scope.priority
        },
        {
            "default_compute": "cpu-cluster",
            "default_datastore": "adls_datastore",
            "force_rerun": False,
            "continue_on_step_failure": True,
            # TODO: enable after feature is available
            # "continue_on_failed_optional_input": True,
            # "timeout": 30,
            # "priority.scope": 950,
            # "on_init": "node",
            # "on_finalize": "node",
            # "identity": "",
        },
    ),  # Scope
    (
        "tests/test_configs/internal/hdi-component/component_spec.yaml",
        {
            "input_path": Input(type=AssetTypes.MLTABLE, path="mltable_imdb_reviews_train@latest"),
        },
        {
            "compute_name": "cpu-cluster",  # runsettings.hdinsight.compute_name
            "queue": "default",  # runsettings.hdinsight.queue
            "driver_memory": "1g",  # runsettings.hdinsight.driver_memory
            "driver_cores": 2,  # runsettings.hdinsight.driver_cores
            "executor_memory": "4g",  # runsettings.hdinsight.executor_memory
            "executor_cores": 3,  # runsettings.hdinsight.executor_cores
            "number_executors": 4,  # runsettings.hdinsight.number_executors
            "conf": {
                "spark.yarn.maxAppAttempts": "1",
                "spark.yarn.appMasterEnv.PYSPARK_PYTHON": "/usr/bin/anaconda/envs/py35/bin/python3",
                "spark.yarn.appMasterEnv.PYSPARK_DRIVER_PYTHON": "/usr/bin/anaconda/envs/py35/bin/python3",
            },  # runsettings.hdinsight.conf
            "hdinsight_spark_job_name": "session_name",  # runsettings.hdinsight.name
        },
        {
            "default_compute": "cpu-cluster",
            "default_datastore": None,
        },
    ),  # HDInsight
    (
        "tests/test_configs/internal/hemera-component/component.yaml",
        {},
        {},  # no specific run settings
        {
            "default_compute": "cpu-cluster",
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
    ),  # Hemera
    (
        "tests/test_configs/internal/data-transfer-component/component_spec.yaml",
        {
            "source_data": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest"),
        },
        {
            "compute": ADF_NAME,
        },
        {
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
    ),  # Data Transfer
    (
        "tests/test_configs/internal/starlite-component/component_spec.yaml",
        {
            "FileList": Input(type=AssetTypes.MLTABLE, path="mltable_starlite_sample_output@latest"),
            "FileListFileName": "\\output.tsv",
        },
        {
            "compute": ADF_NAME,
        },
        {
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
    ),  # Starlite
    (
        "tests/test_configs/internal/ae365exepool-component/component_spec.yaml",
        {
            "HeronId": "c6c849c5-4d52-412a-b4de-6cc5755bca73",
            "DataToLookAt": Input(type=AssetTypes.MLTABLE, path="mltable_reghits@latest"),
            "taskFileTimestamp": "2022.08.11.22.04.00",  # Change the value of this to your own timestamp.
        },
        {
            "compute": "cpu-cluster",  # runsettings.starlite.compute
        },  # no specific run settings
        {
            "default_compute": "cpu-cluster",
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
    ),  # Ae365exepool
    # Pipeline  we can't test this because we can't create a v1.5 pipeline component in v2, instead we test v2 pipeline
    # component containing v1.5 nodes
]

# this is to shorten the test name
TEST_CASE_NAME_ENUMERATE = list(enumerate(map(
    lambda params: Path(params[0]).name,
    PARAMETERS_TO_TEST,
)))


def set_run_settings(node, runsettings_dict):
    for dot_key, value in runsettings_dict.items():
        keys = dot_key.split(".")
        last_key = keys.pop()

        current_obj = node
        for key in keys:
            current_obj = getattr(current_obj, key)
        setattr(current_obj, last_key, value)


def assert_strong_type_intellisense_enabled(node, runsettings_dict):
    failed_attrs = []
    for dot_key, _ in runsettings_dict.items():
        keys = dot_key.split(".")
        last_key = keys.pop()

        current_obj = node
        for key in keys:
            current_obj = getattr(current_obj, key)
        if isinstance(current_obj, _AttrDict):
            if current_obj._is_arbitrary_attr(last_key):
                failed_attrs.append(dot_key)
        elif not hasattr(current_obj, last_key):
            failed_attrs.append(dot_key)

    assert not failed_attrs, f"{failed_attrs} are not pre-defined properties"


def extract_non_primitive(obj):
    if isinstance(obj, dict):
        r = {}
        for key, val in obj.items():
            val = extract_non_primitive(val)
            if val:
                r[key] = val
        return r
    elif isinstance(obj, list):
        r = []
        for val in obj:
            val = extract_non_primitive(val)
            if val:
                r.append(val)
        return r
    elif isinstance(obj, (float, int, str)):
        return None
    else:
        return obj
