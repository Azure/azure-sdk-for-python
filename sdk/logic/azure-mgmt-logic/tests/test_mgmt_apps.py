# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import azure.mgmt.logic
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtApps(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.logic_client = self.create_mgmt_client(
            azure.mgmt.logic.LogicManagementClient
        )

    @ResourceGroupPreparer(location="West US")
    @recorded_by_proxy
    def test_logic(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        workflow_name = '12HourHeartBeat'
        # workflow_name1 = workflow_name+'1'
        workflow=azure.mgmt.logic.models.Workflow(
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
        self.logic_client.workflows.create_or_update(resource_group.name,workflow_name,workflow)

        self.logic_client.workflows.get(resource_group.name, workflow_name)

        # self.logic_client.workflows.update(resource_group.name,workflow_name1)

        self.logic_client.workflows.delete(resource_group.name, workflow_name)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
