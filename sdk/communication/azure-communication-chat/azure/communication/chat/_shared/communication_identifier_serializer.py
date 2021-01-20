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
    def serialize(self, communicationIdentifier):
        """ Serialize the Communication identifier into CommunicationIdentifierModel

        :param identifier: Communication service identifier
        :type identifier: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :return: CommunicationIdentifierModel
        :rtype: ~azure.communication.chat.CommunicationIdentifierModel
        """ 
        if isinstance(communicationIdentifier, CommunicationUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.CommunicationUserValue,
                id=communicationIdentifier.identififier
            )
        elif isinstance(communicationIdentifier, PhoneNumberIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.PhoneNumberValue,
                id=communicationIdentifier.value
            )
        elif isinstance(communicationIdentifier, MicrosoftTeamsUserIdentifier):
            return CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.MicrosoftTeamsUserValue,
                id=communicationIdentifier.user_id
            )
        
        return CommunicationIdentifierModel(
            kind=CommunicationIdentifierKind.UnknownValue,
            id=communicationIdentifier.identifier
        )