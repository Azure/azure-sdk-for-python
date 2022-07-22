# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from .._generated.aio._client import PhoneNumbersClient as PhoneNumbersClientGen
from .._generated.models import (
    PhoneNumberSearchRequest,
    PhoneNumberCapabilitiesRequest,
    PhoneNumberPurchaseRequest,
    PhoneNumberType,
    PhoneNumberAssignmentType
)
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.async_paging import AsyncItemPaged
    from azure.core.polling import AsyncLROPoller
    from .._generated.models import (
        AreaCodeResult,
        PhoneNumberLocality,
        PhoneNumberCountry,
        PhoneNumberOffering,
        PhoneNumberSearchResult,
        PurchasedPhoneNumber,
    )

class PhoneNumbersClient(object): # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Phone Numbers gateway.

    This client provides operations to interact with the phone numbers service
    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The credentials with which to authenticate.
    """
    def __init__(
                self,
                endpoint, # type: str
                credential, # type: AsyncTokenCredential
                **kwargs # type: Any
        ):
        # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._accepted_language = kwargs.pop("accepted_language", None)
        self._phone_number_client = PhoneNumbersClientGen(
            self._endpoint,
            authentication_policy=get_authentication_policy(endpoint, credential, is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str, # type: str
            **kwargs # type: Any
    ):
        # type: (...) -> PhoneNumbersClient
        """Create PhoneNumbersClient from a Connection String.
        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of PhoneNumbersClient.
        :rtype: ~azure.communication.phonenumbers.aio.PhoneNumbersClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace_async
    async def begin_purchase_phone_numbers(
            self,
            search_id, # type: str
            **kwargs # type: Any
    ):
        # type: (...) -> AsyncLROPoller[None]
        """Purchases phone numbers.

        :param search_id: The search id.
        :type search_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls
            for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        """
        purchase_request = PhoneNumberPurchaseRequest(search_id=search_id)

        return await self._phone_number_client.phone_numbers.begin_purchase_phone_numbers(
            body=purchase_request,
            **kwargs
        )

    @distributed_trace_async
    async def begin_release_phone_number(
            self,
            phone_number, # type: str
            **kwargs # type: Any
    ):
        # type: (...) -> AsyncLROPoller[None]
        """Releases an purchased phone number.

        :param phone_number: Phone number to be released, e.g. +11234567890.
        :type phone_number: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls
            for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        """
        return await self._phone_number_client.phone_numbers.begin_release_phone_number(
            phone_number,
            **kwargs
        )

    @distributed_trace_async
    async def begin_search_available_phone_numbers(
            self,
            country_code, # type: str
            phone_number_type, # type: str
            assignment_type, # type: str
            capabilities,
            **kwargs
    ):
        # type: (...) -> AsyncLROPoller[PhoneNumberSearchResult]
        """Search for available phone numbers to purchase.

        :param country_code: The ISO 3166-2 country code, e.g. US.
        :type country_code: str
        :param phone_number_type: Required. The type of phone numbers to search for, e.g. geographic,
            or tollFree. Possible values include: "geographic", "tollFree".
        :type phone_number_type: str or ~azure.communication.phonenumbers.models.PhoneNumberType
        :param assignment_type: Required. The assignment type of the phone numbers to search for. A
            phone number can be assigned to a person, or to an application. Possible values include:
            "user", "application".
        :type assignment_type: str or
            ~azure.communication.phonenumbers.models.PhoneNumberAssignmentType
        :param capabilities: Required. Capabilities of a phone number.
        :type capabilities: ~azure.communication.phonenumbers.models.PhoneNumberCapabilities
        :keyword str area_code: The area code of the desired phone number, e.g. 425. If not set,
            any area code could be used in the final search.
        :keyword int quantity: The quantity of phone numbers in the search. Default is 1.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
         False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls
            for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.communication.phonenumbers.models.PhoneNumberSearchResult]
        """
        search_request = PhoneNumberSearchRequest(
            phone_number_type=phone_number_type,
            assignment_type=assignment_type,
            capabilities=capabilities,
            quantity=kwargs.pop('quantity', None),
            area_code=kwargs.pop('area_code', None)
        )
        return await self._phone_number_client.phone_numbers.begin_search_available_phone_numbers(
            country_code,
            search_request,
            **kwargs
        )

    @distributed_trace_async
    async def begin_update_phone_number_capabilities(
            self,
            phone_number, # type: str
            sms=None, # type: str
            calling=None, # type: str
            **kwargs # type: Any
    ):
        # type: (...) -> AsyncLROPoller[PurchasedPhoneNumber]
        """Updates the capabilities of a phone number.

        :param phone_number: The phone number id in E.164 format. The leading plus can be either + or
            encoded as %2B, e.g. +11234567890.
        :type phone_number: str
        :param calling: Capability value for calling.
        :type calling: str or ~azure.communication.phonenumbers.models.PhoneNumberCapabilityType
        :param sms: Capability value for SMS.
        :type sms: str or ~azure.communication.phonenumbers.models.PhoneNumberCapabilityType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls
            for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.communication.phonenumbers.models.PurchasedPhoneNumber]
        """
        capabilities_request = PhoneNumberCapabilitiesRequest(
            calling=calling,
            sms=sms
        )

        return await self._phone_number_client.phone_numbers.begin_update_capabilities(
            phone_number,
            body=capabilities_request,
            **kwargs
        )

    @distributed_trace_async
    async def get_purchased_phone_number(
            self,
            phone_number, # type: str
            **kwargs # type: Any
    ):
        # type: (...) -> PurchasedPhoneNumber
        """Gets the details of the given purchased phone number.

        :param phone_number: The purchased phone number whose details are to be fetched in E.164 format,
         e.g. +11234567890.
        :type phone_number: str
        :rtype: ~azure.communication.phonenumbers.models.PurchasedPhoneNumber
        """
        return await self._phone_number_client.phone_numbers.get_by_number(
            phone_number,
            **kwargs
        )

    @distributed_trace
    def list_purchased_phone_numbers(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> AsyncItemPaged[PurchasedPhoneNumber]
        """Gets the list of all purchased phone numbers.

        Gets the list of all purchased phone numbers.

        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :keyword top: An optional parameter for how many entries to return, for pagination purposes.
         The default value is 100. Default value is 100.
        :paramtype top: int
        :keyword accept_language: The locale to display in the localized fields in the response.
         Default value is None.
        :paramtype accept_language: str
        :return: An iterator like instance of PurchasedPhoneNumber
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.PurchasedPhoneNumber]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_phone_numbers(
            **kwargs
        )

    @distributed_trace
    def list_available_countries(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> AsyncItemPaged[PhoneNumberCountry]
        """Gets the list of supported countries.

        Gets the list of supported countries.

        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberCountry
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.PhoneNumberCountry]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_available_countries(
            accept_language=self._accepted_language,
            **kwargs
        )

    @distributed_trace
    def list_available_localities(
        self,
        two_letter_iso_country_name, # type: str
        administrative_division = None, # type: str
        **kwargs # type: Any
    ):
        # type: (...) -> AsyncItemPaged[PhoneNumberLocality]
        """Gets the list of cities or towns with available phone numbers.

        Gets the list of cities or towns with available phone numbers.

        :param two_letter_iso_country_name: The ISO 3166-2 country/region code, e.g. US. Required.
        :type two_letter_iso_country_name: str
        :param administrative_division: An optional parameter for the name of the state or province
         in which to search for the area code. e.g. California. Default value is None.
        :type administrative_division: str
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberLocality
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.PhoneNumberLocality]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_available_localities(
            two_letter_iso_country_name,
            administrative_division=administrative_division,
            accept_language=self._accepted_language,
            **kwargs
        )

    @distributed_trace
    def list_available_offerings(
        self,
        two_letter_iso_country_name, # type: str
        phone_number_type = None, # type: PhoneNumberType
        phone_number_assignment_type = None, # type: PhoneNumberAssignmentType
        **kwargs
    ):
        # type: (...) -> AsyncItemPaged[PhoneNumberOffering]
        """List available offerings of capabilities with rates for the given country/region.

        List available offerings of capabilities with rates for the given country/region.

        :param two_letter_iso_country_name: The ISO 3166-2 country/region code, e.g. US. Required.
        :type two_letter_iso_country_name: str
        :param phone_number_type: Filter by phoneNumberType, e.g. Geographic, TollFree. Known values
         are: "geographic" and "tollFree". Default value is None.
        :type phone_number_type: ~azure.communication.phonenumbers.models.PhoneNumberType
        :param phone_number_assignment_type: Filter by assignmentType, e.g. User, Application. Known values are:
         "person" and "application". Default value is None.
        :type phone_number_assignment_type: ~azure.communication.phonenumbers.models.PhoneNumberAssignmentType
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberOffering
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.PhoneNumberOffering]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_offerings(
            two_letter_iso_country_name,
            phone_number_type=phone_number_type,
            phone_number_assignment_type=phone_number_assignment_type,
            **kwargs
        )

    @distributed_trace
    def list_available_toll_free_area_codes(
        self,
        two_letter_iso_country_name, # type: str
        **kwargs # type: Any
    ):
        # type: (...) -> AsyncItemPaged[AreaCodeResult]
        """Gets the list of available toll free area codes.

        Gets the list of available toll free area codes.

        :param two_letter_iso_country_name: The ISO 3166-2 country/region code, e.g. US. Required.
        :type two_letter_iso_country_name: str
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of AreaCodeResult
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.AreaCodeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_area_codes(
            two_letter_iso_country_name,
            phone_number_type=PhoneNumberType.GEOGRAPHIC,
            assignment_type= PhoneNumberAssignmentType.APPLICATION,
            **kwargs
        )

    @distributed_trace
    def list_available_geographic_area_codes(
        self,
        two_letter_iso_country_name, # type: str
        phone_number_assignment_type, #type: PhoneNumberAssignmentType
        locality, # type: str
        administrative_division = None, # type: str
        **kwargs # type: Any
    ):
        # type: (...) -> AsyncItemPaged[AreaCodeResult]
        """Gets the list of available geographic area codes.

        Gets the list of available geographic area codes.

        :param two_letter_iso_country_name: The ISO 3166-2 country/region code, e.g. US. Required.
        :type two_letter_iso_country_name: str
        :param phone_number_assignment_type: Filter by assignmentType, e.g. user, application. Known values are:
         "person" and "application". Default value is None.
        :type phone_number_assignment_type: ~azure.communication.phonenumbers.models.PhoneNumberAssignmentType
        :param locality: The name of locality in which to search for the area code. e.g. Seattle.
         This is required if the phone number type is Geographic. Default value is None.
        :type locality: str
        :param administrative_division: The name of the state or province in which to search for the
         area code. e.g. California. Default value is None.
        :type administrative_division: str
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of AreaCodeResult
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.communication.phonenumbers.models.AreaCodeResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_area_codes(
            two_letter_iso_country_name,
            phone_number_type=PhoneNumberType.GEOGRAPHIC,
            assignment_type= phone_number_assignment_type,
            locality=locality,
            administrative_division=administrative_division,
            **kwargs
        )

    async def __aenter__(self) -> "PhoneNumbersClient":
        await self._phone_number_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.phonenumbers.aio.PhoneNumbersClient` session.
        """
        await self._phone_number_client.__aexit__()
