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
from azure.messaging.webpubsubclient.models import (
    WebPubSubProtocolType,
    SendMessageError,
)


@pytest.mark.live_test_only
class TestWebpubsubClientNoRecoveryNoReconnectAsync(WebpubsubClientTestAsync):
    # disable recovery and auto reconnect
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_disable_recovery_and_autoconnect_async(self, webpubsubclient_endpoint):
        client = await self.create_client(
            endpoint=webpubsubclient_endpoint,
            reconnect_retry_total=0,
            protocol_type=WebPubSubProtocolType.JSON,
        )
        name = "test_disable_recovery_and_autoconnect_async"
        async with client:
            group_name = name
            _, disconnected_event, _ = await self.setup_events(client)
            await client.join_group(group_name)
            await client._ws.session.close()  # close connection
            await asyncio.wait_for(disconnected_event.wait(), timeout=30)
            with pytest.raises(SendMessageError):
                await client.send_to_group(group_name, name, "text")
            await asyncio.sleep(3)  # wait to confirm message was NOT received

        assert name not in TEST_RESULT_ASYNC

    # disable recovery and auto reconnect, then send message concurrently
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_disable_recovery_and_autoconnect_send_concurrently_async(
        self, webpubsubclient_endpoint
    ):
        client = await self.create_client(
            endpoint=webpubsubclient_endpoint,
            reconnect_retry_total=0,
            message_retry_total=3,
            protocol_type=WebPubSubProtocolType.JSON,
        )

        async with client:
            group_name = "test_disable_recovery_and_autoconnect_send_concurrently_async"
            _, disconnected_event, _ = await self.setup_events(client)
            await client.join_group(group_name)
            await client._ws.session.close()  # close connection
            await asyncio.wait_for(disconnected_event.wait(), timeout=30)
            assert not client.is_connected()

            tasks = [client.send_to_group(group_name, "hello", "text") for _ in range(10)]
            for task in asyncio.as_completed(tasks):
                with pytest.raises(SendMessageError):
                    await task
