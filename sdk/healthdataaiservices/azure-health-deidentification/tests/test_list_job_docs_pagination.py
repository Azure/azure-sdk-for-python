from deid_base_test_case import *
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *
from azure.core.polling import LROPoller


class TestHealthDeidentificationCreateAndListJob(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_list_job_docs_pagination(self, **kwargs):
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
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH),
            operation=OperationType.REDACT,
            customizations=JobCustomizationOptions(redaction_format="[{type}]"),
        )

        lro: LROPoller = client.begin_deidentify_documents(jobname, job)
        lro.wait(timeout=60)
        job_documents = client.list_job_documents(job_name=jobname, maxpagesize=2)

        count = 0
        job_ids = []
        for j in job_documents:
            count += 1
            job_ids.append(j.id)

        assert count == 3
        assert len(set(job_ids)) == 3  # Each job ID should be unique
