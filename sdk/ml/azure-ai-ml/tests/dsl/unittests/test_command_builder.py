import re

import pydash
import pytest
from marshmallow import ValidationError
from test_utilities.utils import omit_with_wildcard, parse_local_path

from azure.ai.ml import (
    Input,
    MpiDistribution,
    Output,
    PyTorchDistribution,
    RayDistribution,
    TensorFlowDistribution,
    UserIdentityConfiguration,
    command,
    load_component,
    load_job,
    spark,
)
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import CommandJobLimits, JobResourceConfiguration, QueueSettings
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.job_service import (
    JobService,
    JupyterLabJobService,
    SshJobService,
    TensorBoardJobService,
    VsCodeJobService,
)
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin
from azure.ai.ml.exceptions import JobException, ValidationException

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
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

        # Test print and jupyter rendering for the builder object
        print(test_command)
        test_command._repr_html_()

        expected_command = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "literal", "value": "False"},
                "float": {"job_input_type": "literal", "value": "0.01"},
                "integer": {"job_input_type": "literal", "value": "1"},
                "string": {"job_input_type": "literal", "value": "str"},
                "uri_file": {"job_input_type": "uri_file", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "uri_folder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "name": "my_job",
            "outputs": {"my_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}},
            "type": "command",
        }
        actual_command = pydash.omit(
            test_command._to_rest_object(),
            "componentId",
            "source_job_id",
            "properties",
        )
        assert actual_command == expected_command

        # distribution goes here
        expected_component = {
            "properties": {
                "component_spec": {
                    "_source": "BUILDER",
                    "code": parse_local_path("./tests"),
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
                        "uri_file": {"type": "uri_file", "mode": "download"},
                        "uri_folder": {"type": "uri_folder", "mode": "ro_mount"},
                    },
                    "is_deterministic": True,
                    "outputs": {"my_model": {"type": "mlflow_model", "mode": "rw_mount"}},
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
                    "code": parse_local_path("./tests"),
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
                        "uri_file": {"type": "uri_file", "mode": "download"},
                        "uri_folder": {"type": "uri_folder", "mode": "ro_mount"},
                    },
                    "is_deterministic": False,
                    "outputs": {"my_model": {"type": "mlflow_model", "mode": "rw_mount"}},
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
                "boolean": {"job_input_type": "literal", "value": "False"},
                "float": {"job_input_type": "literal", "value": "0.02"},
                "integer": {"job_input_type": "literal", "value": "1"},
                "string": {"job_input_type": "literal", "value": "str"},
                "uri_file": {"job_input_type": "uri_file", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "uri_folder",
                    "mode": "Download",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "outputs": {"my_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}},
            "type": "command",
        }
        actual_dict = pydash.omit(node1_dict, "componentId", "properties")
        assert actual_dict == expected_dict

    def test_command_function_default_values(self, test_command):
        node1 = test_command()
        node1_dict = pydash.omit(node1._to_rest_object(), "componentId", "properties")
        expected_dict = {
            "_source": "BUILDER",
            "type": "command",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "literal", "value": "False"},
                "float": {"job_input_type": "literal", "value": "0.01"},
                "integer": {"job_input_type": "literal", "value": "1"},
                "string": {"job_input_type": "literal", "value": "str"},
                "uri_file": {"job_input_type": "uri_file", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "uri_folder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "outputs": {"my_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}},
        }
        # node1 copies test_command's dict
        assert node1_dict == expected_dict

        node2 = node1(float=0.02)
        node2.compute = "new-cluster"
        node2.limits = CommandJobLimits(timeout=10)
        node3 = node2()
        node3_dict = pydash.omit(node3._to_rest_object(), "componentId", "properties")
        expected_dict = {
            "_source": "BUILDER",
            "type": "command",
            "computeId": "new-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "boolean": {"job_input_type": "literal", "value": "False"},
                "float": {"job_input_type": "literal", "value": "0.02"},
                "integer": {"job_input_type": "literal", "value": "1"},
                "string": {"job_input_type": "literal", "value": "str"},
                "uri_file": {"job_input_type": "uri_file", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "uri_folder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "limits": {"job_limits_type": "Command", "timeout": "PT10S"},
            "outputs": {"my_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}},
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
            "type": "command",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "inputs": {
                "uri_file": {"job_input_type": "uri_file", "mode": "Download", "uri": "https://my-blob/path/to/data"},
                "uri_folder": {
                    "job_input_type": "uri_folder",
                    "mode": "ReadOnlyMount",
                    "uri": "https://my-blob/path/to/data",
                },
            },
            "outputs": {"my_model": {"job_output_type": "mlflow_model"}},
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
                    "code": parse_local_path("./tests"),
                    "command": "python train.py --input-data " "${{inputs.uri_folder}} --lr " "${{inputs.float}}",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "inputs": {
                        "boolean": {"default": "False", "type": "boolean"},
                        "float": {"default": "1.1", "max": "5.0", "min": "0.0", "type": "number"},
                        "integer": {"default": "2", "max": "4", "min": "-1", "type": "integer"},
                        "string": {"default": "default_str", "type": "string"},
                        "uri_file": {"type": "uri_file", "mode": "download"},
                        "uri_folder": {"type": "uri_folder", "mode": "ro_mount"},
                    },
                    "is_deterministic": True,
                    "outputs": {"my_model": {"type": "mlflow_model"}},
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
        node2.resources = JobResourceConfiguration(
            instance_count=2,
            instance_type="STANDARD_D2",
            properties={"key": "val"},
            docker_args="testCommand",
            shm_size="3g",
        )
        # node with existing resources
        node3 = node2()
        node2.resources = JobResourceConfiguration(
            instance_count=1,
            instance_type="STANDARD_D2",
            properties={"key": "val"},
            docker_args="testCommand",
            shm_size="3g",
        )
        # node with wrong type of resources
        node4 = node2()
        # TODO: do we need to check on this?
        node4.resources = {}

        nodes = [node1, node2, node3, node4]
        for node in nodes:
            node.set_resources(
                instance_count=1,
                instance_type="STANDARD_D2_v2",
                properties={"key": "new_val"},
                docker_args="testCommand",
                shm_size="3g",
            )
            expected_resources = {
                "instance_count": 1,
                "instance_type": "STANDARD_D2_v2",
                "properties": {"key": "new_val"},
                "docker_args": "testCommand",
                "shm_size": "3g",
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
        node1.resources = JobResourceConfiguration(instance_count=2)
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
                    "code": parse_local_path("./tests"),
                    "command": "echo hello",
                    "display_name": "my-fancy-job",
                    "distribution": {"process_count_per_instance": 4, "type": "mpi"},
                    "environment": "azureml:my-env:1",
                    "is_deterministic": True,
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
            *["componentId", "properties"],
        )
        expected_node = {
            "_source": "BUILDER",
            "computeId": "cpu-cluster",
            "display_name": "my-fancy-job",
            "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
            "environment_variables": {"foo": "bar"},
            "name": "my_job",
            "type": "command",
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
        assert rest_dist == {"distribution_type": "TensorFlow", "parameter_server_count": 1}

        node1.distribution = {"type": "mpi", "process_count_per_instance": 1}
        assert isinstance(node1.distribution, MpiDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {"distribution_type": "Mpi", "process_count_per_instance": 1}

        node1.distribution = {
            "type": "ray",
            "port": 1234,
            "include_dashboard": True,
            "dashboard_port": 4321,
            "head_node_additional_args": "--disable-usage-stats",
            "worker_node_additional_args": "--disable-usage-stats",
        }
        assert isinstance(node1.distribution, RayDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {
            "distribution_type": "Ray",
            "port": 1234,
            "include_dashboard": True,
            "dashboard_port": 4321,
            "head_node_additional_args": "--disable-usage-stats",
            "worker_node_additional_args": "--disable-usage-stats",
        }

        node1.distribution = {"type": "ray", "address": "10.0.0.1:1234"}
        assert isinstance(node1.distribution, RayDistribution)
        rest_dist = node1._to_rest_object()["distribution"]
        assert rest_dist == {"distribution_type": "Ray", "address": "10.0.0.1:1234"}

        # invalid
        with pytest.raises(ValidationError):
            node1.distribution = {"type": "unknown", "parameter_server_count": 1}

    def test_docker_args_in_resources_val(self, test_command_params):
        test_command_params.update(
            {
                "distribution": MpiDistribution(process_count_per_instance=2),
                "resources": JobResourceConfiguration(
                    instance_count=2, instance_type="STANDARD_D2", docker_args="test command", shm_size="3g"
                ),
            }
        )
        command_func = command(**test_command_params)

        node1 = command_func()
        # can set nested properties
        node1.distribution.process_count_per_instance = 4
        node1.resources.instance_count = 4
        rest_dict = node1._to_rest_object()

        assert rest_dict["distribution"] == {"distribution_type": "Mpi", "process_count_per_instance": 4}
        assert rest_dict["resources"] == {
            "instance_count": 4,
            "instance_type": "STANDARD_D2",
            "docker_args": "test command",
            "shm_size": "3g",
        }

    def test_distribution_resources_default_val(self, test_command_params):
        test_command_params.update(
            {
                "distribution": MpiDistribution(process_count_per_instance=2),
                "resources": JobResourceConfiguration(instance_count=2, instance_type="STANDARD_D2"),
            }
        )
        command_func = command(**test_command_params)

        node1 = command_func()
        # can set nested properties
        node1.distribution.process_count_per_instance = 4
        node1.resources.instance_count = 4
        rest_dict = node1._to_rest_object()

        assert rest_dict["distribution"] == {"distribution_type": "Mpi", "process_count_per_instance": 4}
        assert rest_dict["resources"] == {"instance_count": 4, "instance_type": "STANDARD_D2"}

    def test_resources_from_dict(self, test_command_params):
        expected_resources = {"instance_count": 4, "instance_type": "STANDARD_D2"}
        test_command_params.update(
            {
                "resources": JobResourceConfiguration(instance_count=4, instance_type="STANDARD_D2"),
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
        assert rest_dict["resources"] == {"instance_type": "STANDARD_D2"}

    def test_queue_settings(self, test_command_params):
        expected_queue_settings = {"job_tier": "Standard", "priority": 2}
        test_command_params.update(
            {
                "queue_settings": QueueSettings(job_tier="standard", priority="medium"),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["queue_settings"] == expected_queue_settings

        test_command_params.update(
            {
                "queue_settings": dict(job_tier="standard", priority="medium"),
            }
        )
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["queue_settings"] == expected_queue_settings

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
        job_dict = load_job(source=test_path)._to_dict()
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
        job_dict = load_job(source=test_path)._to_dict()
        binding_2_expected_type = {
            "${{parent.outputs.job_out_file}}": {"type": "uri_file", "mode": "rw_mount"},
        }

        for job_output, input_type in binding_2_expected_type.items():
            assert ComponentTranslatableMixin._to_output(job_output, job_dict)._to_dict() == input_type

    def test_spark_job_with_dynamic_allocation_disabled(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
        )
        result = node._validate()
        message = "Should not specify min or max executors when dynamic allocation is disabled."
        assert "*" in result.error_messages and message == result.error_messages["*"]

    def test_executor_instances_is_mandatory_when_dynamic_allocation_disabled(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
        )
        result = node._validate()
        message = (
            "spark.driver.cores, spark.driver.memory, spark.executor.cores, spark.executor.memory and "
            "spark.executor.instances are mandatory fields."
        )
        assert "*" in result.error_messages and message == result.error_messages["*"]

    def test_executor_instances_is_specified_as_min_executor_if_unset(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
        )
        node._to_rest_object()
        assert node.executor_instances == 1

    def test_excutor_instances_throw_error_when_out_of_range(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=4,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
        )
        result = node._validate()
        message = (
            "Executor instances must be a valid non-negative integer and must be between "
            "spark.dynamicAllocation.minExecutors and spark.dynamicAllocation.maxExecutors"
        )
        assert "*" in result.error_messages and message == result.error_messages["*"]

    def test_spark_job_with_additional_conf(self):
        node = spark(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.2.0"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            conf={
                "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
                "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
                "spark.jars.excludes": "slf4j",
            },
        )
        expected_conf = {
            "spark.driver.cores": 1,
            "spark.driver.memory": "2g",
            "spark.executor.cores": 2,
            "spark.executor.memory": "2g",
            "spark.executor.instances": 2,
            "spark.jars.packages": "com.microsoft.ml.spark:mmlspark_2.11:0.15",
            "spark.jars.repositories": "https://mmlspark.azureedge.net/maven",
            "spark.jars.excludes": "slf4j",
        }
        assert node._to_rest_object()["conf"] == expected_conf

    def test_command_services_nodes(self) -> None:
        services = {
            "my_jupyterlab": JobService(type="jupyter_lab", nodes="all"),
            "my_tensorboard": JobService(
                type="tensor_board",
                properties={
                    "logDir": "~/tblog",
                },
            ),
        }
        command_obj = command(
            name="interactive-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            services=services,
        )

        rest_obj = command_obj._to_rest_object()
        assert rest_obj["services"]["my_jupyterlab"].get("nodes") == {"nodes_value_type": "All"}
        assert rest_obj["services"]["my_tensorboard"].get("nodes") == None

        with pytest.raises(ValidationException, match="nodes should be either 'all' or None"):
            services_invalid_nodes = {"my_service": JobService(nodes="All")}

    def test_command_services(self) -> None:
        services = {
            "my_ssh": JobService(type="ssh"),
            "my_tensorboard": JobService(
                type="tensor_board",
                properties={
                    "logDir": "~/tblog",
                },
            ),
            "my_jupyterlab": JobService(type="jupyter_lab"),
        }
        rest_services = {
            "my_ssh": {"job_service_type": "SSH"},
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {
                    "logDir": "~/tblog",
                },
            },
            "my_jupyterlab": {"job_service_type": "JupyterLab"},
        }
        node = command(
            name="interactive-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            services=services,
        )

        for name, service in node.services.items():
            assert isinstance(service, JobService)

        command_job = node._to_job()
        for name, service in command_job.services.items():
            assert isinstance(service, JobService)

        node_rest_obj = node._to_rest_object()
        assert node_rest_obj["services"] == rest_services

        # test invalid services
        invalid_services_0 = "ssh"
        with pytest.raises(ValidationException, match="Services must be a dict"):
            node = command(
                name="interactive-command-job",
                description="description",
                environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                command="ls",
                compute="testCompute",
                services=invalid_services_0,
            )
            assert node

        invalid_services_1 = {"my_service": 3}
        with pytest.raises(ValidationException, match="Service value for key 'my_service' must be a dict"):
            node = command(
                name="interactive-command-job",
                description="description",
                environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                command="ls",
                compute="testCompute",
                services=invalid_services_1,
            )
            assert node

        invalid_services_2 = {"my_service": {"unsupported_key": "unsupported_value"}}
        with pytest.raises(ValidationError, match="Unknown field"):
            node = command(
                name="interactive-command-job",
                description="description",
                environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                command="ls",
                compute="testCompute",
                services=invalid_services_2,
            )
            assert node

    def test_command_services_subtypes(self) -> None:
        services = {
            "my_ssh": SshJobService(),
            "my_tensorboard": TensorBoardJobService(log_dir="~/tblog"),
            "my_jupyterlab": JupyterLabJobService(),
            "my_vscode": VsCodeJobService(),
        }
        rest_services = {
            "my_ssh": {"job_service_type": "SSH"},
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {
                    "logDir": "~/tblog",
                },
            },
            "my_jupyterlab": {"job_service_type": "JupyterLab"},
            "my_vscode": {"job_service_type": "VSCode"},
        }
        node = command(
            name="interactive-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            services=services,
        )

        node_services = node.services
        assert isinstance(node_services.get("my_ssh"), SshJobService)
        assert isinstance(node_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(node_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(node_services.get("my_vscode"), VsCodeJobService)

        command_job_services = node._to_job().services
        assert isinstance(command_job_services.get("my_ssh"), SshJobService)
        assert isinstance(command_job_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(command_job_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(command_job_services.get("my_vscode"), VsCodeJobService)

        node_rest_obj = node._to_rest_object()
        assert node_rest_obj["services"] == rest_services

    def test_command_hash(self, test_command_params):
        node1 = command(**test_command_params)
        node2 = command(**test_command_params)
        assert hash(node1) == hash(node2)
        assert node1 == node2

        component_func = load_component("./tests/test_configs/components/helloworld_component_no_paths.yml")
        node3 = component_func()
        node4 = component_func()
        assert hash(node3) == hash(node4)
        assert node3 == node4

        node5 = command(**test_command_params, is_deterministic=False)
        assert hash(node1) != hash(node5)

    def test_pipeline_node_identity_with_builder(self, test_command_params):
        test_command_params["identity"] = UserIdentityConfiguration()
        command_node = command(**test_command_params)
        rest_dict = command_node._to_rest_object()
        assert rest_dict["identity"] == {"type": "user_identity"}

        @pipeline
        def my_pipeline():
            command_node()

        pipeline_job = my_pipeline()
        omit_fields = ["jobs.*.componentId", "jobs.*._source"]
        actual_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict()["properties"], *omit_fields)

        assert actual_dict["jobs"] == {
            "my_job": {
                "computeId": "cpu-cluster",
                "display_name": "my-fancy-job",
                "distribution": {"distribution_type": "Mpi", "process_count_per_instance": 4},
                "environment_variables": {"foo": "bar"},
                "identity": {"type": "user_identity"},
                "inputs": {
                    "boolean": {"job_input_type": "literal", "value": "False"},
                    "float": {"job_input_type": "literal", "value": "0.01"},
                    "integer": {"job_input_type": "literal", "value": "1"},
                    "string": {"job_input_type": "literal", "value": "str"},
                    "uri_file": {
                        "job_input_type": "uri_file",
                        "mode": "Download",
                        "uri": "https://my-blob/path/to/data",
                    },
                    "uri_folder": {
                        "job_input_type": "uri_folder",
                        "mode": "ReadOnlyMount",
                        "uri": "https://my-blob/path/to/data",
                    },
                },
                "name": "my_job",
                "outputs": {"my_model": {"job_output_type": "mlflow_model", "mode": "ReadWriteMount"}},
                "type": "command",
            }
        }

    def test_set_identity(self, test_command):
        from azure.ai.ml.entities._credentials import AmlTokenConfiguration

        node1 = test_command()
        node2 = node1()
        node2.identity = AmlTokenConfiguration()
        node3 = node1()
        node3.identity = {"type": "AMLToken"}
        assert node2.identity == node3.identity

    def test_sweep_set_search_space(self, test_command):
        from azure.ai.ml.entities._job.sweep.search_space import Choice

        node1 = test_command()
        command_node_to_sweep_1 = node1()
        sweep_node_1 = command_node_to_sweep_1.sweep(
            primary_metric="AUC",
            goal="maximize",
            sampling_algorithm="random",
        )
        sweep_node_1.search_space = {"batch_size": {"type": "choice", "values": [25, 35]}}

        command_node_to_sweep_2 = node1()
        sweep_node_2 = command_node_to_sweep_2.sweep(
            primary_metric="AUC",
            goal="maximize",
            sampling_algorithm="random",
        )
        sweep_node_2.search_space = {"batch_size": Choice(values=[25, 35])}
        assert sweep_node_1.search_space == sweep_node_2.search_space

    def test_unsupported_positional_args(self, test_command):
        with pytest.raises(ValidationException) as e:
            test_command(1)
        msg = (
            "Component function doesn't support positional arguments, got (1,) "
            "for my_job. Please use keyword arguments like: "
            "component_func(float=xxx, integer=xxx, string=xxx, boolean=xxx, uri_folder=xxx, uri_file=xxx)."
        )
        assert msg in str(e.value)
