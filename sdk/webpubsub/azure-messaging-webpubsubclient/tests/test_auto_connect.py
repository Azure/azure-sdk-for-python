# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, TEST_RESULT
from azure.messaging.webpubsubclient.models import WebPubSubProtocolType


@pytest.mark.live_test_only
class TestWebpubsubClientAutoConnect(WebpubsubClientTest):
    # auto_connect will be triggered if connection is dropped by accident and we disable recovery
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_auto_connect(self, webpubsubclient_endpoint):
        client = self.create_client(
            endpoint=webpubsubclient_endpoint,
            protocol_type=WebPubSubProtocolType.JSON,
            message_retry_total=10,
            reconnect_retry_total=10,
            reconnect_retry_mode="fixed",
            reconnect_retry_backoff_factor=0.1,
        )
        name = "test_auto_connect"
        connected_event, _, message_event = self.setup_events(client)
        with client:
            assert connected_event.wait(timeout=30), "Timed out waiting for initial connection"
            conn_id0 = client._connection_id
            client.join_group(name)
            connected_event.clear()  # reset for reconnection detection
            client._ws.sock.close(1001)  # close the connection to trigger auto connect
            # wait for reconnect
            assert connected_event.wait(timeout=30), "Timed out waiting for reconnection"
            self.retry_send_until_message(client, name, name, message_event, retries=10)
            conn_id1 = client._connection_id
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 != conn_id1
        assert name in TEST_RESULT
