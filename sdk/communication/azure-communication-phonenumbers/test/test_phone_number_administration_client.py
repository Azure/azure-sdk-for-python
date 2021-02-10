import pytest
from azure.communication.phonenumbers import PhoneNumbersClient
from _shared.testcase import CommunicationTestCase, ResponseReplacerProcessor, BodyReplacerProcessor
from azure.communication.phonenumbers import PhoneNumberAssignmentType, PhoneNumberCapabilities, PhoneNumberCapabilityValue, PhoneNumberType

class NewTests(CommunicationTestCase):
    def setUp(self):
        super(NewTests, self).setUp()
        self.phone_number_client = PhoneNumbersClient.from_connection_string(self.connection_str)
        self.recording_processors.extend([
            BodyReplacerProcessor(),
            ResponseReplacerProcessor(keys=[self._resource_name])])

    def test_list_acquired_phone_numbers(self):
        phone_numbers = self.phone_number_client.list_acquired_phone_numbers()
        assert phone_numbers.next()

    def test_get_phone_number(self):
        phone_number = self.phone_number_client.get_phone_number("+16194895875")
        assert phone_number.phone_number == "+16194895875"
    
    def test_update_phone_number(self):
        updated_phone_number = self.phone_number_client.update_phone_number(
            "+16194895842",
            "",
            ""
        )
        assert updated_phone_number.application_id == ""

    def test_release_phone_number(self):
        poller = self.phone_number_client.begin_release_phone_number("+16194895886")
        assert poller.status() == 'succeeded'
    

    def test_search_available_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        poller = self.phone_number_client.begin_search_available_phone_numbers(
            "US",
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            "833",
            1,
            polling = True
        )
        assert poller.result()
    
    def test_update_phone_number_capabilities(self):
        poller = self.phone_number_client.begin_update_phone_number_capabilities(
          "+16194895842",
          PhoneNumberCapabilityValue.OUTBOUND,
          PhoneNumberCapabilityValue.OUTBOUND,
          polling = True
        )
        assert poller.result()

    def test_purchase_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling = PhoneNumberCapabilityValue.INBOUND,
            sms = PhoneNumberCapabilityValue.INBOUND_OUTBOUND
        )
        search_poller = self.phone_number_client.begin_search_available_phone_numbers(
            "US",
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            "833",
            1,
            polling = True
        )
        phone_number_to_buy = search_poller.result()
        purchase_poller = self.phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
        assert purchase_poller.result()
        release_poller = self.phone_number_client.begin_release_phone_number("+")
        assert release_poller.status() == 'succeeded'
