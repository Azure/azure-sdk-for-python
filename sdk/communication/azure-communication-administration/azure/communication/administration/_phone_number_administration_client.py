# pylint: disable=R0904
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.communication.administration._phonenumber._generated.models import ReleaseStatus
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from ._polling import ReleasePhoneNumberPolling, ReservePhoneNumberPolling, PurchaseReservationPolling

from ._phonenumber._generated._phone_number_administration_service\
    import PhoneNumberAdministrationService as PhoneNumberAdministrationClientGen

from ._phonenumber._generated.models import (
    AcquiredPhoneNumbers,
    AreaCodes,
    LocationOptionsResponse,
    NumberConfigurationResponse,
    NumberUpdateCapabilities,
    PhoneNumberCountries,
    PhoneNumberEntities,
    PhoneNumberRelease,
    PhoneNumberReservation,
    PhonePlanGroups,
    PhonePlansResponse,
    PstnConfiguration,
    SearchStatus,
    UpdateNumberCapabilitiesResponse,
    UpdatePhoneNumberCapabilitiesResponse
)

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
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._phone_number_administration_client = PhoneNumberAdministrationClientGen(
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
    def list_all_phone_numbers(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AcquiredPhoneNumbers]
        """Gets the list of the acquired phone numbers.

        :keyword str locale: A language-locale pairing which will be used to localise the names of countries.
        The default is "en-US".
        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.AcquiredPhoneNumbers]
        """
        return self._phone_number_administration_client.phone_number_administration.get_all_phone_numbers(
            **kwargs
        )

    @distributed_trace
    def get_all_area_codes(
            self,
            location_type,  # type: str
            country_code,  # type: str
            phone_plan_id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> AreaCodes
        """Gets a list of the supported area codes.

        :param location_type: The type of location information required by the plan.
        :type location_type: str
        :param country_code: The ISO 3166-2 country code.
        :type country_code: str
        :param phone_plan_id: The plan id from which to search area codes.
        :type phone_plan_id: str
        :keyword List["LocationOptionsQuery"] location_options:
        Represents the underlying list of countries.
        :rtype: ~azure.communication.administration.AreaCodes
        """
        return self._phone_number_administration_client.phone_number_administration.get_all_area_codes(
            location_type=location_type,
            country_code=country_code,
            phone_plan_id=phone_plan_id,
            **kwargs
        )

    @distributed_trace
    def get_capabilities_update(
        self,
        capabilities_update_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> UpdatePhoneNumberCapabilitiesResponse
        """Get capabilities by capabilities update id.

        :param capabilities_update_id:
        :type capabilities_update_id: str
        :rtype: ~azure.communication.administration.UpdatePhoneNumberCapabilitiesResponse
        """
        return self._phone_number_administration_client.phone_number_administration.get_capabilities_update(
            capabilities_update_id,
            **kwargs
        )

    @distributed_trace
    def update_capabilities(
        self,
        phone_number_capabilities_update,  # type: Dict[str, NumberUpdateCapabilities]
        **kwargs  # type: Any
    ):
        # type: (...) -> UpdateNumberCapabilitiesResponse
        """Adds or removes phone number capabilities.

        :param phone_number_capabilities_update: The map of phone numbers to the capabilities update
         applied to the phone number.
        :type phone_number_capabilities_update:
         dict[str, ~azure.communication.administration.NumberUpdateCapabilities]
        :rtype: ~azure.communication.administration.UpdateNumberCapabilitiesResponse
        """
        return self._phone_number_administration_client.phone_number_administration.update_capabilities(
            phone_number_capabilities_update,
            **kwargs
        )

    @distributed_trace
    def list_all_supported_countries(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhoneNumberCountries]
        """Gets a list of supported countries.

        :keyword str locale: A language-locale pairing which will be used to localise the names of countries.
        The default is "en-US".
        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.PhoneNumberCountries]
        """
        return self._phone_number_administration_client.phone_number_administration.get_all_supported_countries(
            **kwargs
        )

    @distributed_trace
    def get_number_configuration(
        self,
        phone_number,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> NumberConfigurationResponse
        """Endpoint for getting number configurations.

        :param phone_number: The phone number in the E.164 format.
        :type phone_number: str
        :rtype: ~azure.communication.administration.NumberConfigurationResponse
        """
        return self._phone_number_administration_client.phone_number_administration.get_number_configuration(
            phone_number,
            **kwargs
        )

    @distributed_trace
    def configure_number(
        self,
        pstn_configuration,  # type: PstnConfiguration
        phone_number,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Endpoint for configuring a pstn number.

        :param pstn_configuration: Definition for pstn number configuration.
        :type pstn_configuration: ~azure.communication.administration.PstnConfiguration
        :param phone_number: The phone number to configure.
        :type phone_number: str
        :rtype: None
        """
        return self._phone_number_administration_client.phone_number_administration.configure_number(
            pstn_configuration,
            phone_number,
            **kwargs
        )

    @distributed_trace
    def unconfigure_number(
        self,
        phone_number,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Endpoint for unconfiguring a pstn number by removing the configuration.

        :param phone_number: The phone number in the E.164 format.
        :type phone_number: str
        :rtype: None
        """
        return self._phone_number_administration_client.phone_number_administration.unconfigure_number(
            phone_number,
            **kwargs
        )

    @distributed_trace
    def list_phone_plan_groups(
        self,
        country_code,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhonePlanGroups]
        """Gets a list of phone plan groups for the given country.

        :param country_code: The ISO 3166-2 country code.
        :type country_code: str
        :keyword str locale: A language-locale pairing which will be used to localise the names of countries.
        The default is "en-US".
        :keyword include_rate_information bool: An optional boolean parameter for including rate information in result.
        The default is False".
        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.PhonePlanGroups]
        """
        return self._phone_number_administration_client.phone_number_administration.get_phone_plan_groups(
            country_code,
            **kwargs
        )

    @distributed_trace
    def list_phone_plans(
        self,
        country_code,  # type: str
        phone_plan_group_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhonePlansResponse]
        """Gets a list of phone plans for a phone plan group.

        :param country_code: The ISO 3166-2 country code.
        :type country_code: str
        :param phone_plan_group_id:
        :type phone_plan_group_id: str
        :keyword str locale: A language-locale pairing which will be used to localise the names of countries.
        The default is "en-US".
        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.PhonePlansResponse]
        """
        return self._phone_number_administration_client.phone_number_administration.get_phone_plans(
            country_code,
            phone_plan_group_id,
            **kwargs
        )

    @distributed_trace
    def get_phone_plan_location_options(
        self,
        country_code,  # type: str
        phone_plan_group_id,  # type: str
        phone_plan_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> LocationOptionsResponse
        """Gets a list of location options for a phone plan.

        :param country_code: The ISO 3166-2 country code.
        :type country_code: str
        :param phone_plan_group_id:
        :type phone_plan_group_id: str
        :param phone_plan_id:
        :type phone_plan_id: str
        :keyword str locale: A language-locale pairing which will be used to localise the names of countries.
        The default is "en-US".
        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.communication.administration.LocationOptionsResponse
        """
        return self._phone_number_administration_client.phone_number_administration.get_phone_plan_location_options(
            country_code=country_code,
            phone_plan_group_id=phone_plan_group_id,
            phone_plan_id=phone_plan_id,
            **kwargs
        )

    @distributed_trace
    def get_release_by_id(
            self,
            release_id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> PhoneNumberRelease
        """Gets a release by a release id.

        :param release_id: Represents the release id.
        :type release_id: str
        :rtype: ~azure.communication.administration.PhoneNumberRelease
        """
        return self._phone_number_administration_client.phone_number_administration.get_release_by_id(
            release_id,
            **kwargs
        )

    @distributed_trace
    def begin_release_phone_numbers(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[PhoneNumberRelease]
        """Begins creating a release for the given phone numbers.
        Caller must provide either phone_numbers, or continuation_token keywords to use the method.
        If both phone_numbers and continuation_token are specified, only continuation_token will be used to
        restart a poller from a saved state, and keyword phone_numbers will be ignored.

        :keyword list[str] phone_numbers: The list of phone numbers in the release request.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.PhoneNumberRelease]
        """
        cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]

        release_polling = ReleasePhoneNumberPolling(
            is_terminated=lambda status: status in [
                ReleaseStatus.Complete,
                ReleaseStatus.Failed,
                ReleaseStatus.Expired
            ]
        )

        if cont_token is not None:
            return LROPoller.from_continuation_token(
                polling_method=release_polling,
                continuation_token=cont_token,
                client=self._phone_number_administration_client.phone_number_administration
            )

        if "phone_numbers" not in kwargs:
            raise ValueError("Either kwarg 'phone_numbers' or 'continuation_token' needs to be specified")

        create_release_response = self._phone_number_administration_client.\
            phone_number_administration.release_phone_numbers(
                **kwargs
        )

        initial_state = self._phone_number_administration_client.phone_number_administration.get_release_by_id(
            release_id=create_release_response.release_id
        )

        return LROPoller(client=self._phone_number_administration_client.phone_number_administration,
                         initial_response=initial_state,
                         deserialization_callback=None,
                         polling_method=release_polling)

    @distributed_trace
    def list_all_releases(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhoneNumberEntities]
        """Gets a list of all releases.

        :keyword int skip: An optional parameter for how many entries to skip, for pagination purposes.
        The default is 0.
        :keyword int take: An optional parameter for how many entries to return, for pagination purposes.
        The default is 100.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.administration.PhoneNumberEntities]
        """
        return self._phone_number_administration_client.phone_number_administration.get_all_releases(
            **kwargs
        )

    @distributed_trace
    def get_reservation_by_id(
        self,
        reservation_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> PhoneNumberReservation
        """Get reservation by reservation id.

        :param reservation_id: The reservation id to get reservation.
        :type reservation_id: str
        :rtype: ~azure.communication.administration.PhoneNumberReservation
        """
        return self._phone_number_administration_client.phone_number_administration.get_search_by_id(
            search_id=reservation_id,
            **kwargs
        )

    @distributed_trace
    def begin_reserve_phone_numbers(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[PhoneNumberReservation]
        """Begins creating a phone number search to reserve phone numbers.
        Caller must provide either options, or continuation_token keywords to use the method.
        If both options and continuation_token are specified, only continuation_token will be used to
        restart a poller from a saved state, and keyword options will be ignored.
        :keyword azure.communication.administration.CreateSearchOptions options: reservation options.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :rtype: ~azure.core.polling.LROPoller[~azure.communication.administration.PhoneNumberReservation]
        """
        cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]

        reservation_polling = ReservePhoneNumberPolling(
            is_terminated=lambda status: status in [
                SearchStatus.Reserved,
                SearchStatus.Expired,
                SearchStatus.Success,
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

        if "options" not in kwargs:
            raise ValueError("Either kwarg 'options' or 'continuation_token' needs to be specified")

        reservation_options = kwargs.pop('options')  # type: str

        create_reservation_response = self._phone_number_administration_client.\
            phone_number_administration.create_search(
                body=reservation_options,
                **kwargs
        )

        initial_state = self._phone_number_administration_client.phone_number_administration.get_search_by_id(
            search_id=create_reservation_response.search_id
        )
        return LROPoller(client=self._phone_number_administration_client.phone_number_administration,
                         initial_response=initial_state,
                         deserialization_callback=None,
                         polling_method=reservation_polling)

    @distributed_trace
    def list_all_searches(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[PhoneNumberEntities]
        """Gets a list of all searches.

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
