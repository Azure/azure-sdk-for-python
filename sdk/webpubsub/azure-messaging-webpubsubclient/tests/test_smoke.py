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
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, on_group_message, TEST_RESULT
from azure.messaging.webpubsubclient.models import OnGroupDataMessageArgs, StartNotStoppedClientError


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
            time.sleep(2.0)
            assert client._sequence_id.sequence_id > 0

    # test on_stop
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_on_stop(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)

        def on_stop():
            client._start()

        with client:
            # start client again after stop
            client.on("stopped", on_stop)
            assert client._is_connected()
            client._stop()
            time.sleep(1.0)
            assert client._is_connected()

            # remove stopped event and stop again
            client.off("stopped", on_stop)
            client._stop()
            time.sleep(1.0)
            assert not client._is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_duplicated_start(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        with pytest.raises(StartNotStoppedClientError):
            with client:
                client._start()
        assert not client._is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_duplicated_stop(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        with client:
            client._stop()
        assert not client._is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_send_event(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string, message_retry_total=0)
        with client:
            # please register event handler in azure portal before run this test
            client.send_event("event", "test_send_event", "text")

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_rejoin_group(self, webpubsubclient_connection_string):
        def _test(enable_auto_rejoin, test_group_name, assert_func):
            client = self.create_client(
                connection_string=webpubsubclient_connection_string, auto_rejoin_groups=enable_auto_rejoin
            )
            group_name = test_group_name
            client.on("group-message", on_group_message)
            with client:
                client.join_group(group_name)

            with client:
                time.sleep(1)  # make sure rejoin group is called
                client.send_to_group(group_name, "test_rejoin_group", "text")
                time.sleep(1)  # wait for on_group_message to be called
                assert assert_func(test_group_name)

        _test(enable_auto_rejoin=True, test_group_name="test_rejoin_group", assert_func=lambda x: x in TEST_RESULT)
        _test(
            enable_auto_rejoin=False,
            test_group_name="test_disable_rejoin_group",
            assert_func=lambda x: x not in TEST_RESULT,
        )
