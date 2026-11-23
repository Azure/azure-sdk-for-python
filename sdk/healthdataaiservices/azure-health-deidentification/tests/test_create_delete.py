from datetime import time
from azure.core.exceptions import ResourceNotFoundError

import pytest
from deid_base_test_case import DeidBaseTestCase, BatchEnv
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *

MAX_POLL_ATTEMPTS = 60


class TestHealthDeidentificationCreateCancelDelete(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_create_cancel_delete(self, **kwargs):
        endpoint: str = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client(endpoint)
        assert client is not None

        jobname = self.generate_job_name()

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix="example_patient_1",
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH, overwrite=True),
            operation_type=DeidentificationOperationType.SURROGATE,
        )

        # The test polls the job itself; a background LRO poller would race it for recorded GET responses.
        client.begin_deidentify_documents(jobname, job, polling=False)

        # The service may delay reporting the NotStarted -> Running transition, so a small job can go straight
        # from NotStarted to a terminal state without ever being observed as Running.
        poll_attempts = 1
        job = client.get_job(jobname)
        while job.status == OperationStatus.NOT_STARTED and poll_attempts < MAX_POLL_ATTEMPTS:
            self.sleep(2)
            job = client.get_job(jobname)
            poll_attempts += 1

        assert (
            job.status != OperationStatus.NOT_STARTED
        ), f"Job '{jobname}' did not leave the NotStarted state after {poll_attempts} polling attempts."
        if job.status == OperationStatus.FAILED:
            pytest.fail(f"Job '{jobname}' failed before it could be canceled.\n{self.describe_job(client, jobname)}")
        assert job.error is None, f"Job '{jobname}' should not have an error: {job.error}"

        if job.status == OperationStatus.RUNNING:
            job = client.cancel_job(jobname)

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

        client.delete_job(jobname)

        with pytest.raises(ResourceNotFoundError):
            job = client.get_job(jobname)
