﻿# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.logic
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtAppsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppsTest, self).setUp()
        self.logic_client = self.create_mgmt_client(
            azure.mgmt.logic.LogicManagementClient
        )

    @ResourceGroupPreparer(location="West US")
    def test_logic(self, resource_group, location):
        workflow_name = '12HourHeartBeat'
        self.logic_client.workflows.create_or_update(
            resource_group.name,
            workflow_name,
            azure.mgmt.logic.models.Workflow(
                location=location,
                definition={ 
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "triggers": {},
                    "actions": {},
                    "outputs": {}
                }
            )
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
