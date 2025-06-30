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
        input_prefix = "example_patient_1"
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client_async(endpoint)
        assert client is not None

        jobname = self.generate_job_name()

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix=input_prefix,
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH, overwrite=True),
            operation_type=DeidentificationOperationType.SURROGATE,
        )

        lro: AsyncLROPoller = await client.begin_deidentify_documents(jobname, job)
        await lro.wait()

        finished_job: DeidentificationJob = await lro.result()

        assert finished_job.status == OperationStatus.SUCCEEDED
        assert finished_job.job_name == jobname
        assert finished_job.operation_type == DeidentificationOperationType.SURROGATE
        assert finished_job.summary is not None
        assert finished_job.summary.total_count == 3
        assert finished_job.summary.successful_count == 3
        assert finished_job.summary.failed_count == 0
        assert finished_job.started_at is not None
        assert finished_job.started_at > finished_job.created_at
        assert finished_job.last_updated_at > finished_job.started_at
        assert finished_job.customizations is not None
        assert finished_job.customizations.surrogate_locale == "en-US"
        assert finished_job.error is None
        assert finished_job.source_location.prefix == input_prefix

        files = client.list_job_documents(jobname)
        count = 0
        async for my_file in files:
            assert len(my_file.id) == 36  # GUID
            assert input_prefix in my_file.input_location.location
            assert my_file.status == OperationStatus.SUCCEEDED
            assert my_file.output_location is not None
            assert self.OUTPUT_PATH in my_file.output_location.location
            count += 1
        assert count == 3, f"Expected 3 files, found {count}"
