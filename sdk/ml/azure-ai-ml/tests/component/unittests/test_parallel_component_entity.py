import pydash
import pytest

from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities import Component, ParallelComponent
from azure.ai.ml.entities._job.pipeline._exceptions import UnexpectedKeywordError
from azure.ai.ml.entities._job.pipeline._io import PipelineInput


@pytest.mark.unittest
class TestParallelComponentEntity:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/components/basic_parallel_component_score.yml"
        parallel_component = Component.load(
            path=component_yaml,
        )
        assert parallel_component.task.get("type") == "function"
        assert parallel_component.code == "../python"

    def test_command_component_to_dict(self):
        # Test optional params exists in component dict
        yaml_path = "./tests/test_configs/components/basic_parallel_component_score.yml"
        yaml_dict = load_yaml(yaml_path)
        yaml_dict["mock_option_param"] = {"mock_key": "mock_val"}
        parallel_component = ParallelComponent._load(data=yaml_dict, yaml_path=yaml_path)
        assert parallel_component._other_parameter.get("mock_option_param") == yaml_dict["mock_option_param"]

    def test_parallel_component_entity(self):
        task = {
            "type": "function",
            "code": "../python",
            "entry_script": "pass_through.py",
            "args": "--label ${{inputs.label}} --model ${{inputs.score_model}} --output_scored_result ${{outputs.scored_result}}",
            "append_row_to": "${{outputs.scoring_summary}}",
            "environment": "AzureML-Minimal:2",
        }

        component = ParallelComponent(
            name="batch_score",
            display_name="BatchScore",
            description="parallel component for batch score",
            version="1.0.0",
            outputs={
                "scored_result": {"type": "mltable"},
                "scoring_summary": {"type": "uri_file"},
            },
            resources={"instance_count": 2},
            retry_settings={"max_retries": 10, "timeout": 3},
            mini_batch_size="10kb",
            input_data="${{inputs.score_input}}",
            max_concurrency_per_instance=12,
            error_threshold=10,
            mini_batch_error_threshold=5,
            logging_level="DEBUG",
            task=task,
        )
        component_dict = component._to_rest_object().as_dict()
        component_dict = pydash.omit(
            component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.inputs",
        )

        yaml_path = "./tests/test_configs/components/basic_parallel_component_score.yml"
        yaml_component = Component.load(path=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(
            yaml_component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.inputs",
        )

        assert component_dict == yaml_component_dict

    def test_parallel_component_version_as_a_function_with_inputs(self):
        expected_rest_component = {
            "componentId": "fake_component",
            "computeId": None,
            "display_name": None,
            "input_data": "${{inputs.score_input}}",
            "inputs": {
                "component_in_number": {"job_input_type": "Literal", "value": "10"},
                "component_in_path": {
                    "job_input_type": "Literal",
                    "value": "${{parent.inputs.pipeline_input}}",
                },
            },
            "name": None,
            "outputs": {},
            "tags": {},
            "input_data": "${{inputs.score_input}}",
            "type": "parallel",
            "error_threshold": None,
            "logging_level": None,
            "max_concurrency_per_instance": None,
            "mini_batch_error_threshold": None,
            "mini_batch_size": 10485760,
            "retry_settings": None,
            "resources": None,
            "environment_variables": {},
            "task": {
                "append_row_to": "${{outputs.scoring_summary}}",
                "args": "--label ${{inputs.label}} --model ${{inputs.model}} " "--output ${{outputs.scored_result}}",
                "code": "azureml:./src",
                "entry_script": "score.py",
                "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                "type": "function",
            },
        }
        yaml_path = "./tests/test_configs/components/helloworld_parallel.yml"
        yaml_component_version = Component.load(path=yaml_path)
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        yaml_component = yaml_component_version(component_in_number=10, component_in_path=pipeline_input)

        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()

        assert expected_rest_component == rest_yaml_component
