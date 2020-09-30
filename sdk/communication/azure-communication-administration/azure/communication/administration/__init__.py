# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._communication_identity_client import CommunicationIdentityClient
from ._phone_number_administration_client import PhoneNumberAdministrationClient

from ._identity._generated.models import (
    CommunicationTokenRequest,
    CommunicationIdentityToken
)

from ._phonenumber._generated.models import (
    AcquiredPhoneNumber,
    AcquiredPhoneNumbers,
    AreaCodes,
    CreateSearchResponse,
    LocationOptionsQuery,
    LocationOptionsResponse,
    NumberConfigurationResponse,
    NumberUpdateCapabilities,
    PhoneNumberCountries,
    PhoneNumberEntities,
    PhoneNumberRelease,
    PhoneNumberSearch,
    PhonePlanGroups,
    PhonePlansResponse,
    PstnConfiguration,
    ReleaseResponse,
    UpdateNumberCapabilitiesResponse,
    UpdatePhoneNumberCapabilitiesResponse,
    CreateSearchOptions
)

from ._shared.models import (
    CommunicationUser,
    PhoneNumber,
    UnknownIdentifier
)

__all__ = [
    'CommunicationIdentityClient',
    'PhoneNumberAdministrationClient',

    # from _identity
    'CommunicationTokenRequest',
    'CommunicationIdentityToken',

    # from _phonenumber
    'AcquiredPhoneNumber',
    'AcquiredPhoneNumbers',
    'AreaCodes',
    'CreateSearchResponse',
    'LocationOptionsQuery',
    'LocationOptionsResponse',
    'NumberConfigurationResponse',
    'NumberUpdateCapabilities',
    'PhoneNumberCountries',
    'PhoneNumberEntities',
    'PhoneNumberRelease',
    'PhoneNumberSearch',
    'PhonePlanGroups',
    'PhonePlansResponse',
    'PstnConfiguration',
    'ReleaseResponse',
    'UpdateNumberCapabilitiesResponse',
    'UpdatePhoneNumberCapabilitiesResponse',
    'CreateSearchOptions',

    # from _shared
    'CommunicationUser',
    'PhoneNumber',
    'UnknownIdentifier'
]
