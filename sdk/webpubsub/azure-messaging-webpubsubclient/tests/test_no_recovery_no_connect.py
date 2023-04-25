# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import time
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, TEST_RESULT, on_group_message, SafeThread
from azure.messaging.webpubsubclient.models import WebPubSubProtocolType, DisconnectedError


@pytest.mark.live_test_only
class TestWebpubsubClientNoRecoveryNoReconnect(WebpubsubClientTest):
    # disable recovery and auto reconnect
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_disable_recovery_and_autoconnect(self, webpubsubclient_connection_string):
        client = self.create_client(
            connection_string=webpubsubclient_connection_string,
            reconnect_retry_total=0,
            protocol_type=WebPubSubProtocolType.JSON,
        )
        name = "test_disable_recovery_and_autoconnect"
        with client:
            group_name = name
            client.on("group-message", on_group_message)
            client.join_group(group_name)
            client._ws.sock.close(1001)  # close connection
            with pytest.raises(DisconnectedError):
                client.send_to_group(group_name, name, "text")
            time.sleep(1)  # wait for on_group_message to be called

        assert name not in TEST_RESULT

    # disable recovery and auto reconnect, then send message concurrently
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_disable_recovery_and_autoconnect_send_concurrently(self, webpubsubclient_connection_string):
        client = self.create_client(
            connection_string=webpubsubclient_connection_string,
            reconnect_retry_total=0,
            message_retry_total=3,
            protocol_type=WebPubSubProtocolType.JSON,
        )

        with client:
            group_name = "test"
            client.join_group(group_name)

            def send(idx):
                client.send_to_group(group_name, f"hello_{idx}", "text")

            all_threads = []
            for i in range(100):
                t = SafeThread(target=send, args=(i,))
                t.start()
                all_threads.append(t)
                if i == 50:
                    client._ws.sock.close(1001)  # close connection

            for i, t in enumerate(all_threads):
                if i > 50:
                    with pytest.raises(Exception):
                        t.join()
