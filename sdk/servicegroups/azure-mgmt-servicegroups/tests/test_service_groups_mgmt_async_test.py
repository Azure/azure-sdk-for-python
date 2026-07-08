# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import pytest
from azure.mgmt.servicegroups.aio import ServiceGroupsMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"
SERVICE_GROUP_NAME = "test-service-group-python-sdk"


@pytest.mark.live_test_only
class TestServiceGroupsMgmtOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ServiceGroupsMgmtClient, is_async=True)
        self.tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_get_delete_service_group(self, resource_group):
        # Create a service group under the tenant root service group
        create_response = await (
            await self.client.begin_create_or_update_service_group(
                service_group_name=SERVICE_GROUP_NAME,
                create_service_group_request={
                    "properties": {
                        "displayName": "ServiceGroup 1 Name",
                        "parent": {
                            "resourceId": f"/providers/Microsoft.Management/serviceGroups/{self.tenant_id}",
                        },
                    },
                },
            )
        ).result()
        assert create_response is not None
        assert create_response["name"] == SERVICE_GROUP_NAME

        # Get the service group
        get_response = await self.client.service_groups.get(
            service_group_name=SERVICE_GROUP_NAME,
        )
        assert get_response is not None
        assert get_response["name"] == SERVICE_GROUP_NAME

        # Delete the service group
        await (
            await self.client.begin_delete_service_group(
                service_group_name=SERVICE_GROUP_NAME,
            )
        ).result()
