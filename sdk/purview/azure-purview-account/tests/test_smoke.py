# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from .testcase import PurviewAccountTest, PurviewAccountPowerShellPreparer
from azure.purview.account.rest import accounts


class PurviewAccountSmokeTest(PurviewAccountTest):

    @PurviewAccountPowerShellPreparer()
    def test_basic_smoke_test(self, purviewaccount_endpoint):
        client = self.create_client(endpoint=purviewaccount_endpoint)
        request = accounts.build_get_request()
        response = client.send_request(request)
        response.raise_for_status()
        assert response.status_code == 200
        json_response = response.json()
        assert set(json_response.keys()) == set(['value', 'count'])
        assert len(json_response['value']) == json_response['count']
