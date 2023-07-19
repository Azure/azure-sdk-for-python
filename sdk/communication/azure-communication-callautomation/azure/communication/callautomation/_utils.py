# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict, Any, Union
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    UnknownIdentifier,
    CommunicationIdentifierKind
)
from ._generated.models import (
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    PhoneNumberIdentifierModel
)

def serialize_identifier(
        identifier:CommunicationIdentifier
        ) -> Dict[str, Any]:
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: Identifier object
    :type identifier: CommunicationIdentifier
    :return: CommunicationIdentifierModel
    :rtype: dict[str, any]
    """
    try:
        request_model = {'raw_id': identifier.raw_id}

        if identifier.kind and identifier.kind != CommunicationIdentifierKind.UNKNOWN:
            request_model[identifier.kind] = dict(identifier.properties)
        return request_model
    except AttributeError:
        raise TypeError("Unsupported identifier type " + # pylint: disable=raise-missing-from
                        identifier.__class__.__name__)

def serialize_phone_identifier(
        identifier:PhoneNumberIdentifier
        ) -> PhoneNumberIdentifierModel:
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: PhoneNumberIdentifier
    :type identifier: PhoneNumberIdentifier
    :return: PhoneNumberIdentifierModel
    :rtype: ~azure.communication.callautomation._generated.models.PhoneNumberIdentifierModel
    """
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.PHONE_NUMBER:
            request_model = PhoneNumberIdentifierModel(value=identifier.properties['value'])
            return request_model
        raise AttributeError
    except AttributeError:
        raise TypeError("Unsupported identifier type " + # pylint: disable=raise-missing-from
                        identifier.__class__.__name__)

def serialize_communication_user_identifier(
        identifier:CommunicationUserIdentifier
        ) -> CommunicationUserIdentifierModel:
    """Serialize the CommunicationUserIdentifier into CommunicationUserIdentifierModel

    :param identifier: CommunicationUserIdentifier
    :type identifier: CommunicationUserIdentifier
    :return: CommunicationUserIdentifierModel
    :rtype: ~azure.communication.callautomation._generated.models.CommunicationUserIdentifierModel
    """
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.COMMUNICATION_USER:
            request_model = CommunicationUserIdentifierModel(id=identifier.properties['id'])
            return request_model
        raise AttributeError
    except AttributeError:
        raise TypeError("Unsupported identifier type " + # pylint: disable=raise-missing-from
                        identifier.__class__.__name__)

def deserialize_identifier(
        identifier_model:CommunicationIdentifierModel
        )->CommunicationIdentifier:
    """
    Deserialize the CommunicationIdentifierModel into Communication Identifier

    :param identifier_model: CommunicationIdentifierModel
    :type identifier_model: CommunicationIdentifierModel
    :return: CommunicationIdentifier
    :rtype: ~azure.communication.callautomation.CommunicationIdentifier
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

def deserialize_phone_identifier(
        identifier_model:PhoneNumberIdentifierModel
        ) -> Union[PhoneNumberIdentifier, None]:
    """
    Deserialize the PhoneNumberIdentifierModel into PhoneNumberIdentifier

    :param identifier_model: PhoneNumberIdentifierModel
    :type identifier_model: PhoneNumberIdentifierModel
    :return: PhoneNumberIdentifier
    :rtype: ~azure.communication.callautomation.PhoneNumberIdentifier
    """
    if identifier_model:
        return PhoneNumberIdentifier(identifier_model.value)
    return None

def deserialize_comm_user_identifier(
        identifier_model:CommunicationUserIdentifierModel
        ) -> Union[CommunicationUserIdentifierModel, None]:
    """
    Deserialize the CommunicationUserIdentifierModel into CommunicationUserIdentifier

    :param identifier_model: CommunicationUserIdentifierModel
    :type identifier_model: CommunicationUserIdentifierModel
    :return: CommunicationUserIdentifier
    :rtype: ~azure.communication.callautomation.CommunicationUserIdentifier
    """
    return CommunicationUserIdentifierModel(id=identifier_model.id) if identifier_model else None
