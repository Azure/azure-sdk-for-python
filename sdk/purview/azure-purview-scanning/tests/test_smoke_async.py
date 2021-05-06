# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningPowerShellPreparer
from testcase_async import PurviewScanningTestAsync
from azure.purview.scanning.rest import data_sources

class PurviewScanningSmokeTestAsync(PurviewScanningTestAsync):

    @PurviewScanningPowerShellPreparer()
    async def test_basic_smoke_test(self, purviewscanning_endpoint):
        request = data_sources.build_list_all_request()

        client = self.create_async_client(endpoint=purviewscanning_endpoint)
        response = await client.send_request(request)
        response.raise_for_status()
        assert response.status_code == 200
        json_response = response.json()
        assert set(json_response.keys()) == set(['value', 'count'])
        assert len(json_response['value']) == json_response['count']
