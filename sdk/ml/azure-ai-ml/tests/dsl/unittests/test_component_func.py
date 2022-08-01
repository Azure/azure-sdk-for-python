from typing import Union, Callable

import marshmallow
import pytest
from pathlib import Path
from azure.ai.ml import PyTorchDistribution, load_component
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutput
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities import Component as ComponentEntity, ResourceConfiguration, Data
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.pipeline._exceptions import UnexpectedKeywordError
from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml._ml_exceptions import ValidationException

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"
DATA_DIR = tests_root_dir / "test_configs/mldesigner_component_code_specified"


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestComponentFunc:
    def test_generate_component_function(self) -> None:
        component_func = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component = component_func()
        assert component.inputs.keys() == {"component_in_number", "component_in_path"}
        assert component.outputs.keys() == {"component_out_path"}
        assert component.component._source == "YAML.COMPONENT"

        component = component_func(component_in_number=10, component_in_path=Input(path="azureml:fake_path:1"))
        assert component._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": Input(path="azureml:fake_path:1"),
        }

        component.inputs.component_in_number = 20
        component.inputs.component_in_path = Input(path="another_path")
        assert component._build_inputs() == {
            "component_in_number": 20,
            "component_in_path": Input(path="another_path"),
        }

        # positional args is not allowed
        with pytest.raises(Exception) as error_info:
            component_func(10, "fake_path")
        assert "[component] CommandComponentBasic() takes 0 positional arguments but 2 were given" in str(error_info)

        # wrong kwargs is not allowed
        with pytest.raises(UnexpectedKeywordError) as error_info:
            component_func(wrong_kwarg=10)

        assert (
            "[component] CommandComponentBasic() got an unexpected keyword argument 'wrong_kwarg', "
            "valid keywords: 'component_in_number', 'component_in_path'." in str(error_info)
        )

    def test_required_component_inputs_missing(self):
        component_func = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component = component_func()

        # required input not provided
        with pytest.raises(ValidationException, match="Required input 'component_in_path'"):
            component._validate(raise_error=True)

    def test_component_inputs(self):
        component_func = load_component(path="./tests/test_configs/components/helloworld_component.yml")

        # set inputs via parameter
        test_job_input = Input(path="azureml:fake_data:1")
        component: Command = component_func(component_in_number=10, component_in_path=test_job_input)
        # change component's name otherwise a guid will be generated
        component.name = "microsoftsamplesCommandComponentBasic"
        assert component._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": test_job_input,
        }

        # set inputs via assignment
        component2: Command = component_func()
        component2.inputs.component_in_number = 10
        component2.inputs.component_in_path = test_job_input
        assert component2._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": test_job_input,
        }

        # set inputs via pipeline input binding
        with pytest.raises(ValidationException) as error_info:
            component2.inputs.component_in_path = component.inputs.component_in_path
        assert "Can not bind input to another component's input." in str(error_info)

        component2.inputs.component_in_path = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        assert component2._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": Input(path="${{parent.inputs.pipeline_input}}", type="uri_folder", mode=None),
        }

        # set inputs via component output binding
        component2.inputs.component_in_path = component.outputs.component_out_path
        assert component2._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": Input(
                path="${{parent.jobs.microsoftsamplesCommandComponentBasic.outputs.component_out_path}}",
                type="uri_folder",
                mode=None,
            ),
        }

        # configure inputs
        component.inputs.component_in_path.mode = "download"
        assert component._build_inputs() == {
            "component_in_number": 10,
            "component_in_path": Input(path="azureml:fake_data:1", mode="download"),
        }

        # default inputs
        component_entity = load_component(
            path="./tests/test_configs/components/helloworld_component_with_paths.yml",
            params_override=[
                {"inputs.component_in_path_1.optional": "True", "inputs.component_in_path_2.optional": "True"}
            ],
        )
        component_func = _generate_component_function(component_entity)
        component: Command = component_func(component_in_number=10)
        # un-configured inputs won't build
        assert component._build_inputs() == {
            "component_in_number": 10,
        }

        # when configuring mode, a default input will be built
        component.inputs.component_in_path_1.mode = "download"
        assert component._build_inputs() == {
            "component_in_number": 10,
            "component_in_path_1": Input(path=None, mode="download"),
        }

        component.inputs.component_in_path_2 = Input(
            type="uri_file", path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv"
        )
        # TODO need to define the behavior
        # assert component.inputs.component_in_path_2.type == "uri_file"
        assert (
            component.inputs.component_in_path_2.path
            == "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv"
        )

    def test_component_outputs(self):
        component_func = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component: Command = component_func()

        # un-configured output won't build
        assert component._build_outputs() == {}

        # configure mode and default Output is built
        component.outputs.component_out_path.mode = "upload"
        assert component._build_outputs() == {"component_out_path": Output(mode="upload")}

        # configure data
        component: Command = component_func()
        output_data = Output(dataset=Data(name="fakeData", version="1"))
        component.outputs.component_out_path = output_data
        assert component._build_outputs() == {"component_out_path": output_data}

        # set output via output binding
        component.outputs.component_out_path._data = PipelineOutput(name="pipeline_output", owner="pipeline", meta=None)
        assert component._build_outputs() == {
            "component_out_path": Output(path="${{parent.outputs.pipeline_output}}", type="uri_folder", mode=None)
        }

    @pytest.mark.parametrize(
        "component_path, expected",
        [
            ("./tests/test_configs/components/invalid/unsupported_fields.yml", lambda x: True),
            ("./tests/test_configs/components/component_no_version.yml", lambda x: x.version is None),
            ("./tests/test_configs/components/invalid/empty.yml", "Target yaml file is empty"),
            (
                "./tests/test_configs/components/invalid/non_dict.yml",
                "Expect dict but get <class 'str'> after parsing yaml file",
            ),
            ("./tests/test_configs/components/invalid/name_none.yml", "{'name': ['Field may not be null.']}"),
            (
                "./tests/test_configs/components/invalid/no_environment.yml",
                "{'environment': ['Missing data for required field.']}",
            ),
            ("./tests/test_configs/components/invalid/error_format.yml", "Error while parsing yaml file"),
        ],
    )
    def test_invalid_component(self, component_path: str, expected: Union[str, Callable]):
        if isinstance(expected, str):
            with pytest.raises(Exception) as error_info:
                load_component(path=component_path)
            assert expected in str(error_info)
        else:
            component = load_component(path=component_path)
            assert expected(component)

    def test_component_str(self):
        component_entity = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component_func = _generate_component_function(component_entity)

        test_data_object = Input(path="azureml:fake_data:1")
        component: Command = component_func(component_in_number=10, component_in_path=test_data_object)
        component_str = str(component)
        assert "component_in_number: 10" in component_str

        component: Command = component_func()
        # unprovided inputs won't be in str
        assert "inputs: {}" in str(component)

    def test_component_static_dynamic_fields(self):
        component_entity = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component_func = _generate_component_function(component_entity)

        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        component: Command = component_func(component_in_number=10, component_in_path=pipeline_input)

        # set static fields
        component.resources = ResourceConfiguration()
        component.resources.instance_count = 2
        component.distribution = PyTorchDistribution()
        component.distribution.process_count_per_instance = 2
        component.environment_variables["key"] = "val"
        # user can set these fields but we won't pass to backend
        # TODO: Agree on if we should allow this
        # component.command = "new command"
        component.environment = "new environment"

        # set dynamic fields
        component.field1 = 1
        component.field_group.field2 = "filed"

        component._component = "fake_arm_id"
        assert component._to_rest_object() == {
            "_source": "REMOTE.WORKSPACE.COMPONENT",
            "componentId": "fake_arm_id",
            "computeId": None,
            "display_name": None,
            "distribution": {"distribution_type": "PyTorch", "process_count_per_instance": 2},
            "environment_variables": {"key": "val"},
            "field1": 1,
            "field_group": {"field2": "filed"},
            "inputs": {
                "component_in_number": {"job_input_type": "Literal", "value": "10"},
                "component_in_path": {"job_input_type": "Literal", "value": "${{parent.inputs.pipeline_input}}"},
            },
            "limits": None,
            "name": None,
            "outputs": {},
            "resources": {"instance_count": 2, "properties": {}},
            "tags": {},
        }

    def test_component_func_dict_distribution(self):
        component_entity = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        component_func = _generate_component_function(component_entity)

        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)
        component: Command = component_func(component_in_number=10, component_in_path=pipeline_input)

        expected_distribution = {"distribution_type": "PyTorch", "process_count_per_instance": 2}

        # set dict distribution
        component.distribution = {"type": "Pytorch", "process_count_per_instance": 2}
        assert component._to_rest_object()["distribution"] == expected_distribution

        # set object distribution
        component.distribution = PyTorchDistribution()
        component.distribution.process_count_per_instance = 2
        assert component._to_rest_object()["distribution"] == expected_distribution

    def test_component_func_default_distribution_resources(self):
        pipeline_input = PipelineInput(name="pipeline_input", owner="pipeline", meta=None)

        mpi_func = load_component(path=str(components_dir / "helloworld_component_mpi.yml"))
        mpi_node = mpi_func(component_in_number=10, component_in_path=pipeline_input)
        assert mpi_node._to_rest_object()["distribution"] == {
            "distribution_type": "Mpi",
            "process_count_per_instance": 1,
        }
        assert mpi_node._to_rest_object()["resources"] == {"instance_count": 2, "properties": {}}

        pytorch_func = load_component(path=str(components_dir / "helloworld_component_pytorch.yml"))
        pytorch_node = pytorch_func(component_in_number=10, component_in_path=pipeline_input)
        assert pytorch_node._to_rest_object()["distribution"] == {
            "distribution_type": "PyTorch",
            "process_count_per_instance": 4,
        }
        assert pytorch_node._to_rest_object()["resources"] == {"instance_count": 2, "properties": {}}

        tensorflow_func = load_component(path=str(components_dir / "helloworld_component_tensorflow.yml"))
        tensorflow_node = tensorflow_func(component_in_number=10, component_in_path=pipeline_input)
        assert tensorflow_node._to_rest_object()["distribution"] == {
            "distribution_type": "TensorFlow",
            "parameter_server_count": 1,
            "worker_count": 2,
        }
        assert tensorflow_node._to_rest_object()["resources"] == {"instance_count": 2, "properties": {}}

    def test_component_invalid_convert(self):
        component = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        base_rest_obj, base_dict = component._to_rest_object(), component._to_dict()
        invalid_name = "invalid-name"
        component.name = invalid_name
        assert not component._validate().passed
        cmp_rest_obj, cmp_dict = component._to_rest_object(), component._to_dict()
        base_dict["name"] = invalid_name
        base_rest_obj.name, base_rest_obj.properties.component_spec["name"] = invalid_name, invalid_name
        assert cmp_dict == base_dict
        assert cmp_rest_obj.as_dict() == base_rest_obj.as_dict()
