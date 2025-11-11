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
from azure.communication.sms.aio import OptOutsClient
from azure.core.exceptions import HttpResponseError
from _shared.utils import async_create_token_credential, get_http_logging_policy
from acs_sms_test_case import ACSSMSTestCase


@pytest.mark.asyncio
class TestOptOutsClientAsync(ACSSMSTestCase):
    def setup_method(self):
        super().setUp()

    @recorded_by_proxy_async
    async def test_add_opt_out_single_async(self):
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # Add a single phone number to opt-out list
            opt_out_results = await opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number)

            assert len(opt_out_results) == 1
            self.verify_successful_opt_out_response(opt_out_results[0])

    @recorded_by_proxy_async
    async def test_add_opt_out_multiple_async(self):
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # Add multiple phone numbers to opt-out list
            opt_out_results = await opt_outs_client.add_opt_out(
                from_=self.phone_number, 
                to=[self.phone_number, self.phone_number]
            )

            assert len(opt_out_results) == 2
            for result in opt_out_results:
                self.verify_successful_opt_out_response(result)

    @recorded_by_proxy_async
    async def test_check_opt_out_status_async(self):
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # First add to opt-out list
            await opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number)
            
            # Then check opt-out status
            check_results = await opt_outs_client.check_opt_out(from_=self.phone_number, to=self.phone_number)

            assert len(check_results) == 1
            result = check_results[0]
            if self.is_live:
                assert result.to == self.phone_number
            assert result.http_status_code == 200
            assert result.is_opted_out is not None  # Could be True or False depending on state

    @recorded_by_proxy_async
    async def test_remove_opt_out_async(self):
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # First add to opt-out list
            await opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number)
            
            # Then remove from opt-out list
            remove_results = await opt_outs_client.remove_opt_out(from_=self.phone_number, to=self.phone_number)

            assert len(remove_results) == 1
            self.verify_successful_opt_out_response(remove_results[0])

    @recorded_by_proxy_async
    async def test_opt_out_workflow_async(self):
        """Test complete opt-out workflow: add -> check -> remove -> check"""
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # Step 1: Add to opt-out list
            add_results = await opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(add_results) == 1
            self.verify_successful_opt_out_response(add_results[0])

            # Step 2: Check status (should be opted out)
            check_results_1 = await opt_outs_client.check_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(check_results_1) == 1
            
            # Step 3: Remove from opt-out list
            remove_results = await opt_outs_client.remove_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(remove_results) == 1
            self.verify_successful_opt_out_response(remove_results[0])

            # Step 4: Check status again (should not be opted out)
            check_results_2 = await opt_outs_client.check_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(check_results_2) == 1

    @recorded_by_proxy_async
    async def test_opt_out_concurrent_operations_async(self):
        """Test concurrent opt-out operations"""
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            # Perform multiple operations concurrently
            import asyncio
            
            # Create multiple concurrent add operations
            tasks = [
                opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number),
                opt_outs_client.check_opt_out(from_=self.phone_number, to=self.phone_number),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # At least one should succeed (the timing might affect which ones work)
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            assert success_count >= 1

    @recorded_by_proxy_async
    async def test_opt_out_unauthorized_from_phone_number_async(self):
        opt_outs_client = self.create_opt_outs_client_from_connection_string()

        async with opt_outs_client:
            with pytest.raises(HttpResponseError) as ex:
                # Try to add opt-out with unauthorized phone number
                await opt_outs_client.add_opt_out(from_="+14255550123", to=[self.phone_number])

            assert str(ex.value.status_code) == "401"
            assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_add_opt_out_from_managed_identity_async(self):
        """Test opt-out operations using token credential (managed identity) async"""
        if not is_live():
            credential = AsyncFakeCredential()
        else:
            credential = get_credential(is_async=True)
        opt_outs_client = OptOutsClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

        async with opt_outs_client:
            # Add a single phone number to opt-out list using token credential
            opt_out_results = await opt_outs_client.add_opt_out(from_=self.phone_number, to=self.phone_number)

            assert len(opt_out_results) == 1
            self.verify_successful_opt_out_response(opt_out_results[0])

            # Test check opt-out status with token credential
            check_results = await opt_outs_client.check_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(check_results) == 1

            # Test remove opt-out with token credential
            remove_results = await opt_outs_client.remove_opt_out(from_=self.phone_number, to=self.phone_number)
            assert len(remove_results) == 1
            self.verify_successful_opt_out_response(remove_results[0])

    def verify_successful_opt_out_response(self, opt_out_response):
        if self.is_live:
            assert opt_out_response.to == self.phone_number
        assert opt_out_response.http_status_code == 200
        assert opt_out_response.error_message is None

    def create_opt_outs_client_from_connection_string(self):
        return OptOutsClient.from_connection_string(self.connection_str, http_logging_policy=get_http_logging_policy())
