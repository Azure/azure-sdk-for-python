# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from {{ namespace }} import {{ client_name }}


class {{ test_prefix.capitalize() }}Test(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential({{ client_name }})
        return self.create_client_from_credential(
            {{ client_name }},
            credential=credential,
            endpoint=endpoint,
        )


{{ test_prefix.capitalize() }}Preparer = functools.partial(
    PowerShellPreparer,
    "{{ test_prefix }}",
    {{ test_prefix }}_endpoint="https://myservice.azure.com"
)
