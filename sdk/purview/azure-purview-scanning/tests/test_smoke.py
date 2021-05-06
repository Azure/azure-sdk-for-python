# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningTest, PurviewScanningPowerShellPreparer
from azure.purview.scanning.rest import data_sources

class PurviewScanningSmokeTest(PurviewScanningTest):

    @PurviewScanningPowerShellPreparer()
    def test_basic_smoke_test(self, purviewscanning_endpoint):
        client = self.create_client(endpoint=purviewscanning_endpoint)
        request = data_sources.build_list_all_request()
        response = client.send_request(request)
        response.raise_for_status()
        assert response.status_code == 200
        json_response = response.json()
        assert set(json_response.keys()) == set(['value', 'count'])
        assert len(json_response['value']) == json_response['count']
