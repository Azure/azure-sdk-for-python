# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(WebpubsubTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint=None, hub=None, reverse_proxy_endpoint=None, **kwargs):
        if kwargs.get("connection_string"):
            return WebPubSubServiceClient.from_connection_string(kwargs.pop("connection_string"), hub, **kwargs)
        credential = self.get_credential(WebPubSubServiceClient)
        return self.create_client_from_credential(
            WebPubSubServiceClient,
            credential=credential,
            endpoint=endpoint,
            hub=hub,
            reverse_proxy_endpoint=reverse_proxy_endpoint
        )


WebpubsubPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsub",
    webpubsub_endpoint="https://myservice.webpubsub.azure.com",
    webpubsub_reverse_proxy_endpoint="https://myservice.azure-api.net",
    webpubsub_connection_string="Endpoint=https://myservice.webpubsub.azure.com;AccessKey=aaaaaaaaaaaaa;Version=1.0;"
)
