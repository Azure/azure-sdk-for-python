# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import logging
import sys

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
