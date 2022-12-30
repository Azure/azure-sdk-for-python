# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningTest, PurviewScanningPowerShellPreparer
from devtools_testutils import recorded_by_proxy

class TestPurviewScanningSmoke(PurviewScanningTest):

    @PurviewScanningPowerShellPreparer()
    @recorded_by_proxy
    def test_basic_smoke_test(self, purviewscanning_endpoint):
        client = self.create_client(endpoint=purviewscanning_endpoint)
        response = client.data_sources.list_all()
        result = [item for item in response]
        assert len(result) >= 1
