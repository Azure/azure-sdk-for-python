# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import logging
import sys
import asyncio
import time

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils import get_credential, is_live
from azure.communication.sms.aio import SmsClient
from azure.communication.sms.aio import DeliveryReportsClient
from azure.core.exceptions import HttpResponseError
from _shared.utils import async_create_token_credential, get_http_logging_policy
from acs_sms_test_case import ACSSMSTestCase


@pytest.mark.asyncio
class TestDeliveryReportsClientAsync(ACSSMSTestCase):
    def setup_method(self):
        super().setUp()
        # Ensure phone number is available for tests
        assert self.phone_number is not None, "Phone number must be set for SMS tests"

    @recorded_by_proxy_async 
    async def test_get_delivery_status_existing_message_async(self):
        """Test getting delivery status for an existing message"""
        # First send an SMS to get a message ID
        sms_client = self.create_sms_client_from_connection_string()
        
        async with sms_client:
            sms_responses = await sms_client.send(from_=self.phone_number, to=self.phone_number, message="Hello World via SMS")
        
        assert len(sms_responses) == 1
        message_id = sms_responses[0].message_id
        assert message_id is not None

        time.sleep(5)

        # Now get delivery status
        delivery_client = self.create_delivery_reports_client_from_connection_string()
        
        async with delivery_client:
            delivery_report = await delivery_client.get_status(message_id)

        # Verify delivery report structure
        assert delivery_report is not None
        assert delivery_report.message_id == message_id
        if self.is_live:
            assert delivery_report.from_property == self.phone_number
            assert delivery_report.to == self.phone_number
        assert delivery_report.delivery_status is not None
        assert hasattr(delivery_report, 'received_timestamp')

    @recorded_by_proxy_async
    async def test_get_delivery_status_nonexistent_message_async(self):
        """Test getting delivery status for a non-existent message ID"""
        delivery_client = self.create_delivery_reports_client_from_connection_string()
        
        # Use a fake message ID that doesn't exist
        fake_message_id = "00000000-0000-0000-0000-000000000000"
        
        async with delivery_client:
            with pytest.raises(HttpResponseError) as ex:
                await delivery_client.get_status(fake_message_id)

        # Should get a 404 or similar error
        assert ex.value.status_code in [404, 400]
        assert ex.value.message is not None

    def create_sms_client_from_connection_string(self):
        return SmsClient.from_connection_string(self.connection_str, http_logging_policy=get_http_logging_policy())

    def create_delivery_reports_client_from_connection_string(self):
        return DeliveryReportsClient.from_connection_string(self.connection_str, http_logging_policy=get_http_logging_policy())
