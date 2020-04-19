# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 567
# Methods Covered : 106
# Examples Total  : 126
# Examples Tested : 0
# Coverage %      : 0
# ----------------------

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        DOMAIN_NAME = "myDomain"
        NAME = "my"
        LOCATION = "myLocation"
        DELETED_SITE_ID = "myDeletedSiteId"
        DETECTOR_NAME = "myDetector"
        SITE_NAME = "mySite"
        DIAGNOSTIC_CATEGORY = "myDiagnosticCategory"
        ANALYSIS_NAME = "myAnalysis"
        SLOT = "mySlot"
        APP_SETTING_KEY = "myAppSettingKey"
        INSTANCE_ID = "myInstanceId"
        OPERATION_ID = "myOperationId"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        AUTHPROVIDER = "myAuthprovider"
        USERID = "myUserid"
        PR_ID = "myPrId"


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
