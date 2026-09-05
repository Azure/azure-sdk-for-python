# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer

from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient
from azure.messaging.webpubsubservice.chat.aio import (
    WebPubSubChatServiceClient as AsyncWebPubSubChatServiceClient,
)

from chat_message_seed import (
    create_chat_message,
    create_chat_message_async,
    verify_chat_connection,
    verify_chat_connection_async,
)


class WebPubSubChatTest(AzureRecordedTestCase):
    def create_client(self, endpoint):
        return WebPubSubChatServiceClient(
            endpoint,
            "test_hub",
            self.get_credential(WebPubSubChatServiceClient),
        )

    def create_async_client(self, endpoint):
        return AsyncWebPubSubChatServiceClient(
            endpoint,
            "test_hub",
            self.get_credential(AsyncWebPubSubChatServiceClient, is_async=True),
        )

    @staticmethod
    def create_key_client(connection_string):
        return WebPubSubChatServiceClient.from_connection_string(
            connection_string, "test_hub"
        )

    @staticmethod
    def create_async_key_client(connection_string):
        return AsyncWebPubSubChatServiceClient.from_connection_string(
            connection_string, "test_hub"
        )

    def assert_client_access(self, access, endpoint):
        expected_base_url = f"wss://{endpoint.removeprefix('https://').rstrip('/')}/client/hubs/test_hub"
        assert access["baseUrl"] == expected_base_url
        assert access["url"] == f"{expected_base_url}?access_token={access['token']}"
        if not self.is_playback():
            verify_chat_connection(access["url"])

    async def assert_client_access_async(self, access, endpoint):
        expected_base_url = f"wss://{endpoint.removeprefix('https://').rstrip('/')}/client/hubs/test_hub"
        assert access["baseUrl"] == expected_base_url
        assert access["url"] == f"{expected_base_url}?access_token={access['token']}"
        if not self.is_playback():
            await verify_chat_connection_async(access["url"])

    def seed_chat_message(self, client, user_id, conversation_id, content):
        if not self.is_playback():
            access = client.get_client_access_token(user_id=user_id)
            create_chat_message(access["url"], conversation_id, content)

    async def seed_chat_message_async(self, client, user_id, conversation_id, content):
        if not self.is_playback():
            access = await client.get_client_access_token(user_id=user_id)
            await create_chat_message_async(access["url"], conversation_id, content)

    @staticmethod
    def cleanup(action, *args):
        try:
            action(*args)
        except HttpResponseError:
            pass

    @staticmethod
    async def cleanup_async(action, *args):
        try:
            await action(*args)
        except HttpResponseError:
            pass


WebPubSubChatPreparer = functools.partial(
    PowerShellPreparer,
    "wps_chat",
    wps_chat_endpoint="https://myservice.webpubsub.azure.com",
)

WebPubSubChatAccessPreparer = functools.partial(
    WebPubSubChatPreparer,
    wps_chat_connection_string=(
        "Endpoint=https://myservice.webpubsub.azure.com;"
        "AccessKey=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH;"
    ),
    wps_chat_disable_local_auth="false",
)
