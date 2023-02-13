# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import {{ test_prefix.capitalize() }}Preparer
from testcase_async import {{ test_prefix.capitalize() }}AsyncTest


# For more info about how to write and run test, please refer to https://github.com/Azure/azure-sdk-for-python/wiki/Dataplane-Codegen-Quick-Start-for-Test
class {{ test_prefix.capitalize() }}SmokeAsyncTest({{ test_prefix.capitalize() }}AsyncTest):

    @{{ test_prefix.capitalize() }}Preparer()
    @recorded_by_proxy_async
    async def test_smoke_async(self, {{ test_prefix }}_endpoint):
        client = self.create_client(endpoint={{ test_prefix }}_endpoint)
        # test your code here, for example:
        # result = await client.xxx.xx(...)
        # assert result is not None
