# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import AddedClientTestBase, AddedPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestAdded(AddedClientTestBase):
    @AddedPreparer()
    @recorded_by_proxy
    def test_v1(self, added_endpoint):
        client = self.create_client(endpoint=added_endpoint)
        response = client.v1(
            body={"enumProp": "str", "prop": "str", "unionProp": "str"},
            header_v2="str",
        )

        # please add some check logic here by yourself
        # ...

    @AddedPreparer()
    @recorded_by_proxy
    def test_v2(self, added_endpoint):
        client = self.create_client(endpoint=added_endpoint)
        response = client.v2(
            body={"enumProp": "str", "prop": "str", "unionProp": "str"},
        )

        # please add some check logic here by yourself
        # ...
