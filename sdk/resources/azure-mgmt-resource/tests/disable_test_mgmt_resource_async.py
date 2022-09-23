# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import unittest

import azure.mgmt.resource.resources.v2019_10_01

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

from _aio_testcase import AzureMgmtAsyncTestCase


class MgmtResourceAioTest(AzureMgmtAsyncTestCase):

    def setUp(self):
        super(MgmtResourceAioTest, self).setUp()
        from azure.mgmt.resource.resources.aio import ResourceManagementClient
        self.resource_client = self.create_mgmt_aio_client(
            ResourceManagementClient
        )

    @unittest.skip('hard to test')
    def test_resource_groups(self):
        group_name = "test_mgmt_resource_test_resource_groups457f1050"
        # Create or update
        params_create = azure.mgmt.resource.resources.v2019_10_01.models.ResourceGroup(
            location=self.region,
            tags={
                'tag1': 'value1',
            },
        )
        result = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.create_or_update(
                group_name,
                params_create,
            )
        )

        # Get
        result_get = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.get(group_name)
        )
        self.assertEqual(result_get.name, group_name)
        self.assertEqual(result_get.tags['tag1'], 'value1')

        # Check existence
        result_check = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.check_existence(
                group_name,
            )
        )
        self.assertTrue(result_check)

        result_check = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.check_existence(
                'unknowngroup',
            )
        )
        self.assertFalse(result_check)

        # List
        result_list = self.to_list(
            self.resource_client.resource_groups.list()
        )
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        result_list_top = self.resource_client.resource_groups.list(top=2)

        # Patch
        params_patch = azure.mgmt.resource.resources.v2019_10_01.models.ResourceGroupPatchable(
            tags={
                'tag1': 'valueA',
                'tag2': 'valueB',
            },
        )
        result_patch = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.update(
                group_name,
                params_patch,
            )
        )
        self.assertEqual(result_patch.tags['tag1'], 'valueA')
        self.assertEqual(result_patch.tags['tag2'], 'valueB')

        # List resources
        resources = self.to_list(
            self.resource_client.resources.list_by_resource_group(
                group_name
            )
        )

        resources = list(resources)

        # Export template
        BODY = {
          'resources': ['*']
        }
        result = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.begin_export_template(
                group_name,
                BODY
            )
        )
        template = self.event_loop.run_until_complete(
            result.result()
        )
        # self.assertTrue(hasattr(template, 'template'))

        # Delete
        result = self.event_loop.run_until_complete(
            self.resource_client.resource_groups.begin_delete(group_name)
        )
        self.event_loop.run_until_complete(
            result.result()
        )
