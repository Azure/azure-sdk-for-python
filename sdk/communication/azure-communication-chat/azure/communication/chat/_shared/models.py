# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum, EnumMeta
from six import with_metaclass
from typing import Mapping, Optional, Union, Any
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

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

    :ivar str id: The identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
    """
    id = None  # type: Optional[str]
    kind = None  # type: Optional[Union[CommunicationIdentifierKind, str]]
    properties = {}  # type: Mapping[str, Any]


CommunicationUserProperties = TypedDict(
    'CommunicationUserProperties',
    identifier=str
)


class CommunicationUserIdentifier(object):
    """
    Represents a user in Azure Communication Service.

    :ivar str id: The identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
     The keys in this mapping include:
        - `identifier`(str): Identifier to initialize CommunicationUserIdentifier.

    """
    kind = CommunicationIdentifierKind.COMMUNICATION_USER

    def __init__(self, identifier):
        # type: (str) -> None
        self.id = identifier
        self.properties = CommunicationUserProperties(identifier)


PhoneNumberProperties = TypedDict(
    'CommunicationUserProperties',
    phone_number=str
)


class PhoneNumberIdentifier(object):
    """
    Represents a phone number.

    :ivar str id: The identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `phone_number`(str): The phone number in E.164 format.

    """
    kind = CommunicationIdentifierKind.PHONE_NUMBER

    def __init__(self, phone_number, **kwargs):
        # type: (str, Any) -> None
        self.id = kwargs.get('identifier')
        self.properties = PhoneNumberProperties(phone_number)


class UnknownIdentifier(object):
    """
    Represents an identifier of an unknown type.
    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.

    :ivar str id: The identifier
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
    """
    kind = CommunicationIdentifierKind.UNKOWN

    def __init__(self, identifier):
        # type: (str) -> None
        self.id = identifier
        self.properties = {}


MicrosoftTeamsUserProperties = TypedDict(
    'MicrosoftTeamsUserProperties',
    user_id=str,
    is_anonymous=bool,
    cloud=Union[CommunicationCloudEnvironment, str]
)


class MicrosoftTeamsUserIdentifier(object):
    """
    Represents an identifier for a Microsoft Teams user.

    :ivar str id: The identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `user_id`(str): The id of the Microsoft Teams user. If the user isn't anonymous,
          the id is the AAD object id of the user.
        - `is_anonymous` (bool): Set this to true if the user is anonymous for example when joining
          a meeting with a share link.
        - `cloud` (str): Cloud environment that this identifier belongs to.

    """
    kind = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER

    def __init__(self, user_id, **kwargs):
        # type: (str, Any) -> None
        self.id = kwargs.get('identifier')
        self.properties = MicrosoftTeamsUserProperties(
            user_id=user_id,
            is_anonymous=kwargs.get('is_anonymous', False),
            cloud=kwargs.get('cloud') or CommunicationCloudEnvironment.Public
        )
