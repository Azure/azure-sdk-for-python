# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import WebpubsubTest, WebpubsubPowerShellPreparer


class WebpubsubSmokeTest(WebpubsubTest):

    @WebpubsubPowerShellPreparer()
    def test_health_api_status(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint)
        client.health_api.get_service_status()

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint)
        client.web_pub_sub.send_to_all('Hub', {'hello': 'test_webpubsub_send_to_all'})

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all_api_management_proxy(self, webpubsub_endpoint, reverse_proxy_endpoint=None):
        client = self.create_client(endpoint=webpubsub_endpoint, reverse_proxy_endpoint=reverse_proxy_endpoint)
        client.web_pub_sub.send_to_all('Hub', {'hello': 'test_webpubsub_send_to_all_api_management_proxy'})