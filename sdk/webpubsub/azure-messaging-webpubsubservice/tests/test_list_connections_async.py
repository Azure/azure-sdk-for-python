# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from websockets import connect as ws_connect
from testcase import WebpubsubPowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from testcase_async import WebpubsubAsyncTest


@pytest.mark.asyncio
class TestListConnectionsAsync(WebpubsubAsyncTest):

    @WebpubsubPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_connections(self, **kwargs):
        webpubsub_connection_string = kwargs.get("webpubsub_connection_string")
        # Test cases with different pagination scenarios
        test_cases = [
            {"total_connection_count": 6, "max_count_to_list": 6, "expected_total_count": 6, "expected_page_count": 1},
            {"total_connection_count": 6, "max_count_to_list": 3, "expected_total_count": 3, "expected_page_count": 1},
            {
                "total_connection_count": 6,
                "max_count_to_list": None,
                "expected_total_count": 6,
                "expected_page_count": 1,
            },
            {"total_connection_count": 6, "max_count_to_list": 5, "expected_total_count": 5, "expected_page_count": 1},
        ]

        for test_case in test_cases:
            client = self.create_client(connection_string=webpubsub_connection_string, hub="test_list_connections")
            async with client:
                group_name = "group1"
                ws_clients = []

                # Get client access token
                token = await client.get_client_access_token(groups=[group_name])
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
                connections = client.list_connections(group=group_name, top=test_case["max_count_to_list"])

                async for member in connections:
                    assert member.connection_id is not None

                # Count pages and connections
                async for page in connections.by_page():
                    page_count = 0
                    async for item in page:
                        page_count += 1
                    actual_connection_count += page_count
                    actual_page_count += 1

            # Verify results
            assert (
                actual_page_count == test_case["expected_page_count"]
            ), f"Expected {test_case['expected_page_count']} pages, got {actual_page_count}"
            assert (
                actual_connection_count == test_case["expected_total_count"]
            ), f"Expected {test_case['expected_total_count']} connections, got {actual_connection_count}"

            # Close WebSocket connections if not in playback mode
            if not self.is_playback():
                for ws in ws_clients:
                    await ws.close()
