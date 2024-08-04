from datetime import time
from time import sleep
from azure.core.exceptions import HttpResponseError

import pytest
from deid_base_test_case import DeidBaseTestCase, BatchEnv
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *
from azure.core.polling import LROPoller


class TestHealthDeidentificationExceptionThrows(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_exception_throws(self, **kwargs):
        endpoint: str = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client(endpoint)
        assert client is not None

        jobname = self.generate_job_name()

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix="no_files_in_this_folder",
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH),
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAINTEXT,
        )

        lro: LROPoller = client.begin_create_job(jobname, job)
        with pytest.raises(HttpResponseError):
            lro.wait(timeout=60)

        job = client.get_job(jobname)

        assert job.status == JobStatus.FAILED
        assert job.error is not None
        assert job.error.code == "JobValidationError"
        assert len(job.error.message) > 10
