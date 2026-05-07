# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import List, Any
import time
import threading
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import (
    WebpubsubClientTest,
    WebpubsubClientPowerShellPreparer,
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
        callback_completed = threading.Event()
        callback_count = 0
        callback_count_lock = threading.Lock()

        def on_group_message(msg: OnGroupDataMessageArgs):
            nonlocal callback_count
            client.send_to_group(group_name, msg.data, "text", no_echo=True)
            with callback_count_lock:
                callback_count += 1
                if callback_count >= 3:
                    callback_completed.set()

        with client:
            client.join_group(group_name)
            client.subscribe("group-message", on_group_message)
            client.send_to_group(group_name, "hello test_call_back_deadlock1", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock2", "text")
            client.send_to_group(group_name, "hello test_call_back_deadlock3", "text")
            assert callback_completed.wait(timeout=30), "Timed out waiting for callbacks to finish"

    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_context_manager(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        _, _, message_event = self.setup_events(client)
        with client:
            group_name = "test_context_manager"
            client.join_group(group_name)
            client.send_to_group(group_name, "test_context_manager", "text")
            assert message_event.wait(timeout=30), "Timed out waiting for context manager message"
            assert client._sequence_id.sequence_id > 0

    # test on_stop
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_on_stop(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        connected_event, disconnected_event, _ = self.setup_events(client)
        reopen_error = None
        reopen_complete = threading.Event()

        def on_stop():
            nonlocal reopen_error
            try:
                # close() can race with immediate reopen, so retry briefly before failing.
                for _ in range(10):
                    try:
                        client.open()
                        break
                    except OpenClientError:
                        time.sleep(1)
                else:
                    raise RuntimeError("Failed to reopen client in stopped callback")

                if not connected_event.wait(timeout=30):
                    raise RuntimeError("Timed out waiting for client to reconnect in stopped callback")
                assert client.is_connected()
            except Exception as e:
                reopen_error = e
            finally:
                reopen_complete.set()

        with client:
            # open client again after close
            client.subscribe("stopped", on_stop)
            assert connected_event.wait(timeout=30), "Timed out waiting for initial connection"
            assert client.is_connected()
            connected_event.clear()
            client.close()
            # wait for on_stop callback to finish reopening
            if not reopen_complete.wait(timeout=60):
                pytest.fail("on_stop callback failed to complete within 60 seconds")
            assert reopen_error is None, f"on_stop callback failed: {reopen_error}"

            # remove stopped event and close again
            client.unsubscribe("stopped", on_stop)
            disconnected_event.clear()
            client.close()
            assert disconnected_event.wait(timeout=30), "Timed out waiting for client to disconnect"
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
            connected_event, _, message_event = self.setup_events(client)
            with client:
                client.join_group(test_group_name)

            connected_event.clear()
            message_event.clear()
            with client:
                assert connected_event.wait(timeout=30), "Timed out waiting for connection"
                if enable_auto_rejoin:
                    self.retry_send_until_message(client, test_group_name, test_group_name, message_event)
                else:
                    client.send_to_group(test_group_name, test_group_name, "text")
            # wait for on_group_message callback to fire
            message_event.wait(timeout=10)
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
