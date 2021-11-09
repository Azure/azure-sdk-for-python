# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient


class WebpubsubTestAsync(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(WebpubsubTestAsync, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint, reverse_proxy_endpoint=None):
        credential = self.get_credential(WebPubSubServiceClient, is_async=True)
        return self.create_client_from_credential(
            WebPubSubServiceClient,
            credential=credential,
            endpoint=endpoint,
            reverse_proxy_endpoint=reverse_proxy_endpoint
        )
