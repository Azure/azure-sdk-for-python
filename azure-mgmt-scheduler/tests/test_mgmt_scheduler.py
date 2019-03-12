﻿# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from datetime import timedelta
import unittest

import azure.mgmt.scheduler.models
import azure.mgmt.scheduler.patch

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

    @ResourceGroupPreparer()
    def test_scheduler_job_custom_time(self, resource_group, location):
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

        job_properties = azure.mgmt.scheduler.models.JobProperties.from_dict(
            {
                "action": {
                    "request": {
                        "uri": "http://example.org",
                        "method": "GET"
                    },
                    "type": "HTTP",
                    "retry_policy": {
                        "retry_type": "fixed",
                        "retry_interval": timedelta(days=1),
                        "retry_count": 4
                    },
                },
                "recurrence": {
                    "frequency": "hour",
                    "end_time": "2017-09-10T18:50:16.905Z",
                    "interval": 10
                },
                "state": "Disabled"
            }
        )
        self.assertEqual(job_properties.action.retry_policy.retry_interval, timedelta(days=1))

        job_name = "myjob"
        self.scheduler_client.jobs.create_or_update(
            resource_group.name,
            jobcollection_name,
            job_name,
            job_properties
        )

        job = self.scheduler_client.jobs.get(
            resource_group.name,
            jobcollection_name,
            job_name
        )
        self.assertEqual(job.properties.action.retry_policy.retry_interval, timedelta(days=1))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
