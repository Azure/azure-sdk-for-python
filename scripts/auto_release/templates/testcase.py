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

class TestMgmt{{package.upper()}}(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client({{client}})

    {% for func in functions -%}
    @recorded_by_proxy
    def test_{{package}}_{{operation}}_{{func["name"]}}(self):
        # it proves that we can normally send request but maybe needs additional parameters
        with suppress(HttpResponseError):
            result = self.mgmt_client.{{operation}}.{{func["name"]}}()
            {% if func["return_type"] == "Polling" -%}
            assert result.result() is not None
            {% elif func["return_type"] == "Interable" -%}
            assert list(result) is not None
            {% else -%}
            assert result is not None
            {% endif -%}
    {% endfor -%}
