# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.webpubsub.client import WebPubSubClient
from azure.webpubsub.client import WebPubSubClientOptions
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubClientTest(AzureRecordedTestCase):

    def create_client(self, connection_string, hub: str = "Hub", auto_reconnect: bool = False,
                      roles: List[str] = ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]):
        service_client = WebPubSubServiceClient.from_connection_string(connection_string, hub)
        url = service_client.get_client_access_token(roles=roles)["url"]

        return WebPubSubClient(credential=url, options=WebPubSubClientOptions(auto_reconnect=auto_reconnect))


WebpubsubClientPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsubclient",
    webpubsubclient_connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=aaaaaaaaaaaaa;Version=1.0;",
)
