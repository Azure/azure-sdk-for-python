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
        self.locks_client = self.create_mgmt_client(
            azure.mgmt.resource.ManagementLockClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_locks(self):
        lock_name = 'pylockrg'

        lock = self.locks_client.management_locks.create_or_update_at_resource_group_level(
            self.group_name,
            lock_name,
            {
                'level': 'CanNotDelete'
            }
        )
        self.assertIsNotNone(lock)

        locks = list(self.locks_client.management_locks.list_at_resource_group_level(
            self.group_name
        ))
        self.assertEqual(len(locks), 1)

        lock = self.locks_client.management_locks.delete_at_resource_group_level(
            self.group_name,
            lock_name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
