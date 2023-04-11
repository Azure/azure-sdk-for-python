# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, TEST_RESULT, on_group_message
from azure.webpubsub.client.models import WebPubSubProtocolType

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
            with pytest.raises(Exception):
                client.send_to_group(group_name, name, "text")
        assert name not in TEST_RESULT
