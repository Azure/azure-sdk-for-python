# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.communication.sms import SmsClient
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
    def test_send_sms_single(self):

        # calling send() with sms values
        sms_responses = self.sms_client.send(
            from_=self.phone_number,
            to=self.phone_number,
            message="Hello World via SMS",
            enable_delivery_report=True,  # optional property
            tag="custom-tag")  # optional property
        
        assert len(sms_responses) is 1

        for sms_response in sms_responses:
            self.verify_sms_response(sms_response)
    
    @pytest.mark.live_test_only
    def test_send_sms_multiple(self):

        # calling send() with sms values
        sms_responses = self.sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number, self.phone_number],
            message="Hello World via SMS",
            enable_delivery_report=True,  # optional property
            tag="custom-tag")  # optional property
        
        assert len(sms_responses) is 2

        for sms_response in sms_responses:
            self.verify_sms_response(sms_response)
    
    @pytest.mark.live_test_only
    def test_send_sms_invalid_to_phone_number(self):

        # calling send() with sms values
        sms_responses = self.sms_client.send(
            from_=self.phone_number,
            to=["+1234567891011"],
            message="Hello World via SMS",
            enable_delivery_report=True,  # optional property
            tag="custom-tag")  # optional property
        
        assert len(sms_responses) is 1

        for sms_response in sms_responses:
            assert sms_response.http_status_code == 400
            assert not sms_response.successful
    
    @pytest.mark.live_test_only
    def test_send_sms_unique_message_ids(self):

        # calling send() with sms values
        sms_responses_1 = self.sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number],
            message="Hello World via SMS")
        
        # calling send() again with the same sms values
        sms_responses_2 = self.sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number],
            message="Hello World via SMS")
        
        # message ids should be unique due to having a different idempotency key
        assert sms_responses_1[0].message_id != sms_responses_2[0].message_id

    def verify_sms_response(self, sms_response):
        assert sms_response.to == self.phone_number
        assert sms_response.message_id is not None
        assert sms_response.http_status_code == 202
        assert sms_response.error_message is None
        assert sms_response.successful
        