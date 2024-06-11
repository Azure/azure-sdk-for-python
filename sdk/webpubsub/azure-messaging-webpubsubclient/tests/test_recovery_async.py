# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import WebpubsubClientPowerShellPreparer
from testcase_async import WebpubsubClientTestAsync, TEST_RESULT_ASYNC, on_group_message


@pytest.mark.live_test_only
class TestWebpubsubClientRecoveryAsync(WebpubsubClientTestAsync):
    # recovery will be triggered if connection is dropped by accident
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_recovery_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string, message_retry_total=10)
        name = "test_recovery_async"
        async with client:
            await asyncio.sleep(0.001)  # wait for connection_id to be updated
            conn_id0 = client._connection_id
            group_name = name
            await client.subscribe("group-message", on_group_message)
            await client.join_group(group_name)
            await client._ws.session.close()  # close connection to trigger recovery
            await client.send_to_group(group_name, name, "text")
            conn_id1 = client._connection_id
            await asyncio.sleep(1)  # wait for on_group_message to be called

        assert name in TEST_RESULT_ASYNC
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 == conn_id1
