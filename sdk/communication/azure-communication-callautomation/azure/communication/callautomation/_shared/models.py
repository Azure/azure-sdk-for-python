# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from typing import Mapping, Optional, Union, Any

from typing_extensions import TypedDict, Protocol
from azure.core import CaseInsensitiveEnumMeta


class CommunicationIdentifierKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Communication Identifier Kind.

    For checking yet unknown identifiers it is better to rely on the presence of the `raw_id` property,
    as new or existing distinct type identifiers always contain the `raw_id` property.
    It is not advisable to rely on the `kind` property with a value `unknown`,
    as it could become a new or existing distinct type in the future.
    """

    UNKNOWN = "unknown"
    COMMUNICATION_USER = "communication_user"
    PHONE_NUMBER = "phone_number"
    MICROSOFT_TEAMS_USER = "microsoft_teams_user"
    MICROSOFT_BOT = "microsoft_bot"


class CommunicationCloudEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


CommunicationUserProperties = TypedDict("CommunicationUserProperties", {"id": str})

PHONE_NUMBER_PREFIX = "4:"
BOT_PREFIX = "28:"
BOT_PUBLIC_CLOUD_PREFIX = "28:orgid:"
BOT_DOD_CLOUD_PREFIX = "28:dod:"
BOT_DOD_CLOUD_GLOBAL_PREFIX = "28:dod-global:"
BOT_GCCH_CLOUD_PREFIX = "28:gcch:"
BOT_GCCH_CLOUD_GLOBAL_PREFIX = "28:gcch-global:"
TEAMS_USER_ANONYMOUS_PREFIX = "8:teamsvisitor:"
TEAMS_USER_PUBLIC_CLOUD_PREFIX = "8:orgid:"
TEAMS_USER_DOD_CLOUD_PREFIX = "8:dod:"
TEAMS_USER_GCCH_CLOUD_PREFIX = "8:gcch:"
ACS_USER_PREFIX = "8:acs:"
ACS_USER_DOD_CLOUD_PREFIX = "8:dod-acs:"
ACS_USER_GCCH_CLOUD_PREFIX = "8:gcch-acs:"
SPOOL_USER_PREFIX = "8:spool:"


class CommunicationUserIdentifier:
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

    def __init__(self, id: str, **kwargs: Any) -> None:
        self.raw_id = kwargs.get("raw_id", id)
        self.properties = CommunicationUserProperties(id=id)
        if self.raw_id is None:
            self.raw_id = _communication_user_raw_id(self)

    def __eq__(self, other):
        try:
            return self.raw_id == other.properties["id"]
        except Exception:  # pylint: disable=broad-except
            return False


def _communication_user_raw_id(identifier: CommunicationUserIdentifier) -> str:
    if identifier.raw_id:
        return str(identifier.raw_id)
    return str(identifier.properties["id"])


PhoneNumberProperties = TypedDict("PhoneNumberProperties", {"value": str})


class PhoneNumberIdentifier:
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

    def __init__(self, value: str, **kwargs: Any) -> None:
        self.raw_id = kwargs.get("raw_id")
        self.properties = PhoneNumberProperties(value=value)
        if self.raw_id is None:
            self.raw_id = _phone_number_raw_id(self)

    def __eq__(self, other):
        try:
            return self.raw_id == _phone_number_raw_id(other)
        except Exception:  # pylint: disable=broad-except
            return False


def _phone_number_raw_id(identifier: PhoneNumberIdentifier) -> str:
    if identifier.raw_id:
        return str(identifier.raw_id)
    value = identifier.properties["value"]
    # We just assume correct E.164 format here because
    # validation should only happen server-side, not client-side.
    return f"{PHONE_NUMBER_PREFIX}{value}"


class UnknownIdentifier:
    """Represents an identifier of an unknown type.

    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.

    For checking yet unknown identifiers it is better to rely on the presence of the `raw_id` property,
    as new or existing distinct type identifiers always contain the `raw_id` property.
    It is not advisable to rely on the `kind` property with a value `unknown`,
    as it could become a new or existing distinct type in the future.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
    :param str identifier: The ID of the identifier.
    """

    kind = CommunicationIdentifierKind.UNKNOWN

    def __init__(self, identifier: str) -> None:
        self.raw_id = identifier
        self.properties = {}  # type: Any

    def __eq__(self, other):
        try:
            return self.raw_id == other.raw_id
        except Exception:  # pylint: disable=broad-except
            return False


MicrosoftTeamsUserProperties = TypedDict(
    "MicrosoftTeamsUserProperties",
    {
        "user_id": str,
        "is_anonymous": bool,
        "cloud": Union[CommunicationCloudEnvironment, str],
    },
)


class MicrosoftTeamsUserIdentifier:
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

    def __init__(self, user_id: str, **kwargs: Any) -> None:
        self.raw_id = kwargs.get("raw_id")
        self.properties = MicrosoftTeamsUserProperties(
            user_id=user_id,
            is_anonymous=kwargs.get("is_anonymous", False),
            cloud=kwargs.get("cloud") or CommunicationCloudEnvironment.PUBLIC,
        )
        if self.raw_id is None:
            self.raw_id = _microsoft_teams_user_raw_id(self)

    def __eq__(self, other):
        try:
            return self.raw_id == _microsoft_teams_user_raw_id(other)
        except Exception:  # pylint: disable=broad-except
            return False


def _microsoft_teams_user_raw_id(identifier: MicrosoftTeamsUserIdentifier) -> str:
    if identifier.raw_id:
        return str(identifier.raw_id)
    user_id = identifier.properties["user_id"]
    if identifier.properties["is_anonymous"]:
        return f"{TEAMS_USER_ANONYMOUS_PREFIX}{user_id}"
    cloud = identifier.properties["cloud"]
    if cloud == CommunicationCloudEnvironment.DOD:
        return f"{TEAMS_USER_DOD_CLOUD_PREFIX}{user_id}"
    if cloud == CommunicationCloudEnvironment.GCCH:
        return f"{TEAMS_USER_GCCH_CLOUD_PREFIX}{user_id}"
    if cloud == CommunicationCloudEnvironment.PUBLIC:
        return f"{TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"
    return f"{TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"


MicrosoftBotProperties = TypedDict(
    "MicrosoftBotProperties",
    {
        "bot_id": str,
        "is_resource_account_configured": bool,
        "cloud": Union[CommunicationCloudEnvironment, str],
    },
)


class MicrosoftBotIdentifier:
    """Represents an identifier for a Microsoft bot.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar MicrosoftBotProperties: The properties of the identifier.
     The keys in this mapping include:
        - `bot_id`(str): The id of the Microsoft bot.
        - `is_resource_account_configured` (bool): Set this to false if the bot is global.
        The default is `true` for tennantized bots.
        - `cloud` (str): Cloud environment that this identifier belongs to.

    :param str bot_id: Microsoft bot id.
    :keyword bool is_resource_account_configured: `False` if the identifier is global.
    Default value is `True` for tennantzed bots.
    :keyword cloud: Cloud environment that the bot belongs to. Default value is `PUBLIC`.
    :paramtype cloud: str or ~azure.communication.chat.CommunicationCloudEnvironment
    """

    kind = CommunicationIdentifierKind.MICROSOFT_BOT

    def __init__(self, bot_id: str, **kwargs: Any) -> None:
        self.raw_id = kwargs.get("raw_id")
        self.properties = MicrosoftBotProperties(
            bot_id=bot_id,
            is_resource_account_configured=kwargs.get(
                "is_resource_account_configured", True
            ),
            cloud=kwargs.get("cloud") or CommunicationCloudEnvironment.PUBLIC,
        )
        if self.raw_id is None:
            self.raw_id = _microsoft_bot_raw_id(self)

    def __eq__(self, other):
        try:
            return self.raw_id == _microsoft_bot_raw_id(other)
        except Exception:  # pylint: disable=broad-except
            return False


def _microsoft_bot_raw_id(identifier: MicrosoftBotIdentifier) -> str:  # pylint: disable=too-many-return-statements
    if identifier.raw_id:
        return str(identifier.raw_id)
    bot_id = identifier.properties["bot_id"]
    cloud = identifier.properties["cloud"]
    if identifier.properties["is_resource_account_configured"] is False:
        if cloud == CommunicationCloudEnvironment.DOD:
            return f"{BOT_DOD_CLOUD_GLOBAL_PREFIX}{bot_id}"
        if cloud == CommunicationCloudEnvironment.GCCH:
            return f"{BOT_GCCH_CLOUD_GLOBAL_PREFIX}{bot_id}"
        return f"{BOT_PREFIX}{bot_id}"

    if cloud == CommunicationCloudEnvironment.DOD:
        return f"{BOT_DOD_CLOUD_PREFIX}{bot_id}"
    if cloud == CommunicationCloudEnvironment.GCCH:
        return f"{BOT_GCCH_CLOUD_PREFIX}{bot_id}"
    return f"{BOT_PUBLIC_CLOUD_PREFIX}{bot_id}"


def identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier:  # pylint: disable=too-many-return-statements
    """
    Creates a CommunicationIdentifier from a given raw ID.

    When storing raw IDs use this function to restore the identifier that was encoded in the raw ID.

    :param str raw_id: A raw ID to construct the CommunicationIdentifier from.
    :return: The CommunicationIdentifier parsed from the raw_id.
    :rtype: CommunicationIdentifier
    """
    if raw_id.startswith(PHONE_NUMBER_PREFIX):
        return PhoneNumberIdentifier(
            value=raw_id[len(PHONE_NUMBER_PREFIX) :], raw_id=raw_id
        )  # type: ignore

    segments = raw_id.split(":", maxsplit=2)
    if len(segments) != 3:
        if len(segments) == 2 and raw_id.startswith(BOT_PREFIX):
            return MicrosoftBotIdentifier(
                bot_id=segments[1],
                is_resource_account_configured=False,
                cloud=CommunicationCloudEnvironment.PUBLIC,
                raw_id=raw_id,
            )  # type: ignore
        return UnknownIdentifier(identifier=raw_id)  # type: ignore

    prefix = f"{segments[0]}:{segments[1]}:"
    suffix = segments[2]
    if prefix == TEAMS_USER_ANONYMOUS_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix, is_anonymous=True, raw_id=raw_id
        )  # type: ignore
    if prefix == TEAMS_USER_PUBLIC_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.PUBLIC,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == TEAMS_USER_DOD_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.DOD,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == TEAMS_USER_GCCH_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.GCCH,
            raw_id=raw_id,
        )  # type: ignore
    if prefix in [
        ACS_USER_PREFIX,
        ACS_USER_DOD_CLOUD_PREFIX,
        ACS_USER_GCCH_CLOUD_PREFIX,
        SPOOL_USER_PREFIX,
    ]:
        return CommunicationUserIdentifier(id=raw_id, raw_id=raw_id)  # type: ignore
    if prefix == BOT_GCCH_CLOUD_GLOBAL_PREFIX:
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.GCCH,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == BOT_PUBLIC_CLOUD_PREFIX:
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.PUBLIC,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == BOT_DOD_CLOUD_GLOBAL_PREFIX:
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.DOD,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == BOT_GCCH_CLOUD_PREFIX:
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.GCCH,
            raw_id=raw_id,
        )  # type: ignore
    if prefix == BOT_DOD_CLOUD_PREFIX:
        return MicrosoftBotIdentifier(
            bot_id=suffix,
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.DOD,
            raw_id=raw_id,
        )  # type: ignore
    return UnknownIdentifier(identifier=raw_id)  # type: ignore
