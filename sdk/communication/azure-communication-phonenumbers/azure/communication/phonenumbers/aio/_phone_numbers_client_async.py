from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from .._generated.aio._phone_numbers_client import PhoneNumbersClient as PhoneNumbersClientGen
from .._generated.models import PhoneNumberSearchRequest
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._version import SDK_MONIKER
import pytest


class PhoneNumbersClient(object):
    def __init__(
                self,
                endpoint,  # type: str
                credential,  # type: str
                **kwargs  # type: Any
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
            self._phone_number_client = PhoneNumbersClientGen(
                self._endpoint,
                authentication_policy=get_authentication_policy(endpoint, credential, is_async=True),
                sdk_moniker=SDK_MONIKER,
                **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            **kwargs  # type: Any
    ):  # type: (...) -> PhoneNumbersAdministrationClient
        """Create PhoneNumbersAdministrationClient from a Connection String.
        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of PhoneNumbersAdministrationClient.
        :rtype: ~azure.communication.PhoneNumbersAdministrationClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)
    
    
    @distributed_trace_async
    async def begin_purchase_phone_numbers(
            self, 
            search_id,
            **kwargs
    ):
         # type: (...) -> AsyncLROPollerLROPoller[PhoneNumberSearchResult]
        """Purchases phone numbers.

        :param search_id: The search id.
        :type search_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.communication.phonenumbers.models.PhoneNumberSearchResult]
        """
        return await self._phone_number_client.phone_numbers.begin_purchase_phone_numbers(
            search_id,
            **kwargs
        )
    
    @distributed_trace_async
    async def begin_release_phone_number(
            self, 
            phone_number, 
            **kwargs
    ):
        # type: (...) -> AsyncLROPoller[None]
        """Releases an acquired phone number.

        :param phone_number: Phone number to be released, e.g. +11234567890.
        :type phone_number: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        """
        return await self._phone_number_client.phone_numbers.begin_release_phone_number(
            phone_number,
            **kwargs
        )

    @distributed_trace_async
    async def begin_search_available_phone_numbers(
            self, 
            country_code, 
            phone_number_type, 
            assignment_type, 
            capabilities, 
            area_code, 
            quantity = 1,
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
        :param area_code: The area code of the desired phone number, e.g. 425.
        :type area_code: str
        :param quantity: The quantity of phone numbers in the search. Should be at least 1.
        :type quantity: int
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
         False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.communication.phonenumbers.models.PhoneNumberSearchResult]
        """
        search_request = PhoneNumberSearchRequest(
            phone_number_type = phone_number_type,
            assignment_type = assignment_type,
            capabilities = capabilities,
            area_code = area_code,
            quantity = quantity
        )
        return await self._phone_number_client.phone_numbers.begin_search_available_phone_numbers(
            country_code,
            search_request,
            **kwargs
        )

    @distributed_trace_async
    async def begin_update_phone_number_capabilities(
            self, 
            phone_number, 
            sms, 
            calling, 
            **kwargs
    ):
        # type: (...) -> AsyncLROPoller["_models.AcquiredPhoneNumber"]
        """Updates the capabilities of a phone number.

        :param phone_number: The phone number id in E.164 format. The leading plus can be either + or
            encoded as %2B, e.g. +11234567890.
        :type phone_number: str
        :param calling: Capability value for calling.
        :type calling: str or ~azure.communication.phonenumbers.models.PhoneNumberCapabilityValue
        :param sms: Capability value for SMS.
        :type sms: str or ~azure.communication.phonenumbers.models.PhoneNumberCapabilityValue
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: Pass in True if you'd like the LROBasePolling polling method,
            False for no polling, or your own initialized polling object for a personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :rtype: ~azure.core.polling.AsyncLROPoller[AcquiredPhoneNumber]
        """
        return await self._phone_number_client.phone_numbers.begin_update_capabilities(
            phone_number,
            calling,
            sms,
            **kwargs
        ) 

    @distributed_trace_async
    async def get_phone_number(
            self, 
            phone_number,
            **kwargs
    ):
        # type: (...) -> AcquiredPhoneNumber
        """Gets the details of the given acquired phone number.

        :param phone_number: The acquired phone number whose details are to be fetched in E.164 format,
         e.g. +11234567890.
        :type phone_number: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :rtype: ~azure.communication.phonenumbers.models.AcquiredPhoneNumber
        """
        return await self._phone_number_client.phone_numbers.get_by_number(
            phone_number,
            **kwargs
        )

    @distributed_trace
    def list_acquired_phone_numbers(
        self, 
        **kwargs
    ):
         # type: (...) -> AsyncItemPaged[AcquiredPhoneNumbers]
        """Gets the list of all acquired phone numbers.

        :param skip: An optional parameter for how many entries to skip, for pagination purposes. The
         default value is 0.
        :type skip: int
        :param top: An optional parameter for how many entries to return, for pagination purposes. The
         default value is 100.
        :type top: int
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.communication.phonenumbers.models.AcquiredPhoneNumbers]
        """
        return self._phone_number_client.phone_numbers.list_phone_numbers(
            **kwargs
        )
    
    @distributed_trace_async
    async def update_phone_number(
            self, 
            phone_number,
            callback_uri,
            application_id,
            **kwargs
    ):
        # type: (...) -> AcquiredPhoneNumber
        """Updates the configuration of a phone number.

        :param phone_number: Phone number to be updated, e.g. +11234567890.
        :type phone_number: str
        :param callback_uri: The webhook for receiving incoming events.
         e.g. "https://{{site-name}}.azurewebsites.net/api/updates".
         Please read https://docs.microsoft.com/en-us/azure/communication-services/concepts/event-
         handling
         for integration with Azure Event Grid to deliver real-time event notifications.
        :type callback_uri: str
        :param application_id: The application id of the application to which to configure.
        :type application_id: str
        :rtype: ~azure.communication.phonenumbers.models.AcquiredPhoneNumber
        """
        return await self._phone_number_client.phone_numbers.update(
            phone_number,
            callback_uri,
            application_id,
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