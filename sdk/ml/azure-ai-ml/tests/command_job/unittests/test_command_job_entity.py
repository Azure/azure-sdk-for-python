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
