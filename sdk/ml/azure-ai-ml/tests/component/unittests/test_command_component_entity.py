import enum
import os
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pydash
import pytest
from test_utilities.utils import (
    build_temp_folder,
    mock_artifact_download_to_temp_directory,
    verify_entity_load_and_dump,
)

from azure.ai.ml import Input, MpiDistribution, Output, TensorFlowDistribution, command, load_component
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities import CommandComponent, CommandJobLimits, Component, JobResourceConfiguration
from azure.ai.ml.entities._assets import Code, Environment
from azure.ai.ml.entities._builders import Command, Sweep
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.exceptions import UnexpectedKeywordError, ValidationException
from azure.ai.ml.sweep import Choice
from conftest import normalized_arm_id_in_object

from .._util import _COMPONENT_TIMEOUT_SECOND


class AdditionalIncludesCheckFunc(enum.Enum):
    """Enum for additional includes check function"""

    SKIP = 0
    SELF_IS_FILE = 1
    PARENT_EXISTS = 2
    NOT_EXISTS = 3
    NO_PARENT = 4


@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
@pytest.mark.usefixtures("enable_private_preview_schema_features")
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
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        component_dict = component._to_rest_object().as_dict()
        omits = [
            "properties.component_spec.$schema",
            "properties.component_spec._source",
            "properties.properties.client_component_hash",
        ]
        component_dict = pydash.omit(component_dict, *omits)

        yaml_path = "./tests/test_configs/components/basic_component_code_arm_id.yml"
        yaml_component = load_component(source=yaml_path)
        yaml_component_dict = yaml_component._to_rest_object().as_dict()
        yaml_component_dict = pydash.omit(yaml_component_dict, *omits)

        assert component_dict == yaml_component_dict

    def test_command_component_with_additional_includes(self):
        tests_root_dir = Path(__file__).parent.parent.parent
        samples_dir = tests_root_dir / "test_configs/components/"
        with mock_artifact_download_to_temp_directory():
            component = CommandComponent(
                name="additional_files",
                description="A sample to demonstrate component with additional files",
                version="0.0.1",
                command="echo Hello World",
                environment=Environment(image="zzn2/azureml_sdk"),
                # as sdk will take working directory as root folder, so we need to specify the absolution path
                additional_includes=[
                    str(samples_dir / "additional_includes/assets/LICENSE"),
                    str(samples_dir / "additional_includes/library.zip"),
                    str(samples_dir / "additional_includes/library1"),
                ],
            )
            component.additional_includes.append(
                {
                    "type": "artifact",
                    "organization": "https://msdata.visualstudio.com/",
                    "project": "Vienna",
                    "feed": "component-sdk-test-feed",
                    "name": "test_additional_include",
                    "version": "version_2",
                    "scope": "project",
                }
            )
            assert component._validate().passed, repr(component._validate())
            with component._build_code() as code:
                code_path: Path = code.path
                assert code_path.is_dir()
                assert (code_path / "LICENSE").is_file()
                assert (code_path / "library.zip").is_file()
                assert ZipFile(code_path / "library.zip").namelist() == [
                    "library/",
                    "library/hello.py",
                    "library/world.py",
                ]
                assert (code_path / "library1" / "hello.py").is_file()
                assert (code_path / "library1" / "world.py").is_file()
                assert (code_path / "file_version_2").is_file()
                assert (code_path / "version_2" / "file").is_file()

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
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
            "properties.properties.client_component_hash",
        )
        yaml_component_dict = pydash.omit(
            yaml_component_dict,
            "properties.component_spec.$schema",
            "properties.component_spec.distribution.added_property",
            "properties.component_spec.resources.properties",
            "properties.component_spec._source",
            "properties.properties.client_component_hash",
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
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
            with component._build_code() as code:
                Path(code.path).resolve().name == "components"
        finally:
            os.chdir(old_cwd)

    def test_command_component_code_git_path(self):
        from azure.ai.ml.operations._component_operations import _try_resolve_code_for_component

        yaml_path = "./tests/test_configs/components/component_git_path.yml"
        yaml_dict = load_yaml(yaml_path)
        component = load_component(yaml_path)

        def mock_get_arm_id_and_fill_back(asset: Code, azureml_type: str) -> None:
            assert isinstance(asset, Code)
            assert azureml_type == AzureMLResourceType.CODE
            assert asset.path == yaml_dict["code"]

        _try_resolve_code_for_component(component, mock_get_arm_id_and_fill_back)

    @pytest.mark.skipif(
        sys.version_info[1] == 11,
        reason=f"This test is not compatible with Python 3.11, skip in CI.",
    )
    def test_command_component_version_as_a_function(self):
        expected_rest_component = {
            "componentId": "fake_component",
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
        with pytest.raises(ValidationException) as error_info:
            yaml_component_version(1)
        assert "Component function doesn't has any parameters" in str(error_info)

        # unknown kw arg
        with pytest.raises(UnexpectedKeywordError) as error_info:
            yaml_component_version(unknown=1)
        assert "[component] CommandComponentBasic() got an unexpected keyword argument 'unknown'." in str(error_info)

    def test_command_component_version_as_a_function_with_inputs(self):
        expected_rest_component = {
            "componentId": "fake_component",
            "inputs": {
                "component_in_number": {"job_input_type": "literal", "value": "10"},
                "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.pipeline_input}}"},
            },
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
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
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
            for piece in [
                "outputs:\n  my_model:\n    mode: rw_mount\n    type: mlflow_model\n",
                "environment: azureml:my-env:1\n",
                "code: azureml:./src\n",
                "resources:\n  instance_count: 2",
            ]:
                assert piece in outstr

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

    def test_sweep_early_termination_setter(self):
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
        sweep_job1.early_termination = {
            "type": "bandit",
            "evaluation_interval": 100,
            "delay_evaluation": 200,
            "slack_factor": 40.0,
        }
        from azure.ai.ml.entities._job.sweep.early_termination_policy import BanditPolicy

        assert isinstance(sweep_job1.early_termination, BanditPolicy)
        assert [
            sweep_job1.early_termination.evaluation_interval,
            sweep_job1.early_termination.delay_evaluation,
            sweep_job1.early_termination.slack_factor,
        ] == [100, 200, 40.0]

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
            "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            "is_deterministic": True,
            "name": "sample_command_component_basic",
            "outputs": {
                "component_out_boolean": {"description": "A boolean", "type": "boolean"},
                "component_out_integer": {"description": "A integer", "type": "integer"},
                "component_out_number": {"description": "A ranged number", "type": "number"},
                "component_out_string": {"description": "A string", "type": "string"},
                "component_out_early_available_string": {
                    "description": "A early available string",
                    "type": "string",
                    "early_available": True,
                },
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
                "component_out_early_available_string": {
                    "description": "A early available string",
                    "type": "string",
                    "is_control": True,
                    "early_available": True,
                },
            },
            command="echo Hello World",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./helloworld_components_with_env",
        )
        actual_component_dict2 = pydash.omit(
            component2._to_rest_object().as_dict()["properties"]["component_spec"], *omits
        )
        assert actual_component_dict2 == expected_rest_component

    def test_invalid_component_outputs(self) -> None:
        yaml_path = "./tests/test_configs/components/invalid/helloworld_component_invalid_early_available_output.yml"
        component = load_component(yaml_path)
        params_override = [
            {
                "outputs": {
                    "component_out_string": {
                        "description": "A string",
                        "type": "string",
                        "is_control": True,
                        "early_available": True,
                    }
                }
            },
        ]
        component = load_component(yaml_path, params_override=params_override)
        validation_result = component._validate()
        assert validation_result.passed

    def test_component_code_asset_ignoring_pycache(self) -> None:
        component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        component = load_component(component_yaml)
        with build_temp_folder(
            source_base_dir="./tests/test_configs/components",
            relative_files_to_copy=["helloworld_component.yml"],
            extra_files_to_create={"__pycache__/a.pyc": None},
        ) as temp_dir:
            # resolve and test for ignore_file's is_file_excluded
            component.code = temp_dir
            with component._build_code() as code:
                excluded = []
                for root, _, files in os.walk(code.path):
                    for name in files:
                        path = os.path.join(root, name)
                        if code._ignore_file.is_file_excluded(path):
                            excluded.append(path)
                # use samefile to avoid windows path auto shortening issue
                assert len(excluded) == 1
                assert os.path.isabs(excluded[0])
                assert Path(excluded[0]).samefile((Path(temp_dir) / "__pycache__/a.pyc"))

    def test_normalized_arm_id_in_component_dict(self):
        component_dict = {
            "code": "azureml:/subscriptions/123ABC_+-=/resourceGroups/123ABC_+-=/providers/Microsoft.MachineLearningServices/workspaces/123ABC_+-=/codes/xxx",
            "environment": "azureml:/subscriptions/123ABC_+-=/resourceGroups/123ABC_+-=/providers/Microsoft.MachineLearningServices/workspaces/123ABC_+-=/environments/xxx",
        }
        normalized_arm_id_in_object(component_dict)

        expected_dict = {
            "code": "azureml:/subscriptions/00000000-0000-0000-0000-000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/codes/xxx",
            "environment": "azureml:/subscriptions/00000000-0000-0000-0000-000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/environments/xxx",
        }
        assert component_dict == expected_dict

    @pytest.mark.usefixtures("enable_private_preview_schema_features")
    def test_component_with_ipp_fields(self):
        # code is specified in yaml, value is respected
        component_yaml = "./tests/test_configs/components/component_ipp.yml"

        command_component = load_component(
            source=component_yaml,
        )

        expected_output_dict = {
            "model_output_not_ipp": {
                "type": "path",
                "intellectual_property": {"protection_level": "none"},
            },
            "model_output_ipp": {
                "type": "path",
                "intellectual_property": {"protection_level": "all"},
            },
        }
        expected_training_data_input_dict = {
            "type": "path",
            "optional": False,
            "intellectual_property": {"protection_level": "none"},
        }

        # check top-level component
        assert command_component._intellectual_property
        assert command_component._intellectual_property.publisher == "contoso"
        assert command_component._intellectual_property.protection_level == "all"

        rest_component = command_component._to_rest_object()

        assert rest_component.properties.component_spec["intellectualProperty"]
        assert rest_component.properties.component_spec["intellectualProperty"] == {
            "publisher": "contoso",
            "protectionLevel": "all",
        }
        assert rest_component.properties.component_spec["outputs"] == expected_output_dict

        assert rest_component.properties.component_spec["inputs"]["training_data"] == expected_training_data_input_dict

        # because there's a mismatch between what the service accepts for IPP fields and what it returns
        # (accepts camelCase for IPP, returns snake_case IPP), mock out the service response

        rest_component.properties.component_spec.pop("intellectualProperty")
        yaml_dict = {
            "publisher": "contoso",
            "protection_level": "all",
        }
        rest_component.properties.component_spec["intellectual_property"] = yaml_dict

        from_rest_dict = Component._from_rest_object(rest_component)._to_dict()
        assert from_rest_dict["intellectual_property"]
        assert from_rest_dict["intellectual_property"] == yaml_dict
        assert from_rest_dict["outputs"] == expected_output_dict
        assert from_rest_dict["inputs"]["training_data"] == expected_training_data_input_dict

    def test_additional_includes(self) -> None:
        yaml_path = (
            "./tests/test_configs/components/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        component = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._build_code() as code:
            code_path: Path = code.path
            assert code_path.is_dir()
            assert (code_path / "LICENSE").is_file()
            assert (code_path / "library.zip").is_file()
            assert ZipFile(code_path / "library.zip").namelist() == ["library/", "library/hello.py", "library/world.py"]
            assert (code_path / "library1" / "hello.py").is_file()
            assert (code_path / "library1" / "world.py").is_file()

    @pytest.mark.parametrize(
        "test_files",
        [
            pytest.param(
                [
                    (
                        "component_with_additional_includes/.amlignore",
                        "test_ignore/*\nlibrary1/ignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "component_with_additional_includes/test_ignore/a.py",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    ("additional_includes/library1/ignore.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                    # will be saved to library1/test_ignore, should be kept
                    ("additional_includes/library1/test_ignore/a.py", None, AdditionalIncludesCheckFunc.SELF_IS_FILE),
                ],
                id="amlignore",
            ),
            pytest.param(
                [
                    ("component_with_additional_includes/hello.py", None, AdditionalIncludesCheckFunc.SELF_IS_FILE),
                    (
                        "component_with_additional_includes/test_code/.amlignore",
                        "hello.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    (
                        "component_with_additional_includes/test_code/hello.py",
                        None,
                        AdditionalIncludesCheckFunc.NOT_EXISTS,
                    ),
                    # shall we keep the empty folder?
                    (
                        "component_with_additional_includes/test_code/a/hello.py",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                ],
                id="amlignore_subfolder",
            ),
            pytest.param(
                [
                    (
                        "additional_includes/library1/.amlignore",
                        "test_ignore\nignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    ("additional_includes/library1/ignore.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                    # will be saved to library1/test_ignore, should be kept
                    ("additional_includes/library1/test_ignore/a.py", None, AdditionalIncludesCheckFunc.NOT_EXISTS),
                ],
                id="amlignore_in_additional_includes_folder",
            ),
            pytest.param(
                [
                    (
                        "additional_includes/library1/test_ignore/.amlignore",
                        "ignore.py",
                        AdditionalIncludesCheckFunc.SELF_IS_FILE,
                    ),
                    # will be saved to library1/ignore.py, should be ignored
                    (
                        "additional_includes/library1/test_ignore/ignore.py",
                        None,
                        AdditionalIncludesCheckFunc.NOT_EXISTS,
                    ),
                ],
                id="amlignore_in_additional_includes_subfolder",
            ),
            pytest.param(
                [
                    (
                        "component_with_additional_includes/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    (
                        "component_with_additional_includes/test/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                    ("additional_includes/library1/__pycache__/a.pyc", None, AdditionalIncludesCheckFunc.NO_PARENT),
                    (
                        "additional_includes/library1/test/__pycache__/a.pyc",
                        None,
                        AdditionalIncludesCheckFunc.NO_PARENT,
                    ),
                ],
                id="pycache",
            ),
        ],
    )
    def test_additional_includes_with_ignore_file(self, test_files) -> None:
        with build_temp_folder(
            source_base_dir="./tests/test_configs/components/",
            relative_dirs_to_copy=["component_with_additional_includes", "additional_includes"],
            extra_files_to_create={file: content for file, content, _ in test_files},
        ) as test_configs_dir:
            yaml_path = (
                Path(test_configs_dir)
                / "component_with_additional_includes"
                / "code_and_additional_includes"
                / "component_spec.yml"
            )

            component = load_component(source=yaml_path)

            # resolve and check snapshot directory
            with component._build_code() as code:
                for file, content, check_func in test_files:
                    # original file is based on test_configs_dir, need to remove the leading
                    # "component_with_additional_includes" or "additional_includes" to get the relative path
                    resolved_file_path = Path(os.path.join(code.path, *Path(file).parts[1:]))
                    if check_func == AdditionalIncludesCheckFunc.NO_PARENT:
                        assert not resolved_file_path.parent.exists(), f"{file} should not have parent"
                    elif check_func == AdditionalIncludesCheckFunc.SELF_IS_FILE:
                        assert resolved_file_path.is_file(), f"{file} is not a file"
                        if content is not None:
                            assert resolved_file_path.read_text() == content, f"{file} content is not expected"
                    elif check_func == AdditionalIncludesCheckFunc.PARENT_EXISTS:
                        assert resolved_file_path.parent.is_dir(), f"{file} should have parent"
                    elif check_func == AdditionalIncludesCheckFunc.NOT_EXISTS:
                        assert not resolved_file_path.exists(), f"{file} should not exist"
                    elif check_func == AdditionalIncludesCheckFunc.SKIP:
                        pass
                    else:
                        raise ValueError(f"Unknown check func: {check_func}")

    def test_additional_includes_merge_folder(self) -> None:
        yaml_path = (
            "./tests/test_configs/components/component_with_additional_includes/additional_includes_merge_folder.yml"
        )
        component = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        with component._build_code() as code:
            code_path = code.path
            # first folder
            assert (code_path / "library1" / "__init__.py").is_file()
            assert (code_path / "library1" / "hello.py").is_file()
            # second folder content
            assert (code_path / "library1" / "utils").is_dir()
            assert (code_path / "library1" / "utils" / "__init__.py").is_file()
            assert (code_path / "library1" / "utils" / "salute.py").is_file()

    @pytest.mark.parametrize(
        "yaml_path,has_additional_includes",
        [
            # ("code_only/component_spec.yml", False),
            ("code_and_additional_includes/component_spec.yml", True),
        ],
    )
    def test_additional_includes_with_code_specified(self, yaml_path: str, has_additional_includes: bool) -> None:
        yaml_path = os.path.join("./tests/test_configs/components/component_with_additional_includes/", yaml_path)
        component = load_component(source=yaml_path)
        assert component._validate().passed, repr(component._validate())
        # resolve
        with component._build_code() as code:
            code_path = code.path
            assert code_path.is_dir()
            if has_additional_includes:
                # additional includes is specified, code will be tmp folder and need to check each item
                # manually list here to avoid temp folder like __pycache__ breaking test.
                for path in [
                    "additional_includes_merge_folder.yml",
                    "code_and_additional_includes",
                    "code_only",
                    "helloworld_additional_includes.yml",
                    "helloworld_invalid_additional_includes_existing_file.yml",
                    "helloworld_invalid_additional_includes_root_directory.yml",
                    "helloworld_invalid_additional_includes_zip_file_not_found.yml",
                ]:
                    assert (code_path / path).is_file() if ".yml" in path else (code_path / path).is_dir()
                assert (code_path / "LICENSE").is_file()
            else:
                # additional includes not specified, code should be specified path (default yaml folder)
                yaml_dict = load_yaml(yaml_path)
                specified_code_path = Path(yaml_path).parent / yaml_dict.get("code", "./")
                assert code_path.resolve() == specified_code_path.resolve()

    def test_artifacts_in_additional_includes(self):
        with mock_artifact_download_to_temp_directory():
            yaml_path = "./tests/test_configs/components/component_with_additional_includes/with_artifacts.yml"
            component = load_component(source=yaml_path)
            assert component._validate().passed, repr(component._validate())
            with component._build_code() as code:
                code_path = code.path
                assert code_path.is_dir()
                for path in [
                    "version_1/",
                    "version_1/file",
                    "version_2/",
                    "version_2/file",
                    "file_version_1",
                    "file_version_2",
                    "DockerFile",
                ]:
                    assert (code_path / path).exists()

            yaml_path = (
                "./tests/test_configs/components/component_with_additional_includes/"
                "artifacts_additional_includes_with_conflict.yml"
            )
            component = load_component(source=yaml_path)
            with pytest.raises(
                RuntimeError,
                match="There are conflict files in additional include"
                ".*test_additional_include:version_1 in component-sdk-test-feed"
                ".*test_additional_include:version_3 in component-sdk-test-feed",
            ):
                with component._build_code():
                    pass

    @pytest.mark.parametrize(
        "yaml_path,expected_error_msg_prefix",
        [
            pytest.param(
                "helloworld_invalid_additional_includes_root_directory.yml",
                "Root directory is not supported for additional includes",
                id="root_as_additional_includes",
            ),
            pytest.param(
                "helloworld_invalid_additional_includes_existing_file.yml",
                "A file already exists for additional include",
                id="file_already_exists",
            ),
            pytest.param(
                "helloworld_invalid_additional_includes_zip_file_not_found.yml",
                "Unable to find additional include ../additional_includes/assets/LICENSE.zip",
                id="zip_file_not_found",
            ),
        ],
    )
    def test_invalid_additional_includes(self, yaml_path: str, expected_error_msg_prefix: str) -> None:
        component = load_component(
            os.path.join("./tests/test_configs/components/component_with_additional_includes", yaml_path)
        )
        validation_result = component._validate()
        assert validation_result.passed is False
        assert validation_result.error_messages["additional_includes"].startswith(expected_error_msg_prefix)
