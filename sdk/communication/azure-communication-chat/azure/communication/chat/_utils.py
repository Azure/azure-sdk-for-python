# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def _to_utc_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def return_response(response, deserialized, _):  # pylint: disable=unused-argument
    return response, deserialized


class CommunicationErrorResponseConverter(object):
    """
    Util to convert to List[Tuple[ChatParticipant, Optional[AddChatParticipantsErrors]]

    This is a one-way converter for converting the follwing:
     - AddChatParticipantsResult -> List[Tuple[ChatParticipant, AddChatParticipantsErrors]
     - CreateChatThreadResult -> List[Tuple[ChatParticipant, AddChatParticipantsErrors]
    """

    @classmethod
    def convert(cls, participants, chat_errors):
        # type: (...) -> list[(ChatThreadParticipant, ChatError)]
        """
        Util function to convert AddChatParticipantsResult.

        Function used to consolidate List[ChatParticipant] and List[ChatError]
        into a list of tuples of ChatParticipant -> ChatError. In case of no error, empty
        list is returned

        :param participants: Request object for adding participants to thread
        :type: participants: list(~azure.communication.chat.ChatParticipant)
        :param chat_errors: list of ChatError
        :type chat_errors: list[~azure.communication.chat.ChatError]
        :return: A list of (ChatParticipant, ChatError)
        :rtype: list[(~azure.communication.chat.ChatParticipant, ~azure.communication.chat.ChatError)]
        """

        def create_dict(participants):
            # type: (...) -> Dict(str, ChatThreadParticipant)
            """
            Create dictionary of id -> ChatParticipant

            :param list participants: list of ChatThreadParticipant
            :return: Dictionary of id -> ChatThreadParticipant
            :rtype: dict
            """
            result = {}
            for participant in participants:
                result[participant.identifier.properties["id"]] = participant
            return result

        _thread_participants_dict = create_dict(participants=participants)

        failed_chat_thread_participants = []

        if chat_errors is not None:
            for chat_error in chat_errors:
                _thread_participant = _thread_participants_dict.get(chat_error.target)
                failed_chat_thread_participants.append((_thread_participant, chat_error))

        return failed_chat_thread_participants
