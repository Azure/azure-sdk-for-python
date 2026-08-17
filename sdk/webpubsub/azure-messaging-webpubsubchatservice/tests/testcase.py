# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer

from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient
from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient as AsyncWebPubSubChatServiceClient


class WebPubSubChatTest(AzureRecordedTestCase):
    def create_client(self, connection_string):
        return WebPubSubChatServiceClient.from_connection_string(connection_string, "test_hub")

    def create_async_client(self, connection_string):
        return AsyncWebPubSubChatServiceClient.from_connection_string(connection_string, "test_hub")

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
    wps_chat_connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=Kg==;Version=1.0;",
)
