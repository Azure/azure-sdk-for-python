import os
from devtools_testutils.aio import recorded_by_proxy_async
import pytest
from _shared.utils import async_create_token_credential, get_header_policy, get_http_logging_policy
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.communication.phonenumbers import (
    PhoneNumberAssignmentType,
    PhoneNumberCapabilities,
    PhoneNumberCapabilityType,
    PhoneNumberType,
)
from azure.communication.phonenumbers._generated.models import PhoneNumberOperationStatus
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from phone_numbers_testcase import PhoneNumbersTestCase

SKIP_PURCHASE_PHONE_NUMBER_TESTS = True
PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON = "Phone numbers shouldn't be purchased in live tests"

SKIP_INT_PHONE_NUMBER_TESTS = os.getenv("COMMUNICATION_SKIP_INT_PHONENUMBERS_TEST", "false") == "true"
INT_PHONE_NUMBER_TEST_SKIP_REASON = (
    "Phone numbers setting SMS capability does not support in INT. Skip these tests in INT."
)

SKIP_UPDATE_CAPABILITIES_TESTS = os.getenv("COMMUNICATION_SKIP_CAPABILITIES_LIVE_TEST", "false") == "true"
SKIP_UPDATE_CAPABILITIES_TESTS_REASON = "Phone number capabilities are skipped."


def _get_test_phone_number():
    if SKIP_UPDATE_CAPABILITIES_TESTS:
        return os.environ["AZURE_PHONE_NUMBER"]

    test_agent = os.environ["AZURE_TEST_AGENT"]
    return os.environ["AZURE_PHONE_NUMBER_" + test_agent]


def is_client_error_status_code(
    status_code,  # type: int
):
    return status_code >= 400 and status_code < 500


@pytest.mark.asyncio
class TestPhoneNumbersClientAsync(PhoneNumbersTestCase):
    def setup_method(self):
        super(TestPhoneNumbersClientAsync, self).setUp(use_dynamic_resource=False)
        if self.is_playback():
            self.phone_number = "sanitized"
            self.country_code = "US"
        else:
            self.phone_number = _get_test_phone_number()
            self.country_code = os.getenv("AZURE_COMMUNICATION_SERVICE_COUNTRY_CODE", "US")

        self.phone_number_client = PhoneNumbersClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )

    def _get_managed_identity_phone_number_client(self):
        endpoint, *_ = parse_connection_str(self.connection_str)
        credential = async_create_token_credential()
        return PhoneNumbersClient(
            endpoint, credential, http_logging_policy=get_http_logging_policy(), headers_policy=get_header_policy()
        )

    @recorded_by_proxy_async
    async def test_list_purchased_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            phone_numbers = phone_number_client.list_purchased_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_purchased_phone_numbers(self):
        async with self.phone_number_client:
            phone_numbers = self.phone_number_client.list_purchased_phone_numbers()
            items = []
            async for item in phone_numbers:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_get_purchased_phone_number_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            phone_number = await phone_number_client.get_purchased_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @recorded_by_proxy_async
    async def test_get_purchased_phone_number(self):
        async with self.phone_number_client:
            phone_number = await self.phone_number_client.get_purchased_phone_number(self.phone_number)
        assert phone_number.phone_number == self.phone_number

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy_async
    async def test_search_available_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND, sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with phone_number_client:
            poller = await phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling=True,
            )
        assert poller.result()

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy_async
    async def test_search_available_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND, sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling=True,
            )
        assert poller.result()

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @recorded_by_proxy_async
    async def test_update_phone_number_capabilities(self):
        async with self.phone_number_client:
            current_phone_number = await self.phone_number_client.get_purchased_phone_number(self.phone_number)
            calling_capabilities = (
                PhoneNumberCapabilityType.INBOUND
                if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND
                else PhoneNumberCapabilityType.OUTBOUND
            )
            sms_capabilities = (
                PhoneNumberCapabilityType.INBOUND_OUTBOUND
                if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND
                else PhoneNumberCapabilityType.OUTBOUND
            )
            poller = await self.phone_number_client.begin_update_phone_number_capabilities(
                self.phone_number, sms_capabilities, calling_capabilities, polling=True
            )
            assert await poller.result()
            assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_INT_PHONE_NUMBER_TESTS, reason=INT_PHONE_NUMBER_TEST_SKIP_REASON)
    @pytest.mark.skipif(SKIP_UPDATE_CAPABILITIES_TESTS, reason=SKIP_UPDATE_CAPABILITIES_TESTS_REASON)
    @recorded_by_proxy_async
    async def test_update_phone_number_capabilities_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            current_phone_number = await phone_number_client.get_purchased_phone_number(self.phone_number)
            calling_capabilities = (
                PhoneNumberCapabilityType.INBOUND
                if current_phone_number.capabilities.calling == PhoneNumberCapabilityType.OUTBOUND
                else PhoneNumberCapabilityType.OUTBOUND
            )
            sms_capabilities = (
                PhoneNumberCapabilityType.INBOUND_OUTBOUND
                if current_phone_number.capabilities.sms == PhoneNumberCapabilityType.OUTBOUND
                else PhoneNumberCapabilityType.OUTBOUND
            )
            poller = await phone_number_client.begin_update_phone_number_capabilities(
                self.phone_number, sms_capabilities, calling_capabilities, polling=True
            )
            assert await poller.result()
            assert poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy_async
    async def test_purchase_phone_numbers_from_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND, sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with phone_number_client:
            search_poller = await phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling=True,
            )
            phone_number_to_buy = await search_poller.result()
            purchase_poller = await phone_number_client.begin_purchase_phone_numbers(
                phone_number_to_buy.search_id, polling=True
            )

            await purchase_poller.result()
            assert purchase_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

            release_poller = await phone_number_client.begin_release_phone_number(phone_number_to_buy.phone_numbers[0])
            await release_poller.result()
            assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @pytest.mark.skipif(SKIP_PURCHASE_PHONE_NUMBER_TESTS, reason=PURCHASE_PHONE_NUMBER_TEST_SKIP_REASON)
    @recorded_by_proxy_async
    async def test_purchase_phone_numbers(self):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND, sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )
        async with self.phone_number_client:
            search_poller = await self.phone_number_client.begin_search_available_phone_numbers(
                self.country_code,
                PhoneNumberType.TOLL_FREE,
                PhoneNumberAssignmentType.APPLICATION,
                capabilities,
                polling=True,
            )
            phone_number_to_buy = await search_poller.result()
            purchase_poller = await self.phone_number_client.begin_purchase_phone_numbers(
                phone_number_to_buy.search_id, polling=True
            )

            await purchase_poller.result()
            assert purchase_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

            release_poller = await self.phone_number_client.begin_release_phone_number(
                phone_number_to_buy.phone_numbers[0]
            )
            await release_poller.result()
            assert release_poller.status() == PhoneNumberOperationStatus.SUCCEEDED.value

    @recorded_by_proxy_async
    async def test_get_purchased_phone_number_with_invalid_phone_number(self):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = "+14255550123"

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.get_purchased_phone_number(phone_number)

        assert (
            is_client_error_status_code(ex.value.status_code) is True
        ), "Status code {ex.value.status_code} does not indicate a client error"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy_async
    async def test_search_available_phone_numbers_with_invalid_country_code(self):
        capabilities = PhoneNumberCapabilities(
            calling=PhoneNumberCapabilityType.INBOUND, sms=PhoneNumberCapabilityType.INBOUND_OUTBOUND
        )

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.begin_search_available_phone_numbers(
                    "XX", PhoneNumberType.TOLL_FREE, PhoneNumberAssignmentType.APPLICATION, capabilities, polling=True
                )

    @recorded_by_proxy_async
    async def test_update_phone_number_capabilities_with_unauthorized_number(self):
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
                    polling=True,
                )

        assert (
            is_client_error_status_code(ex.value.status_code) is True
        ), "Status code {ex.value.status_code} does not indicate a client error"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy_async
    async def test_update_phone_number_capabilities_with_invalid_number(self):
        if self.is_playback():
            phone_number = "invalid_phone_number"
        else:
            phone_number = "invalid_phone_number"

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.begin_update_phone_number_capabilities(
                    phone_number,
                    PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                    PhoneNumberCapabilityType.INBOUND,
                    polling=True,
                )

        assert (
            is_client_error_status_code(ex.value.status_code) is True
        ), "Status code {ex.value.status_code} does not indicate a client error"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy_async
    async def test_update_phone_number_capabilities_with_empty_number(self):
        if self.is_playback():
            phone_number = ""
        else:
            phone_number = ""

        with pytest.raises(ValueError) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.begin_update_phone_number_capabilities(
                    phone_number,
                    PhoneNumberCapabilityType.INBOUND_OUTBOUND,
                    PhoneNumberCapabilityType.INBOUND,
                    polling=True,
                )

    @recorded_by_proxy_async
    async def test_list_toll_free_area_codes_with_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            area_codes = phone_number_client.list_available_area_codes(
                "US", PhoneNumberType.TOLL_FREE, assignment_type=PhoneNumberAssignmentType.APPLICATION
            )
            items = []
            async for item in area_codes:
                items.append(item.area_code)

        expected_area_codes = {"888", "877", "866", "855", "844", "800", "833", "88"}
        for area_code in items:
            assert area_code in expected_area_codes

        assert area_codes is not None

    @recorded_by_proxy_async
    async def test_list_toll_free_area_codes(self):
        async with self.phone_number_client:
            area_codes = self.phone_number_client.list_available_area_codes(
                "US", PhoneNumberType.TOLL_FREE, assignment_type=PhoneNumberAssignmentType.APPLICATION
            )
            items = []
            async for item in area_codes:
                items.append(item.area_code)

        expected_area_codes = {"888", "877", "866", "855", "844", "800", "833", "88"}
        for area_code in items:
            assert area_code in expected_area_codes

        assert area_codes is not None

    @recorded_by_proxy_async
    async def test_list_geographic_area_codes_with_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            localities = phone_number_client.list_available_localities("US")
            async for first_locality in localities:
                area_codes = self.phone_number_client.list_available_area_codes(
                    "US",
                    PhoneNumberType.GEOGRAPHIC,
                    assignment_type=PhoneNumberAssignmentType.PERSON,
                    locality=first_locality.localized_name,
                    administrative_division=first_locality.administrative_division.abbreviated_name,
                )
                items = []
                async for item in area_codes:
                    items.append(item)
                break
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_geographic_area_codes(self):
        async with self.phone_number_client:
            localities = self.phone_number_client.list_available_localities("US")
            async for first_locality in localities:
                area_codes = self.phone_number_client.list_available_area_codes(
                    "US",
                    PhoneNumberType.GEOGRAPHIC,
                    assignment_type=PhoneNumberAssignmentType.PERSON,
                    locality=first_locality.localized_name,
                    administrative_division=first_locality.administrative_division.abbreviated_name,
                )
                items = []
                async for item in area_codes:
                    items.append(item)
                break
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_countries_with_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            countries = phone_number_client.list_available_countries()
            items = []
            async for item in countries:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_countries(self):
        async with self.phone_number_client:
            countries = self.phone_number_client.list_available_countries()
            items = []
            async for item in countries:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_localities_with_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            localities = phone_number_client.list_available_localities("US")
            items = []
            async for item in localities:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_localities(self):
        async with self.phone_number_client:
            localities = self.phone_number_client.list_available_localities("US")
            items = []
            async for item in localities:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_localities_with_ad_and_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            localities = phone_number_client.list_available_localities("US")
            async for first_locality in localities:
                localities = phone_number_client.list_available_localities(
                    "US", administrative_division=first_locality.administrative_division.abbreviated_name
                )
                items = []
                async for item in localities:
                    items.append(item)
                break
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_localities_with_ad(self):
        async with self.phone_number_client:
            localities = self.phone_number_client.list_available_localities("US")
            async for first_locality in localities:
                localities = self.phone_number_client.list_available_localities(
                    "US", administrative_division=first_locality.administrative_division.abbreviated_name
                )
                items = []
                async for item in localities:
                    items.append(item)
                break
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_offerings_with_managed_identity(self):
        phone_number_client = self._get_managed_identity_phone_number_client()
        async with phone_number_client:
            offerings = phone_number_client.list_available_offerings("US")
            items = []
            async for item in offerings:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_list_offerings(self):
        async with self.phone_number_client:
            offerings = self.phone_number_client.list_available_offerings("US")
            items = []
            async for item in offerings:
                items.append(item)
        assert len(items) > 0

    @recorded_by_proxy_async
    async def test_search_operator_information_with_too_many_phone_numbers(self):
        if self.is_playback():
            phone_numbers = ["sanitized", "sanitized"]
        else:
            phone_numbers = [self.phone_number, self.phone_number]

        with pytest.raises(Exception) as ex:
            async with self.phone_number_client:
                await self.phone_number_client.search_operator_information(phone_numbers)

        assert (
            is_client_error_status_code(ex.value.status_code) is True
        ), "Status code {ex.value.status_code} does not indicate a client error"  # type: ignore
        assert ex.value.message is not None  # type: ignore

    @recorded_by_proxy_async
    async def test_search_operator_information_with_list(self):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = self.phone_number

        async with self.phone_number_client:
            results = await self.phone_number_client.search_operator_information([phone_number])
        assert len(results.values) == 1
        assert results.values[0].phone_number == self.phone_number

    @recorded_by_proxy_async
    async def test_search_operator_information_with_single_string(self):
        if self.is_playback():
            phone_number = "sanitized"
        else:
            phone_number = self.phone_number

        async with self.phone_number_client:
            results = await self.phone_number_client.search_operator_information(phone_number)
        assert len(results.values) == 1
        assert results.values[0].phone_number == self.phone_number
