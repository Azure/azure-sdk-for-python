# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import {{ test_prefix.capitalize() }}PowerShellPreparer
from testcase_async import {{ test_prefix.capitalize() }}AsyncTest


class {{ test_prefix.capitalize() }}SmokeAsyncTest({{ test_prefix.capitalize() }}AsyncTest):

    @{{ test_prefix.capitalize() }}PowerShellPreparer()
    async def test_smoke_async(self, {{ test_prefix }}_endpoint):
        client = self.create_client(endpoint={{ test_prefix }}_endpoint)
        # test your code here, for example:
        # result = await client.xxx.xx(...)
        # assert result is not None
