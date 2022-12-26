# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from testcase import LoadtestingPowerShellPreparer, LoadtestingTest
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher, set_custom_default_matcher

DISPLAY_NAME = "TestingResource"
class TestLoadTestAdministrationClient(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.create_or_update_test(
            loadtesting_test_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "loadTestConfig": {
                    "engineSize": "m",
                    "engineInstances": 1,
                    "splitAllCSVs": False,
                },
                "secrets": {},
                "environmentVariables": {},
                "passFailCriteria": {"passFailMetrics": {}},
                "keyvaultReferenceIdentityType": "SystemAssigned",
                "keyvaultReferenceIdentityId": None,
            },
        )
        assert result is not None