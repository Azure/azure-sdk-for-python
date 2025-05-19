from deid_base_test_case import *
from devtools_testutils import (
    recorded_by_proxy,
)

from azure.health.deidentification.models import *
from azure.core.paging import ItemPaged


class TestHealthDeidentificationCreateAndListJob(DeidBaseTestCase):
    @BatchEnv()
    @recorded_by_proxy
    def test_list_job_docs_pagination(self, **kwargs):
        """
        This test is verifying that pagination is working as expected.
        The nextLink is being obfuscated by the SDK so we want to verify it is being used and not ignored
        """
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
            target_location=TargetStorageLocation(location=storage_location, prefix=self.OUTPUT_PATH, overwrite=True),
            operation_type=DeidentificationOperationType.REDACT,
            customizations=DeidentificationJobCustomizationOptions(redaction_format="[{type}]"),
        )

        client.begin_deidentify_documents(jobname, job).result(180)
        job_documents = client.list_job_documents(job_name=jobname, maxpagesize=2)

        _get_next = job_documents._args[0]  # type: ignore
        _extract_data = job_documents._args[1]  # type: ignore

        job_documents_paged = ItemPaged(
            get_next=_get_next,
            extract_data=_extract_data,
        )

        job_ids = []

        # Verify the first page contains our maxpagesize of 2
        page_iterator = job_documents_paged.by_page()
        first_page = next(page_iterator)
        first_page_items = list(first_page)
        assert len(first_page_items) == 2, f"Expected 2 items in the first page, found {len(first_page_items)}"
        job_ids.extend(item.id for item in first_page_items)

        # Verify there are no duplicates
        assert len(set(job_ids)) == 2

        # Verify the second page has the remaining 1 item
        second_page = next(page_iterator)
        second_page_items = list(second_page)
        assert len(second_page_items) == 1, f"Expected 1 item in the second page, found {len(second_page_items)}"
        job_ids.extend(item.id for item in second_page_items)

        # Verify the total count and uniqueness of job IDs
        assert len(set(job_ids)) == 3, "Each job ID should be unique"
