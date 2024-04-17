# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import asyncio
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import WebpubsubClientPowerShellPreparer
from testcase_async import WebpubsubClientTestAsync


@pytest.mark.live_test_only
class TestWebpubsubClientSendConcurrentlyAsync(WebpubsubClientTestAsync):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_concurrently_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)
        async with client:
            group_name = "test_send_concurrently_async"
            await client.join_group(group_name)
            await asyncio.gather(*[client.send_to_group(group_name, f"hello_{idx}", "text") for idx in range(100)])
