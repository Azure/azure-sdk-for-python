# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from testcase import WebpubsubTest, WebpubsubPowerShellPreparer
from azure.messaging.webpubsubservice.operations._operations import build_send_to_all_request
from azure.core.exceptions import ServiceRequestError

class WebpubsubSmokeTest(WebpubsubTest):


    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint)
        client.send_to_all('Hub', {'hello': 'test_webpubsub_send_to_all'})

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all_api_management_proxy(self, webpubsub_endpoint, webpubsub_reverse_proxy_endpoint=None):
        client = self.create_client(endpoint=webpubsub_endpoint, reverse_proxy_endpoint=webpubsub_reverse_proxy_endpoint)
        client.send_to_all('Hub', {'hello': 'test_webpubsub_send_to_all_api_management_proxy'})

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_request(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint)
        request = build_send_to_all_request('Hub', content='test_webpubsub_send_request', content_type='text/plain')
        response = client.send_request(request)
        assert response.status_code == 202

    # If reverse_proxy_endpoint is not available, `ServiceRequestError` will be raised
    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all_api_management_proxy_counter_test(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, reverse_proxy_endpoint='https://example.azure-api.net')
        with pytest.raises(ServiceRequestError):
            client.send_to_all('Hub', {'hello': 'test_webpubsub_send_to_all_api_management_proxy_counter_test'})