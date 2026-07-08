# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.messaging.webpubsubservice import WebPubSubServiceClient


class WebpubsubTest(AzureRecordedTestCase):
    def create_client(self, endpoint=None, hub=None, reverse_proxy_endpoint=None, **kwargs):
        credential = self.get_credential(WebPubSubServiceClient)
        return self.create_client_from_credential(
            WebPubSubServiceClient,
            credential=credential,
            endpoint=endpoint,
            hub=hub,
            reverse_proxy_endpoint=reverse_proxy_endpoint,
        )


WebpubsubPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "webpubsub",
    webpubsub_endpoint="https://myservice.webpubsub.azure.com",
    webpubsub_reverse_proxy_endpoint="https://myservice.webpubsub.azure.com",
    webpubsub_socketio_endpoint="https://myservice-socketio.webpubsub.azure.com",
)
