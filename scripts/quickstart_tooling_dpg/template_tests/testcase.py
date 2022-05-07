# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from {{ namespace }} import {{ client_name }}


class {{ test_prefix.capitalize() }}Test(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super({{ test_prefix.capitalize() }}Test, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential({{ client_name }})
        return self.create_client_from_credential(
            {{ client_name }},
            credential=credential,
            endpoint=endpoint,
        )


{{ test_prefix.capitalize() }}PowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "{{ test_prefix }}",
    {{ test_prefix }}_endpoint="https://myservice.azure.com"
)
