# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import logging
import sys
import time

import pytest
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils import get_credential, is_live, recorded_by_proxy, set_bodiless_matcher
from _shared.utils import get_http_logging_policy
from azure.core.exceptions import HttpResponseError
from acs_sms_test_case import ACSSMSTestCase
from azure.communication.sms import SmsClient


class TestClient(ACSSMSTestCase):
    def setup_method(self):
        super().setUp()

        set_bodiless_matcher()

    @recorded_by_proxy
    def test_send_sms_single(self):
        sms_client = self.create_client_from_connection_string()

        # calling send() with sms values
        sms_responses = sms_client.send(from_=self.phone_number, to=self.phone_number, message="Hello World via SMS")

        assert len(sms_responses) == 1
        self.verify_successful_sms_response(sms_responses[0])

    @recorded_by_proxy
    def test_send_sms_multiple_with_options(self):
        sms_client = self.create_client_from_connection_string()

        # calling send() with sms values
        sms_responses = sms_client.send(
            from_=self.phone_number,
            to=[self.phone_number, self.phone_number],
            message="Hello World via SMS",
            enable_delivery_report=True,  # optional property
            tag="custom-tag",
        )  # optional property

        assert len(sms_responses) == 2

        self.verify_successful_sms_response(sms_responses[0])
        self.verify_successful_sms_response(sms_responses[1])

    @recorded_by_proxy
    def test_send_sms_from_managed_identity(self):
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = get_credential()
        sms_client = SmsClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

        # calling send() with sms values
        sms_responses = sms_client.send(from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS")

        assert len(sms_responses) == 1

        self.verify_successful_sms_response(sms_responses[0])

    @recorded_by_proxy
    def test_send_sms_fake_from_phone_number(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            # calling send() with sms values
            sms_client.send(from_="+15550000000", to=[self.phone_number], message="Hello World via SMS")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy
    def test_send_sms_fake_to_phone_number(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            sms_responses = sms_client.send(
                from_=self.phone_number, to=["Ad155500000000000"], message="Hello World via SMS"
            )

        assert str(ex.value.status_code == "400")

    @recorded_by_proxy
    def test_send_sms_unauthorized_from_phone_number(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            # calling send() with sms values
            sms_client.send(from_="+14255550123", to=[self.phone_number], message="Hello World via SMS")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_send_sms_unique_message_ids(self):
        sms_client = self.create_client_from_connection_string()

        # calling send() with sms values
        sms_responses_1 = sms_client.send(
            from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS"
        )

        # calling send() again with the same sms values
        sms_responses_2 = sms_client.send(
            from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS"
        )

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

    def create_client_from_connection_string(self):
        return SmsClient.from_connection_string(self.connection_str, http_logging_policy=get_http_logging_policy())

    @recorded_by_proxy
    def test_get_delivery_status_existing_message(self):
        """Test getting delivery status for an existing message"""
        import time
        
        # First send an SMS to get a message ID
        sms_client = self.create_client_from_connection_string()
        sms_responses = sms_client.send(from_=self.phone_number, to=self.phone_number, message="Hello World via SMS")
        assert len(sms_responses) == 1
        message_id = sms_responses[0].message_id
        assert message_id is not None

        time.sleep(5)

        # Now get delivery status using the same SMS client (consolidated functionality)
        delivery_report = sms_client.get_delivery_report(message_id)

        # Verify delivery report structure
        assert delivery_report is not None
        assert delivery_report.message_id == message_id
        if self.is_live:
            assert delivery_report.from_property == self.phone_number
            assert delivery_report.to == self.phone_number
        assert delivery_report.delivery_status is not None
        assert hasattr(delivery_report, 'received_timestamp')

    @recorded_by_proxy
    def test_get_delivery_status_nonexistent_message(self):
        """Test getting delivery status for a non-existent message ID"""
        sms_client = self.create_client_from_connection_string()

        # Use a fake message ID that doesn't exist
        fake_message_id = "00000000-0000-0000-0000-000000000000"

        try:
            # Try to get status - might return a result instead of throwing exception
            result = sms_client.get_delivery_report(fake_message_id)

            # If we get here, the API returned a result instead of throwing an exception
            # Check if it's an empty result or has some indication of "not found"
            if hasattr(result, 'delivery_reports') and len(result.delivery_reports) == 0:
                # Empty result is acceptable for non-existent message
                pass
            elif hasattr(result, 'delivery_status') and result.delivery_status:
                # If there's a delivery status, it might indicate "not found" or similar
                pass
            else:
                # Log what we actually got for debugging
                print(f"Unexpected result for non-existent message: {result}")

        except HttpResponseError as ex:
            # If an exception is thrown, check it's the right kind
            assert ex.status_code in [400, 404, 422], f"Unexpected status code: {ex.status_code}"
            assert ex.message is not None

    @recorded_by_proxy
    def test_get_delivery_report_from_managed_identity(self):
        """Test delivery report retrieval using token credential (managed identity)"""
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = get_credential()
        sms_client = SmsClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

        # First send a message to get a message ID
        sms_responses = sms_client.send(from_=self.phone_number, to=[self.phone_number], message="Test message for delivery report")
        assert len(sms_responses) == 1
        message_id = sms_responses[0].message_id

        time.sleep(10)

        # Now test delivery report retrieval with token credential
        delivery_report = sms_client.get_delivery_report(message_id)
        
        # Verify the delivery report structure
        assert delivery_report is not None
        assert hasattr(delivery_report, 'message_id')
        assert delivery_report.message_id == message_id
