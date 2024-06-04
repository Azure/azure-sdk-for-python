# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient


class WebpubsubAsyncTest(AzureRecordedTestCase):
    def create_client(self, endpoint=None, hub=None, reverse_proxy_endpoint=None, **kwargs):
        if kwargs.get("connection_string"):
            return WebPubSubServiceClient.from_connection_string(kwargs.pop("connection_string"), hub, **kwargs)
        credential = self.get_credential(WebPubSubServiceClient, is_async=True)
        return self.create_client_from_credential(
            WebPubSubServiceClient,
            credential=credential,
            endpoint=endpoint,
            hub=hub,
            reverse_proxy_endpoint=reverse_proxy_endpoint
        )
