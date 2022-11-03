import copy
import json
import logging
from pathlib import Path

import pytest
import yaml

from azure.ai.ml import Input, load_component, load_job
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml.entities import PipelineComponent, PipelineJob, Component
from azure.ai.ml.entities._inputs_outputs import GroupInput
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, _GroupAttrDict

from .._util import _COMPONENT_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineComponentEntity:
    def test_inline_helloworld_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_inline_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)
        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "name": "helloworld_pipeline_component",
            "version": "1",
            "display_name": "Hello World Pipeline Component",
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "inputs": {
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number",
                },
                "component_in_path": {"type": "uri_folder", "description": "A path"},
                "node_compute": {"type": "string", "default": "azureml:cpu-cluster"},
            },
            "outputs": {},
            "type": "pipeline",
            "jobs": {
                "component_a_job": {
                    "properties": {},
                    "component": {
                        "command": 'echo "hello" && echo ' '"world" > ' "${{outputs.world_output}}/world.txt",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
                        "inputs": {},
                        "is_deterministic": True,
                        "name": "azureml_anonymous",
                        "outputs": {"world_output": {"type": "uri_folder"}},
                        "tags": {},
                        "type": "command",
                        "version": "1",
                    },
                    "compute": "${{parent.inputs.node_compute}}",
                    "environment_variables": {},
                    "inputs": {},
                    "outputs": {},
                    "type": "command",
                },
            },
        }
        component_dict = component._to_dict()

        assert component_dict == exptected_dict

    def test_helloworld_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)
        assert component._base_path is not None
        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "description": "This is the basic pipeline component",
            "display_name": "Hello World Pipeline Component",
            "inputs": {
                "component_in_number": {
                    "default": "10.99",
                    "description": "A number",
                    "optional": True,
                    "type": "number",
                },
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            "jobs": {
                "component_a_job": {
                    "properties": {},
                    "component": {
                        "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
                        "command": "echo Hello World & "
                        "echo "
                        "$[[${{inputs.component_in_number}}]] "
                        "& echo "
                        "${{inputs.component_in_path}} "
                        "& echo "
                        "${{outputs.component_out_path}} "
                        "> "
                        "${{outputs.component_out_path}}/component_in_number",
                        "description": "This is the basic " "command component",
                        "display_name": "CommandComponentBasic",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                        "inputs": {
                            "component_in_number": {
                                "default": "10.99",
                                "description": "A " "number",
                                "optional": True,
                                "type": "number",
                            },
                            "component_in_path": {"description": "A " "path", "type": "uri_folder"},
                        },
                        "is_deterministic": True,
                        "name": "azureml_anonymous",
                        "outputs": {"component_out_path": {"type": "uri_folder"}},
                        "tags": {"owner": "sdkteam", "tag": "tagvalue"},
                        "type": "command",
                        "version": "1",
                    },
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {"component_out_path": "${{parent.outputs.output_path}}"},
                    "type": "command",
                }
            },
            "name": "helloworld_pipeline_component",
            "outputs": {"output_path": {"type": "uri_folder"}},
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "pipeline",
            "version": "1",
        }
        component_dict = component._to_dict()
        assert component_dict == exptected_dict

    def test_helloworld_nested_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_nested_pipeline_component.yml"
        component: PipelineComponent = load_component(source=component_path)

        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "description": "This is the basic pipeline component",
            "display_name": "Hello World Pipeline Component",
            "inputs": {
                "component_in_number": {
                    "default": "10.99",
                    "description": "A number for pipeline " "component",
                    "optional": True,
                    "type": "number",
                },
                "component_in_path": {"description": "A path for pipeline " "component", "type": "uri_folder"},
            },
            "jobs": {
                "pipeline_component": {
                    "component": {
                        "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
                        "creation_context": None,
                        "description": "This is the " "basic pipeline " "component",
                        "display_name": "Hello World " "Pipeline " "Component",
                        "id": None,
                        "inputs": {
                            "component_in_number": {
                                "default": "10.99",
                                "description": "A " "number",
                                "optional": True,
                                "type": "number",
                            },
                            "component_in_path": {"description": "A " "path", "type": "uri_folder"},
                        },
                        "is_deterministic": None,
                        "jobs": {
                            "component_a_job": {
                                "component": {
                                    "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
                                    "command": "echo "
                                    "Hello "
                                    "World "
                                    "& "
                                    "echo "
                                    "$[[${{inputs.component_in_number}}]] "
                                    "& "
                                    "echo "
                                    "${{inputs.component_in_path}} "
                                    "& "
                                    "echo "
                                    "${{outputs.component_out_path}} "
                                    "> "
                                    "${{outputs.component_out_path}}/component_in_number",
                                    "description": "This " "is " "the " "basic " "command " "component",
                                    "display_name": "CommandComponentBasic",
                                    "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                                    "inputs": {
                                        "component_in_number": {
                                            "default": "10.99",
                                            "description": "A " "number",
                                            "optional": True,
                                            "type": "number",
                                        },
                                        "component_in_path": {"description": "A " "path", "type": "uri_folder"},
                                    },
                                    "is_deterministic": True,
                                    "name": "azureml_anonymous",
                                    "outputs": {"component_out_path": {"type": "uri_folder"}},
                                    "tags": {"owner": "sdkteam", "tag": "tagvalue"},
                                    "type": "command",
                                    "version": "1",
                                },
                                "environment_variables": {},
                                "inputs": {
                                    "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                                    "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                                },
                                "outputs": {"component_out_path": "${{parent.outputs.output_path}}"},
                                "properties": {},
                                "type": "command",
                            }
                        },
                        "latest_version": None,
                        "name": "azureml_anonymous",
                        "outputs": {"output_path": {"type": "uri_folder"}},
                        "tags": {"owner": "sdkteam", "tag": "tagvalue"},
                        "type": "pipeline",
                        "version": "1",
                    },
                    "properties": {},
                    "inputs": {"component_in_path": {"path": "${{parent.inputs.component_in_path}}"}},
                    "outputs": {},
                    "type": "pipeline",
                }
            },
            "name": "helloworld_pipeline_component",
            "outputs": {"nested_output": {"type": "uri_folder"}, "nested_output2": {"type": "uri_folder"}},
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "pipeline",
            "version": "1",
        }
        component_dict = component._to_dict()
        assert component_dict == exptected_dict

    def test_pipeline_job_to_component(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        job: PipelineJob = load_job(source=test_path)

        pipeline_component = job._to_component()
        expected_dict = {
            "inputs": {
                "job_in_number": {"default": "10", "type": "integer"},
                "job_in_other_number": {"default": "15", "type": "integer"},
                "job_in_path": {"type": "uri_folder", "mode": "ro_mount"},
            },
            "jobs": {
                "hello_world_component": {
                    "properties": {},
                    "component": "azureml:microsoftsamplesCommandComponentBasic_second:1",
                    "compute": "azureml:cpu-cluster",
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.job_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.job_in_path}}"},
                    },
                    "outputs": {},
                    "type": "command",
                },
                "hello_world_component_2": {
                    "properties": {},
                    "component": "azureml:microsoftsamplesCommandComponentBasic_second:1",
                    "compute": "azureml:cpu-cluster",
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.job_in_other_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.job_in_path}}"},
                    },
                    "outputs": {},
                    "type": "command",
                },
            },
            "name": "azureml_anonymous",
            "outputs": {},
            "tags": {},
            "type": "pipeline",
            "version": "1",
        }
        component_dict = pipeline_component._to_dict()
        assert component_dict == expected_dict

    def test_pipeline_job_translation_warning(self, caplog):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        job: PipelineJob = load_job(source=test_path)

        from azure.ai.ml.entities._job.pipeline import pipeline_job

        # Set original module_logger with name 'azure.ai.ml.entities._job.pipeline.pipeline_job'
        # To 'PipelineJob' to enable caplog capture logs
        pipeline_job.module_logger = logging.getLogger("PipelineJob")

        with caplog.at_level(logging.WARNING):
            job._to_component()
        assert (
            "['compute'] ignored when translating PipelineJob 'simplepipelinejob' to PipelineComponent."
            in caplog.messages
        )

        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults.yml"
        job: PipelineJob = load_job(source=test_path)

        with caplog.at_level(logging.WARNING):
            job._to_component()
        assert (
            "['compute', 'settings'] ignored when translating PipelineJob 'simplePipelineJobWithInlineComps' to PipelineComponent."
            in caplog.messages
        )

        job.compute = None
        job.settings = None
        with caplog.at_level(logging.WARNING):
            job._to_component()
        # assert no new warnings.
        assert len(caplog.messages) == 2

    def test_pipeline_job_input_translation(self):
        input = PipelineInput(name="input", meta=None, data=10)
        assert input._to_input()._to_dict() == {"type": "integer", "default": 10}
        input = PipelineInput(name="input", meta=None, data="test")
        assert input._to_input()._to_dict() == {"type": "string", "default": "test"}
        input = PipelineInput(name="input", meta=None, data=1.5)
        assert input._to_input()._to_dict() == {"type": "number", "default": 1.5}
        input = PipelineInput(name="input", meta=None, data=True)
        assert input._to_input()._to_dict() == {"type": "boolean", "default": True}
        input = PipelineInput(name="input", meta=None, data=True)
        assert input._to_input()._to_dict() == {"type": "boolean", "default": True}
        input = PipelineInput(name="input", meta=None, data=Input())
        assert input._to_input()._to_dict() == {"type": "uri_folder"}
        input = PipelineInput(name="input", meta=None, data=Input(type="uri_file", mode="download", path="fake"))
        assert input._to_input()._to_dict() == {"type": "uri_file", "mode": "download"}

    def test_pipeline_component_with_group(self) -> None:
        component_path = "./tests/test_configs/components/pipeline_component_with_group.yml"
        component: PipelineComponent = load_component(component_path)
        assert len(component.inputs) == 2
        assert isinstance(component.inputs["group"], GroupInput)
        component_dict = component._to_dict()
        assert component_dict["inputs"] == {
            "component_in_path": {"type": "uri_folder", "description": "A path"},
            "group.component_in_number": {
                "type": "number",
                "optional": True,
                "default": "10.99",
                "description": "A number",
            },
            "group.sub.component_in_number2": {
                "type": "number",
                "optional": True,
                "default": "10.99",
                "description": "A number",
            },
        }
        assert component_dict["jobs"]["node1"]["inputs"] == {
            "component_in_number": {"path": "${{parent.inputs.group.component_in_number}}"},
            "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
        }
        assert component_dict["jobs"]["node2"]["inputs"] == {
            "component_in_number": {"path": "${{parent.inputs.group.sub.component_in_number}}"},
            "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
        }

    def test_nested_pipeline_component_with_group(self) -> None:
        component_path = "./tests/test_configs/components/nested_pipeline_component_with_group.yml"
        component: PipelineComponent = load_component(component_path)
        assert len(component.inputs) == 2
        assert isinstance(component.inputs["top_group"], GroupInput)
        nested_pipeline_component = component.jobs["component_a_job"]
        assert len(nested_pipeline_component.inputs) == 2
        assert isinstance(nested_pipeline_component.inputs.group, _GroupAttrDict)
        component_dict = component._to_dict()
        assert component_dict["inputs"] == {
            "component_in_path": {"type": "uri_folder", "description": "A path"},
            "top_group.component_in_number": {
                "type": "number",
                "optional": True,
                "default": "10.99",
                "description": "A number",
            },
            "top_group.sub2.component_in_number2": {
                "type": "number",
                "optional": True,
                "default": "10.99",
                "description": "A number",
            },
        }
        assert component_dict["jobs"]["component_a_job"]["inputs"] == {
            "component_in_path": {"path": "${{parent.inputs.group.component_in_path}}"},
            "group.component_in_number": {"path": "${{parent.inputs.top_group.component_in_number}}"},
            "group.sub.component_in_number2": {"path": "${{parent.inputs.top_group.sub2.component_in_number2}}"},
        }
        assert component_dict["jobs"]["component_a_job"]["component"]["inputs"] == {
            "component_in_path": {"description": "A path", "type": "uri_folder"},
            "group.component_in_number": {
                "default": "10.99",
                "description": "A number",
                "optional": True,
                "type": "number",
            },
            "group.sub.component_in_number2": {
                "default": "10.99",
                "description": "A number",
                "optional": True,
                "type": "number",
            },
        }

    def test_invalid_nested_pipeline_component_with_group(self) -> None:
        component_path = "./tests/test_configs/components/invalid/invalid_nested_pipeline_component_with_group.yml"
        with pytest.raises(Exception) as e:
            load_component(component_path)
        assert (
            "'group' is defined as a parameter group but got input '${{parent.inputs.top_group}}' with type '<class 'str'>'"
            in str(e.value)
        )

    def test_simple_jobs_from_rest(self) -> None:
        test_path = "./tests/test_configs/components/pipeline_component_jobs_rest_data.json"
        with open(test_path, "r") as f:
            json_in_file = yaml.safe_load(f)
        job_dict = copy.deepcopy(json_in_file['properties']['component_spec']['jobs'])
        jobs = PipelineComponent._resolve_sub_nodes(job_dict)
        node_dict = {key: node._to_rest_object() for key, node in jobs.items()}['component_a_job']
        assert node_dict['computeId'] == '${{parent.inputs.node_compute}}'
        assert node_dict['outputs'] == {
            'output_binding': {'type': 'literal', 'value': '${{parent.outputs.output}}'},
            'output_binding2': {'type': 'literal', 'value': '${{parent.outputs.output}}'},
            'output_data': {'job_output_type': 'uri_folder', 'mode': 'Upload'},
            'output_data_legacy': {'job_output_type': 'uri_folder', 'mode': 'Upload'}}
        assert node_dict['inputs'] == {
            'binding_input': {'job_input_type': 'literal', 'value': '${{parent.inputs.component_in_path}}'},
            'data_input': {'job_input_type': 'uri_file',
                           'mode': 'Download',
                           'uri': 'https://my-blob/path/to/data'},
            'data_input_legacy': {'job_input_type': 'uri_file',
                                  'mode': 'Download',
                                  'uri': 'https://my-blob/path/to/data'},
            'literal_input': {'job_input_type': 'literal', 'value': '11'},
            'literal_input2': {'job_input_type': 'literal', 'value': '12'}}
        assert node_dict['resources'] == {'instance_count': 1, 'properties': {
            'target_selector': {'my_resource_only': 'false', 'allow_spot_vm': 'true'}}, 'shm_size': '2g'}

        rest_obj = ComponentVersionData.from_dict(json.loads(json.dumps(json_in_file)))
        pipeline_component = Component._from_rest_object(rest_obj)
        assert pipeline_component.jobs
        obj_node_dict = {key: node._to_rest_object() for key, node in pipeline_component.jobs.items()}['component_a_job']
        assert obj_node_dict == node_dict
