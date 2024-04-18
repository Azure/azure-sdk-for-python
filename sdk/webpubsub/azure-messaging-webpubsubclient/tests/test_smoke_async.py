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
    on_group_message,
    TEST_RESULT_ASYNC,
)
from azure.messaging.webpubsubclient.models import (
    OnGroupDataMessageArgs,
    OpenClientError,
    SendMessageError,
)


@pytest.mark.live_test_only
class TestWebpubsubClientSmokeAsync(WebpubsubClientTestAsync):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_call_back_deadlock_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)
        group_name = "test_call_back_deadlock_async"

        async def on_group_message(msg: OnGroupDataMessageArgs):
            await client.send_to_group(group_name, msg.data, "text", no_echo=True)

        async with client:
            await client.join_group(group_name)
            await client.subscribe("group-message", on_group_message)
            await client.send_to_group(group_name, "hello test_call_back_deadlock1", "text")
            await client.send_to_group(group_name, "hello test_call_back_deadlock2", "text")
            await client.send_to_group(group_name, "hello test_call_back_deadlock3", "text")
            # sleep to make sure the callback has enough time to execute before close
            await asyncio.sleep(1)

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_context_manager_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)
        async with client:
            group_name = "test_context_manager_async"
            await client.join_group(group_name)
            await client.send_to_group(group_name, "test_context_manager", "text")
            await asyncio.sleep(2.0)
            assert client._sequence_id.sequence_id > 0

    # test on_stop
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_on_stop_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)

        async def on_stop():
            await client.open()

        async with client:
            # open client again after close
            await client.subscribe("stopped", on_stop)
            await asyncio.sleep(0.1)
            assert client.is_connected()
            await client.close()
            await asyncio.sleep(1.0)
            assert client.is_connected()

            # remove stopped event and close again
            await client.unsubscribe("stopped", on_stop)
            await client.close()
            await asyncio.sleep(1.0)
            assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_duplicated_start_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)
        with pytest.raises(OpenClientError):
            async with client:
                await client.open()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_duplicated_stop_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string)
        async with client:
            await client.close()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_event_async(self, webpubsubclient_connection_string):
        client = await self.create_client(connection_string=webpubsubclient_connection_string, message_retry_total=0)
        async with client:
            # please register event handler in azure portal before run this test
            try:
                await client.send_event("event", "test_send_event", "text")
            except SendMessageError as err:
                assert err.error_detail.name == "InternalServerError"

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_rejoin_group_async(self, webpubsubclient_connection_string):
        async def _test(enable_auto_rejoin, test_group_name, assert_func):
            client = await self.create_client(
                connection_string=webpubsubclient_connection_string,
                auto_rejoin_groups=enable_auto_rejoin,
            )
            group_name = test_group_name
            await client.subscribe("group-message", on_group_message)
            async with client:
                await client.join_group(group_name)

            async with client:
                await asyncio.sleep(1)  # make sure rejoin group is called
                await client.send_to_group(group_name, group_name, "text")
                await asyncio.sleep(1)  # wait for on_group_message to be called
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
        client = await self.create_client(
            connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=aaaaaaaaaaaaa;Version=1.0;",
        )
        start_time = time.time()
        with pytest.raises(OpenClientError) as err:
            async with client:
                await asyncio.sleep(0)
        assert time.time() - start_time < client._start_timeout
        assert "During the process, an error occurred" in str(err)
