# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.webpubsub.client import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubClientTest(AzureRecordedTestCase):
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


WebpubsubClientPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsubclient",
    webpubsubclient_connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=aaaaaaaaaaaaa;Version=1.0;",
)
