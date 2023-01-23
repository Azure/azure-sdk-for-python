# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmPowerShellPreparer

class EasmDiscoveryTemplatesTest(EasmTest):
    partial_name = 'taco'
    template_id = '44368'
    @EasmPowerShellPreparer()
    def test_list_discovery_templates(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        response = client.discovery_templates.list(filter=self.partial_name)
        template = response.next()
        assert self.partial_name in template['name'].lower()
        assert template['id']

    @EasmPowerShellPreparer()
    def test_get_discovery_template(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        template = client.discovery_templates.get(self.template_id)
        assert template['name']
        assert template['id']

