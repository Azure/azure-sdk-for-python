# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.imagebuilder import ImageBuilderClient
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtImageBuilder(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(ImageBuilderClient)

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_list_by_resource_group(self, resource_group):
        assert list(self.client.virtual_machine_image_templates.list_by_resource_group(resource_group.name)) == []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())
