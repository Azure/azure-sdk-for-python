# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import AddedClientTestBase, AddedPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestAddedInterfaceV2Operations(AddedClientTestBase):
    @AddedPreparer()
    @recorded_by_proxy
    def test_interface_v2_v2_in_interface(self, added_endpoint):
        client = self.create_client(endpoint=added_endpoint)
        response = client.interface_v2.v2_in_interface(
            body={"enumProp": "str", "prop": "str", "unionProp": "str"},
        )

        # please add some check logic here by yourself
        # ...
