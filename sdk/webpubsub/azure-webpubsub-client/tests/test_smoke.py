# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer
from azure.messaging.webpubsubservice._operations._operations import build_send_to_all_request
from azure.core.exceptions import ServiceRequestError

class WebpubsubClientSmokeTest(WebpubsubClientTest):


    @WebpubsubClientPowerShellPreparer()
    def test_webpubsub_send_to_all(self, webpubsub_endpoint):
        client = self.create_client(endpoint=webpubsub_endpoint, hub='hub')
        client.send_to_all({'hello': 'test_webpubsub_send_to_all'})