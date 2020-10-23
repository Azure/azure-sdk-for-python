# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.machinelearningservices import AzureMachineLearningWorkspaces

AZURE_LOCATION = 'eastus'


class MgmtMLServicesTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMLServicesTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(AzureMachineLearningWorkspaces)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_mlservices(self, resource_group):
        self.mgmt_client.operations.list()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
