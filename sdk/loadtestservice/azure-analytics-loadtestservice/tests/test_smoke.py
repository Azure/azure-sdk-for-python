# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestserviceTest, LoadtestservicePowerShellPreparer


class LoadtestserviceSmokeTest(LoadtestserviceTest):

    @LoadtestservicePowerShellPreparer()
    def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(endpoint=loadtestservice_endpoint)
        result = client.test.list_load_test_search()
        assert result is not None

    @LoadtestservicePowerShellPreparer()
    def test_smoke_test_runs_search(self, loadtestservice_endpoint):
        client = self.create_client(endpoint=loadtestservice_endpoint)
        result = client.test_run.list_test_runs_search()
        assert result is not None



