# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.sms import SmsClient
from azure.communication.sms._shared.utils import parse_connection_str
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from azure.identity import DefaultAzureCredential

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class SMSClientTest(CommunicationTestCase):
    def __init__(self, method_name):
        super(SMSClientTest, self).__init__(method_name)

    def setUp(self):
        super(SMSClientTest, self).setUp()

        if self.is_playback():
            self.phone_number = "+14255550123"
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["to", "from", "messageId", "repeatabilityRequestId", "repeatabilityFirstSent"])])
        else:
            self.phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["to", "from", "messageId", "repeatabilityRequestId", "repeatabilityFirstSent"]),
                ResponseReplacerProcessor(keys=[self._resource_name])])
    
    def test_send_sms_single(self):
        
        sms_client = SmsClient.from_connection_string(self.connection_str)

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=self.phone_number,
            message="Hello World via SMS")

        assert len(sms_responses) == 1

        self.verify_successful_sms_response(sms_responses[0])
    
    def test_send_sms_multiple_with_options(self):
        
        sms_client = SmsClient.from_connection_string(self.connection_str)
        
        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number, self.phone_number],
            message="Hello World via SMS",
            enable_delivery_report=True,  # optional property
            tag="custom-tag")  # optional property
        
        assert len(sms_responses) == 2

        self.verify_successful_sms_response(sms_responses[0])
        self.verify_successful_sms_response(sms_responses[1])
    
    def test_send_sms_from_managed_identity(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        sms_client = SmsClient(endpoint, credential)

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number],
            message="Hello World via SMS")
        
        assert len(sms_responses) == 1

        self.verify_successful_sms_response(sms_responses[0])

    def test_send_sms_fake_from_phone_number(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)
        
        with pytest.raises(HttpResponseError) as ex:
            # calling send() with sms values
            sms_client.send(
                from_="+15550000000",
                to=[self.phone_number],
                message="Hello World via SMS")
        
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_send_sms_fake_to_phone_number(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=["+15550000000"],
            message="Hello World via SMS")
        
        assert len(sms_responses) == 1

        assert sms_responses[0].message_id is None
        assert sms_responses[0].http_status_code == 400
        assert sms_responses[0].error_message == "Invalid To phone number format."
        assert not sms_responses[0].successful
    
    def test_send_sms_unauthorized_from_phone_number(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)
        
        with pytest.raises(HttpResponseError) as ex:
            # calling send() with sms values
            sms_client.send(
                from_="+14255550123",
                to=[self.phone_number],
                message="Hello World via SMS")
        
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_send_sms_unique_message_ids(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        # calling send() with sms values
        sms_responses_1 = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number],
            message="Hello World via SMS")
        
        # calling send() again with the same sms values
        sms_responses_2 = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number],
            message="Hello World via SMS")
        
        self.verify_successful_sms_response(sms_responses_1[0])
        self.verify_successful_sms_response(sms_responses_2[0])
        # message ids should be unique due to having a different idempotency key
        assert sms_responses_1[0].message_id != sms_responses_2[0].message_id

    def verify_successful_sms_response(self, sms_response):
        if self.is_live:
            assert sms_response.to == self.phone_number
        assert sms_response.message_id is not None
        assert sms_response.http_status_code == 202
        assert sms_response.error_message is None
        assert sms_response.successful
        