# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.datafactory import DataFactoryManagementClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDataFactoryManagementIntegrationRuntimesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DataFactoryManagementClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_list_by_factory(self, resource_group):
        response = self.client.integration_runtimes.list_by_factory(
            resource_group_name=resource_group.name,
            factory_name="str",
            api_version="2018-06-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_create_or_update(self, resource_group):
        response = self.client.integration_runtimes.create_or_update(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            integration_runtime={
                "properties": "integration_runtime",
                "etag": "str",
                "id": "str",
                "name": "str",
                "type": "str",
            },
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_get(self, resource_group):
        response = self.client.integration_runtimes.get(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_update(self, resource_group):
        response = self.client.integration_runtimes.update(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            update_integration_runtime_request={"autoUpdate": "str", "updateDelayOffset": "str"},
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_delete(self, resource_group):
        response = self.client.integration_runtimes.delete(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_get_status(self, resource_group):
        response = self.client.integration_runtimes.get_status(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_list_outbound_network_dependencies_endpoints(self, resource_group):
        response = self.client.integration_runtimes.list_outbound_network_dependencies_endpoints(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_get_connection_info(self, resource_group):
        response = self.client.integration_runtimes.get_connection_info(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_regenerate_auth_key(self, resource_group):
        response = self.client.integration_runtimes.regenerate_auth_key(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            regenerate_key_parameters={"keyName": "str"},
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_list_auth_keys(self, resource_group):
        response = self.client.integration_runtimes.list_auth_keys(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_begin_start(self, resource_group):
        response = self.client.integration_runtimes.begin_start(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_begin_stop(self, resource_group):
        response = self.client.integration_runtimes.begin_stop(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_sync_credentials(self, resource_group):
        response = self.client.integration_runtimes.sync_credentials(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_get_monitoring_data(self, resource_group):
        response = self.client.integration_runtimes.get_monitoring_data(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_upgrade(self, resource_group):
        response = self.client.integration_runtimes.upgrade(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_remove_links(self, resource_group):
        response = self.client.integration_runtimes.remove_links(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            linked_integration_runtime_request={"factoryName": "str"},
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_integration_runtimes_create_linked_integration_runtime(self, resource_group):
        response = self.client.integration_runtimes.create_linked_integration_runtime(
            resource_group_name=resource_group.name,
            factory_name="str",
            integration_runtime_name="str",
            create_linked_integration_runtime_request={
                "dataFactoryLocation": "str",
                "dataFactoryName": "str",
                "name": "str",
                "subscriptionId": "str",
            },
            api_version="2018-06-01",
        )

        # please add some check logic here by yourself
        # ...
