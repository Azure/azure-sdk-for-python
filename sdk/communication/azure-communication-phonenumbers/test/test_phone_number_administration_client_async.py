import os
import pytest
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import ResponseReplacerProcessor, BodyReplacerProcessor
from _shared.utils import create_token_credential
from azure.communication.phonenumbers import (
    PhoneNumberAssignmentType, 
    PhoneNumberCapabilities, 
    PhoneNumberCapabilityType, 
    PhoneNumberType, 
    PhoneNumberOperationStatus
)
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from phone_number_helper import PhoneNumberUriReplacer

SKIP_PURCHASE_PHONE_NUMBER_TESTS = True
PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers shouldn't be purchased in live tests"

SKIP_SEARCH_AVAILABLE_PHONE_NUMBER_TESTS = True
SEARCH_AVAILABLE_PHONE_NUMBER_TEST_SKIP_REASON = "Temporarily skipping test"


class PhoneNumbersClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(PhoneNumbersClientTestAsync, self).setUp()
        if self.is_playback():
            self.phone_number = "sanitized"
            self.country_code = "US"
        else:
            self.phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")
            self.country_code = os.getenv("AZURE_COMMUNICATION_SERVICE_COUNTRY_CODE", "US")
        self.phone_number_client = PhoneNumbersClient.from_connection_string(self.connection_str)
        self.recording_processors.extend([
            BodyReplacerProcessor(
                keys=["id", "token", "phoneNumber", "searchId"]
            ),
            PhoneNumberUriReplacer(),
            ResponseReplacerProcessor()])
            
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_purchased_phone_numbers_from_managed_identity(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        phone_number_client = PhoneNumbersClient(endpoint, credential)
        async with self.phone_number_client:
            phone_numbers = phone_number_client.list_purchased_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_purchased_phone_numbers(self):
        async with self.phone_number_client:
            phone_numbers = self.phone_number_client.list_purchased_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_purchased_phone_number(self):
        async with self.phone_number_client:
            phone_number = await self.phone_number_client.get_purchased_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @pytest.mark.skipif(SKIP_SEARCH_AVAILABLE_PHONE_NUMBER_TESTS, reason=SEARCH_AVAILABLE_PHONE_NUMBER_TEST_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_search_available_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling = True
            )
        assert poller.result()
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_phone_number_capabilities(self):
        async with self.phone_number_client:
            poller = await self.phone_number_client.begin_update_phone_number_capabilities(
                self.phone_number,
                PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                PhoneNumberCapabilityType.INBOUND,
                polling = True
            )
        assert poller.result()
        
    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_purchase_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            search_poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling = True
            )
            phone_number_to_buy = await search_poller.result()
            purchase_poller = await self.phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
            await purchase_poller.result()
            release_poller = await self.phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_numbers[0])
        assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value
