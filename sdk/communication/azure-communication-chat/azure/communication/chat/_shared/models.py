# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum
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
    MICROSOFT_BOT = "microsoft_bot"


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


def _phone_number_raw_id(identifier: PhoneNumberIdentifier) -> str:
    value = identifier.properties['value']
    # We just assume correct E.164 format here because
    # validation should only happen server-side, not client-side.
    return f'4:{value}'


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


MicrosoftBotProperties = TypedDict(
    'MicrosoftBotProperties',
    bot_id=str,
    is_global=bool,
    cloud=Union[CommunicationCloudEnvironment, str]
)


class MicrosoftBotIdentifier(object):
    """Represents an identifier for a Microsoft bot.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `bot_id`(str): The id of the Microsoft bot.
        - `is_global` (bool): Set this to true if the bot is global.
        - `cloud` (str): Cloud environment that this identifier belongs to.

    :param str bot_id: Microsoft bot id.
    :keyword bool is_global: `True` if the identifier is global. Default value is `False`.
    :keyword cloud: Cloud environment that the bot belongs to. Default value is `PUBLIC`.
    :paramtype cloud: str or ~azure.communication.chat.CommunicationCloudEnvironment
    """
    kind = CommunicationIdentifierKind.MICROSOFT_BOT

    def __init__(self, bot_id, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id')
        self.properties = MicrosoftBotProperties(
            bot_id=bot_id,
            is_global=kwargs.get('is_global', False),
            cloud=kwargs.get('cloud') or CommunicationCloudEnvironment.PUBLIC
        )
        if self.raw_id is None:
            self.raw_id = _microsoft_bot_raw_id(self)


def _microsoft_bot_raw_id(identifier: MicrosoftBotIdentifier) -> str:
    bot_id = identifier.properties['bot_id']
    cloud = identifier.properties['cloud']
    if identifier.properties['is_global']:
        if cloud == CommunicationCloudEnvironment.DOD:
            return '28:dod-global:{}'.format(bot_id)
        elif cloud == CommunicationCloudEnvironment.GCCH:
            return '28:gcch-global:{}'.format(bot_id)
        return '28:{}'.format(bot_id)

    if cloud == CommunicationCloudEnvironment.DOD:
        return '28:dod:{}'.format(bot_id)
    elif cloud == CommunicationCloudEnvironment.GCCH:
        return '28:gcch:{}'.format(bot_id)
    return '28:orgid:{}'.format(bot_id)


def identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier:
    """
    Creates a CommunicationIdentifier from a given raw ID.

    When storing raw IDs use this function to restore the identifier that was encoded in the raw ID.

    :param str raw_id: A raw ID to construct the CommunicationIdentifier from.
    """
    if raw_id.startswith('4:'):
        return PhoneNumberIdentifier(
            value=raw_id[len('4:'):]
        )

    segments = raw_id.split(':', maxsplit=2)
    if len(segments) < 3:
        if len(segments) == 2 and segments[0] == '28':
            return MicrosoftBotIdentifier(
                bot_id=segments[1],
                is_global=True,
                cloud=CommunicationCloudEnvironment.PUBLIC
            )
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
            cloud=CommunicationCloudEnvironment.PUBLIC
        )
    elif prefix == '8:dod:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.DOD
        )
    elif prefix == '8:gcch:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.GCCH
        )
    elif prefix in ['8:acs:', '8:spool:', '8:dod-acs:', '8:gcch-acs:']:
        return CommunicationUserIdentifier(
            id=raw_id
        )
    elif prefix == '28:gcch-global:':
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_global=True,
            cloud=CommunicationCloudEnvironment.GCCH
        )
    elif prefix == '28:orgid:':
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_global=False,
            cloud=CommunicationCloudEnvironment.PUBLIC
        )
    elif prefix == '28:dod-global:':
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_global=True,
            cloud=CommunicationCloudEnvironment.DOD
        )
    elif prefix == '28:gcch:':
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_global=False,
            cloud=CommunicationCloudEnvironment.GCCH
        )
    elif prefix == '28:dod:':
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_global=False,
            cloud=CommunicationCloudEnvironment.DOD
        )
    return UnknownIdentifier(
        identifier=raw_id
    )
