# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, Optional, Union, Any

from azure.core.credentials import TokenCredential, AzureKeyCredential
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError

from ._generated._client import PhoneNumbersClient as PhoneNumbersClientGen
from ._generated.models import (
    PhoneNumberSearchRequest,
    PhoneNumberCapabilitiesRequest,
    PhoneNumberPurchaseRequest,
    PhoneNumberType,
    OperatorInformationRequest,
    OperatorInformationOptions,
    OperatorInformationResult,
    PhoneNumberAssignmentType,
    PhoneNumberAreaCode,
    PhoneNumberCapabilities,
    PhoneNumberCapabilityType,
    PhoneNumberCountry,
    PhoneNumberOffering,
    PhoneNumberLocality,
    PhoneNumberSearchResult,
    PurchasedPhoneNumber,
)
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION

_DEFAULT_POLLING_INTERVAL_IN_SECONDS = 2


class PhoneNumbersClient:
    """A client to interact with the AzureCommunicationService Phone Numbers gateway.

    This client provides operations to interact with the phone numbers service

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword api_version: Azure Communication Phone Number API version.
        The default value is "2022-01-11-preview2".
        Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[TokenCredential, AzureKeyCredential], **kwargs: Any) -> None:
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError as e:
            raise ValueError("Account URL must be a string.") from e

        if not credential:
            raise ValueError("You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._accepted_language = kwargs.pop("accepted_language", None)
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION.value)
        self._phone_number_client = PhoneNumbersClientGen(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "PhoneNumbersClient":
        """Create PhoneNumbersClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of PhoneNumbersClient.
        :rtype: ~azure.communication.phonenumbers.PhoneNumbersClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace
    def begin_purchase_phone_numbers(self, search_id: str, **kwargs: Any) -> LROPoller[None]:
        """Purchases phone numbers.

        :param search_id: The search id.
        :type search_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time (seconds) between two polls
            for LRO operations if no Retry-After header is present.
        :returns: A poller to wait on the completion of the purchase.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        purchase_request = PhoneNumberPurchaseRequest(search_id=search_id)

        polling_interval = kwargs.pop("polling_interval", _DEFAULT_POLLING_INTERVAL_IN_SECONDS)
        return self._phone_number_client.phone_numbers.begin_purchase_phone_numbers(
            body=purchase_request, polling_interval=polling_interval, **kwargs
        )

    @distributed_trace
    def begin_release_phone_number(self, phone_number: str, **kwargs: Any) -> LROPoller[None]:
        """Releases an purchased phone number.

        :param phone_number: Phone number to be released, e.g. +55534567890.
        :type phone_number: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time (seconds) between two polls
            for LRO operations if no Retry-After header is present.
        :returns: A poller to wait on the status of the release operation.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        polling_interval = kwargs.pop("polling_interval", _DEFAULT_POLLING_INTERVAL_IN_SECONDS)
        return self._phone_number_client.phone_numbers.begin_release_phone_number(
            phone_number, polling_interval=polling_interval, **kwargs
        )

    @distributed_trace
    def begin_search_available_phone_numbers(
        self,
        country_code: str,
        phone_number_type: Union[PhoneNumberType, str],
        assignment_type: Union[PhoneNumberAssignmentType, str],
        capabilities: PhoneNumberCapabilities,
        **kwargs: Any
    ) -> LROPoller[PhoneNumberSearchResult]:
        """Search for available phone numbers to purchase.

        :param country_code: The ISO 3166-2 country code, e.g. US.
        :type country_code: str
        :param phone_number_type: Required. The type of phone numbers to search for, e.g. geographic,
            or tollFree. Possible values include: "geographic", "tollFree".
        :type phone_number_type: str or ~azure.communication.phonenumbers.PhoneNumberType
        :param assignment_type: Required. The assignment type of the phone numbers to search for. A
            phone number can be assigned to a person, or to an application. Possible values include:
            "user", "application".
        :type assignment_type: str or
            ~azure.communication.phonenumbers.PhoneNumberAssignmentType
        :param capabilities: Required. Capabilities of a phone number.
        :type capabilities: ~azure.communication.phonenumbers.PhoneNumberCapabilities
        :keyword str area_code: The area code of the desired phone number, e.g. 425. If not set,
            any area code could be used in the final search.
        :keyword int quantity: The quantity of phone numbers in the search. Default is 1.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
         False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time (seconds) between two polls
            for LRO operations if no Retry-After header is present.
        :returns: A poller to wait on the search results.
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.phonenumbers.PhoneNumberSearchResult]
        """
        search_request = PhoneNumberSearchRequest(
            phone_number_type=phone_number_type,
            assignment_type=assignment_type,
            capabilities=capabilities,
            quantity=kwargs.pop("quantity", None),
            area_code=kwargs.pop("area_code", None),
        )
        polling_interval = kwargs.pop("polling_interval", _DEFAULT_POLLING_INTERVAL_IN_SECONDS)
        return self._phone_number_client.phone_numbers.begin_search_available_phone_numbers(
            country_code, search_request, polling_interval=polling_interval, **kwargs
        )

    @distributed_trace
    def begin_update_phone_number_capabilities(
        self,
        phone_number: str,
        sms: Optional[Union[str, PhoneNumberCapabilityType]] = None,
        calling: Optional[Union[str, PhoneNumberCapabilityType]] = None,
        **kwargs: Any
    ) -> LROPoller[PurchasedPhoneNumber]:
        """Updates the capabilities of a phone number.

        :param phone_number: The phone number id in E.164 format. The leading plus can be either + or
            encoded as %2B, e.g. +55534567890.
        :type phone_number: str
        :param sms: Capability value for SMS.
        :type sms: str or ~azure.communication.phonenumbers.PhoneNumberCapabilityType
        :param calling: Capability value for calling.
        :type calling: str or ~azure.communication.phonenumbers.PhoneNumberCapabilityType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time (seconds) between two polls
            for LRO operations if no Retry-After header is present.
        :returns: A poller to wait on the update operation.
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.phonenumbers.PurchasedPhoneNumber]
        """

        capabilities_request = PhoneNumberCapabilitiesRequest(calling=calling, sms=sms)

        polling_interval = kwargs.pop("polling_interval", _DEFAULT_POLLING_INTERVAL_IN_SECONDS)

        if not phone_number:
            raise ValueError("phone_number can't be empty")

        poller = self._phone_number_client.phone_numbers.begin_update_capabilities(
            phone_number, body=capabilities_request, polling_interval=polling_interval, **kwargs
        )

        result_properties = poller.result().additional_properties
        if "status" in result_properties and result_properties["status"].lower() == "failed":
            raise HttpResponseError(message=result_properties["error"]["message"])

        return poller

    @distributed_trace
    def get_purchased_phone_number(self, phone_number: str, **kwargs: Any) -> PurchasedPhoneNumber:
        """Gets the details of the given purchased phone number.

        :param phone_number: The purchased phone number whose details are to be fetched in E.164 format,
         e.g. +11234567890.
        :type phone_number: str
        :return: The details of the given purchased phone number.
        :rtype: ~azure.communication.phonenumbers.PurchasedPhoneNumber
        """
        return self._phone_number_client.phone_numbers.get_by_number(phone_number, **kwargs)

    @distributed_trace
    def list_purchased_phone_numbers(self, **kwargs: Any) -> ItemPaged[PurchasedPhoneNumber]:
        """Gets the list of all purchased phone numbers.

        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :keyword top: An optional parameter for how many entries to return, for pagination purposes.
         The default value is 100. Default value is 100.
        :paramtype top: int
        :returns: An iterator of purchased phone numbers.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.phonenumbers.PurchasedPhoneNumber]
        """
        return self._phone_number_client.phone_numbers.list_phone_numbers(**kwargs)

    @distributed_trace
    def list_available_countries(self, **kwargs: Any) -> ItemPaged[PhoneNumberCountry]:
        """Gets the list of supported countries.

        Gets the list of supported countries.

        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberCountry
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.communication.phonenumbers.PhoneNumberCountry]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_available_countries(
            accept_language=self._accepted_language, **kwargs
        )

    @distributed_trace
    def list_available_localities(self, country_code: str, **kwargs: Any) -> ItemPaged[PhoneNumberLocality]:
        """Gets the list of cities or towns with available phone numbers.

        Gets the list of cities or towns with available phone numbers.

        :param country_code: The ISO 3166-2 country/region two letter code, e.g. US. Required.
        :type country_code: str
        :keyword administrative_division: An optional parameter for the name of the state or province
         in which to search for the area code. e.g. California. Default value is None.
        :paramtype administrative_division: str
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberLocality
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.communication.phonenumbers.PhoneNumberLocality]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_available_localities(
            country_code,
            administrative_division=kwargs.pop("administrative_division", None),
            accept_language=self._accepted_language,
            **kwargs
        )

    @distributed_trace
    def list_available_offerings(self, country_code: str, **kwargs: Any) -> ItemPaged[PhoneNumberOffering]:
        """List available offerings of capabilities with rates for the given country/region.

        List available offerings of capabilities with rates for the given country/region.

        :param country_code: The ISO 3166-2 country/region two letter code, e.g. US. Required.
        :type country_code: str
        :keyword phone_number_type: Filter by phoneNumberType, e.g. Geographic, TollFree. Known values
         are: "geographic" and "tollFree". Default value is None.
        :paramtype phone_number_type: ~azure.communication.phonenumbers.PhoneNumberType
        :keyword assignment_type: Filter by assignmentType, e.g. User, Application. Known values are:
         "person" and "application". Default value is None.
        :paramtype assignment_type: ~azure.communication.phonenumbers.PhoneNumberAssignmentType
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberOffering
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.communication.phonenumbers.PhoneNumberOffering]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_offerings(
            country_code,
            phone_number_type=kwargs.pop("phone_number_type", None),
            assignment_type=kwargs.pop("assignment_type", None),
            **kwargs
        )

    @distributed_trace
    def list_available_area_codes(
        self, country_code: str, phone_number_type: PhoneNumberType, **kwargs: Any
    ) -> ItemPaged[PhoneNumberAreaCode]:
        """Gets the list of available area codes.

        :param country_code: The ISO 3166-2 country/region two letter code, e.g. US. Required.
        :type country_code: str
        :param phone_number_type: Filter by phone number type, e.g. Geographic, TollFree. Known values are:
         "geographic" and "tollFree". Required.
        :type phone_number_type: ~azure.communication.phonenumbers.PhoneNumberType
        :keyword assignment_type: Filter by assignmentType, e.g. User, Application. Known values are:
         "person" and "application". Default value is None.
        :paramtype assignment_type: ~azure.communication.phonenumbers.PhoneNumberAssignmentType
        :keyword locality: The name of locality in which to search for the area code. e.g. Seattle.
         This is required if the phone number type is Geographic. Default value is None.
        :paramtype locality: str
        :keyword administrative_division: The name of the state or province in which to search for the
         area code. e.g. California. Default value is None.
        :paramtype administrative_division: str
        :keyword skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0. Default value is 0.
        :paramtype skip: int
        :return: An iterator like instance of PhoneNumberAreaCode
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.phonenumbers.PhoneNumberAreaCode]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._phone_number_client.phone_numbers.list_area_codes(
            country_code,
            phone_number_type=phone_number_type,
            assignment_type=kwargs.pop("assignment_type", None),
            locality=kwargs.pop("locality", None),
            administrative_division=kwargs.pop("administrative_division", None),
            **kwargs
        )

    @distributed_trace
    def search_operator_information(
        self, phone_numbers: Union[str, List[str]], options: Optional[OperatorInformationOptions] = None, **kwargs: Any
    ) -> OperatorInformationResult:
        """Searches for operator information for a given list of phone numbers.

        :param phone_numbers: The phone number(s) whose operator information should be searched
        :type phone_numbers: str or list[str]
        :param options: Options to modify the search.  Please note: use of options can affect the cost of the search.
        :type options: OperatorInformationOptions
        :return: A search result containing operator information associated with the requested phone numbers
        :rtype: ~azure.communication.phonenumbers.OperatorInformationResult
        """
        if not isinstance(phone_numbers, list):
            phone_numbers = [phone_numbers]
        if options is None:
            options = OperatorInformationOptions(include_additional_operator_details=False)
        request = OperatorInformationRequest(phone_numbers=phone_numbers, options=options)
        return self._phone_number_client.phone_numbers.operator_information_search(request, **kwargs)
