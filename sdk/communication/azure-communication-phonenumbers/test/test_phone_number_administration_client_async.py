import os
import pytest
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor
from _shared.utils import (
    async_create_token_credential, 
    get_header_policy,
    get_http_logging_policy
)
from azure.communication.phonenumbers import (
    PhoneNumberAssignmentType, 
    PhoneNumberCapabilities, 
    PhoneNumberCapabilityType, 
    PhoneNumberType, 
)
from azure.communication.phonenumbers._generated.models import PhoneNumberOperationStatus
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from phone_number_helper import PhoneNumberUriReplacer, PhoneNumberResponseReplacerProcessor

SKIP_PURCHASE_PHONE_NUMBER_TESTS = True
PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers shouldn't be purchased in live tests"

SKIP_INT_PHONE_NUMBER_TESTS = os.getenv("COMMUNICATION_SKIP_INT_PHONENUMBERS_TEST", "false") == "true"
INT_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers setting SMS capability does not support in INT. Skip these tests in INT."

SKIP_UPDATE_CAPABILITIES_TESTS = os.getenv("COMMUNICATION_SKIP_CAPABILITIES_LIVE_TEST", "false") == "true"
SKIP_UPDATE_CAPABILITIES_TESTS_REASON = "Phone number capabilities are skipped."

API_VERSION = "2022-01-11-preview2"

def get_test_phone_number():
    if SKIP_UPDATE_CAPABILITIES_TESTS:
        return os.getenv("AZURE_PHONE_NUMBER")

    test_agent = os.getenv("AZURE_TEST_AGENT")
    return os.getenv("AZURE_PHONE_NUMBER_" + test_agent)

class PhoneNumbersClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(PhoneNumbersClientTestAsync, self).setUp()
        if self.is_playback():
            self.phone_number = "sanitized"
            self.country_code = "US"
        else:
            self.phone_number = get_test_phone_number()
            self.country_code = os.getenv("AZURE_COMMUNICATION_SERVICE_COUNTRY_CODE", "US")
        self.phone_number_client = PhoneNumbersClient.from_connection_string(
            self.connection_str, 
            http_logging_policy=get_http_logging_policy(),
            headers_policy=get_header_policy(),
            api_version=API_VERSION
        )
        self.recording_processors.extend([
            BodyReplacerProcessor(
                keys=["id", "token", "phoneNumber", "searchId"]
            ),
            PhoneNumberUriReplacer(),
            PhoneNumberResponseReplacerProcessor()])

    def _get_managed_identity_phone_number_client(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return PhoneNumbersClient(
            endpoint, 
            credential, 
            http_logging_policy=get_http_logging_policy(),
            headers_policy=get_header_policy()
        )

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_purchased_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
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
    async def test_get_purchased_phone_number_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            phone_number = await phone_number_client.get_purchased_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_purchased_phone_number(self):
        async with self.phone_number_client:
            phone_number = await self.phone_number_client.get_purchased_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_search_available_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with phone_number_client:
            poller = await phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling = True
            )
        assert poller.result()

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
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

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_phone_number_capabilities(self):
        async with self.phone_number_client:
            current_phone_number = await self.phone_number_client.get_purchased_phone_number(self.phone_number)
            calling_capabilities = PhoneNumberCapabilityType.INBOUND if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
            sms_capabilities = PhoneNumberCapabilityType.INBOUND_OUTBOUND if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
            poller = await self.phone_number_client.begin_update_phone_number_capabilities(
                self.phone_number,
                sms_capabilities,
                calling_capabilities,
                polling = True
            )
            assert await poller.result()
            assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_phone_number_capabilities_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            current_phone_number = await phone_number_client.get_purchased_phone_number(self.phone_number)
            calling_capabilities = PhoneNumberCapabilityType.INBOUND if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
            sms_capabilities = PhoneNumberCapabilityType.INBOUND_OUTBOUND if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
            poller = await phone_number_client.begin_update_phone_number_capabilities(
                self.phone_number,
                sms_capabilities,
                calling_capabilities,
                polling = True
            )
            assert await poller.result()
            assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_purchase_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with phone_number_client:
            search_poller = await phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling = True
            )
            phone_number_to_buy = await search_poller.result()
            purchase_poller = await phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
            await purchase_poller.result()
            release_poller = await phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_numbers[0])
        assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

        
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
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_purchased_phone_number_with_invalid_phone_number(self):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = "+14255550123"

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.get_purchased_phone_number(phone_number)
        
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_search_available_phone_numbers_with_invalid_country_code(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityType.INBOUND,
            sms = PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.begin_search_available_phone_numbers(
                    "XX",
                    PhoneNumberType.TOLL_FREE,
                    PhoneNumberAssignmentType.APPLICATION,
                    capabilities,
                    polling = True
                )
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_phone_number_capabilities_with_invalid_phone_number(self):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = "+14255555111"

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.begin_update_phone_number_capabilities(
                    phone_number,
                    PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                    PhoneNumberCapabilityType.INBOUND,
                    polling = True
                )
        
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None
