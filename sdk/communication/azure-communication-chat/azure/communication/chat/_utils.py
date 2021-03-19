# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._communication_identifier_serializer import CommunicationUserIdentifierSerializer

def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')

def return_response(response, deserialized, _):  # pylint: disable=unused-argument
    return response, deserialized

class CommunicationUserIdentifierConverter(object):
    """
    utility class to interact with CommunicationUserIdentifierSerializer

    """
    @classmethod
    def to_identifier_model(cls, communicationIdentifier):
        """
        Util function to convert the Communication identifier into CommunicationIdentifierModel

        :param communicationIdentifier: Identifier object
        :type communicationIdentifier: Union[CommunicationUserIdentifier,
           PhoneNumberIdentifier, MicrosoftTeamsUserIdentifier, UnknownIdentifier]
        :return: CommunicationIdentifierModel
        :rtype: ~azure.communication.chat.CommunicationIdentifierModel
        :raises Union[TypeError, ValueError]
        """
        return CommunicationUserIdentifierSerializer.serialize(communicationIdentifier)

    @classmethod
    def from_identifier_model(cls, identifierModel):
        """
        Util function to convert the CommunicationIdentifierModel into Communication Identifier

        :param identifierModel: CommunicationIdentifierModel
        :type identifierModel: CommunicationIdentifierModel
        :return: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rtype: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rasies: ValueError
        """
        return CommunicationUserIdentifierSerializer.deserialize(identifierModel)

class CommunicationErrorResponseConverter(object):
    """
    Util to convert to List[Tuple[ChatThreadParticipant, Optional[AddChatParticipantsErrors]]

    This is a one-way converter for converting the follwing:
     - AddChatParticipantsResult -> List[Tuple[ChatThreadParticipant, AddChatParticipantsErrors]
     - CreateChatThreadResult -> List[Tuple[ChatThreadParticipant, AddChatParticipantsErrors]
    """

    @classmethod
    def _convert(cls, participants, chat_errors):
        # type: (...) -> list[(ChatThreadParticipant, ChatError)]
        """
        Util function to convert AddChatParticipantsResult.

        Function used to consolidate List[ChatThreadParticipant] and List[ChatError]
        into a list of tuples of ChatThreadParticipant -> ChatError. In case of no error, empty
        list is returned

        :param participants: Request object for adding participants to thread
        :type: participants: list(~azure.communication.chat.ChatThreadParticipant)
        :param chat_errors: list of ChatError
        :type chat_errors: list[~azure.communication.chat.ChatError]
        :return: A list of (ChatThreadParticipant, ChatError)
        :rtype: list[(~azure.communication.chat.ChatThreadParticipant, ~azure.communication.chat.ChatError)]
        """
        def create_dict(participants):
            # type: (...) -> Dict(str, ChatThreadParticipant)
            """
            Create dictionary of id -> ChatThreadParticipant
            """
            result = {}
            for participant in participants:
                result[participant.user.identifier] = participant
            return result

        _thread_participants_dict = create_dict(participants=participants)

        failed_chat_thread_participants = []

        if chat_errors is not None:
            for chat_error in chat_errors:
                _thread_participant = _thread_participants_dict.get(chat_error.target)
                failed_chat_thread_participants.append((_thread_participant, chat_error))

        return failed_chat_thread_participants
