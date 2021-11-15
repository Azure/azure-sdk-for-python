# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import WebpubsubPowerShellPreparer
from testcase_async import WebpubsubAsyncTest


class WebpubsubSmokeAsyncTest(WebpubsubAsyncTest):

    @WebpubsubPowerShellPreparer()
    async def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        await client.send_to_all({'hello': 'test_webpubsub_send_to_all'})

    @WebpubsubPowerShellPreparer()
    async def test_webpubsub_send_to_all_apim_proxy(self, webpubsub_endpoint, webpubsub_reverse_proxy_endpoint=None):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub', reverse_proxy_endpoint=webpubsub_reverse_proxy_endpoint)
        await client.send_to_all({'hello': 'test_webpubsub_send_to_all_apim_proxy'})

    @WebpubsubPowerShellPreparer()
    async def test_get_client_access_token(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        access_token = await client.get_client_access_token()
        assert len(access_token) == 3
        assert access_token['baseUrl'][:3] == "wss"
        assert access_token['token']
        assert access_token['url'][:3] == "wss"

    @WebpubsubPowerShellPreparer()
    async def test_hello_world_with_connection_string(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message="Hello, World!", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    async def test_hello_world_with_connection_string_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message={"hello": "world!"})

    @WebpubsubPowerShellPreparer()
    async def test_hello_world_with_connection_string_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message=b"Hello, World!", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    async def test_no_users_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        assert not await client.user_exists(user_id="fake user")
        assert not await client.group_exists(group="fake group")
