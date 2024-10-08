# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.hdinsight.aio import HDInsightManagementClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestHDInsightManagementPrivateEndpointConnectionsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(HDInsightManagementClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_by_cluster(self, resource_group):
        response = self.client.private_endpoint_connections.list_by_cluster(
            resource_group_name=resource_group.name,
            cluster_name="str",
            api_version="2024-08-01-preview",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_begin_create_or_update(self, resource_group):
        response = await (
            await self.client.private_endpoint_connections.begin_create_or_update(
                resource_group_name=resource_group.name,
                cluster_name="str",
                private_endpoint_connection_name="str",
                parameters={
                    "privateLinkServiceConnectionState": {
                        "status": "str",
                        "actionsRequired": "str",
                        "description": "str",
                    },
                    "id": "str",
                    "linkIdentifier": "str",
                    "name": "str",
                    "privateEndpoint": {"id": "str"},
                    "provisioningState": "str",
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
                api_version="2024-08-01-preview",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get(self, resource_group):
        response = await self.client.private_endpoint_connections.get(
            resource_group_name=resource_group.name,
            cluster_name="str",
            private_endpoint_connection_name="str",
            api_version="2024-08-01-preview",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_begin_delete(self, resource_group):
        response = await (
            await self.client.private_endpoint_connections.begin_delete(
                resource_group_name=resource_group.name,
                cluster_name="str",
                private_endpoint_connection_name="str",
                api_version="2024-08-01-preview",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...
