# coding=utf-8
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer import DeidentificationPreparer
from testpreparer_async import DeidentificationClientTestBaseAsync


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDeidentificationAsync(DeidentificationClientTestBaseAsync):
    @DeidentificationPreparer()
    @recorded_by_proxy_async
    async def test_get_job(self, deidentification_endpoint):
        client = self.create_async_client(endpoint=deidentification_endpoint)
        response = await client.get_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy_async
    async def test_begin_deidentify_documents(self, deidentification_endpoint):
        client = self.create_async_client(endpoint=deidentification_endpoint)
        response = await (
            await client.begin_deidentify_documents(
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
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy_async
    async def test_cancel_job(self, deidentification_endpoint):
        client = self.create_async_client(endpoint=deidentification_endpoint)
        response = await client.cancel_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy_async
    async def test_delete_job(self, deidentification_endpoint):
        client = self.create_async_client(endpoint=deidentification_endpoint)
        response = await client.delete_job(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @DeidentificationPreparer()
    @recorded_by_proxy_async
    async def test_deidentify_text(self, deidentification_endpoint):
        client = self.create_async_client(endpoint=deidentification_endpoint)
        response = await client.deidentify_text(
            body={
                "inputText": "str",
                "customizations": {"redactionFormat": "str", "surrogateLocale": "str"},
                "operation": "str",
            },
        )

        # please add some check logic here by yourself
        # ...
