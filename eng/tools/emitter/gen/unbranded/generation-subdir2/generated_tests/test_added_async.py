# coding=utf-8
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer import AddedPreparer
from testpreparer_async import AddedClientTestBaseAsync


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestAddedAsync(AddedClientTestBaseAsync):
    @AddedPreparer()
    @recorded_by_proxy_async
    async def test_v1(self, added_endpoint):
        client = self.create_async_client(endpoint=added_endpoint)
        response = await client.v1(
            body={"enumProp": "str", "prop": "str", "unionProp": "str"},
            header_v2="str",
        )

        # please add some check logic here by yourself
        # ...

    @AddedPreparer()
    @recorded_by_proxy_async
    async def test_v2(self, added_endpoint):
        client = self.create_async_client(endpoint=added_endpoint)
        response = await client.v2(
            body={"enumProp": "str", "prop": "str", "unionProp": "str"},
        )

        # please add some check logic here by yourself
        # ...
