import pydash
import pytest
from unittest.mock import patch
from io import StringIO

from azure.ai.ml import command, MpiDistribution, Input, Output, load_component
from azure.ai.ml._restclient.v2022_05_01.models import TensorFlow
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities import (
    Component,
    CommandComponent,
    ResourceConfiguration,
    CommandJobLimits,
)
from azure.ai.ml.sweep import Choice
from azure.ai.ml.entities._job.pipeline._exceptions import UnexpectedKeywordError
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._builders import Command, Sweep


@pytest.mark.unittest
class TestCommandComponentEntity:
    def test_component_load(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/components/basic_component_code_local_path.yml"
        command_component = load_component(
            path=component_yaml,
        )
        assert command_component.code == "./helloworld_components_with_env"
        component_yaml = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        command_component = load_component(
            path=component_yaml,
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
        component_dict = pydash.omit(component_dict, "properties.component_spec.$schema")

        yaml_path = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        yaml_component = load_component(path=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, "properties.component_spec.$schema")

        assert component_dict == yaml_component_dict

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
            distribution=TensorFlow(
                parameter_server_count=1,
                worker_count=2,
                # No affect because TensorFlow object does not allow extra fields
                added_property=7,
            ),
            instance_count=2,
        )
        component_dict = component._to_rest_object().as_dict()

        yaml_path = "./tests/test_configs/components/helloworld_component_tensorflow.yml"
        yaml_component = load_component(path=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()

        component_dict = pydash.omit(
            component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.distribution.added_property",
            "properties.component_spec.resources.properties",
        )
        yaml_component_dict = pydash.omit(
            yaml_component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.distribution.added_property",
            "properties.component_spec.resources.properties",
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
        yaml_component = load_component(path=yaml_path)
        assert component.code == yaml_component.code

    def test_command_component_version_as_a_function(self):
        expected_rest_component = {
            "componentId": "fake_component",
            "computeId": None,
            "display_name": None,
            "distribution": None,
            "environment_variables": {},
            "inputs": {},
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": None,
            "tags": {},
        }

        yaml_path = "./tests/test_configs/components/basic_component_code_local_path.yml"
        yaml_component_version = load_component(path=yaml_path)
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
                "component_in_number": {"job_input_type": "Literal", "value": "10"},
                "component_in_path": {"job_input_type": "Literal", "value": "${{parent.inputs.pipeline_input}}"},
            },
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": None,
            "tags": {},
        }

        yaml_path = "./tests/test_configs/components/helloworld_component.yml"
        yaml_component_version = load_component(path=yaml_path)
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        yaml_component = yaml_component_version(component_in_number=10, component_in_path=pipeline_input)

        yaml_component._component = "fake_component"
        rest_yaml_component = yaml_component._to_rest_object()
        print(rest_yaml_component)
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
        basic_component = load_component(path="./tests/test_configs/components/basic_component_code_local_path.yml")
        sweep_component = load_component(path="./tests/test_configs/components/helloworld_component_for_sweep.yml")

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
            resources=ResourceConfiguration(instance_count=2, instance_type="STANDARD_D2"),
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
                "outputs:\n  my_model:\n    mode: rw_mount\n    type: mlflow_model\ncommand: python train.py --input-data ${{inputs.input_data}} --lr ${{inputs.learning_rate}}\n"
                in outstr
            )

    def test_sweep_help_function(self):
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        component_to_sweep: CommandComponent = load_component(path=yaml_file)
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
