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

import azure.mgmt.scheduler
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtSchedulerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSchedulerTest, self).setUp()
        self.scheduler_client = self.create_mgmt_client(
            azure.mgmt.scheduler.SchedulerManagementClientConfiguration,
            azure.mgmt.scheduler.SchedulerManagementClient
        )

    @record
    def test_scheduler(self):
        self.create_resource_group()

        account_name = self.get_resource_name('pyarmscheduler')

        jobcollection_name = "myjobcollection"
        self.scheduler_client.job_collections.create_or_update(
            self.group_name,
            jobcollection_name,
            azure.mgmt.scheduler.models.JobCollectionDefinition(
                location="West US",
                properties=azure.mgmt.scheduler.models.JobCollectionProperties(
                    sku=azure.mgmt.scheduler.models.Sku(name="Free")
                )
            )
        )

        result = self.scheduler_client.job_collections.get(
            self.group_name, 
            jobcollection_name,
        )
        self.assertEqual(result.name, jobcollection_name)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
