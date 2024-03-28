# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import functools
import threading
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubclient.aio import WebPubSubClient
from azure.messaging.webpubsubclient import WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubClientTestAsync(AzureRecordedTestCase):
    def create_client(
        self,
        connection_string,
        hub: str = "Hub",
        roles: List[str] = ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"],
        **kwargs,
    ):
        service_client = WebPubSubServiceClient.from_connection_string(connection_string, hub)
        return WebPubSubClient(
            credential=WebPubSubClientCredential(lambda: service_client.get_client_access_token(roles=roles)["url"]),
            **kwargs,
        )

TEST_RESULT_ASYNC = set()

async def on_group_message(msg: OnGroupDataMessageArgs):
    TEST_RESULT_ASYNC.add(msg.data)
