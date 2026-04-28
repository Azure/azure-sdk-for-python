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


@pytest.mark.live_test_only
class TestWebpubsubClientRecovery(WebpubsubClientTest):
    # recovery will be triggered if connection is dropped by accident
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_recovery(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint, message_retry_total=10)
        name = "test_recovery"
        with client:
            # wait for connection_id to be updated
            for _ in range(30):
                if client._connection_id is not None:
                    break
                time.sleep(1)
            conn_id0 = client._connection_id
            group_name = name
            client.subscribe("group-message", on_group_message)
            client.join_group(group_name)
            client._ws.sock.close(1001)  # close connection to trigger recovery
            client.send_to_group(group_name, name, "text")
            conn_id1 = client._connection_id
            # wait for on_group_message callback to fire
            for _ in range(10):
                if name in TEST_RESULT:
                    break
                time.sleep(1)

        assert name in TEST_RESULT
        assert conn_id0 is not None
        assert conn_id1 is not None
        assert conn_id0 == conn_id1
