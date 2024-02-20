# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmDiscoveryTemplateClient(EasmTest):
    partial_name = 'taco'
    template_id = '44368'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_list_discovery_templates(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        response = client.discovery_templates.list(filter=self.partial_name)
        template = response.next()
        assert self.partial_name in template['name'].lower()
        assert template['id']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_get_discovery_template(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        template = client.discovery_templates.get(self.template_id)
        assert template['name']
        assert template['id']

