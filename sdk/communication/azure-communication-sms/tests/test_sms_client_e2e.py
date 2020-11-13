# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.communication.sms import (
    PhoneNumber, SendSmsOptions, SmsClient
)
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)

class SMSClientTest(CommunicationTestCase):
    def __init__(self, method_name):
        super(SMSClientTest, self).__init__(method_name)

    def setUp(self):
        super(SMSClientTest, self).setUp()
        
        if self.is_playback():
            self.phone_number = "+18000005555"
        else:
            self.phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["to", "from", "messageId"]),
            ResponseReplacerProcessor(keys=[self._resource_name])])

        self.sms_client = SmsClient.from_connection_string(self.connection_str)

    @pytest.mark.live_test_only
    def test_send_sms(self):

        # calling send() with sms values
        sms_response = self.sms_client.send(
            from_phone_number=PhoneNumber(self.phone_number),
            to_phone_numbers=[PhoneNumber(self.phone_number)],
            message="Hello World via SMS",
            send_sms_options=SendSmsOptions(enable_delivery_report=True))  # optional property

        assert sms_response.message_id is not None
