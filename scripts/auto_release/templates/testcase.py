# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import {{package_name_dot}}
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmt{{package}}(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            {{package_name_dot}}.{{client}})

    @recorded_by_proxy
    def test_{{package}}_{{operation}}_list(self):
        result = self.mgmt_client.{{operation}}.{{function}}()
        assert list(result) is not None

