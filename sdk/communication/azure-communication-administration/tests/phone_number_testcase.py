# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.communication.administration._shared.utils import parse_connection_str
from _shared.testcase import CommunicationTestCase

class PhoneNumberCommunicationTestCase(CommunicationTestCase):
    def setUp(self):
        super(PhoneNumberCommunicationTestCase, self).setUp()

        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized/;accesskey=fake==="
        else:
            self.connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
            endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
            self.scrubber.register_name_pair(self._resource_name, "sanitized")
