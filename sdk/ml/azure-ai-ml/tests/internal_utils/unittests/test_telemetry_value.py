# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from unittest.mock import patch

import pytest

from azure.ai.ml import Input, Output, command, dsl, load_component, load_job
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR
from azure.ai.ml.entities import CommandComponent, CommandJob, CommandJobLimits, JobResourceConfiguration

from .._util import _UTILS_TIMEOUT_SECOND


@pytest.mark.timeout(_UTILS_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestTelemetryValue:
    def test_component_node_telemetry_value(self):
        # From yaml
        component_func = load_component("./tests/test_configs/components/helloworld_component.yml")
        v = component_func._get_telemetry_values()
        assert v["type"] == "command"
        assert v["source"] == "YAML.COMPONENT"
        assert v["is_anonymous"] is False
        component = component_func()
        v = component._get_telemetry_values()
        assert v["type"] == "command"
        assert v["source"] == "YAML.COMPONENT"

        # From class
        code = (
            "/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/"
            "test-rg-centraluseuap-v2-2021W10/providers/Microsoft.MachineLearningServices/"
            "workspaces/sdk_vnext_cli/codes/e736692c-8542-11eb-b746-6c2b59f8af4d/versions/1"
        )
        component = CommandComponent(
            name="sample_command_component_basic",
            display_name="CommandComponentBasic",
            description="This is the basic command component",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            version="1",
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World",
            code=code,
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        v = component._get_telemetry_values()
        assert v["type"] == "command"
        assert v["source"] == "CLASS"
        assert v["is_anonymous"] is False

        # From builder
        test_command = command(
            name="my-job",
            display_name="my-fancy-job",
            description="This is a fancy job",
            tags=dict(),
            command="python train.py --input-data ${{inputs.input_data}} --lr ${{inputs.learning_rate}}",
            code="./src",
            compute="cpu-cluster",
            environment="my-env:1",
            environment_variables=dict(foo="bar"),
            # Customers can still do this:
            resources=JobResourceConfiguration(instance_count=2, instance_type="STANDARD_D2"),
            limits=CommandJobLimits(timeout=300),
            inputs={
                "float": 0.01,
                "integer": 1,
                "string": "str",
                "boolean": False,
                "uri_folder": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
                "uri_file": dict(type="uri_file", path="https://my-blob/path/to/data", mode="download"),
            },
            outputs={"my_model": Output(type="mlflow_model", mode="rw_mount")},
        )
        v = test_command._get_telemetry_values()
        assert v["type"] == "command"
        assert v["source"] == "BUILDER"

    def test_pipeline_telemetry_value(self):
        # standalone command job
        basic_job = CommandJob(
            display_name="hello-world-job",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
        )
        v = basic_job._get_telemetry_values()
        assert v["type"] == "command"

        # pipeline job
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_classification.yml"
        job = load_job(test_path)
        v = job._get_telemetry_values()
        assert v["type"] == "pipeline"
        assert v["source"] == "YAML.JOB"
        assert v["node_count"] == 1
        assert v["node_type"] == '{"automl": 1}'
        assert v["node_source"] == '{"BUILDER": 1}'

    def test_dsl_pipeline_telemetry_value(self):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(path)
            component_func(component_in_path=Input(path="/a/path/on/ds"), component_in_number=1)

        pipeline1 = pipeline_no_arg()
        v = pipeline1._get_telemetry_values()
        assert v["type"] == "pipeline"
        assert v["source"] == "DSL"
        assert v["node_count"] == 1
        assert v["node_type"] == '{"command": 1}'
        assert v["node_source"] == '{"YAML.COMPONENT": 1}'

    @patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"})
    def test_dsl_subpipeline_telemetry_value(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline(name="sub_pipeline")
        def sub_pipeline(component_in_number: int, component_in_path: str):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(
                component_in_number=component_in_number, component_in_path=node1.outputs.component_out_path
            )
            return {"sub_pipeline_out": node2.outputs.component_out_path}

        @dsl.pipeline(name="root_pipeline")
        def root_pipeline(component_in_number: int, component_in_path: str):
            node1 = sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.compute = "will be ignored"
            node2 = sub_pipeline(
                component_in_number=component_in_number, component_in_path=node1.outputs.sub_pipeline_out
            )
            return node2.outputs

        pipeline1 = root_pipeline(1, "test")
        v = pipeline1._get_telemetry_values()
        assert v["type"] == "pipeline"
        assert v["source"] == "DSL"
        assert v["node_count"] == 2
        assert v["node_type"] == '{"pipeline": 2}'
        assert v["node_source"] == '{"DSL": 2}'
