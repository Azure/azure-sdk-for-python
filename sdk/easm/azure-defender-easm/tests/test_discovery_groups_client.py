# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmDiscoveryGroupClient(EasmTest):
    put_discovery_group_name = 'smoke_test_put_discovery_group'
    delete_discovery_group_name = 'smoke_test_delete_discovery_group'
    known_existing_group = 'test_group'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_discovery_groups(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.discovery_groups.list()
        group = response.next()
        assert group['id']
        assert group['name']
        assert group['displayName']
        assert group['description']
        assert group['tier']
        self.check_timestamp_format(self.time_format, group['createdDate'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_get_discovery_group(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        group = client.discovery_groups.get(self.known_existing_group)
        assert group['id'] == self.known_existing_group
        assert group['name'] == self.known_existing_group
        assert group['displayName'] == self.known_existing_group
        assert group['description']
        assert group['tier']
        self.check_timestamp_format(self.time_format, group['createdDate'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_discovery_runs(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.discovery_groups.list_runs(self.known_existing_group)
        run = response.next()
        assert run['state']
        assert run['tier']
        self.check_timestamp_format(self.time_format, run['submittedDate'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_put_discovery_group(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        request = {
            'description': 'test description',
            'seeds': [{'kind': 'domain', 'name': 'example.org'}]
        }
        group = client.discovery_groups.put(self.put_discovery_group_name, body=request)
        assert group['name'] == self.put_discovery_group_name
        assert group['displayName'] == self.put_discovery_group_name
        assert group['description'] == request['description']
        assert group['seeds'] == request['seeds']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_delete_discovery_group(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.discovery_groups.delete(self.delete_discovery_group_name)
        assert response is None

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_run_discovery_group(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.discovery_groups.run(self.known_existing_group)
        assert response is None
