# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningPowerShellPreparer
from testcase_async import PurviewScanningTestAsync
from devtools_testutils.aio import recorded_by_proxy_async

class TestPurviewScanningSmokeAsync(PurviewScanningTestAsync):

    @PurviewScanningPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_basic_smoke_test(self, purviewscanning_endpoint):
        client = self.create_async_client(endpoint=purviewscanning_endpoint)
        response = client.data_sources.list_all()
        result = [item async for item in response]
        assert len(result) >= 1
