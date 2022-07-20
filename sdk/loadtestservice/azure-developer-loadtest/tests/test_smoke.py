# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestingTest, LoadtestingPowerShellPreparer

class LoadtestingSmokeTest(LoadtestingTest):


    @LoadtestingPowerShellPreparer()
    def test_smoke(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        # test your code here, for example:
        # result = client.xxx.xx(...)
        # assert result is not None
