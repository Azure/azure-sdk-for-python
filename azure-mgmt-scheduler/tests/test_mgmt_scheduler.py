# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.scheduler

from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
)

class MgmtSchedulerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSchedulerTest, self).setUp()
        self.scheduler_client = self.create_mgmt_client(
            azure.mgmt.scheduler.SchedulerManagementClient
        )

    @ResourceGroupPreparer()
    def test_scheduler(self, resource_group, location):
        jobcollection_name = "myjobcollection"
        self.scheduler_client.job_collections.create_or_update(
            resource_group.name,
            jobcollection_name,
            azure.mgmt.scheduler.models.JobCollectionDefinition(
                location=location,
                properties=azure.mgmt.scheduler.models.JobCollectionProperties(
                    sku=azure.mgmt.scheduler.models.Sku(name="Free")
                )
            )
        )

        result = self.scheduler_client.job_collections.get(
            resource_group.name, 
            jobcollection_name,
        )
        self.assertEqual(result.name, jobcollection_name)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
