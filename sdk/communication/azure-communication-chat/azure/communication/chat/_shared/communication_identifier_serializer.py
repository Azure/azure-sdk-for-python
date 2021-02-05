# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .models import (
    CommunicationIdentifierKind,
    CommunicationIdentifierModel,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    UnknownIdentifier
)

class CommunicationUserIdentifierSerializer(object):

    @classmethod
    def serialize(cls, communicationIdentifier):
        """ Serialize the Communication identifier into CommunicationIdentifierModel

        :param identifier: Identifier object
        :type identifier: Union[CommunicationUserIdentifier,
           PhoneNumberIdentifier, MicrosoftTeamsUserIdentifier, UnknownIdentifier]
        :return: CommunicationIdentifierModel
        :rtype: ~azure.communication.chat.CommunicationIdentifierModel
        :raises Union[TypeError, ValueError]
        """
        if isinstance(communicationIdentifier, CommunicationUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.CommunicationUser,
                id=communicationIdentifier.identifier
            )
        if isinstance(communicationIdentifier, PhoneNumberIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.PhoneNumber,
                id=communicationIdentifier.identifier,
                phone_number=communicationIdentifier.phone_number
            )
        if isinstance(communicationIdentifier, MicrosoftTeamsUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                id=communicationIdentifier.identifier,
                microsoft_teams_user_id=communicationIdentifier.user_id,
                communication_cloud_environment=communicationIdentifier.cloud
            )

        if isinstance(communicationIdentifier, UnknownIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.Unknown,
                id=communicationIdentifier.identifier
            )

        raise TypeError("Unsupported identifier type " + communicationIdentifier.__class__.__name__)

    @classmethod
    def deserialize(cls, identifierModel):
        """
        Deserialize the CommunicationIdentifierModel into Communication Identifier

        :param identifierModel: CommunicationIdentifierModel
        :type identifierModel: CommunicationIdentifierModel
        :return: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rtype: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rasies: ValueError
        """

        identifier, kind = identifierModel.id, identifierModel.kind
        if not identifier:
            raise ValueError("Identifier must have a valid id")

        if kind == CommunicationIdentifierKind.CommunicationUser:
            return CommunicationUserIdentifier(id)
        if kind == CommunicationIdentifierKind.PhoneNumber:
            if not identifierModel.phone_number:
                raise ValueError("PhoneNumberIdentifier must have a valid attribute - phone_number")
            return PhoneNumberIdentifier(identifierModel.phone_number, identifier=identifier)
        if kind == CommunicationIdentifierKind.MicrosoftTeamsUser:
            if identifierModel.is_anonymous not in [True, False]:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - is_anonymous")
            if not identifierModel.microsoft_teams_user_id:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - microsoft_teams_user_id")
            if not identifierModel.communication_cloud_environment:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - communication_cloud_environment")
            return MicrosoftTeamsUserIdentifier(
                identifierModel.microsoft_teams_user_id,
                identifier=identifier,
                is_anonymous=identifierModel.is_anonymous,
                cloud=identifierModel.communication_cloud_environment
            )

        return UnknownIdentifier(identifier)
