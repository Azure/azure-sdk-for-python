# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from contextlib import suppress

from {{module}} import {{client}}
import {{module}}.models
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"

class TestMgmt{{package.capitalize()}}(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client({{client}})

    {% for op in operations -%}
    @recorded_by_proxy
    def test_{{op_group}}_{{op["name"]}}(self):
        # it proves that we can normally send request but maybe needs additional parameters
        with suppress(HttpResponseError):
            result = self.mgmt_client.{{op_group}}.{{op["name"]}}()
            {% if op["return_type"] == "Polling" -%}
            assert result.result() is not None
            {% elif op["return_type"] == "Interable" -%}
            assert list(result) is not None
            {% else -%}
            assert result is not None
            {% endif -%}
    {% endfor -%}
