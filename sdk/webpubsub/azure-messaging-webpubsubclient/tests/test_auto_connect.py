# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, TEST_RESULT, on_group_message
from azure.messaging.webpubsubclient.models import WebPubSubProtocolType


@pytest.mark.live_test_only
class TestWebpubsubClientAutoConnect(WebpubsubClientTest):
    # auto_connect will be triggered if connection is dropped by accident and we disable recovery
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_auto_connect(self, webpubsubclient_connection_string):
        client = self.create_client(
            connection_string=webpubsubclient_connection_string,
            protocol_type=WebPubSubProtocolType.JSON,
            message_retry_total=10,
            reconnect_retry_total=10,
            reconnect_retry_mode="fixed",
            reconnect_retry_backoff_factor=0.1,
        )
        name = "test_auto_connect"
        with client:
            time.sleep(0.001)  # wait for connection_id to be updated
            conn_id0 = client._connection_id
            group_name = name
            client.on("group-message", on_group_message)
            client.join_group(group_name)
            client._ws.sock.close(1001)  # close the connection to trigger auto connect
            time.sleep(3)  # wait for reconnect
            client.send_to_group(group_name, name, "text")
            time.sleep(1)  # wait for on_group_message to be called
            conn_id1 = client._connection_id
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 != conn_id1
        assert name in TEST_RESULT
