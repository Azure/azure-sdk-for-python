# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._generated.models import (
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    PhoneNumberIdentifierModel,
    MicrosoftTeamsUserIdentifierModel
)
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    UnknownIdentifier,
    CommunicationIdentifierKind
)


def _assert_maximum_one_nested_model(identifier_model):
    models = [
        identifier_model.communication_user,
        identifier_model.phone_number,
        identifier_model.microsoft_teams_user
    ]
    present_properties = [p for p in models if p]
    if len(present_properties) > 1:
        raise ValueError("Only one of the properties in identifier model should be present.")


def serialize_identifier(identifier):
    # type: (CommunicationIdentifier) -> CommunicationIdentifierModel
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: Identifier object
    :type identifier: CommunicationIdentifier
    :return: CommunicationIdentifierModel
    """
    try:
        if identifier.kind == CommunicationIdentifierKind.COMMUNICATION_USER:
            return CommunicationIdentifierModel(
                raw_id=identifier.id,
                communication_user=CommunicationUserIdentifierModel(
                    id=identifier.properties['identifier']
                )
            )
        if identifier.kind == CommunicationIdentifierKind.PHONE_NUMBER:
            return CommunicationIdentifierModel(
                raw_id=identifier.id,
                phone_number=PhoneNumberIdentifierModel(
                    value=identifier.properties['phone_number'])
            )
        if identifier.kind == CommunicationIdentifierKind.MICROSOFT_TEAMS_USER:
            return CommunicationIdentifierModel(
                raw_id=identifier.id,
                microsoft_teams_user=MicrosoftTeamsUserIdentifierModel(
                    user_id=identifier.properties['user_id'],
                    is_anonymous=identifier.properties['is_anonymous'],
                    cloud=identifier.properties['cloud']
                )
            )
        return CommunicationIdentifierModel(
            raw_id=identifier.id
        )
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
    if not raw_id:
        raise ValueError("Identifier must have a valid id")

    _assert_maximum_one_nested_model(identifier_model)

    if identifier_model.communication_user:
        return CommunicationUserIdentifier(raw_id)
    if identifier_model.phone_number:
        if not identifier_model.phone_number:
            raise ValueError("PhoneNumberIdentifier must have a valid attribute - phone_number")
        return PhoneNumberIdentifier(identifier_model.phone_number.value, identifier=raw_id)
    if identifier_model.microsoft_teams_user is not None:
        if identifier_model.microsoft_teams_user.is_anonymous not in [True, False]:
            raise ValueError("MicrosoftTeamsUser must have a valid attribute - is_anonymous")
        if not identifier_model.microsoft_teams_user.user_id:
            raise ValueError("MicrosoftTeamsUser must have a valid attribute - user_id")
        if not identifier_model.microsoft_teams_user.cloud:
            raise ValueError("MicrosoftTeamsUser must have a valid attribute - cloud")
        return MicrosoftTeamsUserIdentifier(
            identifier=raw_id,
            user_id=identifier_model.microsoft_teams_user.user_id,
            is_anonymous=identifier_model.microsoft_teams_user.is_anonymous,
            cloud=identifier_model.microsoft_teams_user.cloud
        )
    return UnknownIdentifier(raw_id)
