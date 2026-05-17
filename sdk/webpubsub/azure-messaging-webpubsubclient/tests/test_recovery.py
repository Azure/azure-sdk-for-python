# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, TEST_RESULT


@pytest.mark.live_test_only
class TestWebpubsubClientRecovery(WebpubsubClientTest):
    # recovery will be triggered if connection is dropped by accident
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_recovery(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint, message_retry_total=10)
        name = "test_recovery"
        connected_event, _, message_event = self.setup_events(client)
        with client:
            assert connected_event.wait(timeout=30), "Timed out waiting for connection"
            conn_id0 = client._connection_id
            client.join_group(name)
            client._ws.sock.close(1001)  # close connection to trigger recovery
            self.retry_send_until_message(client, name, name, message_event)
            conn_id1 = client._connection_id

        assert name in TEST_RESULT
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 == conn_id1
