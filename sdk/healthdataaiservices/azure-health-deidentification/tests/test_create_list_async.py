from deid_base_test_case import *
from devtools_testutils.aio import (
    recorded_by_proxy_async,
)

from azure.health.deidentification.models import *
import pytest


class TestHealthDeidentificationCreateAndListJob(DeidBaseTestCase):
    @BatchEnv()
    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_create_list_async(self, **kwargs):
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
            target_location=TargetStorageLocation(
                location=storage_location, prefix=self.OUTPUT_PATH
            ),
            operation=OperationType.TAG,
            data_type=DocumentDataType.PLAINTEXT,
        )

        await client.begin_create_job(jobname, job)
        jobs = client.list_jobs()

        job = None
        jobsToLookThrough = 10
        async for j in jobs:
            jobsToLookThrough -= 1
            if j.name == jobname:
                job = j
                break
            elif jobsToLookThrough <= 0:
                raise Exception("Job not found in list_jobs")

        assert job.name == jobname
        assert job.status == JobStatus.NOT_STARTED or job.status == JobStatus.RUNNING
        assert job.operation == OperationType.TAG
        assert job.error is None
        assert job.summary is None
        assert job.created_at is not None
        assert job.last_updated_at is not None
        assert job.redaction_format is None
