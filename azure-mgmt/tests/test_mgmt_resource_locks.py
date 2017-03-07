# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourceLocksTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceLocksTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.resource.Client,
            subscription_id=self.settings.SUBSCRIPTION_ID,
        )

    @record
    def test_locks(self):
        lock_operations = self.client.management_locks()

        self.create_resource_group()
        lock_name = 'pylockrg'

        lock = lock_operations.create_or_update_at_resource_group_level(
            self.group_name,
            lock_name,
            {
                'level': 'CanNotDelete'
            }
        )
        self.assertIsNotNone(lock)

        locks = list(lock_operations.list_at_resource_group_level(
            self.group_name
        ))
        self.assertEqual(len(locks), 1)

        lock = lock_operations.delete_at_resource_group_level(
            self.group_name,
            lock_name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
