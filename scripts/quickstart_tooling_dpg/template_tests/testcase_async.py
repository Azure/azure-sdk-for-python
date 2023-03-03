# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from {{ namespace }}.aio import {{ client_name}}


class {{ test_prefix.capitalize() }}AsyncTest(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential({{ client_name}}, is_async=True)
        return self.create_client_from_credential(
            {{ client_name}},
            credential=credential,
            endpoint=endpoint,
        )
