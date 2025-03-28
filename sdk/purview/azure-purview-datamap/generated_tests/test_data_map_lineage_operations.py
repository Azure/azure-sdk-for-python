# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import DataMapClientTestBase, DataMapPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDataMapLineageOperations(DataMapClientTestBase):
    @DataMapPreparer()
    @recorded_by_proxy
    def test_lineage_get(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.lineage.get(
            guid="str",
            direction="str",
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_lineage_get_next_page(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.lineage.get_next_page(
            guid="str",
            direction="str",
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_lineage_get_by_unique_attribute(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.lineage.get_by_unique_attribute(
            type_name="str",
            direction="str",
        )

        # please add some check logic here by yourself
        # ...
