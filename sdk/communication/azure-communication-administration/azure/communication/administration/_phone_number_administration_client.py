# pylint: disable=R0904
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller

from ._phonenumber._generated._phone_number_administration_service\
    import PhoneNumberAdministrationService as PhoneNumberAdministrationClientGen

from ._shared.utils import parse_connection_str
from ._shared.policy import HMACCredentialsPolicy
from ._version import SDK_MONIKER

class PhoneNumberAdministrationClient(object):
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
        pass

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
        pass

    @distributed_trace
    def begin_search_phone_numbers(
        self,
        country_code, #type: str
        **kwargs  # type: Any
    ):
        # type: (str, Any) -> LROPoller[SearchResult]
        """Begins creating a phone number search to reserve phone numbers.
        :param str country_code: country code for the search
        :keyword number_type: Required. The phone number type. Possible values include: "tollFree",
        "geographic".
        :type number_type: str or ~azure.communication.administration.models.PhoneNumberType
        :keyword assignment_type: Required. The phone number's assignment type. Possible values include:
        "person", "application".
        :type assignment_type: str or ~azure.communication.administration.models.AssignmentType
        :keyword capabilities: Required. The phone number's capabilities.
        :type capabilities: ~azure.communication.administration.models.SearchCapabilities
        :keyword area_code: The desired area code.
        :type area_code: str
        :keyword quantity: The desired quantity of phone numbers.
        :type quantity: int
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.SearchResult]
        """
        pass

    @distributed_trace
    def begin_purchase_phone_numbers(
        self,
        search_id, #type: str
        **kwargs # type: Any
    ):
        #type: (str, Any) -> LROPoller[SearchResult]
        """Begins purchasing a phone number search
        :param str search_id: Id for the search
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.SearchResult]
        """
        pass

    @distributed_trace
    def get_search_result(
        self,
        search_id, #type: str
        **kwargs # type: Any
    ):
        #type: (str, Any) -> SearchResult
        """Gets the search associated with the id
        :param str search_id: Id for the search
        :returns: Search result associated with the search id
        :rtype: ~azure.communication.administration.SearchResult
        """
        pass

    @distributed_trace
    def get_operation(
        self,
        operation_id, #type: str
        **kwargs # type: Any
    ):
        #type: (str, Any) -> Operation
        """Gets the operation associated with the id
        :param str operation_id: Id for the operation
        :returns: Operation associated with the Id
        :rtype: ~azure.communication.administration.Operation
        """
        pass

    @distributed_trace
    def cancel_operation(
        self,
        operation_id, #type: str
        **kwargs # type: Any
    ):
        #type: (str, Any) -> None
        """Cancels the operation associated with the id
        :param str operation_id: Id for the operation
        """
        pass

    @distributed_trace
    def list_acquired_phone_numbers(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AcquiredPhoneNumbers]
        """Gets the list of the acquired phone numbers.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.AcquiredPhoneNumbers]
        """
        pass

    @distributed_trace
    def get_phone_number(
        self,
        phone_number, #type: str
        **kwargs # type: Any
    ):
        #type: (str, Any) -> AcquiredPhoneNumber
        """Gets the details of the phone number
        :param str phone_number: The phone number to get details
        :returns: The phone number details
        :rtype: ~azure.communication.administration.AcquiredPhoneNumber
        """
        pass

    @distributed_trace
    def begin_update_phone_number(
        self,
        phone_number, #type: str
        **kwargs  # type: Any
    ):
        # type: (str, Any) -> LROPoller[AcquiredPhoneNumber]
        """Updates the phone number capabailities
        :param str phone_number: The phone number to get details
        :keyword callback_url: The webhook URL for receiving incoming events.
        :type callback_url: str
        :keyword application_id: The application id the number has been assigned to.
        :type application_id: str
        :keyword capabilities: The new set of enabled capabilities.
        :type capabilities: ~azure.communication.administration.models.Capabilities
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.SearchResult]
        """
        pass

    @distributed_trace
    def begin_release_phone_number(
        self,
        phone_number, #type: str
        **kwargs  # type: Any
    ):
        # type: (str, Any) -> LROPoller[None]
        """Releases an already acquired phone number 
        :param str phone_number: The phone number to get details
        """
        pass

