# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum, EnumMeta
import re
from six import with_metaclass
from typing import Mapping, Optional, Union, Any
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

from azure.core import CaseInsensitiveEnumMeta


class CommunicationIdentifierKind(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Communication Identifier Kind."""

    UNKNOWN = "unknown"
    COMMUNICATION_USER = "communication_user"
    PHONE_NUMBER = "phone_number"
    MICROSOFT_TEAMS_USER = "microsoft_teams_user"


class CommunicationCloudEnvironment(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The cloud environment that the identifier belongs to"""

    PUBLIC = "PUBLIC"
    DOD = "DOD"
    GCCH = "GCCH"


class CommunicationIdentifier(Protocol):
    """Communication Identifier.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
    """
    raw_id = None  # type: Optional[str]
    kind = None  # type: Optional[Union[CommunicationIdentifierKind, str]]
    properties = {}  # type: Mapping[str, Any]


CommunicationUserProperties = TypedDict(
    'CommunicationUserProperties',
    id=str
)


class CommunicationUserIdentifier(object):
    """Represents a user in Azure Communication Service.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
     The keys in this mapping include:
        - `id`(str): ID of the Communication user as returned from Azure Communication Identity.

    :param str id: ID of the Communication user as returned from Azure Communication Identity.
    """
    kind = CommunicationIdentifierKind.COMMUNICATION_USER

    def __init__(self, id, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id', id)
        self.properties = CommunicationUserProperties(id=id)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


PhoneNumberProperties = TypedDict(
    'PhoneNumberProperties',
    value=str
)


class PhoneNumberIdentifier(object):
    """Represents a phone number.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `value`(str): The phone number in E.164 format.

    :param str value: The phone number.
    """
    kind = CommunicationIdentifierKind.PHONE_NUMBER

    def __init__(self, value, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id')
        self.properties = PhoneNumberProperties(value=value)
        if self.raw_id is None:
            self.raw_id = _phone_number_raw_id(self)


_PHONE_NUMBER_PREFIX = re.compile(r'^\+')


def _phone_number_raw_id(identifier: PhoneNumberIdentifier) -> str:
    value = identifier.properties['value']
    # strip the leading +. We just assume correct E.164 format here because
    # validation should only happen server-side, not client-side.
    return '4:{}'.format(_PHONE_NUMBER_PREFIX.sub('', value))


class UnknownIdentifier(object):
    """Represents an identifier of an unknown type.

    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
    :param str identifier: The ID of the identifier.
    """
    kind = CommunicationIdentifierKind.UNKNOWN

    def __init__(self, identifier):
        # type: (str) -> None
        self.raw_id = identifier
        self.properties = {}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


MicrosoftTeamsUserProperties = TypedDict(
    'MicrosoftTeamsUserProperties',
    user_id=str,
    is_anonymous=bool,
    cloud=Union[CommunicationCloudEnvironment, str]
)


class MicrosoftTeamsUserIdentifier(object):
    """Represents an identifier for a Microsoft Teams user.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `user_id`(str): The id of the Microsoft Teams user. If the user isn't anonymous,
          the id is the AAD object id of the user.
        - `is_anonymous` (bool): Set this to true if the user is anonymous for example when joining
          a meeting with a share link.
        - `cloud` (str): Cloud environment that this identifier belongs to.

    :param str user_id: Microsoft Teams user id.
    :keyword bool is_anonymous: `True` if the identifier is anonymous. Default value is `False`.
    :keyword cloud: Cloud environment that the user belongs to. Default value is `PUBLIC`.
    :paramtype cloud: str or ~azure.communication.chat.CommunicationCloudEnvironment
    """
    kind = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER

    def __init__(self, user_id, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id')
        self.properties = MicrosoftTeamsUserProperties(
            user_id=user_id,
            is_anonymous=kwargs.get('is_anonymous', False),
            cloud=kwargs.get('cloud') or CommunicationCloudEnvironment.PUBLIC
        )
        if self.raw_id is None:
            self.raw_id = _microsoft_teams_user_raw_id(self)


def _microsoft_teams_user_raw_id(identifier: MicrosoftTeamsUserIdentifier) -> str:
    user_id = identifier.properties['user_id']
    if identifier.properties['is_anonymous']:
        return '8:teamsvisitor:{}'.format(user_id)
    cloud = identifier.properties['cloud']
    if cloud == CommunicationCloudEnvironment.DOD:
        return '8:dod:{}'.format(user_id)
    elif cloud == CommunicationCloudEnvironment.GCCH:
        return '8:gcch:{}'.format(user_id)
    elif cloud == CommunicationCloudEnvironment.PUBLIC:
        return '8:orgid:{}'.format(user_id)
    return '8:orgid:{}'.format(user_id)


def identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier:
    """
    Creates a CommunicationIdentifier from a given raw ID.

    When storing raw IDs use this function to restore the identifier that was encoded in the raw ID.

    :param str raw_id: A raw ID to construct the CommunicationIdentifier from.
    """
    if raw_id.startswith('4:'):
        return PhoneNumberIdentifier(
            value='+{}'.format(raw_id[len('4:'):])
        )

    segments = raw_id.split(':', maxsplit=2)
    if len(segments) < 3:
        return UnknownIdentifier(identifier=raw_id)

    prefix = '{}:{}:'.format(segments[0], segments[1])
    suffix = raw_id[len(prefix):]
    if prefix == '8:teamsvisitor:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=True
        )
    elif prefix == '8:orgid:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='PUBLIC'
        )
    elif prefix == '8:dod:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='DOD'
        )
    elif prefix == '8:gcch:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='GCCH'
        )
    elif prefix in ['8:acs:', '8:spool:', '8:dod-acs:', '8:gcch-acs:']:
        return CommunicationUserIdentifier(
            id=raw_id
        )
    return UnknownIdentifier(
        identifier=raw_id
    )
