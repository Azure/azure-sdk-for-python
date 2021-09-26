# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningTest, PurviewScanningPowerShellPreparer


class PurviewScanningSmokeTest(PurviewScanningTest):

    @PurviewScanningPowerShellPreparer()
    def test_basic_smoke_test(self, purviewscanning_endpoint):
        client = self.create_client(endpoint=purviewscanning_endpoint)
        response = client.data_sources.list_all()

        result = []
        for item in response:
            result.append(item)
        assert set(response.keys()) == set(['value', 'count'])
        assert len(response['value']) == response['count']
