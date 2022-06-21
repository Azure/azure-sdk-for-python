# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestservicePowerShellPreparer
from testcase_async import LoadtestserviceAsyncTest


class LoadtestserviceSmokeAsyncTest(LoadtestserviceAsyncTest):

    @LoadtestservicePowerShellPreparer()  
    async def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(endpoint=loadtestservice_endpoint)
        result=client.test.list_load_test_search()
        result = await client.test.list_load_test_search()
        assert result is not None
