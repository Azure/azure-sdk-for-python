# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict, Any, TYPE_CHECKING

from ._models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    UnknownIdentifier,
    CommunicationIdentifierKind
)

if TYPE_CHECKING:
    from ._generated.models import CommunicationIdentifierModel


def serialize_identifier(identifier):
    # type: (CommunicationIdentifier) -> Dict[str, Any]
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: Identifier object
    :type identifier: CommunicationIdentifier
    :return: CommunicationIdentifierModel
    """
    try:
        request_model = {'raw_id': identifier.raw_id}

        if identifier.kind and identifier.kind != CommunicationIdentifierKind.UNKNOWN:
            request_model[identifier.kind] = dict(identifier.properties)
        return request_model
    except AttributeError:
        raise TypeError("Unsupported identifier type " + identifier.__class__.__name__)


def deserialize_identifier(identifier_model):
    # type: (CommunicationIdentifierModel) -> CommunicationIdentifier
    """
    Deserialize the CommunicationIdentifierModel into Communication Identifier

    :param identifier_model: CommunicationIdentifierModel
    :type identifier_model: CommunicationIdentifierModel
    :return: CommunicationIdentifier
    """
    raw_id = identifier_model.raw_id

    if identifier_model.communication_user:
        return CommunicationUserIdentifier(raw_id, raw_id=raw_id)
    if identifier_model.phone_number:
        return PhoneNumberIdentifier(identifier_model.phone_number.value, raw_id=raw_id)
    if identifier_model.microsoft_teams_user:
        return MicrosoftTeamsUserIdentifier(
            raw_id=raw_id,
            user_id=identifier_model.microsoft_teams_user.user_id,
            is_anonymous=identifier_model.microsoft_teams_user.is_anonymous,
            cloud=identifier_model.microsoft_teams_user.cloud
        )
    return UnknownIdentifier(raw_id)