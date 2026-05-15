# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testcase_async import WebpubsubClientTestAsync, TEST_RESULT_ASYNC
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
        connected_event, _, message_event = await self.setup_events(client)
        async with client:
            await asyncio.wait_for(connected_event.wait(), timeout=30)
            conn_id0 = client._connection_id
            await client.join_group(name)
            connected_event.clear()  # reset for reconnection detection
            await client._ws.sock.close(code=1001)  # close the connection to trigger auto connect
            # wait for reconnect
            await asyncio.wait_for(connected_event.wait(), timeout=30)
            await self.retry_send_until_message(client, name, name, message_event, retries=10)
            conn_id1 = client._connection_id
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 != conn_id1
        assert name in TEST_RESULT_ASYNC
