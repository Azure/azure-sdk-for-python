import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live, wait_until_done

from azure.ai.ml import MLClient, load_job
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._builders.command_func import command
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.sweep.early_termination_policy import TruncationSelectionPolicy
from azure.ai.ml.entities._job.sweep.search_space import LogUniform
from azure.ai.ml.operations._run_history_constants import JobStatus, RunHistoryConstants

# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "enable_environment_id_arm_expansion",
)
@pytest.mark.training_experiences_test
class TestSweepJob(AzureRecordedTestCase):
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.e2etest
    def test_sweep_job_submit(self, randstr: Callable[[], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and reousrce group

        job_name = randstr("job_name")

        params_override = [{"name": job_name}]
        sweep_job = load_job(
            source="./tests/test_configs/sweep_job/sweep_job_test.yaml",
            params_override=params_override,
        )
        sweep_job_resource = client.jobs.create_or_update(job=sweep_job)
        assert sweep_job_resource.name == job_name
        assert sweep_job_resource.trial.environment_variables["test_var1"] == "set"
        assert sweep_job_resource.status in RunHistoryConstants.IN_PROGRESS_STATUSES

        sweep_job_resource_2 = client.jobs.get(job_name)
        assert sweep_job_resource.name == sweep_job_resource_2.name

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.e2etest
    def test_sweep_job_submit_with_inputs(self, randstr: Callable[[str], str], client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and reousrce group

        job_name = randstr("job_name")

        params_override = [{"name": job_name}]
        sweep_job = load_job(
            source="./tests/test_configs/sweep_job/sweep_job_test_inputs.yaml",
            params_override=params_override,
        )
        sweep_job_resource = client.jobs.create_or_update(job=sweep_job)
        assert sweep_job_resource.name == job_name
        assert sweep_job_resource.status in RunHistoryConstants.IN_PROGRESS_STATUSES

        sweep_job_resource_2 = client.jobs.get(job_name)
        assert sweep_job_resource.name == sweep_job_resource_2.name
        assert sweep_job_resource_2.inputs is not None
        assert len(sweep_job_resource_2.inputs) == 2
        assert "iris_csv" in sweep_job_resource_2.inputs
        assert "some_number" in sweep_job_resource_2.inputs

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.e2etest
    def test_sweep_job_submit_minimal(self, randstr: Callable[[str], str], client: MLClient) -> None:
        """Ensure the Minimal required properties does not fail on submisison"""
        job_name = randstr("job_name")

        params_override = [{"name": job_name}]
        sweep_job = load_job(
            source="./tests/test_configs/sweep_job/sweep_job_minimal_test.yaml",
            params_override=params_override,
        )
        sweep_job_resource = client.jobs.create_or_update(job=sweep_job)
        assert sweep_job_resource.name == job_name
        assert sweep_job_resource.status in RunHistoryConstants.IN_PROGRESS_STATUSES

        sweep_job_resource_2 = client.jobs.get(job_name)
        assert sweep_job_resource.name == sweep_job_resource_2.name

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.e2etest
    def test_sweep_job_await_completion(self, randstr: Callable[[str], str], client: MLClient) -> None:
        """Ensure sweep job runs to completion"""
        job_name = randstr("job_name")

        params_override = [{"name": job_name}]
        sweep_job = load_job(
            source="./tests/test_configs/sweep_job/sweep_job_minimal_test.yaml",
            params_override=params_override,
        )
        sweep_job_resource = client.jobs.create_or_update(job=sweep_job)

        assert sweep_job_resource.name == job_name
        # wait 3 minutes to check job has not failed.
        sleep_if_live(3 * 60)
        sweep_job_resource = client.jobs.get(job_name)
        assert sweep_job_resource.status in [JobStatus.COMPLETED, JobStatus.RUNNING]

    @pytest.mark.e2etest
    @pytest.mark.skip(reason="flaky test")
    def test_sweep_job_download(self, randstr: Callable[[str], str], client: MLClient) -> None:
        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/sweep_job/sweep_job_minimal_outputs.yaml",
                params_override=[{"name": randstr("name")}],
            )
        )

        wait_until_done(job=job, client=client)

        with TemporaryDirectory() as tmp_dirname:
            tmp_path = Path(tmp_dirname)
            client.jobs.download(name=job.name, download_path=tmp_path, all=True)

            best_child_run_artifact_dir = tmp_path / "artifacts"
            best_child_run_output_dir = tmp_path / "named-outputs"
            parent_run_artifact_dir = tmp_path / "hd-artifacts"

            assert best_child_run_artifact_dir.exists()
            assert next(best_child_run_artifact_dir.iterdir(), None), "No artifacts for child run were downloaded"
            assert best_child_run_output_dir.exists()
            assert next(best_child_run_output_dir.iterdir(), None), "No outputs for child run were downloaded"
            assert parent_run_artifact_dir.exists()
            assert next(parent_run_artifact_dir.iterdir(), None), "No artifacts for parent run were downloaded"

    @pytest.mark.e2etest
    def test_sweep_job_builder(self, randstr: Callable[[str], str], client: MLClient) -> None:
        inputs = {
            "uri": Input(
                type=AssetTypes.URI_FILE, path="azureml://datastores/workspaceblobstore/paths/python/data.csv"
            ),
            "lr": LogUniform(min_value=0.001, max_value=0.1),
        }

        node = command(
            name=randstr("name"),
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs=inputs,
            command="echo ${{inputs.uri}} ${{search_space.learning_rate}}",
            display_name="builder_command_job",
            compute="testCompute",
            experiment_name="mfe-test1-dataset",
        )

        sweep_node = node.sweep(
            sampling_algorithm="random",
            goal="maximize",
            primary_metric="accuracy",
            early_termination_policy=TruncationSelectionPolicy(
                evaluation_interval=100, delay_evaluation=200, truncation_percentage=40
            ),
        )

        sweep_node.set_limits(max_concurrent_trials=2, max_total_trials=10, timeout=300)

        assert sweep_node.trial.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert sweep_node.display_name == "builder_command_job"
        assert sweep_node.compute == "testCompute"
        assert sweep_node.experiment_name == "mfe-test1-dataset"

        sweep_node.description = "new-description"
        sweep_node.display_name = "new_builder_command_job"
        assert sweep_node.description == "new-description"
        assert sweep_node.display_name == "new_builder_command_job"

        result = client.create_or_update(sweep_node)
        assert result.description == "new-description"
        assert result.trial.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert result.display_name == "new_builder_command_job"
        assert result.compute == "testCompute"
        assert result.experiment_name == "mfe-test1-dataset"
