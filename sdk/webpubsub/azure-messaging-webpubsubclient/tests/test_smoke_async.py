# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import WebpubsubClientPowerShellPreparer
from testcase_async import (
    WebpubsubClientTestAsync,
    TEST_RESULT_ASYNC,
)
from azure.messaging.webpubsubclient.aio import WebPubSubClient as AsyncWebPubSubClient, WebPubSubClientCredential as AsyncWebPubSubClientCredential
from azure.messaging.webpubsubclient.models import (
    OnGroupDataMessageArgs,
    OpenClientError,
    SendMessageError,
)


@pytest.mark.live_test_only
class TestWebpubsubClientSmokeAsync(WebpubsubClientTestAsync):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_call_back_deadlock_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint)
        group_name = "test_call_back_deadlock_async"
        callback_completed = asyncio.Event()
        callback_count = 0

        async def on_group_message(msg: OnGroupDataMessageArgs):
            nonlocal callback_count
            await client.send_to_group(group_name, msg.data, "text", no_echo=True)
            callback_count += 1
            if callback_count >= 3:
                callback_completed.set()

        async with client:
            await client.join_group(group_name)
            await client.subscribe("group-message", on_group_message)
            await client.send_to_group(group_name, "hello test_call_back_deadlock1", "text")
            await client.send_to_group(group_name, "hello test_call_back_deadlock2", "text")
            await client.send_to_group(group_name, "hello test_call_back_deadlock3", "text")
            await asyncio.wait_for(callback_completed.wait(), timeout=30)

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_context_manager_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint)
        _, _, message_event = await self.setup_events(client)
        async with client:
            group_name = "test_context_manager_async"
            await client.join_group(group_name)
            await client.send_to_group(group_name, "test_context_manager", "text")
            await asyncio.wait_for(message_event.wait(), timeout=30)
            assert client._sequence_id.sequence_id > 0

    # test on_stop
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_on_stop_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint)
        connected_event, disconnected_event, _ = await self.setup_events(client)
        reopen_error = None
        reopen_complete = asyncio.Event()

        async def on_stop():
            nonlocal reopen_error
            try:
                # close() can race with immediate reopen, so retry briefly before failing.
                for _ in range(10):
                    try:
                        await client.open()
                        break
                    except OpenClientError:
                        await asyncio.sleep(1)
                else:
                    raise RuntimeError("Failed to reopen client in stopped callback")

                await asyncio.wait_for(connected_event.wait(), timeout=30)
                assert client.is_connected()
            except Exception as e:
                reopen_error = e
            finally:
                reopen_complete.set()

        async with client:
            # open client again after close
            await client.subscribe("stopped", on_stop)
            await asyncio.wait_for(connected_event.wait(), timeout=30)
            assert client.is_connected()
            connected_event.clear()
            await client.close()
            # wait for on_stop callback to finish reopening
            await asyncio.wait_for(reopen_complete.wait(), timeout=60)
            assert reopen_error is None, f"on_stop callback failed: {reopen_error}"

            # remove stopped event and close again
            await client.unsubscribe("stopped", on_stop)
            await client.close()
            assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_duplicated_start_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint)
        with pytest.raises(OpenClientError):
            async with client:
                await client.open()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_duplicated_stop_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint)
        async with client:
            await client.close()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_event_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint, message_retry_total=0)
        async with client:
            # please register event handler in azure portal before run this test
            try:
                await client.send_event("event", "test_send_event", "text")
            except SendMessageError as err:
                assert err.error_detail.name == "InternalServerError"

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_rejoin_group_async(self, webpubsubclient_endpoint):
        async def _test(enable_auto_rejoin, test_group_name, assert_func):
            client = await self.create_client(
                endpoint=webpubsubclient_endpoint,
                auto_rejoin_groups=enable_auto_rejoin,
            )
            connected_event, _, message_event = await self.setup_events(client)
            async with client:
                await client.join_group(test_group_name)

            connected_event.clear()
            message_event.clear()
            async with client:
                await asyncio.wait_for(connected_event.wait(), timeout=30)
                if enable_auto_rejoin:
                    await self.retry_send_until_message(client, test_group_name, test_group_name, message_event)
                else:
                    await client.send_to_group(test_group_name, test_group_name, "text")
                # wait for on_group_message callback to fire
                try:
                    await asyncio.wait_for(message_event.wait(), timeout=10)
                except asyncio.TimeoutError:
                    pass
                assert assert_func(test_group_name)

        await _test(
            enable_auto_rejoin=True,
            test_group_name="test_rejoin_group_async",
            assert_func=lambda x: x in TEST_RESULT_ASYNC,
        )
        await _test(
            enable_auto_rejoin=False,
            test_group_name="test_disable_rejoin_group_async",
            assert_func=lambda x: x not in TEST_RESULT_ASYNC,
        )

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_open_client_error_async(self):
        async def _fake_url_provider():
            return "wss://myservice.webpubsub.azure.com/client/hubs/Hub"

        client = AsyncWebPubSubClient(
            credential=AsyncWebPubSubClientCredential(_fake_url_provider),
        )
        start_time = time.time()
        with pytest.raises(OpenClientError) as err:
            async with client:
                await asyncio.sleep(0)
        assert time.time() - start_time < client._start_timeout
        assert "During the process, an error occurred" in str(err)
