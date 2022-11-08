import os
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pydash
import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import Input, MpiDistribution, Output, TensorFlowDistribution, command, load_component
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities import CommandComponent, CommandJobLimits, Component, JobResourceConfiguration
from azure.ai.ml.entities._builders import Command, Sweep
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.exceptions import UnexpectedKeywordError, ValidationException
from azure.ai.ml.sweep import Choice

from .._util import _COMPONENT_TIMEOUT_SECOND


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestCommandComponentEntity:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/components/basic_component_code_local_path.yml"

        def simple_component_validation(command_component):
            assert command_component.code == "./helloworld_components_with_env"

        command_component = verify_entity_load_and_dump(load_component, simple_component_validation, component_yaml)[0]
        component_yaml = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        command_component = load_component(
            source=component_yaml,
        )
        expected_code = (
            "/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/"
            "test-rg-centraluseuap-v2-2021W10/providers/Microsoft.MachineLearningServices/"
            "workspaces/sdk_vnext_cli/codes/e736692c-8542-11eb-b746-6c2b59f8af4d/versions/1"
        )
        assert command_component.code == expected_code

    def test_command_component_to_dict(self):
        # Test optional params exists in component dict
        yaml_path = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        yaml_dict = load_yaml(yaml_path)
        yaml_dict["mock_option_param"] = {"mock_key": "mock_val"}
        command_component = CommandComponent._load(data=yaml_dict, yaml_path=yaml_path)
        assert command_component._other_parameter.get("mock_option_param") == yaml_dict["mock_option_param"]

        yaml_dict["version"] = str(yaml_dict["version"])
        yaml_dict["inputs"] = {}
        component_dict = command_component._to_dict()
        component_dict.pop("is_deterministic")
        assert yaml_dict == component_dict

    def test_command_component_entity(self):
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
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
        )
        component_dict = component._to_rest_object().as_dict()
        omits = ["properties.component_spec.$schema", "properties.component_spec._source"]
        component_dict = pydash.omit(component_dict, *omits)

        yaml_path = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        yaml_component = load_component(source=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, *omits)

        assert component_dict == yaml_component_dict

    def test_command_component_entity_with_io_class(self):
        component = CommandComponent(
            name="sample_command_component_entity_with_io_class",
            display_name="Preprocess data for training",
            description="reads raw price data, normalize and split the data",
            inputs={
                "data_0": Input(type="uri_folder", mode="ro_mount"),
                "data_1": Input(type="uri_file", optional=True),
                "param_float0": Input(type="number", default=1.1, min=0, max=5),
                "param_float1": Input(type="number"),
                "param_integer": Input(type="integer", default=2, min=-1, max=4, optional=True),
                "param_string": Input(type="string", default="default_str"),
                "param_boolean": Input(type="boolean", default=False),
            },
            outputs={
                "train_data_x": Output(type="uri_file"),
                "test_data_x": Output(type="uri_folder"),
            },
            # TODO: reorganize code to minimize the code context
            code=".",
            command="""echo Hello World""",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5",
        )
        component_dict = component._to_rest_object().as_dict()
        inputs = component_dict["properties"]["component_spec"]["inputs"]
        outputs = component_dict["properties"]["component_spec"]["outputs"]
        source = component_dict["properties"]["component_spec"]["_source"]

        assert inputs == {
            "data_0": {"mode": "ro_mount", "type": "uri_folder"},
            "data_1": {"type": "uri_file", "optional": True},
            "param_float0": {"type": "number", "default": "1.1", "max": "5.0", "min": "0.0"},
            "param_float1": {"type": "number"},
            "param_integer": {"type": "integer", "optional": True, "default": "2", "max": "4", "min": "-1"},
            "param_string": {"type": "string", "default": "default_str"},
            "param_boolean": {"type": "boolean", "default": "False"},
        }
        assert outputs == {"train_data_x": {"type": "uri_file"}, "test_data_x": {"type": "uri_folder"}}
        assert source == "CLASS"

    def test_command_component_instance_count(self):
        component = CommandComponent(
            name="microsoftsamples_command_component_tensor_flow",
            display_name="CommandComponentTensorFlow",
            description="This is the TensorFlow command component",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            inputs={
                "component_in_number": {"description": "A number", "type": "number", "default": 10.99},
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World & echo ${{inputs.component_in_number}} & echo ${{inputs.component_in_path}} "
            "& echo ${{outputs.component_out_path}}",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            distribution=TensorFlowDistribution(
                parameter_server_count=1,
                worker_count=2,
                # No affect because TensorFlow object does not allow extra fields
                added_property=7,
            ),
            instance_count=2,
        )
        component_dict = component._to_rest_object().as_dict()

        yaml_path = "./tests/test_configs/components/helloworld_component_tensorflow.yml"
        yaml_component = load_component(source=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()

        component_dict = pydash.omit(
            component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.distribution.added_property",
            "properties.component_spec.resources.properties",
            "properties.component_spec._source",
        )
        yaml_component_dict = pydash.omit(
            yaml_component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.distribution.added_property",
            "properties.component_spec.resources.properties",
            "properties.component_spec._source",
        )
        assert component_dict == yaml_component_dict

    def test_command_component_code(self):
        component = CommandComponent(
            name="SampleCommandComponentBasic",
            display_name="CommandComponentBasic",
            description="This is the basic command component",
            version="1",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            outputs={"component_out_path": {"type": "path"}},
            command="echo Hello World",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            code="./helloworld_components_with_env",
        )

        yaml_path = "./tests/test_configs/components/basic_component_code_local_path.yml"
        yaml_component = load_component(source=yaml_path)
        assert component.code == yaml_component.code

    def test_command_component_code_with_current_folder(self):
        old_cwd = os.getcwd()
        os.chdir("./tests/test_configs/components")
        try:
            yaml_path = "./basic_component_code_current_folder.yml"
            component = load_component(yaml_path)
            with component._resolve_local_code() as code:
                Path(code.path).resolve().name == "components"
        finally:
            os.chdir(old_cwd)

    def test_command_component_code_git_path(self):
        yaml_path = "./tests/test_configs/components/component_git_path.yml"
        yaml_dict = load_yaml(yaml_path)
        component = load_component(yaml_path)
        with component._resolve_local_code() as code:
            assert code.path == yaml_dict["code"]

    @pytest.mark.skipif(
        sys.version_info[1] == 11,
        reason=f"This test is not compatible with Python 3.11, skip in CI.",
    )
    def test_command_component_version_as_a_function(self):
        expected_rest_component = {
            "componentId": "fake_component",
            "computeId": None,
            "display_name": None,
            "distribution": None,
            "environment_variables": {},
            "inputs": {},
            "properties": {},
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": None,
            "tags": {},
            "type": "command",
            "_source": "YAML.COMPONENT",
        }

        yaml_path = "./tests/test_configs/components/basic_component_code_local_path.yml"
        yaml_component_version = load_component(source=yaml_path)
        assert isinstance(yaml_component_version, CommandComponent)

        yaml_component = yaml_component_version()
        assert isinstance(yaml_component, Command)

        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()
        assert rest_yaml_component == expected_rest_component

        # assert positional args is not supported
        with pytest.raises(TypeError) as error_info:
            yaml_component_version(1)
        assert "[component] CommandComponentBasic() takes 0 positional arguments but 1 was given" in str(error_info)

        # unknown kw arg
        with pytest.raises(UnexpectedKeywordError) as error_info:
            yaml_component_version(unknown=1)
        assert "[component] CommandComponentBasic() got an unexpected keyword argument 'unknown'." in str(error_info)

    def test_command_component_version_as_a_function_with_inputs(self):
        expected_rest_component = {
            "componentId": "fake_component",
            "computeId": None,
            "display_name": None,
            "distribution": None,
            "environment_variables": {},
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "10"},
                "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.pipeline_input}}"},
            },
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": None,
            "tags": {},
            "properties": {},
            "type": "command",
            "_source": "YAML.COMPONENT",
        }

        yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        yaml_component_version = load_component(source=yaml_path)
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        yaml_component = yaml_component_version(component_in_number=10, component_in_path=pipeline_input)

        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()

        assert expected_rest_component == rest_yaml_component

    def test_command_component_help_function(self):
        download_unzip_component = CommandComponent(
            name="download_and_unzip",
            version="0.0.1",
            # this component has no code, just a simple unzip command
            command="curl -o local_archive.zip ${{inputs.url}} && "
            "unzip local_archive.zip -d ${{outputs.extracted_data}}",
            # I/O specifications, each using a specific key and type
            inputs={
                # 'url' is the key of this input string
                "url": {"type": "string"}
            },
            outputs={
                # 'extracted_data' will be the key to link this output to other steps in the pipeline
                "extracted_data": {"type": "path"}
            },
            # we're using a curated environment
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:9",
        )
        basic_component = load_component(source="./tests/test_configs/components/basic_component_code_local_path.yml")
        sweep_component = load_component(source="./tests/test_configs/components/helloworld_component_for_sweep.yml")

        with patch("sys.stdout", new=StringIO()) as std_out:
            help(download_unzip_component._func)
            help(basic_component._func)
            help(sweep_component._func)
            assert "name: download_and_unzip" in std_out.getvalue()
            assert "name: sample_command_component_basic" in std_out.getvalue()
            assert "name: microsoftsamples_command_component_for_sweep" in std_out.getvalue()

        with patch("sys.stdout", new=StringIO()) as std_out:
            print(basic_component)
            print(download_unzip_component)
            print(sweep_component)
            assert (
                "name: sample_command_component_basic\nversion: '1'\ndisplay_name: CommandComponentBasic\n"
                in std_out.getvalue()
            )
            assert (
                "name: download_and_unzip\nversion: 0.0.1\ntype: command\ninputs:\n  url:\n    type: string\n"
                in std_out.getvalue()
            )
            assert "name: microsoftsamples_command_component_for_sweep\nversion: 0.0.1\n" in std_out.getvalue()

    def test_command_help_function(self):
        test_command = command(
            name="my-job",
            display_name="my-fancy-job",
            description="This is a fancy job",
            tags=dict(),
            command="python train.py --input-data ${{inputs.input_data}} --lr ${{inputs.learning_rate}}",
            code="./src",
            compute="cpu-cluster",
            environment="my-env:1",
            distribution=MpiDistribution(process_count_per_instance=4),
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

        with patch("sys.stdout", new=StringIO()) as std_out:
            print(test_command)
            outstr = std_out.getvalue()
            assert (
                "outputs:\n  my_model:\n    mode: rw_mount\n    type: mlflow_model\nenvironment: azureml:my-env:1\ncode: azureml:./src\nresources:\n  instance_count: 2"
                in outstr
            )

    def test_sweep_help_function(self):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        component_to_sweep: CommandComponent = load_component(source=yaml_file)
        cmd_node1: Command = component_to_sweep(
            component_in_number=Choice([2, 3, 4, 5]), component_in_path=Input(path="/a/path/on/ds")
        )

        sweep_job1: Sweep = cmd_node1.sweep(
            primary_metric="AUC",  # primary_metric,
            goal="maximize",
            sampling_algorithm="random",
        )
        sweep_job1.set_limits(max_total_trials=10)  # max_total_trials
        with patch("sys.stdout", new=StringIO()) as std_out:
            print(sweep_job1)
            assert (
                "name: microsoftsamples_command_component_basic\n  version: 0.0.1\n  display_name: CommandComponentBasi"
                in std_out.getvalue()
            )

    def test_invalid_component_inputs(self) -> None:
        yaml_path = "./tests/test_configs/components/invalid/helloworld_component_conflict_input_names.yml"
        component = load_component(yaml_path)
        with pytest.raises(ValidationException) as e:
            component._validate(raise_error=True)
        assert "Invalid component input names 'COMPONENT_IN_NUMBER' and 'component_in_number'" in str(e.value)
        component = load_component(
            yaml_path,
            params_override=[
                {"inputs": {"component_in_number": {"description": "1", "type": "number"}}},
            ],
        )
        validation_result = component._validate()
        assert validation_result.passed

        # user can still overwrite input name to illegal
        component.inputs["COMPONENT_IN_NUMBER"] = Input(description="1", type="number")
        validation_result = component._validate()
        assert not validation_result.passed
        assert "inputs.COMPONENT_IN_NUMBER" in validation_result.error_messages

    def test_primitive_output(self):
        expected_rest_component = {
            "command": "echo Hello World",
            "description": "This is the basic command component",
            "display_name": "CommandComponentBasic",
            "environment": "azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            "inputs": {},
            "is_deterministic": True,
            "name": "sample_command_component_basic",
            "outputs": {
                "component_out_boolean": {"description": "A boolean", "type": "boolean", "is_control": True},
                "component_out_integer": {"description": "A integer", "type": "integer", "is_control": True},
                "component_out_number": {"description": "A ranged number", "type": "number"},
                "component_out_string": {"description": "A string", "type": "string"},
            },
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "command",
            "version": "1",
        }
        omits = ["$schema", "_source", "code"]

        # from YAML
        yaml_path = "./tests/test_configs/components/helloworld_component_primitive_outputs.yml"
        component1 = load_component(yaml_path)
        actual_component_dict1 = pydash.omit(
            component1._to_rest_object().as_dict()["properties"]["component_spec"], *omits
        )

        assert actual_component_dict1 == expected_rest_component

        # from CLASS
        component2 = CommandComponent(
            name="sample_command_component_basic",
            display_name="CommandComponentBasic",
            description="This is the basic command component",
            version="1",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            outputs={
                "component_out_boolean": {"description": "A boolean", "type": "boolean", "is_control": True},
                "component_out_integer": {"description": "A integer", "type": "integer", "is_control": True},
                "component_out_number": {"description": "A ranged number", "type": "number"},
                "component_out_string": {"description": "A string", "type": "string"},
            },
            command="echo Hello World",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
            code="./helloworld_components_with_env",
        )
        actual_component_dict2 = pydash.omit(
            component2._to_rest_object().as_dict()["properties"]["component_spec"], *omits
        )
        assert actual_component_dict2 == expected_rest_component

    def test_component_code_asset_ignoring_pycache(self) -> None:
        component_yaml = "./tests/test_configs/components/basic_component_code_local_path.yml"
        component = load_component(component_yaml)
        code_folder = "./tests/test_configs/components/helloworld_components_with_env/"
        with tempfile.TemporaryDirectory(dir=code_folder) as tmp_dir:
            # create temp folder and write some files under pycache
            tmp_pycache_folder = Path(tmp_dir) / "__pycache__"
            tmp_pycache_folder.mkdir()
            (tmp_pycache_folder / "a.pyc").touch()
            (tmp_pycache_folder / "b.pyc").touch()
            # resolve and check if pycache exists in code asset
            with component._resolve_local_code() as code:
                pycache_path = Path(component_yaml).parent / code.path / Path(tmp_dir).name / "__pycache__"
                assert not pycache_path.exists()
