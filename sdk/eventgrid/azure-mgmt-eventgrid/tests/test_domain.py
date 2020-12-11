# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.mgmt.eventgrid import EventGridManagementClient

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtEventGridTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventGridTest, self).setUp()
        self.eventgrid_client = self.create_mgmt_client(EventGridManagementClient)

    @ResourceGroupPreparer()
    def test_domain(self, resource_group, location):
        # create
        DOMAIN_NAME = self.get_resource_name('domain')
        BODY = {
            "location": location
        }
        result = self.eventgrid_client.domains.begin_create_or_update(resource_group.name, DOMAIN_NAME, BODY)
        result.result()

        # update
        BODY = {
            "tags": {
                "tag1": "value1",
                "tag2": "value2"
            }
        }
        result = self.eventgrid_client.domains.begin_update(resource_group.name, DOMAIN_NAME, BODY)
        result.result()

        # get
        self.eventgrid_client.domains.get(resource_group.name, DOMAIN_NAME)

        # delete
        result = self.eventgrid_client.domains.begin_delete(resource_group.name, DOMAIN_NAME)
        result.result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
