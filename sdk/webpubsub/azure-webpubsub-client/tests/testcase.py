# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.webpubsub.client import WebPubSubClient
from azure.webpubsub.client import WebPubSubClientOptions
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubClientTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(WebpubsubClientTest, self).__init__(method_name, **kwargs)

    def create_client(self, connection_string, hub: str = "Hub", auto_reconnect: bool = False, **kwargs):
        service_client = WebPubSubServiceClient.from_connection_string(connection_string, hub, **kwargs)
        roles = kwargs.get("roles", ["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"])
        url = service_client.get_client_access_token(roles=roles)["url"]

        return WebPubSubClient(credential=url, options=WebPubSubClientOptions(auto_reconnect=auto_reconnect))


WebpubsubClientPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsubclient",
    webpubsubclient_connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=aaaaaaaaaaaaa;Version=1.0;",
)
