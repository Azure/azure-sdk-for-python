# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from testcase import WebpubsubPowerShellPreparer
from testcase_async import WebpubsubAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async

@pytest.mark.live_test_only
class TestWebpubsubSmokeAsync(WebpubsubAsyncTest):

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        await client.send_to_all({'hello': 'test_webpubsub_send_to_all'})

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_webpubsub_send_to_all_apim_proxy(self, webpubsub_endpoint, webpubsub_reverse_proxy_endpoint=None):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub', reverse_proxy_endpoint=webpubsub_reverse_proxy_endpoint)
        await client.send_to_all({'hello': 'test_webpubsub_send_to_all_apim_proxy'})

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_client_access_token(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        access_token = await client.get_client_access_token()
        assert len(access_token) == 3
        assert access_token['baseUrl'][:3] == "wss"
        assert access_token['token']
        assert access_token['url'][:3] == "wss"

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_hello_world_with_connection_string(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message="Hello, World!", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_hello_world_with_connection_string_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message={"hello": "world!"})

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_hello_world_with_connection_string_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message=b"Hello, World!", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_no_users_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        assert not await client.user_exists(user_id="fake user")
        assert not await client.group_exists(group="fake group")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_connection_from_all_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.remove_connection_from_all_groups(connection_id="fake connection id")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_with_filter(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.send_to_all(message={"hello": "world!"}, filter="userId ne 'user1'", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_client_access_key_with_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        await client.get_client_access_token(user_id="user1", groups=["groups1"])