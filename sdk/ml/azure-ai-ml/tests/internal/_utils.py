# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from pathlib import Path

import pytest

from azure.ai.ml import Input
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict

ADLS_DATA_STORE_NAME = "workspaceblobstore"  # "searchdm_partner_c09"
ADF_NAME = "cpu-cluster"  # "adftest"
DATA_VERSION = "2"

PARAMETERS_TO_TEST = [
    # which of them are available for other components?
    pytest.param(
        "tests/test_configs/internal/command-component/command-linux/one-line-tsv/component.yaml",
        {
            "content": "1\t2\t3\n4\t5\t6\n7\t8\t9",
        },
        {
            "compute": "cpu-cluster",  # runsettings.target
            "environment_variables": {"verbose": "DEBUG"},  # runsettings.environment_variables
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
        id="CommandComponent",
    ),
    pytest.param(
        "tests/test_configs/internal/distribution-component/component_spec.yaml",
        {
            "input_path": Input(type=AssetTypes.MLTABLE, path="mltable_imdb_reviews_train@latest"),
        },
        {
            "compute": "cpu-cluster",  # runsettings.target
            "environment": None,  # runsettings.environment
            "environment_variables": {"verbose": "DEBUG"},  # runsettings.environment_variables
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
        id="DistributedComponent",
    ),
    pytest.param(
        "tests/test_configs/internal/batch_inference/batch_score.yaml",
        {
            "model_path": Input(type=AssetTypes.MLTABLE, path="mltable_mnist_model@latest"),
            "images_to_score": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest"),
        },
        {
            "resources.instance_count": 1,  # runsettings.parallel.node_count
            "max_concurrency_per_instance": 2,  # runsettings.parallel.process_count_per_node
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
        id="ParallelComponent",
    ),
    pytest.param(
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
            "auto_token": 150,  # runsettings.scope.auto_token
            "tokens": 2,  # runsettings.scope.token
            "vcp": 0.2,  # runsettings.scope.vcp
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
        id="ScopeComponent",
    ),
    pytest.param(
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
        id="HDInsightComponent",
    ),
    pytest.param(
        "tests/test_configs/internal/hemera-component/component.yaml",
        {},
        {},  # no specific run settings
        {
            "default_compute": "cpu-cluster",
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
        id="HemeraComponent",
    ),
    pytest.param(
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
        id="DataTransferComponent",
    ),  # Data Transfer
    pytest.param(
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
        id="StarliteComponent",
    ),
    pytest.param(
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
        id="Ae365exepoolComponent",
    ),
    pytest.param(
        "tests/test_configs/internal/spark-component/spec.yaml",
        {
            "file_input1": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest", mode="direct"),
            "file_input2": Input(type=AssetTypes.MLTABLE, path="mltable_mnist@latest", mode="direct"),
        },
        {
            "driver_cores": 1,
            "driver_memory": "1g",
            "executor_cores": 1,
            "executor_memory": "1g",
            "executor_instances": 1,
            "compute": "cpu-cluster",
        },  # no specific run settings
        {
            "default_compute": "cpu-cluster",
            "default_datastore": ADLS_DATA_STORE_NAME,
        },
        id="SparkComponent",
    ),
    # Pipeline  we can't test this because we can't create a v1.5 pipeline component in v2, instead we test v2 pipeline
    # component containing v1.5 nodes
]


def get_expected_runsettings_items(runsettings_dict, client=None):
    expected_values = copy.deepcopy(runsettings_dict)
    dot_key_map = {"compute": "computeId"}

    for dot_key in dot_key_map:
        if dot_key in expected_values:
            expected_values[dot_key_map[dot_key]] = expected_values.pop(dot_key)

    conf = {}
    conf_key_map = {
        "driver_memory": "spark.driver.memory",
        "driver_cores": "spark.driver.cores",
        "executor_memory": "spark.executor.memory",
        "executor_cores": "spark.executor.cores",
        "executor_instances": "spark.executor.instances",
    }
    # hack: spark component settings will be set to conf
    if all(key in expected_values for key in conf_key_map):
        for dot_key in conf_key_map:
            conf[conf_key_map[dot_key]] = expected_values.pop(dot_key)
        expected_values["conf"] = conf

    for dot_key in expected_values:
        # hack: mini_batch_size will be transformed into str
        if dot_key == "mini_batch_size":
            expected_values[dot_key] = str(expected_values[dot_key])
        # hack: timeout will be transformed into str
        if dot_key == "limits.timeout":
            expected_values[dot_key] = "PT5M"
        # hack: compute_name for hdinsight will be transformed into arm str
        if dot_key == "compute_name" and client is not None:
            expected_values[dot_key] = (
                f"/subscriptions/{client.subscription_id}/"
                f"resourceGroups/{client.resource_group_name}/"
                f"providers/Microsoft.MachineLearningServices/"
                f"workspaces/{client.workspace_name}/"
                f"computes/{expected_values[dot_key]}"
            )
    return expected_values.items()


ANONYMOUS_COMPONENT_TEST_PARAMS = [
    (
        "simple-command/powershell_copy.yaml",
        # Please DO NOT change the expected snapshot id unless you are sure you have changed the component spec
        "75c43313-4777-b2e9-fe3a-3b98cabfaa77",
    ),
    (
        "additional-includes/component_spec.yaml",
        # Please DO NOT change the expected snapshot id unless you are sure you have changed the component spec
        "1dc8271a-9184-df03-c9a5-afac8dcdcf26",
    ),
    # TODO(2076035): skip tests related to zip additional includes for now
    # (
    #     "additional-includes-in-zip/component_spec.yaml",
    #     # Please DO NOT change the expected snapshot id unless you are sure you have changed the component spec
    #     "24f26249-94c3-19c5-effe-030a60205d88"
    # ),
]


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
            if current_obj._is_arbitrary_attr(last_key):  # pylint: disable=protected-access
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
    if isinstance(obj, list):
        r = []
        for val in obj:
            val = extract_non_primitive(val)
            if val:
                r.append(val)
        return r
    if isinstance(obj, (float, int, str)):
        return None
    return obj
