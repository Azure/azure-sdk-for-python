# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewAccountTest, PurviewAccountPowerShellPreparer
from testcase import PurviewMetaPolicyTest, PurviewMetaPolicyPowerShellPreparer
from devtools_testutils import recorded_by_proxy


class TestPurviewAccountSmoke(PurviewAccountTest):

    @PurviewAccountPowerShellPreparer()
    @recorded_by_proxy
    def test_basic_smoke_test(self, purviewaccount_endpoint):
        client = self.create_client(endpoint=purviewaccount_endpoint)
        response = client.accounts.get_access_keys()
        assert set(response.keys()) == set(['atlasKafkaPrimaryEndpoint', 'atlasKafkaSecondaryEndpoint'])

    @PurviewAccountPowerShellPreparer()
    @recorded_by_proxy
    def test_collections_list(self, purviewaccount_endpoint):
        client = self.create_client(endpoint=purviewaccount_endpoint)
        response = client.collections.list_collections()
        result = [item for item in response]
        for item in result:
            assert set(item.keys()) == set(['name', 'friendlyName', 'description', 'systemData', 'collectionProvisioningState'])


class TestPurviewMetaPolicySmoke(PurviewMetaPolicyTest):

    @PurviewMetaPolicyPowerShellPreparer()
    @recorded_by_proxy
    def test_meta_policy_smoke_test(self, purviewmetapolicy_endpoint):
        client = self.create_client(endpoint=purviewmetapolicy_endpoint)
        response = client.metadata_policy.list_all()
        result = [item for item in response]
        assert len(result) >= 1

    @PurviewMetaPolicyPowerShellPreparer()
    @recorded_by_proxy
    def test_meta_roles_smoke_test(self, purviewmetapolicy_endpoint):
        client = self.create_client(endpoint=purviewmetapolicy_endpoint)
        response = client.metadata_roles.list()
        result = [item for item in response]
        assert len(result) >= 4
