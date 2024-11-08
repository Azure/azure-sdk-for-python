from deid_base_test_case import *
from devtools_testutils.aio import (
    recorded_by_proxy_async,
)

from azure.health.deidentification.models import *
from azure.core.polling import AsyncLROPoller
import pytest


class TestHealthDeidentificationCreateJobWaitUntil(DeidBaseTestCase):
    @BatchEnv()
    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_create_wait_finish_async(self, **kwargs):
        endpoint: str = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        inputPrefix = "example_patient_1"
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client_async(endpoint)
        assert client is not None

        jobname = self.generate_job_name()

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix=inputPrefix,
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH),
            operation=OperationType.SURROGATE,
        )

        lro: AsyncLROPoller = await client.begin_deidentify_documents(jobname, job)
        await lro.wait()

        finished_job: DeidentificationJob = await lro.result()

        assert finished_job.status == JobStatus.SUCCEEDED
        assert finished_job.name == jobname
        assert finished_job.operation == OperationType.SURROGATE
        assert finished_job.summary is not None
        assert finished_job.summary.total == 2
        assert finished_job.summary.successful == 2
        assert finished_job.summary.failed == 0
        assert finished_job.started_at is not None
        assert finished_job.started_at > finished_job.created_at
        assert finished_job.last_updated_at > finished_job.started_at
        assert finished_job.customizations is None
        assert finished_job.error is None
        assert finished_job.source_location.prefix == inputPrefix

        files = client.list_job_documents(jobname)
        files = client.list_job_documents_internal(jobname)  # TODO - this method should be private
        count = 0
        async for my_file in files:
            assert len(my_file.id) == 36  # GUID
            assert my_file.input.location.startswith(inputPrefix)
            assert my_file.status == OperationState.SUCCEEDED
            assert my_file.output is not None
            assert my_file.output.location.startswith(self.OUTPUT_PATH)
            count += 1
        assert count == 2, f"Expected 2 files, found {count}"
