# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from testcase import WebpubsubTest, WebpubsubPowerShellPreparer
from azure.messaging.webpubsubservice._operations._operations import build_send_to_all_request
from azure.core.exceptions import ServiceRequestError

class WebpubsubSmokeTest(WebpubsubTest):


    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        client.send_to_all({'hello': 'test_webpubsub_send_to_all'})

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all_api_management_proxy(self, webpubsub_endpoint, webpubsub_reverse_proxy_endpoint=None):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub', reverse_proxy_endpoint=webpubsub_reverse_proxy_endpoint)
        client.send_to_all({'hello': 'test_webpubsub_send_to_all_api_management_proxy'})

    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_request(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        request = build_send_to_all_request('Hub', content='test_webpubsub_send_request', content_type='text/plain')
        response = client.send_request(request)
        assert response.status_code == 202

    # If reverse_proxy_endpoint is not available, `ServiceRequestError` will be raised
    @WebpubsubPowerShellPreparer()
    def test_webpubsub_send_to_all_api_management_proxy_counter_test(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub', reverse_proxy_endpoint='https://example.azure-api.net')
        with pytest.raises(ServiceRequestError):
            client.send_to_all({'hello': 'test_webpubsub_send_to_all_api_management_proxy_counter_test'})

    @WebpubsubPowerShellPreparer()
    def test_get_client_access_token(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        access_token = client.get_client_access_token()
        assert len(access_token) == 3
        assert access_token['baseUrl'][:3] == "wss"
        assert access_token['token']
        assert access_token['url'][:3] == "wss"

    @WebpubsubPowerShellPreparer()
    def test_hello_world_with_connection_string(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        client.send_to_all(message="Hello, World!", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    def test_hello_world_with_connection_string_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        client.send_to_all(message={"hello": "world!"})

    @WebpubsubPowerShellPreparer()
    def test_hello_world_with_connection_string_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        client.send_to_all(message=b"Hello, World!", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    def test_no_users_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        assert not client.user_exists(user_id="fake user")
        assert not client.group_exists(group="fake group")
