# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time

import jwt
import pytest
from devtools_testutils import recorded_by_proxy
from websockets.sync.client import connect as ws_connect

from testcase import WebpubsubPowerShellPreparer, WebpubsubTest


@pytest.mark.live_test_only
class TestLiveApiCoverage(WebpubsubTest):
    def _find_connection_id(self, client, group_name, user_id):
        for _ in range(10):
            members = list(client.list_connections(group=group_name, top=20))
            for member in members:
                if member.user_id == user_id and member.connection_id:
                    return member.connection_id
            time.sleep(1)
        return None

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy
    def test_live_api_coverage_all_apis_and_parameters(self, webpubsub_endpoint, webpubsub_connection_string):
        if not getattr(self, "is_live", False):
            pytest.skip("Live WebSocket coverage test is skipped in playback mode")

        client = self.create_client(connection_string=webpubsub_connection_string, hub="hub")
        aad_client = self.create_client(endpoint=webpubsub_endpoint, hub="hub")

        user_id = "live-user-1"
        group_1 = "group-live-1"
        group_2 = "group-live-2"
        group_3 = "group-live-3"
        group_4 = "group-live-4"

        access_token = client.get_client_access_token(
            user_id=user_id,
            roles=["webpubsub.sendToGroup", "webpubsub.joinLeaveGroup"],
            groups=[group_1],
            minutes_to_expire=15,
            client_protocol="Default",
            jwt_headers={"kid": "live-coverage-kid"},
        )
        assert access_token["token"]
        decoded = jwt.decode(access_token["token"], options={"verify_signature": False})
        assert decoded["sub"] == user_id
        assert "webpubsub.sendToGroup" in decoded["role"]
        assert "webpubsub.joinLeaveGroup" in decoded["role"]
        assert group_1 in decoded["webpubsub.group"]

        socketio_token = client.get_client_access_token(user_id=user_id, groups=[group_1], client_protocol="SocketIO")
        assert socketio_token["token"]

        generated_token = aad_client.generate_client_token(
            user_id=user_id,
            role=["webpubsub.sendToGroup"],
            group=[group_1],
            minutes_to_expire=10,
            client_type="MQTT",
        )
        assert generated_token["token"]

        ws = None
        try:
            ws = ws_connect(access_token["url"])

            assert client.get_service_status()

            connection_id = self._find_connection_id(client, group_1, user_id)
            assert connection_id is not None

            assert client.connection_exists(connection_id=connection_id)
            assert client.user_exists(user_id=user_id)
            assert client.group_exists(group=group_1)

            client.send_to_all(
                message={"kind": "json"}, content_type="application/json", excluded=[connection_id, "fake-conn-id"]
            )
            client.send_to_all(message="plain", content_type="text/plain", filter=f"userId eq '{user_id}'")
            client.send_to_all(message=b"binary", content_type="application/octet-stream")

            client.send_to_group(
                group=group_1,
                message={"kind": "json"},
                content_type="application/json",
                excluded=[connection_id, "fake-conn-id"],
            )
            client.send_to_group(
                group=group_1,
                message="plain",
                content_type="text/plain",
                filter=f"userId eq '{user_id}'",
            )
            client.send_to_group(group=group_1, message=b"binary", content_type="application/octet-stream")

            client.send_to_connection(
                connection_id=connection_id,
                message={"kind": "json"},
                content_type="application/json",
            )
            client.send_to_connection(connection_id=connection_id, message="plain", content_type="text/plain")
            client.send_to_connection(
                connection_id=connection_id,
                message=b"binary",
                content_type="application/octet-stream",
            )

            client.send_to_user(
                user_id=user_id,
                message={"kind": "json"},
                content_type="application/json",
                filter=f"userId eq '{user_id}'",
            )
            client.send_to_user(user_id=user_id, message="plain", content_type="text/plain")
            client.send_to_user(user_id=user_id, message=b"binary", content_type="application/octet-stream")

            client.add_connection_to_group(group=group_2, connection_id=connection_id)
            members_group_2 = list(client.list_connections_in_group(group=group_2, top=20))
            assert any(member.connection_id == connection_id for member in members_group_2)

            client.add_connections_to_groups(groups_to_add={"filter": f"userId eq '{user_id}'", "groups": [group_3]})
            members_group_3 = list(client.list_connections_in_group(group=group_3, top=20))
            assert any(member.connection_id == connection_id for member in members_group_3)

            client.grant_permission(
                permission="sendToGroup",
                connection_id=connection_id,
                target_name=group_1,
            )
            assert client.check_permission(
                permission="sendToGroup",
                connection_id=connection_id,
                target_name=group_1,
            )
            assert client.has_permission(
                permission="sendToGroup",
                connection_id=connection_id,
                target_name=group_1,
            )
            client.revoke_permission(
                permission="sendToGroup",
                connection_id=connection_id,
                target_name=group_1,
            )

            client.add_user_to_group(group=group_4, user_id=user_id)
            client.remove_user_from_group(group=group_4, user_id=user_id)

            client.remove_connections_from_groups(
                groups_to_remove={"filter": f"userId eq '{user_id}'", "groups": [group_3]}
            )
            client.remove_connection_from_group(group=group_2, connection_id=connection_id)
            client.remove_connection_from_all_groups(connection_id=connection_id)
            client.remove_user_from_all_groups(user_id=user_id)

            # --- Close operations: reconnect between each so every close API has a real connection ---

            # close_group_connections (connection auto-joins group_1 via token)
            ws.close()
            ws = ws_connect(access_token["url"])
            conn = self._find_connection_id(client, group_1, user_id)
            assert conn is not None
            client.close_group_connections(group=group_1, reason="live-coverage")
            assert not client.connection_exists(connection_id=conn)

            # close_user_connections
            ws = ws_connect(access_token["url"])
            conn = self._find_connection_id(client, group_1, user_id)
            assert conn is not None
            client.close_user_connections(user_id=user_id, reason="live-coverage")
            assert not client.connection_exists(connection_id=conn)

            # close_connection
            ws = ws_connect(access_token["url"])
            conn = self._find_connection_id(client, group_1, user_id)
            assert conn is not None
            client.close_connection(connection_id=conn, reason="live-coverage")
            assert not client.connection_exists(connection_id=conn)

            # close_all_connections
            ws = ws_connect(access_token["url"])
            conn = self._find_connection_id(client, group_1, user_id)
            assert conn is not None
            client.close_all_connections(reason="live-coverage")
            assert not client.connection_exists(connection_id=conn)
            ws = None

            assert not client.user_exists(user_id="live-user-not-exist")
            assert not client.group_exists(group="live-group-not-exist")
        finally:
            if ws:
                ws.close()
