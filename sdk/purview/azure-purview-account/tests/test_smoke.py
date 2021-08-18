# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewAccountTest, PurviewAccountPowerShellPreparer


class PurviewAccountSmokeTest(PurviewAccountTest):

    @PurviewAccountPowerShellPreparer()
    def test_basic_smoke_test(self, purviewaccount_endpoint):
        client = self.create_client(endpoint=purviewaccount_endpoint)
        response = client.accounts.get_access_keys()
        assert set(response.keys()) == set(['atlasKafkaPrimaryEndpoint', 'atlasKafkaSecondaryEndpoint'])
