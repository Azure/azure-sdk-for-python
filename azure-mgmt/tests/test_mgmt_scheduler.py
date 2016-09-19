# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.scheduler
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtSchedulerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSchedulerTest, self).setUp()
        self.scheduler_client = self.create_mgmt_client(
            azure.mgmt.scheduler.SchedulerManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_scheduler(self):
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
