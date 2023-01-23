# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmPowerShellPreparer

class EasmAssetTest(EasmTest):
    kind = 'domain'
    name = 'hellointernet.fm'
    asset_filter = f'name = {name} and type = {kind}'
    asset_id = f'{kind}$${name}'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmPowerShellPreparer()
    def test_list_assets(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        assets = client.assets.list(filter=self.asset_filter)
        asset = assets.next()
        assert self.kind == asset['kind']
        assert self.name == asset['name']
        self.check_guid_format(asset['uuid'])

    @EasmPowerShellPreparer()
    def test_get_asset(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        asset = client.assets.get(self.asset_id)
        assert self.kind == asset['kind']
        assert self.name == asset['name']
        self.check_guid_format(asset['uuid'])

    @EasmPowerShellPreparer()
    def test_update_asset(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        asset_update_request = {'external_id': 'new_external_id'}
        response = client.assets.update(body=asset_update_request, filter=self.asset_filter)
        assert 'complete' == response['state']
        assert 'complete' == response['phase']
        self.check_timestamp_format(self.time_format, response['startedAt'])
        self.check_timestamp_format(self.time_format, response['completedAt'])
        self.check_guid_format(response['id'])
