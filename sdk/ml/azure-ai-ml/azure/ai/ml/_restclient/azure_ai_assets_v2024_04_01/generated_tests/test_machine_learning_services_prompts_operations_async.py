# coding=utf-8
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer import MachineLearningServicesPreparer
from testpreparer_async import MachineLearningServicesClientTestBaseAsync


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestMachineLearningServicesPromptsOperationsAsync(MachineLearningServicesClientTestBaseAsync):
    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_get(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = await client.prompts.get(
            name="str",
            version="str",
        )

        # please add some check logic here by yourself
        # ...

    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_create_or_update(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = await client.prompts.create_or_update(
            name="str",
            version="str",
            body={
                "dataUri": "str",
                "id": "str",
                "templatePath": "str",
                "description": "str",
                "properties": {"str": "str"},
                "stage": "str",
                "systemData": {
                    "createdAt": "2020-02-20 00:00:00",
                    "createdBy": "str",
                    "createdByType": "str",
                    "lastModifiedAt": "2020-02-20 00:00:00",
                },
                "tags": {"str": "str"},
            },
        )

        # please add some check logic here by yourself
        # ...

    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_list(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = client.prompts.list(
            name="str",
            list_view_type="str",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...

    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_get_latest(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = await client.prompts.get_latest(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_get_next_version(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = await client.prompts.get_next_version(
            name="str",
        )

        # please add some check logic here by yourself
        # ...

    @MachineLearningServicesPreparer()
    @recorded_by_proxy_async
    async def test_prompts_list_latest(self, machinelearningservices_endpoint):
        client = self.create_async_client(endpoint=machinelearningservices_endpoint)
        response = client.prompts.list_latest()
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
