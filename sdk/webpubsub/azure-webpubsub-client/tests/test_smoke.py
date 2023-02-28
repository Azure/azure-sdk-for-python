# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer
from azure.webpubsub.client.models import OnGroupDataMessageArgs


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
            client.send_to_group(group_name, "hello test_context_manager", "text")
