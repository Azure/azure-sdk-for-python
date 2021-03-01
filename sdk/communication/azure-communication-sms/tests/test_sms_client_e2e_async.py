# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.core.credentials import AccessToken
from azure.communication.sms.aio import SmsClient
from azure.communication.sms._shared.utils import parse_connection_str
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import (
    BodyReplacerProcessor, ResponseReplacerProcessor
)
from azure.identity import DefaultAzureCredential

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class SMSClientTestAsync(AsyncCommunicationTestCase):
    def __init__(self, method_name):
        super(SMSClientTestAsync, self).__init__(method_name)

    def setUp(self):
        super(SMSClientTestAsync, self).setUp()

        if self.is_playback():
            self.phone_number = "+18000005555"
        else:
            self.phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["to", "from", "messageId"]),
            ResponseReplacerProcessor(keys=[self._resource_name])])

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_send_sms_single_async(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number,
                to=self.phone_number,
                message="Hello World via SMS",
                enable_delivery_report=True,  # optional property
                tag="custom-tag")  # optional property
            
            assert len(sms_responses) is 1

            for sms_response in sms_responses:
                self.verify_sms_response(sms_response)
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_send_sms_multiple_async(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number,
                to=[self.phone_number, self.phone_number],
                message="Hello World via SMS",
                enable_delivery_report=True,  # optional property
                tag="custom-tag")  # optional property
            
            assert len(sms_responses) is 2

            for sms_response in sms_responses:
                self.verify_sms_response(sms_response)

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_send_sms_async_from_managed_identity(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        from devtools_testutils import is_live
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        sms_client = SmsClient(endpoint, credential)

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number,
                to=[self.phone_number],
                message="Hello World via SMS",
                enable_delivery_report=True,  # optional property
                tag="custom-tag")  # optional property
            
            assert len(sms_responses) is 1

            for sms_response in sms_responses:
                self.verify_sms_response(sms_response)
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_send_sms_invalid_to_phone_number_async(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number,
                to=["+1234567891011"],
                message="Hello World via SMS",
                enable_delivery_report=True,  # optional property
                tag="custom-tag")  # optional property
            
            assert len(sms_responses) is 1

        for sms_response in sms_responses:
            assert sms_response.http_status_code == 400
            assert not sms_response.successful
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_send_sms_unique_message_ids_async(self):

        sms_client = SmsClient.from_connection_string(self.connection_str)

        async with sms_client:
            # calling send() with sms values
            sms_responses_1 = await sms_client.send(
                from_=self.phone_number,
                to=[self.phone_number],
                message="Hello World via SMS")
        
            # calling send() again with the same sms values
            sms_responses_2 = await sms_client.send(
                from_=self.phone_number,
                to=[self.phone_number],
                message="Hello World via SMS")
        
            assert sms_responses_1[0].message_id != sms_responses_2[0].message_id
    
    def verify_sms_response(self, sms_response):
        assert sms_response.to == self.phone_number
        assert sms_response.message_id is not None
        assert sms_response.http_status_code == 202
        assert sms_response.error_message is None
        assert sms_response.successful
            