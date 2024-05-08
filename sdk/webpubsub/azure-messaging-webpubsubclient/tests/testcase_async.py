# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubclient.aio import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient


class WebpubsubClientTestAsync(AzureRecordedTestCase):
    async def create_client(
        self,
        connection_string,
        hub: str = "Hub",
        roles: List[str] = ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"],
        **kwargs,
    ):
        service_client = WebPubSubServiceClient.from_connection_string(connection_string, hub)
        async def client_access_url_provider():
            return (await service_client.get_client_access_token(roles=roles))["url"]
        return WebPubSubClient(
            credential=WebPubSubClientCredential(client_access_url_provider),
            **kwargs,
        )

TEST_RESULT_ASYNC = set()

async def on_group_message(msg: OnGroupDataMessageArgs):
    TEST_RESULT_ASYNC.add(msg.data)
