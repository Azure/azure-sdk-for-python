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
from testcase_async import WebpubsubClientTestAsync, TEST_RESULT_ASYNC


@pytest.mark.live_test_only
class TestWebpubsubClientRecoveryAsync(WebpubsubClientTestAsync):
    # recovery will be triggered if connection is dropped by accident
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_recovery_async(self, webpubsubclient_endpoint):
        client = await self.create_client(endpoint=webpubsubclient_endpoint, message_retry_total=10)
        name = "test_recovery_async"
        connected_event, _, message_event = await self.setup_events(client)
        async with client:
            await asyncio.wait_for(connected_event.wait(), timeout=30)
            conn_id0 = client._connection_id
            await client.join_group(name)
            await client._ws.session.close()  # close connection to trigger recovery
            await self.retry_send_until_message(client, name, name, message_event)
            conn_id1 = client._connection_id

        assert name in TEST_RESULT_ASYNC
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 == conn_id1
