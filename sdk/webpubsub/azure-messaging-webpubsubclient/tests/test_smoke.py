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
from testcase import (
    WebpubsubClientTest,
    WebpubsubClientPowerShellPreparer,
    on_group_message,
    TEST_RESULT,
)
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import (
    OnGroupDataMessageArgs,
    OpenClientError,
    SendMessageError,
)


@pytest.mark.live_test_only
class TestWebpubsubClientSmoke(WebpubsubClientTest):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_call_back_deadlock(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        group_name = "test_call_back_deadlock"

        def on_group_message(msg: OnGroupDataMessageArgs):
            client.send_to_group(group_name, msg.data, "text", no_echo=True)

        with client:
            client.join_group(group_name)
            client.subscribe("group-message", on_group_message)
            client.send_to_group(group_name, "hello test_call_back_deadlock1", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock2", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock3", "text")
            # sleep to make sure the callback has enough time to execute before close
            time.sleep(1)

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_context_manager(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        with client:
            group_name = "test_context_manager"
            client.join_group(group_name)
            client.send_to_group(group_name, "test_context_manager", "text")
            time.sleep(2.0)
            assert client._sequence_id.sequence_id > 0

    # test on_stop
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_on_stop(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)

        def on_stop():
            client.open()

        with client:
            # open client again after close
            client.subscribe("stopped", on_stop)
            time.sleep(0.1)
            assert client.is_connected()
            client.close()
            # wait for on_stop callback to reconnect
            for _ in range(30):
                if client.is_connected():
                    break
                time.sleep(1)
            assert client.is_connected()

            # remove stopped event and close again
            client.unsubscribe("stopped", on_stop)
            client.close()
            # wait for disconnect to finalize
            for _ in range(30):
                if not client.is_connected():
                    break
                time.sleep(1)
            assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_duplicated_start(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        with pytest.raises(OpenClientError):
            with client:
                client.open()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_duplicated_stop(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        with client:
            client.close()
        assert not client.is_connected()

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_send_event(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint, message_retry_total=0)
        with client:
            # please register event handler in azure portal before run this test
            try:
                client.send_event("event", "test_send_event", "text")
            except SendMessageError as err:
                assert err.error_detail.name == "InternalServerError"

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_rejoin_group(self, webpubsubclient_endpoint):
        def _test(enable_auto_rejoin, test_group_name, assert_func):
            client = self.create_client(
                endpoint=webpubsubclient_endpoint,
                auto_rejoin_groups=enable_auto_rejoin,
                message_retry_total=10,
            )
            group_name = test_group_name
            client.subscribe("group-message", on_group_message)
            with client:
                client.join_group(group_name)

            with client:
                # retry send until connection is ready (open() runs in background thread)
                for attempt in range(30):
                    try:
                        if not client.is_connected():
                            time.sleep(1)
                            continue
                        client.send_to_group(group_name, group_name, "text")
                        break
                    except SendMessageError:
                        time.sleep(1)
                else:
                    raise RuntimeError("Failed to send after 30 attempts")
                time.sleep(1)  # wait for on_group_message to be called
                assert assert_func(test_group_name)

        _test(
            enable_auto_rejoin=True,
            test_group_name="test_rejoin_group",
            assert_func=lambda x: x in TEST_RESULT,
        )
        _test(
            enable_auto_rejoin=False,
            test_group_name="test_disable_rejoin_group",
            assert_func=lambda x: x not in TEST_RESULT,
        )

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_open_client_error(self):
        client = WebPubSubClient(
            credential=WebPubSubClientCredential(
                lambda: "wss://myservice.webpubsub.azure.com/client/hubs/Hub"
            ),
        )
        start_time = time.time()
        with pytest.raises(OpenClientError) as err:
            with client:
                pass
        assert time.time() - start_time < client._start_timeout
        assert "During the process, an error occurred" in str(err)
