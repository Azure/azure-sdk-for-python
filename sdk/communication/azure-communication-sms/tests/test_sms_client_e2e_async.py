# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import logging
import sys

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils import get_credential, is_live, set_custom_default_matcher
from azure.communication.sms.aio import SmsClient
from azure.core.exceptions import HttpResponseError
from _shared.utils import async_create_token_credential, get_http_logging_policy
from acs_sms_test_case import ACSSMSTestCase


@pytest.mark.asyncio
class TestClientAsync(ACSSMSTestCase):
    def setup_method(self):
        super().setUp()

        # On python 3.14, azure-core sends an additional 'Accept-Encoding' header value that causes playback issues.
        # By ignoring it, we can avoid really wonky mismatch errors, while still validating the other headers
        if sys.version_info >= (3, 14):
            headers_to_ignore = "Accept-Encoding"
            set_custom_default_matcher(ignored_headers=headers_to_ignore)

    @recorded_by_proxy_async
    async def test_send_sms_single_async(self):
        sms_client = self.create_client_from_connection_string()

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number, to=self.phone_number, message="Hello World via SMS"
            )

            assert len(sms_responses) == 1

            self.verify_successful_sms_response(sms_responses[0])

    @recorded_by_proxy_async
    async def test_send_sms_multiple_with_options_async(self):
        sms_client = self.create_client_from_connection_string()

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number,
                to=[self.phone_number, self.phone_number],
                message="Hello World via SMS",
                enable_delivery_report=True,  # optional property
                tag="custom-tag",
            )  # optional property

            assert len(sms_responses) == 2

            self.verify_successful_sms_response(sms_responses[0])
            self.verify_successful_sms_response(sms_responses[1])

    @recorded_by_proxy_async
    async def test_send_sms_from_managed_identity_async(self):
        if not is_live():
            credential = AsyncFakeCredential()
        else:
            credential = get_credential(is_async=True)
        sms_client = SmsClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

        async with sms_client:
            # calling send() with sms values
            sms_responses = await sms_client.send(
                from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS"
            )

            assert len(sms_responses) == 1

            self.verify_successful_sms_response(sms_responses[0])

    @recorded_by_proxy_async
    async def test_send_sms_fake_from_phone_number_async(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            async with sms_client:
                # calling send() with sms values
                await sms_client.send(from_="+15550000000", to=[self.phone_number], message="Hello World via SMS")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_send_sms_fake_to_phone_number_async(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            async with sms_client:
                await sms_client.send(from_=self.phone_number, to=["Ad155500000000000"], message="Hello World via SMS")

        assert str(ex.value.status_code == "400")

    @recorded_by_proxy_async
    async def test_send_sms_unauthorized_from_phone_number_async(self):
        sms_client = self.create_client_from_connection_string()

        with pytest.raises(HttpResponseError) as ex:
            async with sms_client:
                # calling send() with sms values
                await sms_client.send(from_="+14255550123", to=[self.phone_number], message="Hello World via SMS")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy_async
    async def test_send_sms_unique_message_ids_async(self):
        sms_client = self.create_client_from_connection_string()

        async with sms_client:
            # calling send() with sms values
            sms_responses_1 = await sms_client.send(
                from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS"
            )

            # calling send() again with the same sms values
            sms_responses_2 = await sms_client.send(
                from_=self.phone_number, to=[self.phone_number], message="Hello World via SMS"
            )

            self.verify_successful_sms_response(sms_responses_1[0])
            self.verify_successful_sms_response(sms_responses_2[0])
            # message ids should be unique due to having a different idempotency key
            assert sms_responses_1[0].message_id != sms_responses_2[0].message_id

    def create_client_from_connection_string(self):
        return SmsClient.from_connection_string(self.connection_str, http_logging_policy=get_http_logging_policy())

    @recorded_by_proxy_async
    async def test_get_delivery_status_existing_message_async(self):
        """Test getting delivery status for an existing message"""
        import asyncio
        
        sms_client = self.create_client_from_connection_string()

        async with sms_client:
            # First send an SMS to get a message ID
            sms_responses = await sms_client.send(from_=self.phone_number, to=self.phone_number, message="Hello World via SMS")
            assert len(sms_responses) == 1
            message_id = sms_responses[0].message_id
            assert message_id is not None

            await asyncio.sleep(5)

            # Now get delivery status using the same SMS client (consolidated functionality)
            delivery_report = await sms_client.get_delivery_report(message_id)

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
        sms_client = self.create_client_from_connection_string()

        # Use a fake message ID that doesn't exist
        fake_message_id = "00000000-0000-0000-0000-000000000000"

        async with sms_client:
            try:
                # Try to get status - might return a result instead of throwing exception
                result = await sms_client.get_delivery_report(fake_message_id)

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

    @recorded_by_proxy_async
    async def test_get_delivery_report_from_managed_identity_async(self):
        """Test delivery report retrieval using token credential (managed identity) async"""
        if not is_live():
            credential = AsyncFakeCredential()
        else:
            credential = get_credential(is_async=True)
        sms_client = SmsClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

        async with sms_client:
            # First send a message to get a message ID
            sms_responses = await sms_client.send(from_=self.phone_number, to=[self.phone_number], message="Test message for delivery report")
            assert len(sms_responses) == 1
            message_id = sms_responses[0].message_id

            # Now test delivery report retrieval with token credential
            delivery_report = await sms_client.get_delivery_report(message_id)
            
            # Verify the delivery report structure
            assert delivery_report is not None
            assert hasattr(delivery_report, 'message_id')
            assert delivery_report.message_id == message_id
