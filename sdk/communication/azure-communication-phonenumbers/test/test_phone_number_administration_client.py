import pytest
from azure.communication.phonenumbers import PhoneNumbersClient
from _shared.testcase import CommunicationTestCase, ResponseReplacerProcessor, BodyReplacerProcessor
from azure.communication.phonenumbers import PhoneNumberAssignmentType, PhoneNumberCapabilities, PhoneNumberCapabilityValue, PhoneNumberType

class NewTests(CommunicationTestCase):
    def setUp(self):
        super(NewTests, self).setUp()
        self.phone_number_client = PhoneNumbersClient.from_connection_string(self.connection_str)
        self.recording_processors.extend([
            BodyReplacerProcessor(
                keys=[]
            ),
            ResponseReplacerProcessor(keys=[self._resource_name])])

    @pytest.mark.live_test_only
    def test_list_acquired_phone_numbers(self):
        phone_numbers = self.phone_number_client.list_acquired_phone_numbers()
        assert phone_numbers.next()
    
    @pytest.mark.live_test_only
    def test_get_phone_number(self):
        phone_number = self.phone_number_client.get_phone_number("+18332272412")
        assert phone_number.phone_number == "+18332272412"
    
    @pytest.mark.live_test_only
    def test_release_phone_number(self):
        poller = self.phone_number_client.begin_release_phone_number("+16194895886")
        assert poller.status() == 'succeeded'

    @pytest.mark.live_test_only
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
            "844",
            polling = True
        )
        assert poller.result()

    @pytest.mark.live_test_only
    def test_update_phone_number_capabilities(self):
        poller = self.phone_number_client.begin_update_phone_number_capabilities(
          "+18335260208",
          PhoneNumberCapabilityValue.OUTBOUND,
          PhoneNumberCapabilityValue.INBOUND_OUTBOUND,
          polling = True
        )
        assert poller.result()
    
    @pytest.mark.live_test_only
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
            "844",
            1,
            polling = True
        )
        phone_number_to_buy = search_poller.result()
        purchase_poller = self.phone_number_client.begin_purchase_phone_numbers(phone_number_to_buy.search_id, polling=True)
        assert purchase_poller.result()
        ##release_poller = self.phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_number)
        ##assert release_poller.status() == 'succeeded'
