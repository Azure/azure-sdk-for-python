import re
import pydash
import pytest
from marshmallow import ValidationError

from azure.ai.ml import command, Input, Output, MpiDistribution, PyTorchDistribution, TensorFlowDistribution, load_job
from azure.ai.ml._ml_exceptions import JobException, ValidationException
from azure.ai.ml.entities import CommandJobLimits, ResourceConfiguration, PipelineJob
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestCommandFunction:
    @pytest.fixture
    def test_command_params(self) -> dict:
        return dict(
            name="my_job",
            display_name="my-fancy-job",
            description="This is a fancy job",
            tags=dict(),
            command="python train.py --input-data ${{inputs.uri_folder}} --lr ${{inputs.float}}",
            # code folder need to exist in current working directory
            code="./tests",
            compute="cpu-cluster",
            environment="my-env:1",
            distribution=MpiDistribution(process_count_per_instance=4),
            environment_variables=dict(foo="bar"),
            # Customers can still do this:
            # resources=Resources(instance_count=2, instance_type="STANDARD_D2"),
            # limits=Limits(timeout=300),
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

    @pytest.fixture
    def test_command(self, test_command_params):
        return command(**test_command_params)

    @pytest.fixture
    def test_no_deterministic_command(self, test_command_params):
        return command(**test_command_params, is_deterministic=False)

    @pytest.fixture
    def command_with_artifact_inputs(self):
        return command(
            name="my_job",
            display_name="my-fancy-job",
            description="This is a fancy job",
            tags=dict(),
            command="python train.py --input-data ${{inputs.uri_folder}} --lr ${{inputs.float}}",
            # code folder need to exist in current working directory
            code="./tests",
            compute="cpu-cluster",
            environment="my-env:1",
            distribution=MpiDistribution(process_count_per_instance=4),
            environment_variables=dict(foo="bar"),
            # Customers can still do this:
            # resources=Resources(instance_count=2, instance_type="STANDARD_D2"),
            # limits=Limits(timeout=300),
            inputs={
                "float": Input(type="number", default=1.1, min=0, max=5),
                "integer": Input(type="integer", default=2, min=-1, max=4),
                "string": Input(type="string", default="default_str"),
                "boolean": Input(type="boolean", default=False),
                "uri_folder": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
                "uri_file": Input(type="uri_file", path="https://my-blob/path/to/data", mode="download"),
            },
            outputs={"my_model": Output(type="mlflow_model")},
        )

    def test_command_function(self, test_command):
        assert isinstance(test_command, Command)
        assert test_command._source == "BUILDER"
        expected_command = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "Literal", "value": "False"},
                "float": {"job_input_type": "Literal", "value": "0.01"},
                "integer": {"job_input_type": "Literal", "value": "1"},
                "string": {"job_input_type": "Literal", "value": "str"},
                "uri_file": {"job_input_type": "UriFile", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "UriFolder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": None,
            "name": "my_job",
            "outputs": {"my_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}},
            "resources": None,
            "tags": {},
        }
        actual_command = pydash.omit(
            test_command._to_rest_object(),
            "componentId",
        )
        assert actual_command == expected_command

        # distribution goes here
        expected_component = {
            "properties": {
                "component_spec": {
                    "_source": "BUILDER",
                    "code": "./tests",
                    "description": "This is a fancy job",
                    "command": "python train.py --input-data " "${{inputs.uri_folder}} --lr " "${{inputs.float}}",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "inputs": {
                        "boolean": {"default": "False", "type": "boolean"},
                        "float": {"default": "0.01", "type": "number"},
                        "integer": {"default": "1", "type": "integer"},
                        "string": {"default": "str", "type": "string"},
                        "uri_file": {"type": "uri_file"},
                        "uri_folder": {"type": "uri_folder"},
                    },
                    "is_deterministic": True,
                    "outputs": {"my_model": {"type": "mlflow_model"}},
                    "tags": {},
                    "type": "command",
                },
                "description": "This is a fancy job",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {},
                "tags": {},
            }
        }
        actual_component = pydash.omit(
            test_command._component._to_rest_object().as_dict(), "name", "properties.component_spec.name"
        )
        assert actual_component == expected_component

    def test_no_deterministic_command_function(self, test_no_deterministic_command):
        assert isinstance(test_no_deterministic_command, Command)
        assert test_no_deterministic_command._source == "BUILDER"

        expected_component = {
            "properties": {
                "component_spec": {
                    "_source": "BUILDER",
                    "code": "./tests",
                    "description": "This is a fancy job",
                    "command": "python train.py --input-data " "${{inputs.uri_folder}} --lr " "${{inputs.float}}",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "inputs": {
                        "boolean": {"default": "False", "type": "boolean"},
                        "float": {"default": "0.01", "type": "number"},
                        "integer": {"default": "1", "type": "integer"},
                        "string": {"default": "str", "type": "string"},
                        "uri_file": {"type": "uri_file"},
                        "uri_folder": {"type": "uri_folder"},
                    },
                    "is_deterministic": False,
                    "outputs": {"my_model": {"type": "mlflow_model"}},
                    "tags": {},
                    "type": "command",
                },
                "description": "This is a fancy job",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {},
                "tags": {},
            }
        }
        actual_component = pydash.omit(
            test_no_deterministic_command._component._to_rest_object().as_dict(),
            "name",
            "properties.component_spec.name",
        )
        assert actual_component == expected_component

    def test_command_function_set_inputs(self, test_command):
        test_data = Input(type="uri_folder", path="https://my-blob/path/to/data", mode="download")
        # Command can be called as a function, returning a new Component instance
        node1 = test_command(uri_folder=test_data, float=0.02)
        node2 = test_command(uri_folder=test_data, float=0.02)
        # Result Command instance can be called again to get another instance
        node3 = node2(uri_folder=test_data, float=0.02)
        assert id(test_command) != id(node1)
        assert isinstance(node1, Command)
        assert id(node1) != id(node2)
        assert id(node2) != id(node3)
        assert isinstance(node3, Command)

        # All nodes with same parameter will be translate to same dict
        original_dict = test_command._to_rest_object()
        node1_dict = node1._to_rest_object()
        node2_dict = node2._to_rest_object()
        node3_dict = node3._to_rest_object()
        assert original_dict != node1_dict
        assert node1_dict == node2_dict
        assert node2_dict == node3_dict

        expected_dict = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "Literal", "value": "False"},
                "float": {"job_input_type": "Literal", "value": "0.02"},
                "integer": {"job_input_type": "Literal", "value": "1"},
                "string": {"job_input_type": "Literal", "value": "str"},
                "uri_file": {"job_input_type": "UriFile", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "UriFolder",
                    "mode": "Download",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": None,
            "outputs": {"my_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}},
            "resources": None,
            "name": None,
            "tags": {},
        }
        actual_dict = pydash.omit(
            node1_dict,
            "componentId",
        )
        assert actual_dict == expected_dict

    def test_command_function_default_values(self, test_command):
        node1 = test_command()
        node1_dict = pydash.omit(
            node1._to_rest_object(),
            "componentId",
        )
        expected_dict = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "Literal", "value": "False"},
                "float": {"job_input_type": "Literal", "value": "0.01"},
                "integer": {"job_input_type": "Literal", "value": "1"},
                "string": {"job_input_type": "Literal", "value": "str"},
                "uri_file": {"job_input_type": "UriFile", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "UriFolder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": None,
            "outputs": {"my_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}},
            "resources": None,
            "name": None,
            "tags": {},
        }
        # node1 copies test_command's dict
        assert node1_dict == expected_dict

        node2 = node1(float=0.02)
        node2.compute = "new-cluster"
        node2.limits = CommandJobLimits(timeout=10)
        node3 = node2()
        node3_dict = pydash.omit(
            node3._to_rest_object(),
            "componentId",
        )
        expected_dict = {
            "_source": "BUILDER",
            "computeId": "new-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "Literal", "value": "False"},
                "float": {"job_input_type": "Literal", "value": "0.02"},
                "integer": {"job_input_type": "Literal", "value": "1"},
                "string": {"job_input_type": "Literal", "value": "str"},
                "uri_file": {"job_input_type": "UriFile", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "UriFolder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": {"job_limits_type": "Command", "timeout": "PT10S"},
            "outputs": {"my_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}},
            "resources": None,
            "name": None,
            "tags": {},
        }
        # node3 copies node2's property
        assert node3_dict == expected_dict

    def test_set_limits(self, test_command):
        # node without limits
        node1 = test_command()
        # node with existing limits
        node2 = node1()
        node2.limits = CommandJobLimits(timeout=10)
        # node with wrong type of limits
        node3 = node2()
        # TODO: do we need to check on this?
        node3.limits = {}

        nodes = [node1, node2, node3]
        for node in nodes:
            node.set_limits(timeout=10)
            expected_limits = {"job_limits_type": "Command", "timeout": "PT10S"}
            actual_limits = node1.limits._to_rest_object().as_dict()
            assert actual_limits == expected_limits

    def test_command_with_artifact_inputs(self, command_with_artifact_inputs):
        node1 = command_with_artifact_inputs()
        # node1 won't store actual value of inputs/outputs
        node1_dict = pydash.omit(
            node1._to_rest_object(),
            "componentId",
        )
        expected_dict = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "uri_file": {"job_input_type": "UriFile", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "UriFolder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": None,
            "outputs": {"my_model": {"job_output_type": "MLFlowModel"}},
            "resources": None,
            "name": None,
            "tags": {},
        }
        assert node1_dict == expected_dict

        # node1's component stores proper inputs & outputs
        actual_component = pydash.omit(
            node1._component._to_rest_object().as_dict(), "name", "properties.component_spec.name"
        )
        expected_component = {
            "properties": {
                "component_spec": {
                    "_source": "BUILDER",
                    "description": "This is a fancy job",
                    "code": "./tests",
                    "command": "python train.py --input-data " "${{inputs.uri_folder}} --lr " "${{inputs.float}}",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "inputs": {
                        "boolean": {"default": "False", "type": "boolean"},
                        "float": {"default": "1.1", "max": "5.0", "min": "0.0", "type": "number"},
                        "integer": {"default": "2", "max": "4", "min": "-1", "type": "integer"},
                        "string": {"default": "default_str", "type": "string"},
                        "uri_file": {"type": "uri_file"},
                        "uri_folder": {"type": "uri_folder"},
                    },
                    "is_deterministic": True,
                    "outputs": {"my_model": {"type": "mlflow_model"}},
                    "tags": {},
                    "type": "command",
                },
                "description": "This is a fancy job",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {},
                "tags": {},
            }
        }
        assert actual_component == expected_component

    def test_set_resources(self, test_command):
        # node without resources
        node1 = test_command()
        # node with existing resources
        node2 = node1()
        node2.resources = ResourceConfiguration(
            instance_count=2, instance_type="STANDARD_D2", properties={"key": "val"}
        )
        # node with existing resources
        node3 = node2()
        node2.resources = ResourceConfiguration(
            instance_count=1, instance_type="STANDARD_D2", properties={"key": "val"}
        )
        # node with wrong type of resources
        node4 = node2()
        # TODO: do we need to check on this?
        node4.resources = {}

        nodes = [node1, node2, node3, node4]
        for node in nodes:
            node.set_resources(instance_count=1, instance_type="STANDARD_D2_v2", properties={"key": "new_val"})
            expected_resources = {
                "instance_count": 1,
                "instance_type": "STANDARD_D2_v2",
                "properties": {"key": "new_val"},
            }
            actual_resources = node1.resources._to_rest_object().as_dict()
            assert actual_resources == expected_resources

    def test_inputs_binding(self, test_command):
        node1 = test_command()
        node2 = test_command()
        node3 = test_command(uri_file=node1.outputs.my_model, uri_folder=node2.outputs.my_model)
        node1.name = "new_name1"
        node2.name = "new_name2"

        # check owner of node3's inputs are set to node1 and node2
        assert node3.inputs.uri_file._data._owner is node1
        assert node3.inputs.uri_folder._data._owner is node2

        assert node3._build_inputs() == {
            "boolean": False,
            "float": 0.01,
            "integer": 1,
            "string": "str",
            "uri_file": Input(path="${{parent.jobs.new_name1.outputs.my_model}}", type="uri_folder", mode=None),
            "uri_folder": Input(path="${{parent.jobs.new_name2.outputs.my_model}}", type="uri_folder", mode=None),
        }

        node1 = test_command()
        node2 = node1()
        node3 = node2(uri_file=node1.outputs.my_model, uri_folder=node2.outputs.my_model)
        node1.name = "new_node1"
        node2.name = "new_node2"

        # check owner of node3's inputs are set to node1 and node2
        assert node3.inputs.uri_file._data._owner is node1
        assert node3.inputs.uri_folder._data._owner is node2
        assert node3._build_inputs() == {
            "boolean": False,
            "float": 0.01,
            "integer": 1,
            "string": "str",
            "uri_file": Input(path="${{parent.jobs.new_node1.outputs.my_model}}", type="uri_folder", mode=None),
            "uri_folder": Input(path="${{parent.jobs.new_node2.outputs.my_model}}", type="uri_folder", mode=None),
        }

        node4 = node3()
        # set inputs of node3 as outputs of node1
        node4.inputs.uri_file = node2.outputs.my_model
        # it's uri_file owner should be node2
        assert node4.inputs.uri_file._data._owner is node2
        # it's uri_folder owner should still be node2(copied from node3)
        assert node4.inputs.uri_folder._data._owner is node2
        assert node4._build_inputs() == {
            "boolean": False,
            "float": 0.01,
            "integer": 1,
            "string": "str",
            "uri_file": Input(path="${{parent.jobs.new_node2.outputs.my_model}}", type="uri_folder", mode=None),
            "uri_folder": Input(path="${{parent.jobs.new_node2.outputs.my_model}}", type="uri_folder", mode=None),
        }

    def test_copy_distribution_resources(self, test_command):
        # test new object are created when creating resources
        node1 = test_command()
        node1.distribution = MpiDistribution(process_count_per_instance=2)
        node1.limits = CommandJobLimits(timeout=10)
        node1.resources = ResourceConfiguration(instance_count=2)
        node1.environment_variables = {"key": "val"}

        node2 = node1()

        node3 = test_command()
        node4 = node3()

        # node2 and node1 has different distribution object with same value
        attrs_to_check = ["distribution", "limits", "resources", "environment_variables"]
        for attr in attrs_to_check:
            attr1 = getattr(node1, attr)
            attr2 = getattr(node2, attr)
            assert attr1 is not attr2
            assert attr1 == attr2

            attr1 = getattr(node3, attr)
            attr2 = getattr(node4, attr)
            if attr1 is not None:
                assert attr1 is not attr2
            assert attr1 == attr2

    def test_invalid_command_params(self, test_command_params):
        # currently we only have type check for command properties and let service side do value check.
        params_to_check = ["environment", "resources", "limits", "code"]
        for param in params_to_check:
            params = {**test_command_params, **{param: 1}}
            with pytest.raises(ValidationException) as e:
                command(**params)
            pattern = rf"Expecting \([^)]+\) for {param},"
            assert re.match(pattern, str(e.value)), str(e.value)

    def test_command_unprovided_inputs_outputs(self, test_command_params):
        test_command_params.update({"inputs": None, "outputs": None, "command": "echo hello"})
        node1 = command(**test_command_params)

        actual_component = pydash.omit(
            node1._component._to_rest_object().as_dict(), "name", "properties.component_spec.name"
        )
        expected_component = {
            "properties": {
                "component_spec": {
                    "_source": "BUILDER",
                    "description": "This is a fancy job",
                    "code": "./tests",
                    "command": "echo hello",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "inputs": {},
                    "is_deterministic": True,
                    "outputs": {},
                    "tags": {},
                    "type": "command",
                },
                "description": "This is a fancy job",
                "is_anonymous": False,
                "is_archived": False,
                "properties": {},
                "tags": {},
            }
        }
        assert actual_component == expected_component

        actual_node = pydash.omit(
            node1._to_rest_object(),
            "componentId",
        )
        expected_node = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {},
            "limits": None,
            "name": "my_job",
            "outputs": {},
            "resources": None,
            "tags": {},
        }
        assert actual_node == expected_node

    def test_distribution_from_dict(self, test_command):
        node1 = test_command()

        # valid
        node1.distribution = {"type": "Pytorch", "process_count_per_instance": 4}
        assert isinstance(node1.distribution, PyTorchDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {"distribution_type": "PyTorch", "process_count_per_instance": 4}

        node1.distribution = {"type": "TensorFlow", "parameter_server_count": 1}
        assert isinstance(node1.distribution, TensorFlowDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {"distribution_type": "TensorFlow", "parameter_server_count": 1, "worker_count": None}

        node1.distribution = {"type": "mpi", "process_count_per_instance": 1}
        assert isinstance(node1.distribution, MpiDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {"distribution_type": "Mpi", "process_count_per_instance": 1}

        # invalid
        with pytest.raises(ValidationError):
            node1.distribution = {"type": "unknown", "parameter_server_count": 1}

    def test_distribution_resources_default_val(self, test_command_params):
        test_command_params.update(
            {
                "distribution": MpiDistribution(process_count_per_instance=2),
                "resources": ResourceConfiguration(instance_count=2, instance_type="STANDARD_D2"),
            }
        )
        command_func = command(**test_command_params)

        node1 = command_func()
        # can set nested properties
        node1.distribution.process_count_per_instance = 4
        node1.resources.instance_count = 4
        rest_dict = node1._to_rest_object()

        assert rest_dict["distribution"] == {"distribution_type": "Mpi", "process_count_per_instance": 4}
        assert rest_dict["resources"] == {"instance_count": 4, "instance_type": "STANDARD_D2", "properties": {}}

    def test_resources_from_dict(self, test_command_params):
        expected_resources = {"instance_count": 4, "instance_type": "STANDARD_D2", "properties": {}}
        test_command_params.update(
            {
                "resources": ResourceConfiguration(instance_count=4, instance_type="STANDARD_D2"),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["resources"] == expected_resources

        test_command_params.update(
            {
                "resources": dict(instance_count=4, instance_type="STANDARD_D2"),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["resources"] == expected_resources

        test_command_params.update(
            {
                "resources": dict(instance_count=4, instance_type="STANDARD_D2", unknown_field=1),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["resources"] == expected_resources

        test_command_params.update(
            {
                "resources": dict(instance_type="STANDARD_D2", unknown_field=1),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["resources"] == {"instance_type": "STANDARD_D2", "properties": {}}

    def test_to_component_input(self):
        # test literal input
        literal_input_2_expected_type = {
            1: {"default": 1, "type": "integer"},
            1.1: {"default": 1.1, "type": "number"},
            False: {"default": False, "type": "boolean"},
            "str": {"default": "str", "type": "string"},
        }
        for job_input, input_type in literal_input_2_expected_type.items():
            assert ComponentTranslatableMixin._to_input(job_input, {})._to_dict() == input_type

        with pytest.raises(JobException) as err_info:
            ComponentTranslatableMixin._to_input(None, {})
        assert "'<class 'NoneType'>' is not supported as component input" in str(err_info.value)

        # test input binding
        test_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_inputs_outputs.yml"
        )
        job_dict = load_job(path=test_path)._to_dict()
        binding_2_expected_type = {
            "${{parent.inputs.job_data}}": {"type": "uri_folder"},
            "${{parent.inputs.job_data_uri}}": {"type": "uri_folder"},
            "${{parent.inputs.job_literal_input}}": {"type": "integer"},
        }

        for job_input, input_type in binding_2_expected_type.items():
            assert ComponentTranslatableMixin._to_input(job_input, job_dict)._to_dict() == input_type

    def test_to_component_output(self):
        # test output binding
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_parallel_job_tabular_input_e2e.yml"
        job_dict = load_job(path=test_path)._to_dict()
        binding_2_expected_type = {
            "${{parent.outputs.job_out_file}}": {"type": "uri_file"},
        }

        for job_output, input_type in binding_2_expected_type.items():
            assert ComponentTranslatableMixin._to_output(job_output, job_dict)._to_dict() == input_type
