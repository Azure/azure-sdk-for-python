# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._communication_identity_client import CommunicationIdentityClient
from ._phone_numbers_client import PhoneNumbersClient

from ._identity._generated.models import (
    CommunicationTokenRequest,
    CommunicationIdentityToken
)

from ._phonenumber._generated.models import (
    AcquiredPhoneNumber,
    AcquiredPhoneNumberUpdate,
    PhoneNumberAssignmentType,
    CommunicationError,
    CommunicationErrorResponse,
    PhoneNumberCapabilitiesRequest,
    PhoneNumberCapabilityValue,
    PhoneNumberCost,
    PhoneNumberSearchResult,
    PhoneNumberType
)

from ._shared.models import (
    CommunicationUser,
    PhoneNumber,
    UnknownIdentifier
)

__all__ = [
    'CommunicationIdentityClient',
    'PhoneNumbersClient',

    # from _identity
    'CommunicationTokenRequest',
    'CommunicationIdentityToken',

    # from _phonenumber
    'AcquiredPhoneNumber',
    'AcquiredPhoneNumberUpdate',
    'PhoneNumberAssignmentType',
    'CommunicationError',
    'CommunicationErrorResponse',
    'PhoneNumberCapabilitiesRequest',
    'PhoneNumberCapabilityValue',
    'PhoneNumberCost',
    'PhoneNumberSearchResult',
    'PhoneNumberType',

    # from _shared
    'CommunicationUser',
    'PhoneNumber',
    'UnknownIdentifier'
]
