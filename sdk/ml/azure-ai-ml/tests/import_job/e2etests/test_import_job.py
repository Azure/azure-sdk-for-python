import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import mock
import pytest
from mock import patch

from azure.ai.ml import MLClient, Output, dsl, load_component, load_job
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, AssetTypes
from azure.ai.ml.entities._builders.import_node import Import
from azure.ai.ml.entities._job.import_job import DatabaseImportSource, ImportJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob
from azure.ai.ml.operations._job_ops_helper import _wait_before_polling
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator
from azure.ai.ml.operations._run_history_constants import JobStatus, RunHistoryConstants


from devtools_testutils import AzureRecordedTestCase
from pytest_mock import MockFixture


@pytest.fixture(autouse=True)
def import_job_enabled(mocker: MockFixture):
    mocker.patch("azure.ai.ml.entities._job.import_job.is_private_preview_enabled", return_value=True)
    mocker.patch("azure.ai.ml.entities._job.pipeline.pipeline_job.is_private_preview_enabled", return_value=True)


@pytest.mark.timeout(600)
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_asset_name",
    "mock_code_hash",
    "mock_component_hash",
    "enable_environment_id_arm_expansion",
)
class TestImportJob(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_import_job_submit_cancel(self, client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        job = load_job("./tests/test_configs/import_job/import_job_test.yml")
        self.validate_import_job_submit_cancel(job, client)

    @pytest.mark.e2etest
    def test_import_node_submit_cancel(self, client: MLClient) -> None:
        from azure.ai.ml.entities._builders.import_func import import_job

        source = DatabaseImportSource(
            type="azuresqldb", connection="azureml:my_username_password", query="select * from REGION"
        )
        output = Output(type="uri_folder", path="azureml://datastores/workspaceblobstore/paths/output_dir/")
        job = import_job(source=source, output=output)
        self.validate_import_job_submit_cancel(job, client)

    def validate_import_job_submit_cancel(self, job: ImportJob, client: MLClient) -> None:
        # TODO: need to create a workspace under a e2e-testing-only subscription and resource group

        import_job: ImportJob = client.jobs.create_or_update(job=job)

        assert import_job.type == JobType.IMPORT
        assert import_job.source.type == "azuresqldb"
        assert import_job.source.connection == "azureml:my_username_password"
        assert import_job.source.query == "select * from REGION"
        assert import_job.output.type == AssetTypes.MLTABLE or import_job.output.type == AssetTypes.URI_FOLDER
        assert import_job.output.path == "azureml://datastores/workspaceblobstore/paths/output_dir/"
        assert import_job.status in RunHistoryConstants.IN_PROGRESS_STATUSES

        import_job_2 = client.jobs.get(import_job.name)
        assert isinstance(import_job_2, ImportJob)
        assert import_job_2.type == import_job.type
        assert import_job_2.name == import_job.name
        assert import_job_2.compute == "DataFactory"
        assert import_job_2.source.type == import_job.source.type
        assert import_job_2.source.connection == import_job.source.connection
        assert import_job_2.source.query == import_job.source.query
        assert import_job_2.output.type == import_job.output.type
        assert import_job_2.output.path == import_job.output.path
        assert import_job_2.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.RUNNING, JobStatus.STARTING]

        # Test cancel with submit to save test resource.
        # The job not supposed to succeed and usually failed quickly so status can be 'failed' as well
        client.jobs.cancel(import_job.name)
        import_job_3 = client.jobs.get(import_job.name)
        assert import_job_3.status in (JobStatus.CANCEL_REQUESTED, JobStatus.CANCELED, JobStatus.FAILED)

    @pytest.mark.e2etest
    def test_import_pipeline_submit_cancel(self, client: MLClient) -> None:

        pipeline: PipelineJob = load_job("./tests/test_configs/import_job/import_pipeline_test.yml")
        self.validate_test_import_pipepine_submit_cancel(pipeline, client, is_dsl=False)

    @pytest.mark.e2etest
    def test_import_dsl_pipeline_submit_cancel(self, client: MLClient) -> None:
        def generate_dsl_pipeline():
            # 1. Load component funcs
            import_func = load_component("./tests/test_configs/import_job/import_component_test.yml")
            prep_func = load_component("./tests/test_configs/dsl_pipeline/nyc_taxi_data_regression/prep.yml")

            # 2. Construct pipeline
            @dsl.pipeline(compute="cpu-cluster", default_datastore="workspaceblobstore")
            def sample_pipeline():
                import_job = import_func(
                    type="azuresqldb", connection="azureml:my_username_password", query="select * from REGION"
                )
                prep_job = prep_func(raw_data=import_job.outputs.output)
                return {
                    "pipeline_job_imported_data": import_job.outputs.output,
                    "pipeline_job_prepped_data": prep_job.outputs.prep_data,
                }

            pipeline = sample_pipeline()
            pipeline.outputs.pipeline_job_imported_data.data = "/imported_data"
            pipeline.outputs.pipeline_job_prepped_data.data = "/prepped_data"
            pipeline.outputs.pipeline_job_prepped_data.mode = "rw_mount"
            return pipeline

        pipeline = generate_dsl_pipeline()
        self.validate_test_import_pipepine_submit_cancel(pipeline, client, is_dsl=True)

    def validate_test_import_pipepine_submit_cancel(
        self, pipeline: PipelineJob, client: MLClient, is_dsl: bool
    ) -> None:

        import_pipeline: PipelineJob = client.jobs.create_or_update(job=pipeline)

        import_step = "import_job" if is_dsl else "import_step"
        assert import_step in import_pipeline.jobs
        assert isinstance(import_pipeline.jobs[import_step], Import)
        assert import_pipeline.jobs[import_step].type == JobType.IMPORT
        assert import_pipeline.jobs[import_step].inputs["type"]._data == "azuresqldb"
        assert import_pipeline.jobs[import_step].inputs["connection"]._data == "azureml:my_username_password"
        assert import_pipeline.jobs[import_step].inputs["query"]._data == "select * from REGION"

        if not is_dsl:
            assert (
                import_pipeline.jobs[import_step].outputs["output"].path
                == "azureml://datastores/workspaceblobstore/paths/output_dir/"
            )
            assert import_pipeline.jobs[import_step].outputs["output"]._data.type == AssetTypes.MLTABLE
            assert (
                import_pipeline.jobs[import_step].outputs["output"]._data.path
                == import_pipeline.jobs["import_step"].outputs["output"].path
            )

        import_pipeline_2 = client.jobs.get(import_pipeline.name)
        assert import_step in import_pipeline_2.jobs
        assert isinstance(import_pipeline_2.jobs[import_step], Import)
        assert import_pipeline_2.jobs[import_step].type == import_pipeline.jobs[import_step].type
        assert import_pipeline_2.jobs[import_step].compute == "DataFactory"
        assert (
            import_pipeline_2.jobs[import_step].inputs["type"]._data
            == import_pipeline.jobs[import_step].inputs["type"]._data
        )
        assert (
            import_pipeline_2.jobs[import_step].inputs["connection"]._data
            == import_pipeline.jobs[import_step].inputs["connection"]._data
        )
        assert (
            import_pipeline_2.jobs[import_step].inputs["query"]._data
            == import_pipeline.jobs[import_step].inputs["query"]._data
        )

        if not is_dsl:
            assert (
                import_pipeline_2.jobs[import_step].outputs["output"].path
                == import_pipeline.jobs[import_step].outputs["output"].path
            )
            assert (
                import_pipeline_2.jobs[import_step].outputs["output"]._data.type
                == import_pipeline.jobs[import_step].outputs["output"]._data.type
            )
            assert (
                import_pipeline_2.jobs[import_step].outputs["output"]._data.path
                == import_pipeline.jobs[import_step].outputs["output"]._data.path
            )

        client.jobs.cancel(import_pipeline.name)
        import_pipeline_3 = client.jobs.get(import_pipeline.name)
        assert import_pipeline_3.status in (JobStatus.CANCEL_REQUESTED, JobStatus.CANCELED)

    @pytest.mark.e2etest
    def test_import_job_download(self, randstr: Callable[[str], str], client: MLClient) -> None:
        def wait_until_done(job: Job) -> None:
            poll_start_time = time.time()
            while job.status not in RunHistoryConstants.TERMINAL_STATUSES:
                time.sleep(_wait_before_polling(time.time() - poll_start_time))
                job = client.jobs.get(job.name)
            time.sleep(_wait_before_polling(time.time() - poll_start_time))

        job = client.jobs.create_or_update(
            load_job(
                "./tests/test_configs/import_job/import_job_test.yml",
                params_override=[{"name": randstr("name")}],
            )
        )

        wait_until_done(job)

        with TemporaryDirectory() as tmp_dirname:
            tmp_path = Path(tmp_dirname)
            client.jobs.download(name=job.name, download_path=tmp_path, all=True)

            best_child_run_artifact_dir = tmp_path / "artifacts"

            assert best_child_run_artifact_dir.exists()
            assert next(best_child_run_artifact_dir.iterdir(), None), "No artifacts for child run were downloaded"
