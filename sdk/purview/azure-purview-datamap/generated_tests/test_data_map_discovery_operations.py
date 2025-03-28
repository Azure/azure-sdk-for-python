# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import DataMapClientTestBase, DataMapPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDataMapDiscoveryOperations(DataMapClientTestBase):
    @DataMapPreparer()
    @recorded_by_proxy
    def test_discovery_query(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.discovery.query(
            body={
                "continuationToken": "str",
                "facets": [{"count": 0, "facet": "str", "sort": {"count": "str", "value": "str"}}],
                "filter": {},
                "keywords": "str",
                "limit": 0,
                "orderby": [{}],
                "taxonomySetting": {
                    "assetTypes": ["str"],
                    "facet": {"count": 0, "facet": "str", "sort": {"count": "str", "value": "str"}},
                },
            },
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_discovery_suggest(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.discovery.suggest(
            body={"filter": {}, "keywords": "str", "limit": 0},
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_discovery_auto_complete(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.discovery.auto_complete(
            body={"filter": {}, "keywords": "str", "limit": 0},
        )

        # please add some check logic here by yourself
        # ...
