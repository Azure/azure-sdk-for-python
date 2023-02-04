# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import AzureMgmtTestCase
from azure.communication.callautomation import CallAutomationClient

class CallAutomationTest(AzureMgmtTestCase):
    def setUp(self):
        super(CallAutomationTest, self).setUp()

    def test_temp(self):
        call_automation_client = CallAutomationClient.from_connection_string("endpoint=https://<ResourceUrl>/;accesskey=<KeyValue>")
        call_connection = call_automation_client.get_call_connection("<callconnid>")
        call_media = call_connection.get_call_media()
        call_recording = call_automation_client.get_call_recording()