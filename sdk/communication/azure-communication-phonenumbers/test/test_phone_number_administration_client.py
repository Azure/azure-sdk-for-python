import os
import pytest
from devtools_testutils import recorded_by_proxy
from _shared.testcase import BodyReplacerProcessor
from _shared.utils import (
    create_token_credential,
    get_header_policy,
    get_http_logging_policy
)
from azure.communication.phonenumbers import PhoneNumbersClient
from azure.communication.phonenumbers import (
    PhoneNumberAssignmentType,
    PhoneNumberCapabilities,
    PhoneNumberCapabilityType,
    PhoneNumberType,
)
from azure.communication.phonenumbers._generated.models import PhoneNumberOperationStatus
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from phone_number_helper import PhoneNumberUriReplacer, PhoneNumberResponseReplacerProcessor
from phone_numbers_testcase import PhoneNumbersTestCase

SKIP_PURCHASE_PHONE_NUMBER_TESTS = True
PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers shouldn't be purchased in live tests"

SKIP_INT_PHONE_NUMBER_TESTS = os.getenv(
    "COMMUNICATION_SKIP_INT_PHONENUMBERS_TEST", "false") == "true"
INT_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers setting SMS capability does not support in INT. Skip these tests in INT."

SKIP_UPDATE_CAPABILITIES_TESTS = os.getenv(
    "COMMUNICATION_SKIP_CAPABILITIES_LIVE_TEST", "false") == "true"
SKIP_UPDATE_CAPABILITIES_TESTS_REASON = "Phone number capabilities are skipped."


def _get_test_phone_number():
    if SKIP_UPDATE_CAPABILITIES_TESTS:
        return os.environ["AZURE_PHONE_NUMBER"]

    test_agent = os.environ["AZURE_TEST_AGENT"]
    return os.environ["AZURE_PHONE_NUMBER_" + test_agent]


class TestPhoneNumbersClient(PhoneNumbersTestCase):
    def setup_method(self):
        super(TestPhoneNumbersClient, self).setUp(use_dynamic_resource=False)
        if self.is_playback():
            self.phone_number = "sanitized"
            self.country_code = "US"
        else:
            self.phone_number = _get_test_phone_number()
            self.country_code = os.getenv(
                "AZURE_COMMUNICATION_SERVICE_COUNTRY_CODE", "US")

        self.phone_number_client = PhoneNumbersClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy(),
            headers_policy=get_header_policy()
        )

    def _get_managed_identity_phone_number_client(self):
        endpoint, *_ = parse_connection_str(self.connection_str)
        credential = create_token_credential()
        return PhoneNumbersClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy(),
            headers_policy=get_header_policy()
        )

    @recorded_by_proxy
    def test_list_purchased_phone_numbers_from_managed_identity(self, **kwargs):
        phone_number_client = self._get_managed_identity_phone_number_client()
        phone_numbers = phone_number_client.list_purchased_phone_numbers()
        assert phone_numbers.next()

    @recorded_by_proxy
    def test_list_purchased_phone_numbers(self, **kwargs):
        client = self.phone_number_client
        phone_numbers = client.list_purchased_phone_numbers()
        assert phone_numbers.next()

    @recorded_by_proxy
    def test_get_purchased_phone_number_from_managed_identity(self, **kwargs):
        phone_number_client = self._get_managed_identity_phone_number_client()
        phone_number = phone_number_client.get_purchased_phone_number(
            self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @recorded_by_proxy
    def test_get_purchased_phone_number(self, **kwargs):
        phone_number = self.phone_number_client.get_purchased_phone_number(
            self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy
    def test_search_available_phone_numbers_from_managed_identity(self, **kwargs):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND,
            sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        poller = phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            polling=True
        )
        assert poller.result()

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy
    def test_search_available_phone_numbers(self, **kwargs):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND,
            sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        poller = self.phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            polling=True
        )
        assert poller.result()

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @recorded_by_proxy
    def test_update_phone_number_capabilities_from_managed_identity(self, **kwargs):
        phone_number_client = self._get_managed_identity_phone_number_client()
        current_phone_number = phone_number_client.get_purchased_phone_number(
            self.phone_number)
        calling_capabilities = PhoneNumberCapabilityType.INBOUND if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
        sms_capabilities = PhoneNumberCapabilityType.INBOUND_OUTBOUND if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
        poller = phone_number_client.begin_update_phone_number_capabilities(
            self.phone_number,
            sms_capabilities,
            calling_capabilities,
            polling=True
        )
        assert poller.result()
        assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @recorded_by_proxy
    def test_update_phone_number_capabilities(self, **kwargs):
        current_phone_number = self.phone_number_client.get_purchased_phone_number(
            self.phone_number)
        calling_capabilities = PhoneNumberCapabilityType.INBOUND if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
        sms_capabilities = PhoneNumberCapabilityType.INBOUND_OUTBOUND if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND else PhoneNumberCapabilityType.OUTBOUND
        poller = self.phone_number_client.begin_update_phone_number_capabilities(
            self.phone_number,
            sms_capabilities,
            calling_capabilities,
            polling=True
        )
        assert poller.result()
        assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy
    def test_purchase_phone_number_from_managed_identity(self, **kwargs):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND,
            sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        search_poller = phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            polling=True
        )
        phone_number_to_buy = search_poller.result()
        purchase_poller = phone_number_client.begin_purchase_phone_numbers(
            phone_number_to_buy.search_id, polling=True)
        purchase_poller.result()
        assert purchase_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

        release_poller = phone_number_client.begin_release_phone_number(
            phone_number_to_buy.phone_numbers[0])
        release_poller.result()
        assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy
    def test_purchase_phone_numbers(self, **kwargs):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND,
            sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        search_poller = self.phone_number_client.begin_search_available_phone_numbers(
            self.country_code,
            PhoneNumberType.TOLL_FREE,
            PhoneNumberAssignmentType.APPLICATION,
            capabilities,
            polling=True
        )
        phone_number_to_buy = search_poller.result()
        purchase_poller = self.phone_number_client.begin_purchase_phone_numbers(
            phone_number_to_buy.search_id, polling=True)
        purchase_poller.result()
        assert purchase_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

        release_poller = self.phone_number_client.begin_release_phone_number(
            phone_number_to_buy.phone_numbers[0])
        release_poller.result()
        assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @recorded_by_proxy
    def test_get_purchased_phone_number_with_invalid_phone_number(self, **kwargs):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = "+14255550123"

        with pytest.raises(Exception) as ex:
            self.phone_number_client.get_purchased_phone_number(phone_number)

        assert str(ex.value.status_code) == "404"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy
    def test_search_available_phone_numbers_with_invalid_country_code(self, **kwargs):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND,
            sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )

        with pytest.raises(Exception) as ex:
            self.phone_number_client.begin_search_available_phone_numbers(
                "XX",
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling=True
            )

    @recorded_by_proxy
    def test_update_phone_number_capabilities_with_unauthorized_number(self, **kwargs):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = "+14255555111"

        with pytest.raises(Exception) as ex:
            self.phone_number_client.begin_update_phone_number_capabilities(
                phone_number,
                PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                PhoneNumberCapabilityType.INBOUND,
                polling=True
            )
        assert str(ex.value.status_code) == "403"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy
    def test_update_phone_number_capabilities_with_invalid_number(self, **kwargs):
        if self.is_playback():
            phone_number = "invalid_phone_number"
        else:
            phone_number = "invalid_phone_number"

        with pytest.raises(Exception) as ex:
            self.phone_number_client.begin_update_phone_number_capabilities(
                phone_number,
                PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                PhoneNumberCapabilityType.INBOUND,
                polling=True
            )
        assert str(ex.value.status_code) == "403"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy
    def test_update_phone_number_capabilities_with_empty_number(self, **kwargs):
        if self.is_playback():
            phone_number = ""
        else:
            phone_number = ""

        with pytest.raises(ValueError) as ex:
            self.phone_number_client.begin_update_phone_number_capabilities(
                phone_number,
                PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                PhoneNumberCapabilityType.INBOUND,
                polling=True
            )

    @recorded_by_proxy
    def test_list_toll_free_area_codes_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        area_codes = phone_number_client.list_available_area_codes(
            "US", PhoneNumberType.TOLL_FREE, PhoneNumberAssignmentType.APPLICATION)
        assert area_codes.next()

    @recorded_by_proxy
    def test_list_toll_free_area_codes(self):
        area_codes = self.phone_number_client.list_available_area_codes(
            "US", PhoneNumberType.TOLL_FREE, PhoneNumberAssignmentType.APPLICATION)
        assert area_codes.next()

    @recorded_by_proxy
    def test_list_geographic_area_codes_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        first_locality = phone_number_client.list_available_localities("US").next()
        area_codes = self.phone_number_client.list_available_area_codes(
            "US", PhoneNumberType.GEOGRAPHIC, PhoneNumberAssignmentType.PERSON, first_locality.localized_name, administrative_division=first_locality.administrative_division.abbreviated_name)
        assert area_codes.next()

    @recorded_by_proxy
    def test_list_geographic_area_codes(self):
        first_locality = self.phone_number_client.list_available_localities(
            "US").next()
        area_codes = self.phone_number_client.list_available_area_codes(
            "US", PhoneNumberType.GEOGRAPHIC, PhoneNumberAssignmentType.PERSON, first_locality.localized_name, administrative_division=first_locality.administrative_division.abbreviated_name)
        assert area_codes.next()

    @recorded_by_proxy
    def test_list_countries_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        countries = phone_number_client.list_available_countries()
        assert countries.next()

    @recorded_by_proxy
    def test_list_countries(self):
        countries = self.phone_number_client.list_available_countries()
        assert countries.next()

    @recorded_by_proxy
    def test_list_localities_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        localities = phone_number_client.list_available_localities("US")
        assert localities.next()

    @recorded_by_proxy
    def test_list_localities(self):
        localities = self.phone_number_client.list_available_localities("US")
        assert localities.next()

    @recorded_by_proxy
    def test_list_localities_with_ad_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        first_locality = phone_number_client.list_available_localities("US")
        localities = phone_number_client.list_available_localities(
            "US", administrative_division=first_locality.next().administrative_division.abbreviated_name)
        assert localities.next()

    @recorded_by_proxy
    def test_list_localities_with_ad(self):
        first_locality = self.phone_number_client.list_available_localities(
            "US")
        localities = self.phone_number_client.list_available_localities(
            "US", administrative_division=first_locality.next().administrative_division.abbreviated_name)
        assert localities.next()

    @recorded_by_proxy
    def test_list_offerings_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        offerings = phone_number_client.list_available_offerings("US")
        assert offerings.next()

    @recorded_by_proxy
    def test_list_offerings(self):
        offerings = self.phone_number_client.list_available_offerings("US")
        assert offerings.next()
