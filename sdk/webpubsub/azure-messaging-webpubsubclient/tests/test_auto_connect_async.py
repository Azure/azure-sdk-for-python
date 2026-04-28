# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testcase_async import WebpubsubClientTestAsync, TEST_RESULT_ASYNC, on_group_message
from testcase import WebpubsubClientPowerShellPreparer
from azure.messaging.webpubsubclient.models import WebPubSubProtocolType

@pytest.mark.live_test_only
class TestWebpubsubClientAutoConnectAsync(WebpubsubClientTestAsync):
    # auto_connect will be triggered if connection is dropped by accident and we disable recovery
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_auto_connect_async(self, webpubsubclient_endpoint):
        client = await self.create_client(
            endpoint=webpubsubclient_endpoint,
            protocol_type=WebPubSubProtocolType.JSON,
            message_retry_total=10,
            reconnect_retry_total=10,
            reconnect_retry_mode="fixed",
            reconnect_retry_backoff_factor=0.1,
        )
        name = "test_auto_connect_async"
        async with client:
            # wait for connection_id to be updated
            for _ in range(30):
                if client._connection_id is not None:
                    break
                await asyncio.sleep(1)
            conn_id0 = client._connection_id
            group_name = name
            await client.subscribe("group-message", on_group_message)
            await client.join_group(group_name)
            await client._ws.sock.close(
                code=1001
            )  # close the connection to trigger auto connect
            # wait for reconnect
            for _ in range(30):
                if client.is_connected() and client._connection_id != conn_id0:
                    break
                await asyncio.sleep(1)
            await client.send_to_group(group_name, name, "text")
            # wait for on_group_message callback to fire
            for _ in range(10):
                if name in TEST_RESULT_ASYNC:
                    break
                await asyncio.sleep(1)
            conn_id1 = client._connection_id
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 != conn_id1
        assert name in TEST_RESULT_ASYNC
