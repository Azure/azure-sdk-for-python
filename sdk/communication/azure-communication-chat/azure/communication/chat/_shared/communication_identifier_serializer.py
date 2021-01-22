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

        :param identifier: Communication service identifier
        :type identifier: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :return: CommunicationIdentifierModel
        :rtype: ~azure.communication.chat.CommunicationIdentifierModel
        """
        if isinstance(communicationIdentifier, CommunicationUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.CommunicationUser,
                id=communicationIdentifier.identifier
            )
        if isinstance(communicationIdentifier, PhoneNumberIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.PhoneNumber,
                id=communicationIdentifier.phone_number
            )
        if isinstance(communicationIdentifier, MicrosoftTeamsUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                id=communicationIdentifier.user_id
            )

        return CommunicationIdentifierModel(
            kind=CommunicationIdentifierKind.Unknown,
            id=communicationIdentifier.identifier
        )

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

        if kind == CommunicationIdentifierKind.CommunicationUser:
            if not identifier:
                raise ValueError("CommunictionUser must have a valid id")
            return CommunicationUserIdentifier(id)
        if kind == CommunicationIdentifierKind.PhoneNumber:
            if not identifierModel.phone_number:
                raise ValueError("PhoneNumberIdentifier must have a valid attribute - phone_number")
            return PhoneNumberIdentifier(identifierModel.phone_number)
        if kind == CommunicationIdentifierKind.MicrosoftTeamsUser:
            if identifierModel.is_anonymous not in [True, False]:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - is_anonymous")
            if not identifierModel.microsoft_teams_user_id:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - microsoft_teams_user_id")
            return MicrosoftTeamsUserIdentifier(
                identifierModel.microsoft_teams_user_id,
                is_anonymous=identifierModel.is_anonymous
            )

        if not identifier:
            raise ValueError("UnknownIdentifier must have a valid id")

        return UnknownIdentifier(identifier)
