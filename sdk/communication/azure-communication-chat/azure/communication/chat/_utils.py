# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .communication_identifier_serializer import CommunicationUserIdentifierSerializer

def _to_utc_datetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')

def return_response(response, deserialized, _):  # pylint: disable=unused-argument
    return response, deserialized

class CommunicationUserIdentifierConverter(object):
    """
    utility class to interact with CommunicationUserIdentifierSerializer

    """
    @classmethod
    def _to_identifier_model(cls, communicationIdentifier):
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
    def _from_identifier_model(cls, identifierModel):
        """
        Util function to convert the CommunicationIdentifierModel into Communication Identifier

        :param identifierModel: CommunicationIdentifierModel
        :type identifierModel: CommunicationIdentifierModel
        :return: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rtype: Union[CommunicationUserIdentifier, CommunicationPhoneNumberIdentifier]
        :rasies: ValueError
        """
        return CommunicationUserIdentifierSerializer.deserialize(identifierModel)