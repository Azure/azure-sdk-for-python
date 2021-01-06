# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._communication_identity_client import CommunicationIdentityClient
from ._phone_numbers_client import PhoneNumbersClient
from ._polling import ReservePhoneNumberPolling, PurchaseReservationPolling, ReleasePhoneNumberPolling

from ._identity._generated.models import (
    CommunicationTokenRequest,
    CommunicationIdentityToken
)

from ._phonenumber._generated.models import (
    AcquiredPhoneNumber,
    AcquiredPhoneNumbers,
    AcquiredPhoneNumberUpdate,
    PhoneNumberAssignmentType,
    CommunicationError,
    CommunicationErrorResponse,
    OperationKind,
    PhoneNumberAssignmentType,
    PhoneNumberCapabilitiesRequest,
    PhoneNumberCapabilityValue,
    PhoneNumberCost,
    PhoneNumberOperation,
    PhoneNumberOperationStatusCodes,
    PhoneNumberPurchaseRequest,
    PhoneNumberSearchRequest,
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
    'ReservePhoneNumberPolling',
    'PurchaseReservationPolling',
    'ReleasePhoneNumberPolling',

    # from _identity
    'CommunicationTokenRequest',
    'CommunicationIdentityToken',

    # from _phonenumber
    'AcquiredPhoneNumber',
    'AcquiredPhoneNumbers',
    'AcquiredPhoneNumberUpdate',
    'PhoneNumberAssignmentType',
    'CommunicationError',
    'CommunicationErrorResponse',
    'OperationKind',
    'PhoneNumberAssignmentType',
    'PhoneNumberCapabilitiesRequest',
    'PhoneNumberCapabilityValue',
    'PhoneNumberCost',
    'PhoneNumberOperation',
    'PhoneNumberOperationStatusCodes',
    'PhoneNumberPurchaseRequest',
    'PhoneNumberSearchRequest',
    'PhoneNumberSearchResult',
    'PhoneNumberType',

    # from _shared
    'CommunicationUser',
    'PhoneNumber',
    'UnknownIdentifier'
]
