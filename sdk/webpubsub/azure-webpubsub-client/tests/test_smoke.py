# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer


class TestWebpubsubClientSmoke(WebpubsubClientTest):
    @WebpubsubClientPowerShellPreparer()
    @recorded_by_proxy
    def test_start_stop(self, webpubsubclient_connection_string):
        client = self.create_client(connection_string=webpubsubclient_connection_string)
        client.start()
        assert client.is_connected()
        client.stop()
        assert not client.is_connected()
