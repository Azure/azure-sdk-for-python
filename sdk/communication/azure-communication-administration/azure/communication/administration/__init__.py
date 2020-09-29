# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._communication_identity_client import CommunicationIdentityClient

from ._identity._generated.models import (
    CommunicationTokenRequest,
    CommunicationIdentityToken
)

from ._shared.models import (
    CommunicationUser,
    PhoneNumber,
    UnknownIdentifier
)

__all__ = [
    'CommunicationIdentityClient',

    # from _identity
    'CommunicationTokenRequest',
    'CommunicationIdentityToken',

    # from _shared
    'CommunicationUser',
    'PhoneNumber',
    'UnknownIdentifier'
]
