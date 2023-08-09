# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from typing import TYPE_CHECKING, Any, Dict, Optional  # pylint: disable=unused-import
from _shared.testcase import CommunicationTestCase
from azure.communication.callautomation import CallAutomationClient

class CallAutomationTestCase(CommunicationTestCase):
    def __init__(self, method_name, **kwargs):
        super(CallAutomationTestCase, self).__init__(method_name, **kwargs)
    def create_client(self, endpoint):
        credential = self.get_credential(CallAutomationClient)
        return self.create_client_from_credential(
            CallAutomationClient,
            credential=credential,
            endpoint=endpoint,
        )
    def _get_connection_str(self, resource_type):
        if self.is_playback():
            return "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        else:
            con_str = os.getenv('COMMUNICATION_CONNECTION_STRING_CALLAUTOMATION')
            if con_str == None:
                return super(CallAutomationTestCase, self)._get_connection_str(resource_type)
            return con_str