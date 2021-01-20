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
                id=communicationIdentifier.identififier
            )
        elif isinstance(communicationIdentifier, PhoneNumberIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.PhoneNumber,
                id=communicationIdentifier.value
            )
        elif isinstance(communicationIdentifier, MicrosoftTeamsUserIdentifier):
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

        id, kind = identifierModel.id, identifierModel.kind

        if not id:
            raise ValueError("identiferModel must have a valid id")

        if kind == CommunicationIdentifierKind.CommunicationUser:
            return CommunicationUserIdentifier(id)
        if kind == CommunicationIdentifierKind.PhoneNumber:
            return PhoneNumberIdentifier(id)
        if kind == CommunicationIdentifierKind.MicrosoftTeamsUser:
            is_anonymous = identifierModel.is_anonymous
            if not is_anonymous:
                raise ValueError("MicrosoftTeamsUser must have a valid attribute - is_anonymous")
            return MicrosoftTeamsUserIdentifier(
                id,
                is_anonymous=is_anonymous
            )
        
        return UnknownIdentifier(id)
