import os
import pytest
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import ResponseReplacerProcessor, BodyReplacerProcessor
from _shared.utils import create_token_credential
from azure.communication.phonenumbers import PhoneNumberAssignmentType, PhoneNumberCapabilities, PhoneNumberCapabilityValue, PhoneNumberType
from azure.communication.phonenumbers._shared.utils import parse_connection_str

class NewTests(AsyncCommunicationTestCase):
    def setUp(self):
        super(NewTests, self).setUp()
        if self.is_playback():
            self.phone_number = "+18000005555"
            self.phone_number_to_release = "+18000005556"
            self.country_code = "US"
            self.area_code = "833"
        else:
            self.phone_number = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER")
            self.phone_number_to_release = os.getenv("AZURE_COMMUNICATION_SERVICE_PHONE_NUMBER_TO_RELEASE")
            self.country_code = os.getenv("AZURE_COMMUNICATION_SERVICE_COUNTRY_CODE")
            self.area_code = os.getenv("AZURE_COMMUNICATION_SERIVCE_AREA_CODE")

        self.phone_number_client = PhoneNumbersClient.from_connection_string(self.connection_str)
        self.recording_processors.extend([
            BodyReplacerProcessor(
                keys=["id", "token", "phoneNumber", "phonenumbers"]
            ),
            ResponseReplacerProcessor(keys=[self._resource_name])])

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    def test_list_all_phone_numbers_from_managed_identity(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        phone_number_client = PhoneNumbersClient(endpoint, credential)
        async with self.phone_number_client:
            phone_numbers = phone_number_client.list_acquired_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_list_acquired_phone_numbers(self):
        async with self.phone_number_client:
            phone_numbers = self.phone_number_client.list_acquired_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_get_phone_number(self):
        async with self.phone_number_client:
            phone_number = await self.phone_number_client.get_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number
        
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_release_phone_number(self):
        async with self.phone_number_client:
            poller = await self.phone_number_client.begin_release_phone_number(self.phone_number_to_release)
            result = await poller.result()
        assert result

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_search_available_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                area_code=self.area_code,
                polling = True
            )
        assert poller.result()
    
    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_update_phone_number_capabilities(self):
        async with self.phone_number_client:
            poller = self.phone_number_client.begin_update_phone_number_capabilities(
            self.phone_number,
            PhoneNumberCapabilityValue.OUTBOUND,
            PhoneNumberCapabilityValue.OUTBOUND,
            polling = True
            )
        assert poller.result()

    @AsyncCommunicationTestCase.await_prepared_test
    @pytest.mark.live_test_only
    async def test_purchase_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            search_poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                self.area_code,
                1,
                polling = True
            )
            phone_number_to_buy = search_poller.result()
            purchase_poller = await self.phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
            assert purchase_poller.result()
            release_poller = await self.phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_number)
        assert release_poller.status() == 'succeeded'
