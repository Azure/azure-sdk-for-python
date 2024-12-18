# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import azure.mgmt.resource
import azure.mgmt.resource.changes
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

@pytest.mark.live_test_only
class TestMgmtResourceLinks(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.resource.changes.ChangesClient
        )
        self.resource_client = self.create_mgmt_client(
            azure.mgmt.resource.ResourceManagementClient
        )

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_changes_list(self, resource_group):
        resource_name = self.get_resource_name("test_resource")

        create_result = self.resource_client.resources.begin_create_or_update(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            parameters={'location': 'eastus'},
            api_version = "2019-07-01"
        )

        result = list(self.client.changes.list(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            resource_type="availabilitySets",
            resource_name=resource_name,
        ))

        assert len(result) > 0

        delete_result = self.resource_client.resources.begin_delete(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version = "2019-07-01"
        )
        delete_result.wait()
