﻿# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import azure.mgmt.resource
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

class TestMgmtResourceLinks(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.resource.FeatureClient
        )

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_features_list(self):
        result = list(self.client.features.list_all())
        assert len(result) > 0