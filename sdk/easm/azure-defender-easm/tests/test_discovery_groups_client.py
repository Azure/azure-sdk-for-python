# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmPowerShellPreparer

class EasmDiscoveryGroupsTest(EasmTest):
    put_discovery_group_name = 'smoke_test_put_discovery_group'
    delete_discovery_group_name = 'smoke_test_delete_discovery_group'
    known_existing_group = 'test_group'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmPowerShellPreparer()
    def test_list_discovery_groups(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        response = client.discovery_groups.list()
        group = response.next()
        assert group['id']
        assert group['name']
        assert group['displayName']
        assert group['description']
        assert group['tier']
        self.check_timestamp_format(self.time_format, group['createdDate'])

    @EasmPowerShellPreparer()
    def test_get_discovery_group(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        group = client.discovery_groups.get(self.known_existing_group)
        assert group['id'] == self.known_existing_group
        assert group['name'] == self.known_existing_group
        assert group['displayName'] == self.known_existing_group
        assert group['description']
        assert group['tier']
        self.check_timestamp_format(self.time_format, group['createdDate'])

    @EasmPowerShellPreparer()
    def test_list_discovery_runs(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        response = client.discovery_groups.list_runs(self.known_existing_group)
        run = response.next()
        assert run['state']
        assert run['tier']
        self.check_timestamp_format(self.time_format, run['submittedDate'])

    @EasmPowerShellPreparer()
    def test_put_discovery_group(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        request = {
            'description': 'test description',
            'seeds': [{'kind': 'domain', 'name': 'example.org'}]
        }
        group = client.discovery_groups.put(self.put_discovery_group_name, body=request)
        assert group['name'] == self.put_discovery_group_name
        assert group['displayName'] == self.put_discovery_group_name
        assert group['description'] == request['description']
        assert group['seeds'] == request['seeds']

    @EasmPowerShellPreparer()
    def test_delete_discovery_group(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        response = client.discovery_groups.delete(self.delete_discovery_group_name)
        assert response is None

    @EasmPowerShellPreparer()
    def test_run_discovery_group(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        response = client.discovery_groups.run(self.known_existing_group)
        assert response is None
