from datetime import time
from azure.core.exceptions import ResourceNotFoundError

import pytest
from deid_base_test_case import DeidBaseTestCase, BatchEnv
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *


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
            target_location=TargetStorageLocation(
                location=storage_location, prefix=self.OUTPUT_PATH
            ),
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAINTEXT,
        )

        client.begin_create_job(jobname, job)

        job = client.get_job(jobname)
        while job.status == JobStatus.NOT_STARTED:
            self.sleep(2)
            job = client.get_job(jobname)

        assert job.error is None, "Job should not have an error"
        assert job.status == JobStatus.RUNNING, "Job should be running"

        job = client.cancel_job(jobname)

        assert job.error is None, "Job should not have an error after cancelling"
        assert job.status == JobStatus.CANCELED, "Job should be cancelled"

        client.delete_job(jobname)

        with pytest.raises(ResourceNotFoundError):
            job = client.get_job(jobname)
