import logging
from pathlib import Path
import pytest
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent

from azure.ai.ml import MLClient, load_component, load_job, Input
from azure.ai.ml.entities._job.pipeline._io import PipelineInput

from .._util import _COMPONENT_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestPipelineComponentEntity:
    def test_inline_helloworld_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_inline_pipeline_component.yml"
        component: PipelineComponent = load_component(path=component_path)
        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "name": "helloworld_pipeline_component",
            "version": "1",
            "display_name": "Hello World Pipeline Component",
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "is_deterministic": True,
            "inputs": {
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number",
                },
                "component_in_path": {"type": "uri_folder", "description": "A path"},
            },
            "outputs": {},
            "type": "pipeline",
            "jobs": {
                "component_a_job": {
                    "$schema": "{}",
                    "command": 'echo "hello" && echo "world" > ' "${{outputs.world_output}}/world.txt",
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
                    "compute": "azureml:cpu-cluster",
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
        component: PipelineComponent = load_component(path=component_path)
        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "name": "helloworld_pipeline_component",
            "version": "1",
            "display_name": "Hello World Pipeline Component",
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "is_deterministic": True,
            "inputs": {
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number",
                },
                "component_in_path": {"type": "uri_folder", "description": "A path"},
            },
            "outputs": {},
            "type": "pipeline",
            "jobs": {
                "component_a_job": {
                    "$schema": "{}",
                    "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                    "environment_variables": {},
                    "inputs": {
                        "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                        "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                    },
                    "outputs": {},
                    "component": {
                        "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
                        "name": "azureml_anonymous",
                        "version": "1",
                        "display_name": "CommandComponentBasic",
                        "description": "This is the basic command component",
                        "tags": {"tag": "tagvalue", "owner": "sdkteam"},
                        "is_deterministic": True,
                        "inputs": {
                            "component_in_number": {
                                "type": "number",
                                "optional": True,
                                "default": "10.99",
                                "description": "A number",
                            },
                            "component_in_path": {"type": "uri_folder", "description": "A path"},
                        },
                        "outputs": {"component_out_path": {"type": "uri_folder"}},
                        "type": "command",
                        "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                        "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                    },
                    "type": "command",
                }
            },
        }
        component_dict = component._to_dict()
        assert component_dict == exptected_dict

    def test_helloworld_nested_pipeline_component(self) -> None:
        component_path = "./tests/test_configs/components/helloworld_nested_pipeline_component.yml"
        component: PipelineComponent = load_component(path=component_path)

        exptected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "name": "helloworld_pipeline_component",
            "version": "1",
            "display_name": "Hello World Pipeline Component",
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "is_deterministic": True,
            "inputs": {
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number for pipeline component",
                },
                "component_in_path": {"type": "uri_folder", "description": "A path for pipeline component"},
            },
            "outputs": {},
            "type": "pipeline",
            "jobs": {
                "pipeline_component": {
                    "$schema": "{}",
                    "inputs": {"component_in_path": {"path": "${{parent.inputs.component_in_path}}"}},
                    "outputs": {},
                    "component": {
                        "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
                        "name": "azureml_anonymous",
                        "id": None,
                        "version": "1",
                        "display_name": "Hello World Pipeline Component",
                        "description": "This is the basic pipeline component",
                        "tags": {"tag": "tagvalue", "owner": "sdkteam"},
                        "is_deterministic": True,
                        "inputs": {
                            "component_in_number": {
                                "type": "number",
                                "optional": True,
                                "default": "10.99",
                                "description": "A number",
                            },
                            "component_in_path": {"type": "uri_folder", "description": "A path"},
                        },
                        "outputs": {},
                        "creation_context": None,
                        "type": "pipeline",
                        "jobs": {
                            "component_a_job": {
                                "$schema": "{}",
                                "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                                "environment_variables": {},
                                "inputs": {
                                    "component_in_number": {"path": "${{parent.inputs.component_in_number}}"},
                                    "component_in_path": {"path": "${{parent.inputs.component_in_path}}"},
                                },
                                "outputs": {},
                                "component": {
                                    "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
                                    "name": "azureml_anonymous",
                                    "version": "1",
                                    "display_name": "CommandComponentBasic",
                                    "description": "This is the basic command component",
                                    "tags": {"tag": "tagvalue", "owner": "sdkteam"},
                                    "is_deterministic": True,
                                    "inputs": {
                                        "component_in_number": {
                                            "type": "number",
                                            "optional": True,
                                            "default": "10.99",
                                            "description": "A number",
                                        },
                                        "component_in_path": {"type": "uri_folder", "description": "A path"},
                                    },
                                    "outputs": {"component_out_path": {"type": "uri_folder"}},
                                    "type": "command",
                                    "command": "echo Hello World & echo [${{inputs.component_in_number}}] & echo ${{inputs.component_in_path}} & echo ${{outputs.component_out_path}} > ${{outputs.component_out_path}}/component_in_number",
                                    "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
                                },
                                "type": "command",
                            }
                        },
                        "latest_version": None,
                    },
                    "type": "pipeline",
                }
            },
        }
        component_dict = component._to_dict()
        assert component_dict == exptected_dict

    def test_pipeline_job_to_component(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        job: PipelineJob = load_job(path=test_path)

        pipeline_component = job._to_component()
        expected_dict = {
            "inputs": {
                "job_in_number": {"default": "10", "type": "integer"},
                "job_in_other_number": {"default": "15", "type": "integer"},
                "job_in_path": {"type": "uri_folder"},
            },
            "is_deterministic": True,
            "jobs": {
                "hello_world_component": {
                    "$schema": "{}",
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
                    "$schema": "{}",
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
        job: PipelineJob = load_job(path=test_path)

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
        job: PipelineJob = load_job(path=test_path)

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
