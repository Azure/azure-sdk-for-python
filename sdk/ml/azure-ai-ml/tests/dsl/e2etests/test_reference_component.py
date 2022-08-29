import pydash
import pytest

from azure.ai.ml import dsl, MLClient, Input, Output
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import Data

from dsl.e2etests.test_dsl_pipeline_samples import cancel_pipeline_job

from dsl.e2etests.test_dsl_pipeline import job_input
from dsl._util import _DSL_TIMEOUT_SECOND
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
class TestReferenceComponent:
    def test_reference_command_component(
        self,
        client: MLClient,
        hello_world_component_reference,
        hello_world_component_upper_inputs_reference,
        hello_world_component_reference_remote,
    ):
        @dsl.pipeline(
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
        )
        def pipeline_with_output(job_in_number, job_in_other_number, job_in_path):
            node1 = hello_world_component_reference(component_in_number=job_in_number, component_in_path=job_in_path)
            node1.compute = "cpu-cluster"
            node2 = hello_world_component_reference_remote(
                component_in_number=job_in_other_number, component_in_path=job_in_path
            )
            node2.compute = "cpu-cluster"
            # case insensitive in function call
            node3 = hello_world_component_reference_remote(
                COMPONENT_IN_NUMBER=job_in_other_number, component_in_path=job_in_path
            )
            node3.compute = "cpu-cluster"
            node4 = hello_world_component_upper_inputs_reference(
                component_in_number=job_in_number, component_in_number_upper=job_in_other_number
            )
            node4.compute = "cpu-cluster"
            node5 = hello_world_component_upper_inputs_reference(
                component_in_number=job_in_number, COMPONENT_IN_NUMBER_UPPER=job_in_other_number
            )
            node5.compute = "cpu-cluster"

        pipeline = pipeline_with_output(10, 15, job_input)

        omit_fields = [
            "properties.jobs.node1.componentId",
            "properties.jobs.node4.componentId",
            "properties.jobs.node5.componentId",
        ]
        rest_pipeline = pydash.omit(pipeline._to_rest_object().as_dict(), omit_fields)

        assert rest_pipeline["properties"]["jobs"] == {
            "node1": {
                "_source": "YAML.COMPONENT",
                "computeId": "cpu-cluster",
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "limits": None,
                "name": "node1",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
            "node2": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "componentId": "microsoftsamples_command_component_basic:0.0.1",
                "computeId": "cpu-cluster",
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "limits": None,
                "name": "node2",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
            "node3": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "componentId": "microsoftsamples_command_component_basic:0.0.1",
                "computeId": "cpu-cluster",
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "limits": None,
                "name": "node3",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
            "node4": {
                "_source": "YAML.COMPONENT",
                "computeId": "cpu-cluster",
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "COMPONENT_IN_NUMBER_UPPER": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                },
                "limits": None,
                "name": "node4",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
            "node5": {
                "_source": "YAML.COMPONENT",
                "computeId": "cpu-cluster",
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "COMPONENT_IN_NUMBER_UPPER": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                },
                "limits": None,
                "name": "node5",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
        }
        cancel_pipeline_job(pipeline, client)

    def test_reference_parallel_component(
        self, client: MLClient, batch_inference_component_reference, batch_inference_component_reference_remote
    ):
        @dsl.pipeline(default_compute="cpu-cluster")
        def parallel_in_pipeline(job_data_path):
            node1 = batch_inference_component_reference(job_data_path=job_data_path)
            node1.mini_batch_size = 1
            node2 = batch_inference_component_reference_remote(job_data_path=job_data_path)
            node2.mini_batch_size = 2

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data",
                mode=InputOutputModes.EVAL_MOUNT,
            )
        )
        omit_fields = ["properties.jobs.node1.componentId"]
        rest_pipeline = pydash.omit(pipeline._to_rest_object().as_dict(), omit_fields)

        assert rest_pipeline["properties"]["jobs"] == {
            "node1": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "environment_variables": {},
                "error_threshold": None,
                "input_data": "${{inputs.job_data_path}}",
                "inputs": {"job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"}},
                "logging_level": None,
                "max_concurrency_per_instance": 1,
                "mini_batch_error_threshold": 1,
                "mini_batch_size": 1,
                "name": "node1",
                "outputs": {},
                "resources": {"instance_count": 2, "properties": {}},
                "retry_settings": None,
                "tags": {},
                "task": {
                    "program_arguments": "--job_output_path ${{outputs.job_output_path}}",
                    "code": "./src",
                    "entry_script": "score.py",
                    "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                    "type": "run_function",
                },
                "type": "parallel",
            },
            # Note: for remote components, we will only pass user assigned run settings.
            # Default values for max_concurrency_per_instance, resources, task will be stored in component level
            "node2": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "componentId": "file_batch_score:1.0.0",
                "computeId": None,
                "display_name": None,
                "environment_variables": {},
                "error_threshold": None,
                "input_data": None,
                "inputs": {"job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"}},
                "logging_level": None,
                "max_concurrency_per_instance": None,
                "mini_batch_error_threshold": None,
                "mini_batch_size": 2,
                "name": "node2",
                "outputs": {},
                "resources": None,
                "retry_settings": None,
                "tags": {},
                "task": None,
                "type": "parallel",
            },
        }
        cancel_pipeline_job(pipeline, client)

    def test_reference_component_with_output(self, client: MLClient, hello_world_component_reference):
        @dsl.pipeline(
            description="The hello world pipeline job",
            tags={"owner": "sdkteam", "tag": "tagvalue"},
            compute="cpu-cluster",
        )
        def pipeline_with_output(job_in_number, job_in_other_number, job_in_path):
            node1 = hello_world_component_reference(component_in_number=job_in_number, component_in_path=job_in_path)

            node2 = hello_world_component_reference(
                component_in_number=job_in_other_number,
                component_in_path=node1.outputs.component_out_path,
            )
            return {"job_out_data": node2.outputs.component_out_path}

        pipeline = pipeline_with_output(10, 15, job_input)
        pipeline.outputs.job_out_data = Output(dataset=Data(name="dsl_pipeline_output", version="1"))

        omit_fields = ["properties.jobs.node1.componentId", "properties.jobs.node2.componentId"]
        rest_pipeline = pydash.omit(pipeline._to_rest_object().as_dict(), omit_fields)

        assert rest_pipeline["properties"]["jobs"] == {
            "node1": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "limits": None,
                "name": "node1",
                "outputs": {},
                "resources": None,
                "tags": {},
            },
            "node2": {
                "_source": "YAML.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.node1.outputs.component_out_path}}",
                    },
                },
                "limits": None,
                "name": "node2",
                "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.job_out_data}}"}},
                "resources": None,
                "tags": {},
            },
        }
        cancel_pipeline_job(pipeline, client)
