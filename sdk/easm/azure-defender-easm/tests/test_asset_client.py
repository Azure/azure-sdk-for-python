# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmAssetClient(EasmTest):
    kind = 'domain'
    name = 'hellointernet.fm'
    asset_filter = f'name = {name} and type = {kind}'
    asset_id = f'{kind}$${name}'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_assets(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        assets = client.assets.list(filter=self.asset_filter)
        asset = assets.next()
        assert self.kind == asset['kind']
        assert self.name == asset['name']
        self.check_guid_format(asset['uuid'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_get_asset(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        asset = client.assets.get(self.asset_id)
        assert self.kind == asset['kind']
        assert self.name == asset['name']
        self.check_guid_format(asset['uuid'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_update_asset(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        asset_update_request = {'externalId': 'new_external_id'}
        response = client.assets.update(body=asset_update_request, filter=self.asset_filter)
        assert 'complete' == response['state']
        assert 'complete' == response['phase']
        self.check_timestamp_format(self.time_format, response['startedAt'])
        self.check_timestamp_format(self.time_format, response['completedAt'])
        self.check_guid_format(response['id'])
