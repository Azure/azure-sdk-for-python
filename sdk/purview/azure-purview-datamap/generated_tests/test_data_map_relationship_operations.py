# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import DataMapClientTestBase, DataMapPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDataMapRelationshipOperations(DataMapClientTestBase):
    @DataMapPreparer()
    @recorded_by_proxy
    def test_relationship_create(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.relationship.create(
            body={
                "attributes": {"str": {}},
                "createTime": 0,
                "createdBy": "str",
                "end1": {"guid": "str", "typeName": "str", "uniqueAttributes": {"str": {}}},
                "end2": {"guid": "str", "typeName": "str", "uniqueAttributes": {"str": {}}},
                "guid": "str",
                "homeId": "str",
                "label": "str",
                "lastModifiedTS": "str",
                "provenanceType": 0,
                "status": "str",
                "typeName": "str",
                "updateTime": 0,
                "updatedBy": "str",
                "version": 0,
            },
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_relationship_update(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.relationship.update(
            body={
                "attributes": {"str": {}},
                "createTime": 0,
                "createdBy": "str",
                "end1": {"guid": "str", "typeName": "str", "uniqueAttributes": {"str": {}}},
                "end2": {"guid": "str", "typeName": "str", "uniqueAttributes": {"str": {}}},
                "guid": "str",
                "homeId": "str",
                "label": "str",
                "lastModifiedTS": "str",
                "provenanceType": 0,
                "status": "str",
                "typeName": "str",
                "updateTime": 0,
                "updatedBy": "str",
                "version": 0,
            },
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_relationship_get(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.relationship.get(
            guid="str",
        )

        # please add some check logic here by yourself
        # ...

    @DataMapPreparer()
    @recorded_by_proxy
    def test_relationship_delete(self, datamap_endpoint):
        client = self.create_client(endpoint=datamap_endpoint)
        response = client.relationship.delete(
            guid="str",
        )

        # please add some check logic here by yourself
        # ...
