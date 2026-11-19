from datetime import time
from azure.core.exceptions import ResourceNotFoundError

import pytest
from deid_base_test_case import DeidBaseTestCase, BatchEnv
from devtools_testutils.aio import (
    recorded_by_proxy_async,
)

from azure.health.deidentification.models import *

MAX_POLL_ATTEMPTS = 60


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

        # The service may delay reporting the NotStarted -> Running transition, so a small job can go straight
        # from NotStarted to a terminal state without ever being observed as Running.
        poll_attempts = 1
        job = await client.get_job(jobname)
        while job.status == OperationStatus.NOT_STARTED and poll_attempts < MAX_POLL_ATTEMPTS:
            self.sleep(2)
            job = await client.get_job(jobname)
            poll_attempts += 1

        assert (
            job.status != OperationStatus.NOT_STARTED
        ), f"Job '{jobname}' did not leave the NotStarted state after {poll_attempts} polling attempts."
        if job.status == OperationStatus.FAILED:
            diagnostics = await self.describe_job_async(client, jobname)
            pytest.fail(f"Job '{jobname}' failed before it could be canceled.\n{diagnostics}")
        assert job.error is None, f"Job '{jobname}' should not have an error: {job.error}"

        if job.status == OperationStatus.RUNNING:
            job = await client.cancel_job(jobname)

            assert job.error is None, f"Job '{jobname}' should not have an error after cancelling: {job.error}"
            # Canceling a job that has already completed has no effect, so it may report Succeeded instead.
            assert job.status in (
                OperationStatus.CANCELED,
                OperationStatus.SUCCEEDED,
            ), f"Job '{jobname}' should be Canceled (or Succeeded if it completed before cancellation): {job.status}"
        else:
            assert job.status in (
                OperationStatus.SUCCEEDED,
                OperationStatus.CANCELED,
            ), f"Unexpected job status for '{jobname}': {job.status}"
            print(f"Job '{jobname}' was already {job.status} before cancel; skipping cancel.")

        await client.delete_job(jobname)

        with pytest.raises(ResourceNotFoundError):
            job = await client.get_job(jobname)
