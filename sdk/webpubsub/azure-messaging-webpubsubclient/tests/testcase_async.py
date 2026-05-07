# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import asyncio
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubclient.aio import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs, SendMessageError
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient


class WebpubsubClientTestAsync(AzureRecordedTestCase):
    async def create_client(
        self,
        endpoint,
        hub: str = "Hub",
        roles: List[str] = ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"],
        **kwargs,
    ):
        credential = self.get_credential(WebPubSubServiceClient, is_async=True)
        async def client_access_url_provider():
            async with self.create_client_from_credential(
                WebPubSubServiceClient,
                credential=credential,
                endpoint=endpoint,
                hub=hub,
            ) as service_client:
                return (await service_client.get_client_access_token(roles=roles))["url"]
        return WebPubSubClient(
            credential=WebPubSubClientCredential(client_access_url_provider),
            **kwargs,
        )

    @staticmethod
    async def setup_events(client):
        """Subscribe connected/disconnected/group-message events and return their wait handles."""
        connected_event = asyncio.Event()
        disconnected_event = asyncio.Event()
        message_event = asyncio.Event()

        async def _on_connected(*args, **kwargs):
            connected_event.set()

        async def _on_disconnected(*args, **kwargs):
            disconnected_event.set()

        async def _on_group_message(msg):
            await on_group_message(msg)
            message_event.set()

        await client.subscribe("connected", _on_connected)
        await client.subscribe("disconnected", _on_disconnected)
        await client.subscribe("group-message", _on_group_message)
        return connected_event, disconnected_event, message_event

    @staticmethod
    async def retry_send_until_message(client, group_name, data, message_event, retries=30):
        """Retry send_to_group until message_event fires, handling SendMessageError from rejoin lag."""
        for _ in range(retries):
            try:
                await client.send_to_group(group_name, data, "text")
            except SendMessageError:
                await asyncio.sleep(1)
                continue
            try:
                await asyncio.wait_for(message_event.wait(), timeout=2)
                return
            except asyncio.TimeoutError:
                pass
        try:
            await asyncio.wait_for(message_event.wait(), timeout=2)
        except asyncio.TimeoutError:
            pass


TEST_RESULT_ASYNC = set()

async def on_group_message(msg: OnGroupDataMessageArgs):
    TEST_RESULT_ASYNC.add(msg.data)
