# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum, EnumMeta
from six import with_metaclass
from typing import Mapping, Optional, Union
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


from azure.core import CaseInsensitiveEnumMeta


class CommunicationIdentifierKind(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Communication Identifier Kind.
    """
    UNKOWN = "unknown"
    COMMUNICATION_USER = "communication_user"
    PHONE_NUMBER = "phone_number"
    MICROSOFT_TEAMS_USER = "microsoft_teams_user"


class CommunicationCloudEnvironment(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """
    The cloud enviornment that the identifier belongs to
    """

    Public = "PUBLIC"
    Dod = "DOD"
    Gcch = "GCCH"


class CommunicationIdentifier(Protocol):
    """
    Communication Identifier.

    :ivar str id: The ID
    :ivar kind: The type of identifier.
    :ivar Mapping properties: The properties of the 
    """
    id = None  # type: Optional[str]
    kind = None  # type: Optional[Union[CommunicationIdentifierKind, str]]
    properties = {}  # type: Mapping[str, str]


class CommunicationUserIdentifier(object):
    """
    Represents a user in Azure Communication Service.

    :ivar identifier: Communication user identifier.
    :vartype identifier: str
    :param identifier: Identifier to initialize CommunicationUserIdentifier.
    :type identifier: str
    """
    kind = CommunicationIdentifierKind.COMMUNICATION_USER

    def __init__(self, identifier):
        self.id = identifier
        self.properties = {'identifier', identifier}


class PhoneNumberIdentifier(object):
    """
    Represents a phone number.
    :param phone_number: The phone number in E.164 format.
    :type phone_number: str
    :param raw_id: The full id of the phone number.
    :type raw_id: str
    """
    kind = CommunicationIdentifierKind.PHONE_NUMBER

    def __init__(self, phone_number, **kwargs):
        self.id = kwargs.get('identifier')
        self.properties = {'phone_number', phone_number}


class UnknownIdentifier(object):
    """
    Represents an identifier of an unknown type.
    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.
    :ivar raw_id: Unknown communication identifier.
    :vartype raw_id: str
    :param identifier: Value to initialize UnknownIdentifier.
    :type identifier: str
    """
    kind = CommunicationIdentifierKind.UNKOWN

    def __init__(self, identifier, **kwargs):
        self.id = identifier
        self.properties = kwargs.get('properties') or {}


class MicrosoftTeamsUserIdentifier(object):
    """
    Represents an identifier for a Microsoft Teams user.
    :ivar user_id: The id of the Microsoft Teams user. If the user isn't anonymous, the id is the AAD object id of the user.
    :vartype user_id: str
    :param user_id: Value to initialize MicrosoftTeamsUserIdentifier.
    :type user_id: str
    :ivar raw_id: Raw id of the Microsoft Teams user.
    :vartype raw_id: str
    :ivar cloud: Cloud environment that this identifier belongs to
    :vartype cloud: CommunicationCloudEnvironment
    :ivar is_anonymous: set this to true if the user is anonymous for example when joining a meeting with a share link
    :vartype is_anonymous: bool
    :param is_anonymous: Value to initialize MicrosoftTeamsUserIdentifier.
    :type is_anonymous: bool
    """
    kind = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER

    def __init__(self, user_id, **kwargs):
        self.id = kwargs.get('identifier')
        self.properties = {
            'user_id': user_id,
            'is_anonymous': kwargs.get('is_anonymous', False),
            'cloud': kwargs.get('cloud') or CommunicationCloudEnvironment.Public
        }
