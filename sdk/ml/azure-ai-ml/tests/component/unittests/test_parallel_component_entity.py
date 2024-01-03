from pathlib import Path

import pydash
import pytest
from test_utilities.utils import parse_local_path

from azure.ai.ml import load_component
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._job.pipeline._io import PipelineInput

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestParallelComponentEntity:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/components/basic_parallel_component_score.yml"
        parallel_component = load_component(
            source=component_yaml,
        )
        assert parallel_component.task.get("type") == "run_function"
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
            "type": "run_function",
            "code": "../python",
            "entry_script": "pass_through.py",
            "program_arguments": "--label ${{inputs.label}} --model ${{inputs.score_model}} --output_scored_result ${{outputs.scored_result}}",
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
            logging_level="INFO",
            task=task,
            base_path="./tests/test_configs/components",
        )
        omit_fields = [
            "properties.component_spec.$schema",
            "properties.component_spec.inputs",
            "properties.component_spec._source",
            "properties.properties.client_component_hash",
        ]
        component_dict = component._to_rest_object().as_dict()
        component_dict = pydash.omit(component_dict, *omit_fields)

        yaml_path = "./tests/test_configs/components/basic_parallel_component_score.yml"
        yaml_component = load_component(source=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, *omit_fields)

        assert component_dict == yaml_component_dict

    def test_parallel_component_version_as_a_function_with_inputs(self):
        yaml_path = "./tests/test_configs/components/helloworld_parallel.yml"
        yaml_component_version = load_component(source=yaml_path)
        expected_rest_component = {
            "componentId": "fake_component",
            "_source": "YAML.COMPONENT",
            "input_data": "${{inputs.component_in_path}}",
            "inputs": {
                "model": {"job_input_type": "literal", "value": "SVM"},
                "label": {"job_input_type": "literal", "value": "test"},
                "component_in_path": {
                    "job_input_type": "literal",
                    "value": "${{parent.inputs.pipeline_input}}",
                },
            },
            "input_data": "${{inputs.component_in_path}}",
            "type": "parallel",
            "mini_batch_size": 10485760,
            "task": {
                "append_row_to": "${{outputs.scoring_summary}}",
                "program_arguments": "--label ${{inputs.label}} --model ${{inputs.model}}",
                "code": parse_local_path("../python", yaml_component_version.base_path),
                "entry_script": "score.py",
                "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                "type": "run_function",
            },
        }
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        yaml_component = yaml_component_version(model="SVM", label="test", component_in_path=pipeline_input)

        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()

        assert rest_yaml_component == expected_rest_component

    def test_parallel_component_run_settings_picked_up(self):
        yaml_path = "./tests/test_configs/components/parallel_component_with_run_settings.yml"
        parallel_component = load_component(source=yaml_path)
        parallel_node = parallel_component()
        # Normally, during initiation of nodes, the settings from the yaml file shouldn't be changed
        assert parallel_component.resources.instance_count == parallel_node.resources.instance_count == 1
        assert parallel_component.max_concurrency_per_instance == parallel_node.max_concurrency_per_instance == 16
        assert parallel_component.retry_settings == parallel_node.retry_settings
        assert parallel_component.retry_settings.timeout == 12345
