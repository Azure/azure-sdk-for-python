# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

    @record
    def test_features(self):
        self.create_resource_group()
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
