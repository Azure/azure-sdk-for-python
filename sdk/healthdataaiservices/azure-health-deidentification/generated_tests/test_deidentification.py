# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import DeidentificationClientTestBase, DeidentificationPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDeidentification(DeidentificationClientTestBase):
    @DeidentificationPreparer()
    @recorded_by_proxy
    def test_get_job(self, deidentification_endpoint):
        client = self.create_client(endpoint=deidentification_endpoint)
        response = client.get_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy
    def test_begin_deidentify_documents(self, deidentification_endpoint):
        client = self.create_client(endpoint=deidentification_endpoint)
        response = client.begin_deidentify_documents(
            name="str",
            resource={
                "createdAt": "2020-02-20 00:00:00",
                "lastUpdatedAt": "2020-02-20 00:00:00",
                "name": "str",
                "sourceLocation": {"location": "str", "prefix": "str", "extensions": ["str"]},
                "status": "str",
                "targetLocation": {"location": "str", "prefix": "str", "overwrite": bool},
                "customizations": {"redactionFormat": "str", "surrogateLocale": "str"},
                "error": ~azure.core.ODataV4Format,
                "operation": "str",
                "startedAt": "2020-02-20 00:00:00",
                "summary": {"bytesProcessed": 0, "canceled": 0, "failed": 0, "successful": 0, "total": 0},
            },
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy
    def test_cancel_job(self, deidentification_endpoint):
        client = self.create_client(endpoint=deidentification_endpoint)
        response = client.cancel_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy
    def test_delete_job(self, deidentification_endpoint):
        client = self.create_client(endpoint=deidentification_endpoint)
        response = client.delete_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy
    def test_deidentify_text(self, deidentification_endpoint):
        client = self.create_client(endpoint=deidentification_endpoint)
        response = client.deidentify_text(
            body={
                "inputText": "str",
                "customizations": {"redactionFormat": "str", "surrogateLocale": "str"},
                "operation": "str",
            },
        )

        # please add some check logic here by yourself
        # ...
