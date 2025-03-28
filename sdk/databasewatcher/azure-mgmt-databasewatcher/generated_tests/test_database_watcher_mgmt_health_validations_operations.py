# coding=utf-8
import pytest
from azure.mgmt.databasewatcher import DatabaseWatcherMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDatabaseWatcherMgmtHealthValidationsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DatabaseWatcherMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_health_validations_get(self, resource_group):
        response = self.client.health_validations.get(
            resource_group_name=resource_group.name,
            watcher_name="str",
            health_validation_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_health_validations_list_by_parent(self, resource_group):
        response = self.client.health_validations.list_by_parent(
            resource_group_name=resource_group.name,
            watcher_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_health_validations_begin_start_validation(self, resource_group):
        response = self.client.health_validations.begin_start_validation(
            resource_group_name=resource_group.name,
            watcher_name="str",
            health_validation_name="str",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...
