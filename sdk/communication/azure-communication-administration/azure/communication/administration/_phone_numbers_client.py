# pylint: disable=R0904
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.tracing.decorator import distributed_trace

from ._phonenumber._generated._phone_numbers_client import PhoneNumbersClient as PhoneNumbersClientGen

from ._shared.utils import parse_connection_str
from ._shared.policy import HMACCredentialsPolicy
from ._version import SDK_MONIKER

class PhoneNumbersClient(object):
    """Azure Communication Services Phone Number Management client.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param credential:
        The credentials with which to authenticate. The value is an account
        shared access key
    """
    def __init__(
            self,
            endpoint, # type: str
            credential, # type: str
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
        self._phone_numbers_client = PhoneNumbersClientGen(
            self._endpoint,
            authentication_policy=HMACCredentialsPolicy(endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> PhoneNumberAdministrationClient
        """Create PhoneNumberAdministrationClient from a Connection String.
        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of PhoneNumberAdministrationClient.
        :rtype: ~azure.communication.PhoneNumberAdministrationClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace
    def begin_release_phone_number(
            self,
            phone_number,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[None]
        """Begin releasing an acquired phone number.

        :param phone_number: The phone number id in E.164 format. The leading plus can be either + or
         encoded as %2B.
        :type phone_number: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: True for ARMPolling, False for no polling, or a
         polling object for personal polling strategy
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError"""
        
        return self._phone_numbers_client.phone_numbers.begin_release_phone_number(
            phone_number,
            **kwargs
        )

    @distributed_trace
    def begin_search_available_phone_numbers(
        self,
        country_code,  # type: str
        phone_number_type,  # type: Union[str, "_models.PhoneNumberType"]
        assignment_type,  # type: Union[str, "_models.PhoneNumberAssignmentType"]
        capabilities,  # type: "_models.PhoneNumberCapabilitiesRequest"
        area_code=None,  # type: Optional[str]
        quantity=1,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[None]
        """Search for available phone numbers to purchase.

        Search for available phone numbers to purchase.

        :param country_code: The ISO 3166-2 country code.
        :type country_code: str
        :param phone_number_type: The phone number type.
        :type phone_number_type: str or ~azure.communication.administration.models.PhoneNumberType
        :param assignment_type: The phone number's assignment type.
        :type assignment_type: str or ~azure.communication.administration.models.PhoneNumberAssignmentType
        :param capabilities: The phone number's capabilities.
        :type capabilities: ~azure.communication.administration.models.PhoneNumberCapabilitiesRequest
        :param area_code: The desired area code.
        :type area_code: str
        :param quantity: The desired quantity of phone numbers.
        :type quantity: int
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: True for ARMPolling, False for no polling, or a
         polling object for personal polling strategy
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._phone_numbers_client.phone_numbers.begin_search_available_phone_numbers(
            country_code,
            phone_number_type,
            assignment_type,
            capabilities,
            area_code=area_code,
            quantity=quantity,
            **kwargs
        )

    @distributed_trace
    def begin_purchase_phone_numbers(
        self,
        search_id=None, # type: string
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[None]
        """Begins purchasing phone numbers.
        :param search_id: The id of the search result to purchase.
        :type search_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: True for ARMPolling, False for no polling, or a
         polling object for personal polling strategy
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._phone_numbers_client.phone_numbers.begin_purchase_phone_numbers(
            search_id=search_id,
            **kwargs
        )

    @distributed_trace
    def list_all_reservations(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhoneNumberEntities]
        """Gets a list of all reservations.

        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.PhoneNumberEntities]
        """
        return self._phone_number_administration_client.phone_number_administration.get_all_searches(
            **kwargs
        )

    @distributed_trace
    def cancel_reservation(
        self,
        reservation_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Cancels the reservation. This means existing numbers in the reservation will be made available.

        :param reservation_id: The reservation id to be canceled.
        :type reservation_id: str
        :rtype: None
        """
        return self._phone_number_administration_client.phone_number_administration.cancel_search(
            search_id=reservation_id,
            **kwargs
        )

    @distributed_trace
    def begin_purchase_reservation(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[PhoneNumberReservation]
        """Begins purchase the reserved phone numbers of a phone number search.
        Caller must provide either reservation_id, or continuation_token keywords to use the method.
        If both reservation_id and continuation_token are specified, only continuation_token will be used to
        restart a poller from a saved state, and keyword reservation_id will be ignored.
        :keyword str reservation_id: The reservation id to be purchased.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.PhoneNumberReservation]
        """
        cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]

        reservation_polling = PurchaseReservationPolling(
            is_terminated=lambda status: status in [
                SearchStatus.Success,
                SearchStatus.Expired,
                SearchStatus.Cancelled,
                SearchStatus.Error
            ]
        )

        if cont_token is not None:
            return LROPoller.from_continuation_token(
                polling_method=reservation_polling,
                continuation_token=cont_token,
                client=self._phone_number_administration_client.phone_number_administration
            )

        if "reservation_id" not in kwargs:
            raise ValueError("Either kwarg 'reservation_id' or 'continuation_token' needs to be specified")

        reservation_id = kwargs.pop('reservation_id')  # type: str

        self._phone_number_administration_client.phone_number_administration.purchase_search(
            search_id=reservation_id,
            **kwargs
        )
        initial_state = self._phone_number_administration_client.phone_number_administration.get_search_by_id(
            search_id=reservation_id
        )
        return LROPoller(client=self._phone_number_administration_client.phone_number_administration,
                         initial_response=initial_state,
                         deserialization_callback=None,
                         polling_method=reservation_polling)
