from pathlib import Path
from typing import Callable

import jwt
import pytest
import sys
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live, wait_until_done

from azure.ai.ml import Input, MLClient, command, load_environment, load_job
from azure.ai.ml._azure_environments import _get_base_url_from_metadata, _resource_to_scopes
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml.constants._common import COMMON_RUNTIME_ENV_VAR, LOCAL_COMPUTE_TARGET, TID_FMT, AssetTypes
from azure.ai.ml.entities import AmlTokenConfiguration, QueueSettings
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.distribution import MpiDistribution
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.operations._run_history_constants import JobStatus, RunHistoryConstants
from azure.core.polling import LROPoller

# These params are logged in ..\test_configs\python\simple_train.py. test_command_job_with_params asserts these parameters are
# logged in the training script, so any changes to parameter logging in simple_train.py must preserve this logging or change it both
# here and in the script.
TEST_PARAMS = {"a_param": "1", "another_param": "2"}

# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.timeout(600)
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "enable_environment_id_arm_expansion",
    "mock_anon_component_version",
)
@pytest.mark.training_experiences_test
class TestCommandJob(AzureRecordedTestCase):
    @pytest.mark.skip(
        "Investigate The network connectivity issue encountered for 'Microsoft.MachineLearningServices'; cannot fulfill the request."
    )
    @pytest.mark.e2etest
    def test_command_job(self, randstr: Callable[[], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        job_name = randstr("job_name")
        print(f"Creating job {job_name}")

        try:
            _ = client.jobs.get(job_name)

            # shouldn't happen!
            print(f"Found existing job {job_name}")
        except Exception as ex:
            print(f"Job {job_name} not found: {ex}")

        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)

        assert command_job.name == job_name
        assert command_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES
        assert command_job.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job.compute == "cpu-cluster"
        check_tid_in_url(client, command_job)

        # Test that uri_folder has a trailing slash
        assert job.inputs["hello_input"].type == "uri_folder"
        assert job.inputs["hello_input"].path.endswith("/")

        command_job_2 = client.jobs.get(job_name)
        assert command_job.name == command_job_2.name
        assert command_job.identity.type == command_job_2.identity.type
        assert command_job_2.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job_2.compute == "cpu-cluster"
        check_tid_in_url(client, command_job_2)

    @pytest.mark.e2etest
    def test_command_job_with_singularity(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_singularity_test.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)
        assert command_job.queue_settings == QueueSettings(job_tier="premium", priority="medium")
        assert command_job.resources.locations == ["westus", "eastus"]
        assert command_job.name == job_name
        assert command_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES
        assert command_job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert (
            command_job.compute
            == "/subscriptions/79a1ba0c-35bb-436b-bff2-3074d5ff1f89/resourceGroups/Runtime/providers/Microsoft.MachineLearningServices/virtualclusters/centeuapvc"
        )
        check_tid_in_url(client, command_job)

        command_job_2 = client.jobs.get(job_name)
        assert command_job.name == command_job_2.name
        assert command_job_2.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert (
            command_job_2.compute
            == "/subscriptions/79a1ba0c-35bb-436b-bff2-3074d5ff1f89/resourceGroups/Runtime/providers/Microsoft.MachineLearningServices/virtualclusters/centeuapvc"
        )
        assert command_job_2.queue_settings == command_job.queue_settings
        assert command_job_2.resources.locations == command_job.resources.locations
        check_tid_in_url(client, command_job_2)

    @pytest.mark.e2etest
    def test_command_job_with_dataset(self, randstr: Callable[[], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test_with_local_dataset.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)

        assert command_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES
        assert command_job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job.compute == "testCompute"
        check_tid_in_url(client, command_job)

        command_job_2 = client.jobs.get(job_name)
        assert command_job.name == command_job_2.name
        assert command_job.identity.type == command_job_2.identity.type
        assert command_job_2.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job_2.compute == "testCompute"
        check_tid_in_url(client, command_job_2)

    @pytest.mark.e2etest
    def test_command_job_serverless(self, randstr: Callable[[], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test_serverless.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)

        assert command_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES
        assert command_job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job.queue_settings.job_tier == "standard"
        check_tid_in_url(client, command_job)

        command_job_2 = client.jobs.get(job_name)
        assert command_job.name == command_job_2.name
        assert command_job.identity.type == command_job_2.identity.type
        assert command_job_2.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        check_tid_in_url(client, command_job_2)

    @pytest.mark.e2etest
    def test_command_job_with_dataset_short_uri(self, randstr: Callable[[], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test_with_dataset.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)

        assert command_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES
        assert command_job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job.compute == "testCompute"
        check_tid_in_url(client, command_job)

        command_job_2 = client.jobs.get(job_name)
        assert command_job.name == command_job_2.name
        assert command_job.identity.type == command_job_2.identity.type
        assert command_job_2.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert command_job_2.compute == "testCompute"
        check_tid_in_url(client, command_job_2)

    @pytest.mark.skip("https://dev.azure.com/msdata/Vienna/_workitems/edit/2009659")
    @pytest.mark.e2etest
    def test_command_job_builder(self, data_with_2_versions: str, client: MLClient) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "data_asset": Input(path=f"{data_with_2_versions}:1"),
            "local_data": Input(path="./tests/test_configs/data/"),
        }

        node = command(
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            code="./tests/test_configs/training/",
            command="echo ${{inputs.uri}} ${{inputs.data_asset}} ${{inputs.local_data}}",
            display_name="builder_command_job",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
            identity=AmlTokenConfiguration(),
            distribution=MpiDistribution(process_count_per_instance=2),
        )

        assert node.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert node.display_name == "builder_command_job"
        assert node.compute == "testCompute"
        assert node.experiment_name == "mfe-test1-dataset"
        assert node.identity == AmlTokenConfiguration()

        node.description = "new-description"
        node.display_name = "new_builder_command_job"
        assert node.description == "new-description"
        assert node.display_name == "new_builder_command_job"
        assert isinstance(node.distribution, MpiDistribution)
        assert node.distribution.process_count_per_instance == 2

        result = client.create_or_update(node)
        assert result.description == "new-description"
        assert result.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert result.display_name == "new_builder_command_job"
        assert result.compute == "testCompute"
        assert result.experiment_name == "mfe-test1-dataset"
        assert result.identity == AmlTokenConfiguration()
        assert isinstance(result.distribution, MpiDistribution)
        assert result.distribution.process_count_per_instance == 2

        # Test only overriding one input, the other 2 inputs should be kept as-is.
        new_job = result(data_asset=Input(path=f"{data_with_2_versions}:2"))
        new_result = client.create_or_update(new_job)
        len(new_result.inputs) == 3
        assert result.display_name == new_result.display_name

    @pytest.mark.timeout(900)
    @pytest.mark.e2etest
    @pytest.mark.skipif(
        condition=not sys.platform.startswith(("win32", "cygwin")),
        reason="Skipping for PyPy as docker installation is not supported and skipped in dev_requirement.txt",
    )
    def test_command_job_local(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        try:
            _ = client.jobs.get(job_name)
            print(f"Found existing job {job_name}")
        except Exception as ex:
            print(f"Job {job_name} not found: {ex}")

        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/local_job.yaml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)
        assert command_job.name == job_name
        assert command_job.compute == "local"
        assert command_job.environment_variables[COMMON_RUNTIME_ENV_VAR] == "true"

    @pytest.mark.e2etest
    @pytest.mark.skip("TODO: 1210641- Re-enable when we switch to runner-style tests")
    def test_command_job_with_params(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job: CommandJob = load_job(
            source="./tests/test_configs/command_job/simple_train_test.yml",
            params_override=params_override,
        )
        job = client.jobs.create_or_update(job=job)
        with pytest.raises(ValidationException):  # show that environment is not a ARM id
            AMLVersionedArmId(job.environment)
        assert job.compute == "testCompute"
        client.jobs.stream(job_name)
        assert client.jobs.get(job_name).parameters

    @pytest.mark.skip("https://dev.azure.com/msdata/Vienna/_workitems/edit/2009659")
    @pytest.mark.e2etest
    def test_command_job_with_modified_environment(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test.yml",
            params_override=params_override,
        )
        job = client.jobs.create_or_update(job=job)

        job.name = randstr("job_name_2")
        job.environment = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"

        job = client.jobs.create_or_update(job=job)
        assert job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        job = client.jobs.get(name=job.name)
        assert job.environment == "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"

    @pytest.mark.e2etest
    @pytest.mark.skip("Investigate why cancel does not record some upload requests of code assets")
    def test_command_job_cancel(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        print(f"Creating job to validate the cancel job operation: {job_name}")
        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/simple_train_test.yml",
            params_override=params_override,
        )
        command_job_resource = client.jobs.create_or_update(job=job)
        assert command_job_resource.name == job_name
        cancel_poller = client.jobs.begin_cancel(job_name)
        assert isinstance(cancel_poller, LROPoller)
        assert cancel_poller.result() is None
        command_job_resource_2 = client.jobs.get(job_name)
        assert command_job_resource_2.status in (JobStatus.CANCEL_REQUESTED, JobStatus.CANCELED)

    @pytest.mark.e2etest
    def test_command_job_dependency_label_resolution(self, randstr: Callable[[], str], client: MLClient) -> None:
        """Checks that dependencies of the form azureml:name@label are resolved to a version"""
        from uuid import uuid4

        job_name = randstr("job_name")
        environment_name = randstr("environment_name")
        environment_versions = ["foo", "bar"]
        data_name = randstr("data_name")
        data_versions = ["foobar", "foo"]
        client: MLClient = client
        for version in environment_versions:
            client.environments.create_or_update(
                load_environment(
                    "./tests/test_configs/environment/environment_conda_inline.yml",
                    params_override=[{"name": environment_name}, {"version": version}],
                )
            )
        for version in data_versions:
            client.data.create_or_update(
                Data(
                    name=data_name,
                    version=version,
                    type=AssetTypes.URI_FILE,
                    path="./tests/test_configs/data/sample1.csv",
                )
            )

        job = load_job(
            source="./tests/test_configs/command_job/simple_train_test.yml",
            params_override=[
                {"name": job_name},
                {"environment": f"azureml:{environment_name}@latest"},
                {
                    "inputs": {
                        "testdata": {"path": f"azureml:{data_name}@latest"},
                    }
                },
            ],
        )
        command_job_resource = client.jobs.create_or_update(job=job)
        cancel_poller = client.jobs.begin_cancel(job_name)
        assert isinstance(cancel_poller, LROPoller)
        assert cancel_poller.result() is None

        # Check that environment resolves to latest version
        assert command_job_resource.environment == f"{environment_name}:{environment_versions[-1]}"
        # Check that data asset resolves to latest version
        # After this change Pull Request 823783: Have ml_client.jobs.get() return builder objects
        # returning command job becomes builder and it's input becomes InputsAttrDict[str, InputOutputBase]
        # instead of Dict[str, Input] and it only support access via attribute.
        assert command_job_resource.inputs.testdata.path == f"{data_name}:{data_versions[-1]}"

    @pytest.mark.e2etest
    @pytest.mark.skip(reason="Task 1791832: Inefficient, causing testing pipeline to time out.")
    def test_command_job_archive_restore(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        print(f"Creating job {job_name}")

        params_override = [{"name": job_name}]
        job = load_job(
            source="./tests/test_configs/command_job/command_job_test.yml",
            params_override=params_override,
        )
        command_job: CommandJob = client.jobs.create_or_update(job=job)
        name = command_job.name

        def get_job_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            job_list = client.jobs.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [j.name for j in job_list if j is not None]

        assert name in get_job_list()
        client.jobs.archive(name=name)
        assert name not in get_job_list()
        client.jobs.restore(name=name)
        assert name in get_job_list()

    @pytest.mark.skip(reason="Task 1791832: Inefficient, causing testing pipeline to time out.")
    @pytest.mark.e2etest
    def test_command_job_download(self, tmp_path: Path, randstr: Callable[[], str], client: MLClient) -> None:
        client: MLClient = client

        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/command_job/command_job_quick_with_output.yml",
                params_override=[{"name": randstr("name")}],
            )
        )
        wait_until_done(client=client, job=job)

        client.jobs.download(name=job.name, download_path=tmp_path, all=True)

        artifact_dir = tmp_path / "artifacts"
        output_dir = tmp_path / "named-outputs" / "hello_output"
        assert artifact_dir.exists()
        assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"
        assert output_dir.exists()
        assert next(output_dir.iterdir(), None), "No artifacts were downloaded"

    @pytest.mark.skip(reason="Task 1791832: Inefficient, causing testing pipeline to time out.")
    @pytest.mark.timeout(900)
    @pytest.mark.e2etest
    def test_command_job_local_run_download(self, tmp_path: Path, randstr: Callable[[], str], client: MLClient) -> None:
        client: MLClient = client

        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/command_job/command_job_quick_with_output.yml",
                params_override=[{"name": randstr("name")}, {"compute": LOCAL_COMPUTE_TARGET}],
            )
        )

        wait_until_done(client=client, job=job)

        client.jobs.download(name=job.name, download_path=tmp_path, all=True)

        artifact_dir = tmp_path / "artifacts"
        output_dir = tmp_path / "named-outputs" / "hello_output"
        assert artifact_dir.exists()
        assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"
        assert output_dir.exists()
        assert next(output_dir.iterdir(), None), "No artifacts were downloaded"

    @pytest.mark.e2etest
    def test_command_job_invalid_datastore(self, randstr: Callable[[], str], client: MLClient) -> None:
        job_name = randstr("job_name")
        invalid_datastore_name = "non-existent-ds"  # referenced in command_job_inputs_incorrect_datastore_test.yml
        params_override = [{"name": job_name}]
        job: CommandJob = load_job(
            source="./tests/test_configs/command_job/command_job_inputs_incorrect_datastore_test.yml",
            params_override=params_override,
        )
        with pytest.raises(Exception) as e:
            job = client.jobs.create_or_update(job=job)
            assert f"The datastore {invalid_datastore_name} could not be found in this workspace" in e

    @pytest.mark.e2etest
    def test_command_job_with_inputs_with_datastore_param(
        self, randstr: Callable[[str], str], client: MLClient
    ) -> None:
        job_name = randstr("job_name")
        params_override = [{"name": job_name}, {"inputs.test1.datastore": "workspaceblobstore"}]

        job: CommandJob = load_job(
            source="./tests/test_configs/command_job/command_job_relative_inputs_test.yml",
            params_override=params_override,
        )
        job = client.jobs.create_or_update(job=job)

    @pytest.mark.e2etest
    def test_command_job_parsing_error(self, randstr: Callable[[], str]) -> None:
        job_name = randstr("job_name")
        params_override = [{"name": job_name}]

        with pytest.raises(Exception) as e:
            load_job(
                source="./tests/test_configs/command_job/command_job_bad_parse.yml",
                params_override=params_override,
            )
        assert "Error while parsing yaml file" in e.value.message

    @pytest.mark.e2etest
    def test_command_job_register_output(self, randstr: Callable[[str], str], client: MLClient) -> None:
        job: CommandJob = load_job(
            source="./tests/test_configs/command_job/command_job_register_output.yml",
            params_override=[{"name": randstr("job_name")}],
        )
        job = client.jobs.create_or_update(job=job)
        assert job.outputs.test2.name == "test2_output"
        assert job.outputs.test2.version == "2"
        assert job.outputs.test3.name == "test3_output"
        assert job.outputs.test3.version == "3"

    @pytest.mark.e2etest
    def test_ray_command_job(self, randstr: Callable[[], str], client: MLClient) -> None:
        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/command_job/command_job_dist_ray.yml",
                params_override=[{"name": randstr("job_name")}],
            )
        )

        job_status = wait_until_done(client=client, job=job)

        assert job_status == JobStatus.COMPLETED


def check_tid_in_url(client: MLClient, job: Job) -> None:
    # test that TID is placed in the URL only in live mode
    if is_live():
        default_scopes = _resource_to_scopes(_get_base_url_from_metadata())
        token = client._credential.get_token(*default_scopes).token
        decode = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
        formatted_tid = TID_FMT.format(decode["tid"])
        if job.services:
            studio_endpoint = job.services.get("Studio", None)
            if studio_endpoint:
                studio_url = studio_endpoint.endpoint
                assert job.studio_url == studio_url
                if studio_url:
                    assert formatted_tid in studio_url
