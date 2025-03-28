# coding=utf-8
import pytest
from azure.mgmt.mongocluster import MongoClusterMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestMongoClusterMgmtFirewallRulesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(MongoClusterMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_firewall_rules_get(self, resource_group):
        response = self.client.firewall_rules.get(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
            firewall_rule_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_firewall_rules_begin_create_or_update(self, resource_group):
        response = self.client.firewall_rules.begin_create_or_update(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
            firewall_rule_name="str",
            resource={
                "id": "str",
                "name": "str",
                "properties": {"endIpAddress": "str", "startIpAddress": "str", "provisioningState": "str"},
                "systemData": {
                    "createdAt": "2020-02-20 00:00:00",
                    "createdBy": "str",
                    "createdByType": "str",
                    "lastModifiedAt": "2020-02-20 00:00:00",
                    "lastModifiedBy": "str",
                    "lastModifiedByType": "str",
                },
                "type": "str",
            },
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_firewall_rules_begin_delete(self, resource_group):
        response = self.client.firewall_rules.begin_delete(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
            firewall_rule_name="str",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_firewall_rules_list_by_mongo_cluster(self, resource_group):
        response = self.client.firewall_rules.list_by_mongo_cluster(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
