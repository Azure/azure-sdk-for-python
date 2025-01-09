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
from devtools_testutils import get_credential, is_live
from azure.communication.sms.aio import SmsClient
from azure.core.exceptions import HttpResponseError
from _shared.utils import async_create_token_credential, get_http_logging_policy
from acs_sms_test_case import ACSSMSTestCase


@pytest.mark.asyncio
class TestClientAsync(ACSSMSTestCase):
    def setup_method(self):
        super().setUp()

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
