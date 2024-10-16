from deid_base_test_case import *
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *
from azure.core.polling import LROPoller


class TestHealthDeidentificationCreateJobWaitUntil(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_create_wait_finish(self, **kwargs):
        endpoint: str = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        inputPrefix = "example_patient_1"
        storage_location: str = self.get_storage_location(kwargs)
        client = self.make_client(endpoint)
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
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAINTEXT,
        )

        lro: LROPoller = client.begin_create_job(jobname, job)
        lro.wait(timeout=60)

        finished_job: DeidentificationJob = lro.result()

        assert finished_job.status == JobStatus.SUCCEEDED
        assert finished_job.name == jobname
        assert finished_job.operation == OperationType.SURROGATE
        assert finished_job.data_type == DocumentDataType.PLAINTEXT
        assert finished_job.summary.total == 2
        assert finished_job.summary.successful == 2
        assert finished_job.summary.failed == 0
        assert finished_job.started_at > finished_job.created_at
        assert finished_job.last_updated_at > finished_job.started_at
        assert finished_job.redaction_format is None
        assert finished_job.error is None
        assert finished_job.source_location.prefix == inputPrefix

        files = client.list_job_documents(jobname)
        count = 0
        for my_file in files:
            assert len(my_file.id) == 36  # GUID
            assert my_file.input.path.startswith(inputPrefix)
            assert my_file.status == OperationState.SUCCEEDED
            assert my_file.output.path.startswith(self.OUTPUT_PATH)
            count += 1
        assert count == 2, f"Expected 2 files, found {count}"
