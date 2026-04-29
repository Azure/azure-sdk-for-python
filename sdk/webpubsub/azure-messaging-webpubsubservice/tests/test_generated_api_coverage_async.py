# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import WebpubsubPowerShellPreparer
from testcase_async import WebpubsubAsyncTest


class TestGeneratedApiCoverageAsync(WebpubsubAsyncTest):
    """Recorded async tests that make real HTTP requests for all generated APIs.

    APIs that require a live WebSocket connection (send_to_connection, close_connection,
    add/remove_connection_to/from_group, grant/revoke_permission, add_user_to_group) are covered in
    test_live_api_coverage_async.py instead.
    """

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_service_status(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert await client.get_service_status()

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_generate_client_token(self, webpubsub_endpoint, **kwargs):
        client = self.create_client(endpoint=webpubsub_endpoint, hub="apicoverage")
        token = await client.generate_client_token(
            user_id="user1",
            role=["webpubsub.sendToGroup"],
            group=["group1"],
            minutes_to_expire=10,
            client_type="Default",
        )
        assert token["token"]

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_close_all_connections(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.close_all_connections(excluded=["fake-conn-1", "fake-conn-2"], reason="test")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_add_connections_to_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.add_connections_to_groups(
            groups_to_add={"filter": "userId eq 'nobody'", "groups": ["group1", "group2"]}
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_connections_from_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.remove_connections_from_groups(
            groups_to_remove={"filter": "userId eq 'nobody'", "groups": ["group1", "group2"]}
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_all_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_all(
            message={"hello": "world"},
            content_type="application/json",
            excluded=["fake-conn-1", "fake-conn-2"],
            filter="userId ne 'nobody'",
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_all_text(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_all(message="hello", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_all_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_all(message=b"hello", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_group_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_group(
            group="group1",
            message={"hello": "world"},
            content_type="application/json",
            excluded=["fake-conn-1", "fake-conn-2"],
            filter="userId ne 'nobody'",
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_group_text(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_group(group="group1", message="hello", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_group_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_group(group="group1", message=b"hello", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_user_json(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_user(
            user_id="user1",
            message={"hello": "world"},
            content_type="application/json",
            filter="userId eq 'user1'",
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_user_text(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_user(user_id="user1", message="hello", content_type="text/plain")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_user_binary(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_user(user_id="user1", message=b"hello", content_type="application/octet-stream")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_send_to_connection_with_fake_connection_id(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.send_to_connection(
            connection_id="fake-connection-id",
            message={"hello": "world"},
            content_type="application/json",
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_close_connection_with_fake_connection_id(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.close_connection(connection_id="fake-connection-id", reason="test")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_add_connection_to_group_not_found(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        with pytest.raises(ResourceNotFoundError):
            await client.add_connection_to_group(group="group1", connection_id="fake-connection-id")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_grant_permission_not_found(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        with pytest.raises(ResourceNotFoundError):
            await client.grant_permission(
                permission="sendToGroup", connection_id="fake-connection-id", target_name="group1"
            )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_revoke_permission_with_fake_connection_id(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.revoke_permission(
            permission="sendToGroup", connection_id="fake-connection-id", target_name="group1"
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_add_user_to_group_not_found(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        with pytest.raises(ResourceNotFoundError):
            await client.add_user_to_group(group="group1", user_id="fake-user")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_connection_exists(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert not await client.connection_exists(connection_id="fake-connection-id")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_user_exists(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert not await client.user_exists(user_id="fake-user")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_group_exists(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert not await client.group_exists(group="fake-group")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_check_permission(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert not await client.check_permission(
            permission="sendToGroup", connection_id="fake-connection-id", target_name="group1"
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_has_permission(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        assert not await client.has_permission(
            permission="sendToGroup", connection_id="fake-connection-id", target_name="group1"
        )

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_connection_from_all_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.remove_connection_from_all_groups(connection_id="fake-connection-id")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_user_from_all_groups(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.remove_user_from_all_groups(user_id="fake-user")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_close_group_connections(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.close_group_connections(group="group1", excluded=["fake-conn-1", "fake-conn-2"], reason="test")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_close_user_connections(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.close_user_connections(user_id="user1", excluded=["fake-conn-1", "fake-conn-2"], reason="test")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_user_from_group(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.remove_user_from_group(group="group1", user_id="fake-user")

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_connections_in_group(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        result = [member async for member in client.list_connections_in_group(group="group1", top=10)]
        assert isinstance(result, list)

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_connections(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        result = [member async for member in client.list_connections(group="group1", top=10)]
        assert isinstance(result, list)

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_remove_connection_from_group(self, webpubsub_connection_string):
        client = self.create_client(connection_string=webpubsub_connection_string, hub="apicoverage")
        await client.remove_connection_from_group(group="group1", connection_id="fake-connection-id")
