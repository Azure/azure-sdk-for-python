# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer, SafeThread


@pytest.mark.live_test_only
class TestWebpubsubClientSendConcurrently(WebpubsubClientTest):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_send_concurrently(self, webpubsubclient_endpoint):
        client = self.create_client(endpoint=webpubsubclient_endpoint)
        connected_event, _, _ = self.setup_events(client)
        with client:
            assert connected_event.wait(timeout=30), "Timed out waiting for connection"
            group_name = "test_send_concurrently"
            client.join_group(group_name)

            def send(idx):
                client.send_to_group(group_name, f"hello_{idx}", "text")

            all_threads = []
            for i in range(100):
                t = SafeThread(target=send, args=(i,))
                t.start()
                all_threads.append(t)
            for t in all_threads:
                t.join()
