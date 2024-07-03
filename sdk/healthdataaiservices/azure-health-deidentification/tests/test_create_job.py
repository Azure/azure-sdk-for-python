from deid_base_test_case import *
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *
from azure.core.polling import LROPoller


class TestHealthDeidentificationCreateJob(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_create_job(self, **kwargs):
        endpoint = kwargs.pop("healthdataaiservices_deid_service_endpoint")
        storage_name = kwargs.pop("healthdataaiservices_storage_account_name")
        container_name = kwargs.pop("healthdataaiservices_storage_container_name")
        # storage_location = f"https://{storage_name}.blob.core.windows.net/{container_name}"
        storage_location = kwargs.pop("healthdataaiservices_sas_uri")
        client = self.make_client(endpoint)
        assert client is not None

        jobname = self.generate_job_name()
        print(f"Job name: {jobname}")

        job = DeidentificationJob(
            source_location=SourceStorageLocation(
                location=storage_location,
                prefix="example_patient_1",
            ),
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH),
            operation=OperationType.SURROGATE,
            data_type=DocumentDataType.PLAIN_TEXT,
        )

        lro: LROPoller = client.begin_create_job(jobname, job)
        lro.wait(timeout=60)

        # TODO: This doesn't work...
        finished_job: DeidentificationJob = lro.result()
        # finished_job = client.get_job(jobname)

        assert finished_job.status == JobStatus.SUCCEEDED
        assert finished_job.name == jobname
        assert finished_job.operation == OperationType.SURROGATE
        assert finished_job.data_type == DocumentDataType.PLAIN_TEXT
        assert finished_job.summary.total_documents == 2
        assert finished_job.summary.successful == 2
        assert finished_job.summary.failed == 0
        assert finished_job.started_at > finished_job.created_at
        assert finished_job.last_updated_at > finished_job.started_at
        assert finished_job.redaction_format is None
        assert finished_job.error is None
        assert storage_location.starts_with(finished_job.source_location.location)
        assert finished_job.source_location.prefix == "example_patient_1"
