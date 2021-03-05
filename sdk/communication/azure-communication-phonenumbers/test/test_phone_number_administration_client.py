import os
import pytest
from azure.communication.phonenumbers import PhoneNumbersClient
from _shared.testcase import CommunicationTestCase, ResponseReplacerProcessor, BodyReplacerProcessor
from _shared.utils import create_token_credential
from azure.communication.phonenumbers import PhoneNumberAssignmentType, PhoneNumberCapabilities, PhoneNumberCapabilityValue, PhoneNumberType
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from phone_number_helper import PhoneNumberUriReplacer

SKIP_PURCHASE_PHONE_NUMBER_TESTS = True
PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers shouldn't be purchased in live tests"

class NewTests(CommunicationTestCase):
    def setUp(self):
        super(NewTests, self).setUp()
        if self.is_playback():
            self.phone_number = "sanitized"
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
                keys=["id", "token", "phoneNumber"]
            ),
            PhoneNumberUriReplacer()])

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    def test_list_all_phone_numbers_from_managed_identity(self):
        endpoint, access_key = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        phone_number_client = PhoneNumbersClient(endpoint, credential)
        phone_numbers = phone_number_client.list_all_phone_numbers()
        assert phone_numbers.next()
    
    def test_list_acquired_phone_numbers(self):
        phone_numbers = self.phone_number_client.list_acquired_phone_numbers()
        assert phone_numbers.next()
    
    def test_get_phone_number(self):
        phone_number = self.phone_number_client.get_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    def test_search_available_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        poller = self.phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            area_code=self.area_code,
            polling = True
        )
        assert poller.result()

    def test_update_phone_number_capabilities(self):
        poller = self.phone_number_client.begin_update_phone_number_capabilities(
            self.phone_number,
            PhoneNumberCapabilityValue.INBOUND_OUTBOUND,
            PhoneNumberCapabilityValue.INBOUND,
            polling = True
        )
        assert poller.result()

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    def test_purchase_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        search_poller = self.phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            area_code=self.area_code,
            polling = True
        )
        phone_number_to_buy = search_poller.result()
        purchase_poller = self.phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
        assert purchase_poller.result()
        release_poller = self.phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_numbers[0])
        assert release_poller.status() == 'succeeded'
