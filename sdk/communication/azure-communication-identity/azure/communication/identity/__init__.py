# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._communication_identity_client import CommunicationIdentityClient

from ._generated.models import (
    CommunicationTokenScope
)

from ._shared.models import (
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationUserIdentifier,
    CommunicationUserProperties
)

__all__ = [
    'CommunicationIdentityClient',

    # from _identity
    'CommunicationTokenScope',

    # from _shared
    'CommunicationIdentifier',
    'CommunicationIdentifierKind',
    'CommunicationUserIdentifier',
    'CommunicationUserProperties'
]
