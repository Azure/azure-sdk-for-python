# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewAccountPowerShellPreparer
from testcase_async import PurviewAccountTestAsync
from azure.purview.account.rest import accounts


class PurviewAccountSmokeTestAsync(PurviewAccountTestAsync):

    @PurviewAccountPowerShellPreparer()
    async def test_basic_smoke_test(self, purviewaccount_endpoint):
        request = accounts.build_get_request()

        client = self.create_async_client(endpoint=purviewaccount_endpoint)
        response = await client.send_request(request)
        response.raise_for_status()
        assert response.status_code == 200
