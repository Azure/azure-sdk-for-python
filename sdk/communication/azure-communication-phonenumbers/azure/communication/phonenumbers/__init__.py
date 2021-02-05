# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._phone_number_administration_client import PhoneNumbersAdministrationClient
from ._polling import ReservePhoneNumberPolling, PurchaseReservationPolling, ReleasePhoneNumberPolling

from ._generated.models import (
    AcquiredPhoneNumber,
    AcquiredPhoneNumbers,
    AreaCodes,
    CreateSearchOptions,
    CreateSearchResponse,
    LocationOptionsQuery,
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
    ReleaseResponse,
    UpdateNumberCapabilitiesResponse,
    UpdatePhoneNumberCapabilitiesResponse
)

from ._shared.models import (
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    UnknownIdentifier
)

__all__ = [
    'PhoneNumbersAdministrationClient',
    'ReservePhoneNumberPolling',
    'PurchaseReservationPolling',
    'ReleasePhoneNumberPolling',

    # from _phonenumber
    'AcquiredPhoneNumber',
    'AcquiredPhoneNumbers',
    'AreaCodes',
    'CreateSearchOptions',
    'CreateSearchResponse',
    'LocationOptionsQuery',
    'LocationOptionsResponse',
    'NumberConfigurationResponse',
    'NumberUpdateCapabilities',
    'PhoneNumberCountries',
    'PhoneNumberEntities',
    'PhoneNumberRelease',
    'PhoneNumberReservation',
    'PhonePlanGroups',
    'PhonePlansResponse',
    'PstnConfiguration',
    'ReleaseResponse',
    'UpdateNumberCapabilitiesResponse',
    'UpdatePhoneNumberCapabilitiesResponse',

    # from _shared
    'CommunicationUserIdentifier',
    'PhoneNumberIdentifier',
    'UnknownIdentifier'
]
