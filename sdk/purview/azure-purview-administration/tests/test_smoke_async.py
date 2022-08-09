# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewAccountPowerShellPreparer, PurviewMetaPolicyPowerShellPreparer
from testcase_async import PurviewAccountTestAsync, PurviewMetaPolicyTestAsync
from devtools_testutils.aio import recorded_by_proxy_async


class TestPurviewAccountSmokeAsync(PurviewAccountTestAsync):

    @PurviewAccountPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_basic_smoke_test(self, purviewaccount_endpoint):
        client = self.create_async_client(endpoint=purviewaccount_endpoint)
        response = await client.accounts.get_access_keys()
        assert set(response.keys()) == set(['atlasKafkaPrimaryEndpoint', 'atlasKafkaSecondaryEndpoint'])

    @PurviewAccountPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_collections_list(self, purviewaccount_endpoint):
        client = self.create_async_client(endpoint=purviewaccount_endpoint)
        response = client.collections.list_collections()
        result = [item async for item in response]
        for item in result:
            assert set(item.keys()) == set(['name', 'friendlyName', 'description', 'systemData', 'collectionProvisioningState'])


class TestPurviewMetaDataPolicySmokeAsync(PurviewMetaPolicyTestAsync):

    @PurviewMetaPolicyPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_metadata_policy_smoke_async(self, purviewmetapolicy_endpoint):
        client = self.create_async_client(endpoint=purviewmetapolicy_endpoint)
        response = client.metadata_policy.list_all()
        result = [item async for item in response]
        assert len(result) >= 1

    @PurviewMetaPolicyPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_metadata_role_smoke_async(self, purviewmetapolicy_endpoint):
        client = self.create_async_client(endpoint=purviewmetapolicy_endpoint)
        response = client.metadata_roles.list()
        result = [item async for item in response]
        assert len(result) >= 4
