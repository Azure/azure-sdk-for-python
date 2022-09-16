# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from {{ namespace }}.aio import {{ client_name}}


class {{ test_prefix.capitalize() }}AsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super({{ test_prefix.capitalize() }}AsyncTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential({{ client_name}}, is_async=True)
        return self.create_client_from_credential(
            {{ client_name}},
            credential=credential,
            endpoint=endpoint,
        )
