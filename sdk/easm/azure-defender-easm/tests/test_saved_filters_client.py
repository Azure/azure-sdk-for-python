# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmSavedFilterClient(EasmTest):
    delete_saved_filter_name = 'smoke_test_delete_saved_filter'
    put_saved_filter_name = 'smoke_test_put_saved_filter'
    known_existing_filter = 'sf1'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_saved_filters(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.saved_filters.list()
        saved_filter = response.next()
        assert saved_filter['id']
        assert saved_filter['description']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_get_saved_filter(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        saved_filter = client.saved_filters.get(self.known_existing_filter)
        assert saved_filter['id'] == self.known_existing_filter
        assert saved_filter['name'] == self.known_existing_filter
        assert saved_filter['displayName']
        assert saved_filter['filter']
        assert saved_filter['description']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_put_saved_filter(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        request = {
                'filter': 'name = "example.org"',
                'description': 'test saved filter',
        }
        saved_filter = client.saved_filters.put(self.put_saved_filter_name, body=request)
        assert saved_filter['id'] == self.put_saved_filter_name
        assert saved_filter['name'] == self.put_saved_filter_name
        assert saved_filter['displayName'] == self.put_saved_filter_name
        assert saved_filter['filter'] == request['filter']
        assert saved_filter['description'] == request['description']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_delete_saved_filter(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.saved_filters.delete(self.delete_saved_filter_name)
        assert response is None
