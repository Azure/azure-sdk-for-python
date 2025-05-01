from datetime import time
from azure.core.exceptions import ResourceNotFoundError

import pytest
from deid_base_test_case import DeidBaseTestCase, BatchEnv
from devtools_testutils.aio import (
    recorded_by_proxy_async,
)

from azure.health.deidentification.models import *


class TestHealthDeidentificationCreateCancelDelete(DeidBaseTestCase):
    @BatchEnv()
    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_create_cancel_delete_async(self, **kwargs):
        endpoint: str = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client_async(endpoint)
        assert client is not None

        jobname = self.generate_job_name()

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix="example_patient_1",
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH, overwrite=True),
        )

        await client.begin_deidentify_documents(jobname, job)

        job = await client.get_job(jobname)
        while job.status == OperationStatus.NOT_STARTED:
            self.sleep(2)
            job = await client.get_job(jobname)

        assert job.error is None, "Job should not have an error"
        assert job.status == OperationStatus.RUNNING, "Job should be running"

        job = await client.cancel_job(jobname)

        assert job.error is None, "Job should not have an error after cancelling"
        assert job.status == OperationStatus.CANCELED, "Job should be cancelled"

        await client.delete_job(jobname)

        with pytest.raises(ResourceNotFoundError):
            job = await client.get_job(jobname)
