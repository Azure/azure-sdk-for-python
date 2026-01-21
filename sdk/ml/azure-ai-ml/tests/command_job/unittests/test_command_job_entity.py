import json
from collections import OrderedDict

import pytest

from azure.ai.ml import Input, MpiDistribution
from azure.ai.ml._restclient.v2023_04_01_preview.models import AmlToken, JobBase
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import CommandJob, Environment, Job
from azure.ai.ml.entities._builders.command import Command
from azure.ai.ml.entities._builders.command_func import command
from azure.ai.ml.entities._job.job_limits import CommandJobLimits
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml.entities._job.to_rest_functions import to_rest_job_object
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestCommandJobEntity:
    def test_job_name_generator(self):
        job1 = generate_job_name()

        name_parts = job1.split(sep="_")
        len(name_parts) == 3
        len(name_parts[2]) == 10

        job2 = generate_job_name()
        assert job2 != job1

    @pytest.mark.parametrize(
        "file",
        [
            "./tests/test_configs/command_job/rest_command_job_legacy1_command.json",
            "./tests/test_configs/command_job/rest_command_job_legacy2_command.json",
            "./tests/test_configs/command_job/rest_command_job_env_var_command.json",
        ],
    )
    def test_from_rest_legacy1_command(self, mock_workspace_scope: OperationScope, file: str):
        with open(file, "r") as f:
            resource = json.load(f)
        rest_job = JobBase.deserialize(resource)
        print(type(rest_job.properties))
        job = Job._from_rest_object(rest_job)
        assert job.command == "echo ${{inputs.filePath}} && ls ${{inputs.dirPath}}"

    def test_missing_input_raises(self):
        with open("./tests/test_configs/command_job/rest_command_job_env_var_command.json", "r") as f:
            resource = json.load(f)
        rest_job = JobBase.deserialize(resource)
        job = Job._from_rest_object(rest_job)
        job.command = "echo ${{inputs.missing_input}}"
        with pytest.raises(ValidationException):
            to_rest_job_object(job)

    def test_calling_command_job_constructor_with_promoted_properties(self):
        basic_job = CommandJob(
            display_name="hello-world-job",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
        )
        assert basic_job.compute == "cpu-cluster"

        anon_env_job = CommandJob(
            display_name="hello-world-job-anon-env",
            command='echo "hello world"',
            environment=Environment(image="python:latest"),
            compute="cpu-cluster",
        )
        assert anon_env_job.environment.image == "python:latest"

        distributed_job = CommandJob(
            display_name="distributed-mpi-job",
            experiment_name="tensorflow-mnist",
            command="python train.py",
            code="./src",
            environment="AzureML-tensorflow-2.5-ubuntu20.04-py38-cuda11-gpu:27",
            environment_variables={"FOO": "BAR"},
            compute="gpu-cluster",
        )
        assert distributed_job.code == "./src"

        distributed_job.resources = JobResourceConfiguration()
        distributed_job.resources.instance_count = 4
        assert distributed_job.resources.instance_count == 4

    def test_distribution(self) -> None:
        node = command(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            distribution=MpiDistribution(process_count_per_instance=2),
        )

        distribution = {"type": "mpi", "process_count_per_instance": 2}
        assert OrderedDict(distribution) == OrderedDict(node._to_job().distribution.__dict__)

        from_rest_job = Job._from_rest_object(node._to_job()._to_rest_object())

        assert isinstance(from_rest_job.distribution, MpiDistribution)
        assert from_rest_job.distribution.process_count_per_instance == 2

    def test_command_job_builder_serialization(self) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "data_asset": Input(path="test-data:1"),
            "local_data": Input(path="./tests/test_configs/data/"),
        }

        node = command(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            command="echo ${{inputs.uri}} ${{inputs.data_asset}} ${{inputs.local_data}}",
            display_name="builder-command-job-display",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=AmlToken(),
            tags={"tag1": "value1"},
            properties={"prop1": "value1"},
            distribution=MpiDistribution(),
            environment_variables={"EVN1": "VAR1"},
            outputs={"best_model": {}},
            instance_count=2,
            instance_type="STANDARD_BLA",
            locations=["westus"],
            timeout=300,
            code="./",
            queue_settings=QueueSettings(job_tier="standard", priorty="medium"),
        )

        expected_job = CommandJob(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            command="echo ${{inputs.uri}} ${{inputs.data_asset}} ${{inputs.local_data}}",
            display_name="builder-command-job-display",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=AmlToken(),
            tags={"tag1": "value1"},
            properties={"prop1": "value1"},
            distribution=MpiDistribution(),
            environment_variables={"EVN1": "VAR1"},
            outputs={"best_model": {}},
            limits=CommandJobLimits(timeout=300),
            resources=JobResourceConfiguration(instance_count=2, instance_type="STANDARD_BLA", locations=["westus"]),
            queue_settings=QueueSettings(job_tier="standard", priorty="medium"),
            code="./",
        )

        assert expected_job._to_dict() == node._to_job()._to_dict()

    def test_parent_job_serialization(self) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "data_asset": Input(path="test-data:1"),
            "local_data": Input(path="./tests/test_configs/data/"),
        }
        command_job = command(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            command="echo ${{inputs.uri}} ${{inputs.data_asset}} ${{inputs.local_data}}",
            display_name="builder-command-job-display",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            tags={"tag1": "value1"},
            properties={"prop1": "value1"},
            distribution=MpiDistribution(),
            environment_variables={"EVN1": "VAR1"},
            outputs={"best_model": {}},
            instance_count=2,
            instance_type="STANDARD_BLA",
            locations=["westus"],
            timeout=300,
            code="./",
            queue_settings=QueueSettings(job_tier="standard", priorty="medium"),
            parent_job_name="parent-job",
        )

        job_prop = command_job._to_job()
        assert job_prop.parent_job_name == "parent-job"

    def test_multiple_docker_args_job_serialization(self) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "data_asset": Input(path="test-data:1"),
            "local_data": Input(path="./tests/test_configs/data/"),
        }
        command_job = command(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            distribution=MpiDistribution(process_count_per_instance=2),
            locations=["westus"],
            docker_args=["--shm-size=1g", "--ipc=host"],
        )
        job_prop = command_job._to_job()._to_rest_object().properties
        from_rest_job = Job._from_rest_object(command_job._to_job()._to_rest_object())
        assert hasattr(job_prop.resources, "locations") == False
        assert job_prop.resources.docker_args_list == ["--shm-size=1g", "--ipc=host"]
        assert isinstance(job_prop.resources.docker_args_list, list)
        assert from_rest_job.resources.docker_args == ["--shm-size=1g", "--ipc=host"]

    def test_single_docker_args_job_serialization(self) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "data_asset": Input(path="test-data:1"),
            "local_data": Input(path="./tests/test_configs/data/"),
        }
        command_job = command(
            name="builder-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            distribution=MpiDistribution(process_count_per_instance=2),
            locations=["westus"],
            docker_args="--shm-size=1g",
        )
        job_prop = command_job._to_job()._to_rest_object().properties
        from_rest_job = Job._from_rest_object(command_job._to_job()._to_rest_object())
        assert job_prop.resources.locations == ["westus"]
        assert hasattr(job_prop.resources, "docker_args_list") == False
        assert from_rest_job.resources.docker_args == "--shm-size=1g"

    def test_optional_inputs_with_none_and_empty_string(self) -> None:
        """Test that optional inputs with None or empty string values are not sent to REST API."""
        # Test with None value - should be excluded from REST inputs
        inputs_with_none = {
            "required_input": "value1",
            "optional_input": None,
        }
        command_job = CommandJob(
            display_name="test-optional-inputs",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
            inputs=inputs_with_none,
        )
        rest_obj = command_job._to_rest_object()
        # None values should not be in the REST inputs
        assert "required_input" in rest_obj.properties.inputs
        assert "optional_input" not in rest_obj.properties.inputs

        # Test with empty string value - should be excluded from REST inputs
        inputs_with_empty_string = {
            "required_input": "value1",
            "optional_input": "",
        }
        command_job_empty = CommandJob(
            display_name="test-optional-inputs-empty",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
            inputs=inputs_with_empty_string,
        )
        rest_obj_empty = command_job_empty._to_rest_object()
        # Empty string values should not be in the REST inputs
        assert "required_input" in rest_obj_empty.properties.inputs
        assert "optional_input" not in rest_obj_empty.properties.inputs

        # Test with non-empty value - should be included in REST inputs
        inputs_with_value = {
            "required_input": "value1",
            "optional_input": "value2",
        }
        command_job_value = CommandJob(
            display_name="test-optional-inputs-value",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
            inputs=inputs_with_value,
        )
        rest_obj_value = command_job_value._to_rest_object()
        # Non-empty values should be in the REST inputs
        assert "required_input" in rest_obj_value.properties.inputs
        assert "optional_input" in rest_obj_value.properties.inputs
        assert rest_obj_value.properties.inputs["optional_input"].value == "value2"

        # Test with dict containing None value - should be excluded from REST inputs
        inputs_with_dict_none = {
            "required_input": "value1",
            "optional_input": {"value": None},
        }
        command_job_dict_none = CommandJob(
            display_name="test-optional-inputs-dict-none",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
            inputs=inputs_with_dict_none,
        )
        rest_obj_dict_none = command_job_dict_none._to_rest_object()
        # Dict with None value should not be in the REST inputs
        assert "required_input" in rest_obj_dict_none.properties.inputs
        assert "optional_input" not in rest_obj_dict_none.properties.inputs

        # Test with dict containing empty string - should be excluded from REST inputs
        inputs_with_dict_empty = {
            "required_input": "value1",
            "optional_input": {"value": ""},
        }
        command_job_dict_empty = CommandJob(
            display_name="test-optional-inputs-dict-empty",
            command='echo "hello world"',
            environment="AzureML-Minimal:1",
            compute="cpu-cluster",
            inputs=inputs_with_dict_empty,
        )
        rest_obj_dict_empty = command_job_dict_empty._to_rest_object()
        # Dict with empty string should not be in the REST inputs
        assert "required_input" in rest_obj_dict_empty.properties.inputs
        assert "optional_input" not in rest_obj_dict_empty.properties.inputs
