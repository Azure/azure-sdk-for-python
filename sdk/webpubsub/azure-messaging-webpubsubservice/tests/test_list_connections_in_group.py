# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from websockets import connect as ws_connect
from testcase import WebpubsubTest, WebpubsubPowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async

@pytest.mark.live_test_only
class TestListConnectionsInGroup(WebpubsubTest):

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_connections_in_group(self, webpubsub_connection_string, **kwargs):
        # Test cases with different pagination scenarios
        test_cases = [
            {
                "total_connection_count": 6,
                "max_count_to_list": 6,
                "expected_total_count": 6,
                "expected_page_count": 1
            },
            {
                "total_connection_count": 6,
                "max_count_to_list": 3,
                "expected_total_count": 3,
                "expected_page_count": 1
            },
            {
                "total_connection_count": 6,
                "max_count_to_list": None,
                "expected_total_count": 6,
                "expected_page_count": 1
            },
            {
                "total_connection_count": 6,
                "max_count_to_list": 5,
                "expected_total_count": 5,
                "expected_page_count": 1
            }
        ]

        for test_case in test_cases:
            client = self.create_client(connection_string = webpubsub_connection_string, hub='test_list_connections_in_group')
            group_name = "group1"
            ws_clients = []

            # Get client access token
            token = client.get_client_access_token(groups=[group_name])
            client_url = token["url"]

            # Create WebSocket connections if not in playback mode
            if not self.is_playback():
                for _ in range(test_case["total_connection_count"]):
                    ws = await ws_connect(client_url)
                    ws_clients.append(ws)

            # List connections with pagination
            actual_page_count = 0
            actual_connection_count = 0

            # Get connections with pagination
            connections = client.list_connections_in_group(
                group=group_name,
                top=test_case["max_count_to_list"]
            )

            for member in connections:
                assert member.connection_id is not None

            # Count pages and connections
            for page in connections.by_page():
                actual_connection_count += len(list(page))
                actual_page_count += 1

            # Verify results
            assert actual_page_count == test_case["expected_page_count"], \
                f"Expected {test_case['expected_page_count']} pages, got {actual_page_count}"
            assert actual_connection_count == test_case["expected_total_count"], \
                f"Expected {test_case['expected_total_count']} connections, got {actual_connection_count}"

            # Close WebSocket connections if not in playback mode
            if not self.is_playback():
                for ws in ws_clients:
                    await ws.close()