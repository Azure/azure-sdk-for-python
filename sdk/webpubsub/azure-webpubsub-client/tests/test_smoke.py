# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import List, Any
import time
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer
from azure.webpubsub.client.models import OnGroupDataMessageArgs, WebPubSubProtocolType

TEST_RESULT = set()


def on_group_message(msg: OnGroupDataMessageArgs):
    TEST_RESULT.add(msg.data)


@pytest.mark.live_test_only
class TestWebpubsubClientSmoke(WebpubsubClientTest):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_call_back_deadlock(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        group_name = "test"

        def on_group_message(msg: OnGroupDataMessageArgs):
            client.send_to_group(group_name, msg.data, "text", no_echo=True)

        with client:
            client.join_group(group_name)
            client.on("group-message", on_group_message)
            client.send_to_group(group_name, "hello test_call_back_deadlock1", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock2", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock3", "text")
            # sleep to make sure the callback has enough time to execute before stop
            time.sleep(0.001)

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_context_manager(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        with client:
            group_name = "test"
            client.join_group(group_name)
            client.send_to_group(group_name, "test_context_manager", "text")
            assert client._sequence_id.sequence_id > 0

    # auto_connect will be triggered if connection is dropped by accident
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_auto_connect(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        name = "test_auto_connect"
        with client:
            conn_id0 = client._connection_id
            group_name = "test"
            client.on("group-message", on_group_message)
            client.join_group(group_name)
            client._ws.sock.close()
            time.sleep(0.001)
            client.send_to_group(group_name, name, "text")
            conn_id1 = client._connection_id
        assert name in TEST_RESULT
        assert conn_id0 != conn_id1

    # recovery will be triggered if connection is dropped by accident and disable auto reconnect
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_recovery(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string, reconnect_retry_total=0)
        name = "test_recovery"
        with client:
            conn_id0 = client._connection_id
            group_name = "test"
            client.on("group-message", on_group_message)
            client.join_group(group_name)
            # close connection with abnormal code
            client._ws.sock.close(1001)
            time.sleep(0.001)
            client.send_to_group(group_name, name, "text")
            conn_id1 = client._connection_id
        assert name in TEST_RESULT
        assert conn_id0 == conn_id1

    # disable recovery and auto reconnect
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_disable_recovery_autoconnect(self, webpubsubclient_connection_string):
        client = self.create_client(
            connection_string=webpubsubclient_connection_string,
            reconnect_retry_total=0,
            protocol_type=WebPubSubProtocolType.JSON,
        )
        name = "test_disable_recovery_autoconnect"
        with client:
            group_name = "test"
            client.on("group-message", on_group_message)
            client.join_group(group_name)
            # close connection with abnormal code
            client._ws.sock.close(1001)
            time.sleep(0.001)
            client.send_to_group(group_name, name, "text")
        assert name not in TEST_RESULT
