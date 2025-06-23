# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
import warnings
from typing import Mapping, Optional, Union, Any, cast
from typing_extensions import Literal, TypedDict, Protocol, runtime_checkable, NotRequired

from azure.core import CaseInsensitiveEnumMeta


class DeprecatedEnumMeta(CaseInsensitiveEnumMeta):

    def __getattribute__(cls, item):
        if item.upper() == "MICROSOFT_BOT":
            warnings.warn(
                "MICROSOFT_BOT is deprecated and has been replaced by \
                          MICROSOFT_TEAMS_APP identifier.",
                DeprecationWarning,
            )
            item = "MICROSOFT_TEAMS_APP"
        return super().__getattribute__(item)


class CommunicationIdentifierKind(str, Enum, metaclass=DeprecatedEnumMeta):
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
    MICROSOFT_TEAMS_APP = "microsoft_teams_app"
    TEAMS_EXTENSION_USER = "teams_extension_user"


class CommunicationCloudEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The cloud environment that the identifier belongs to"""

    PUBLIC = "PUBLIC"
    DOD = "DOD"
    GCCH = "GCCH"


@runtime_checkable
class CommunicationIdentifier(Protocol):
    """Communication Identifier."""

    @property
    def raw_id(self) -> str:
        """The raw ID of the identifier."""
        ...

    @property
    def kind(self) -> CommunicationIdentifierKind:
        """The type of identifier."""
        ...

    @property
    def properties(self) -> Mapping[str, Any]:
        """The properties of the identifier."""
        ...


PHONE_NUMBER_PREFIX = "4:"
BOT_PREFIX = "28:"
BOT_PUBLIC_CLOUD_PREFIX = "28:orgid:"
BOT_DOD_CLOUD_PREFIX = "28:dod:"
BOT_DOD_CLOUD_GLOBAL_PREFIX = "28:dod-global:"
BOT_GCCH_CLOUD_PREFIX = "28:gcch:"
BOT_GCCH_CLOUD_GLOBAL_PREFIX = "28:gcch-global:"
TEAMS_APP_PUBLIC_CLOUD_PREFIX = "28:orgid:"
TEAMS_APP_DOD_CLOUD_PREFIX = "28:dod:"
TEAMS_APP_GCCH_CLOUD_PREFIX = "28:gcch:"
TEAMS_USER_ANONYMOUS_PREFIX = "8:teamsvisitor:"
TEAMS_USER_PUBLIC_CLOUD_PREFIX = "8:orgid:"
TEAMS_USER_DOD_CLOUD_PREFIX = "8:dod:"
TEAMS_USER_GCCH_CLOUD_PREFIX = "8:gcch:"
ACS_USER_PREFIX = "8:acs:"
ACS_USER_DOD_CLOUD_PREFIX = "8:dod-acs:"
ACS_USER_GCCH_CLOUD_PREFIX = "8:gcch-acs:"
SPOOL_USER_PREFIX = "8:spool:"

PHONE_NUMBER_ANONYMOUS_SUFFIX = "anonymous"


class CommunicationUserProperties(TypedDict):
    """Dictionary of properties for a CommunicationUserIdentifier."""

    id: str
    """ID of the Communication user as returned from Azure Communication Identity."""


class CommunicationUserIdentifier:
    """Represents a user in Azure Communication Service."""

    kind: Literal[CommunicationIdentifierKind.COMMUNICATION_USER] = CommunicationIdentifierKind.COMMUNICATION_USER
    """The type of identifier."""
    properties: CommunicationUserProperties
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(self, id: str, **kwargs: Any) -> None:
        """
        :param str id: ID of the Communication user as returned from Azure Communication Identity.
        :keyword str raw_id: The raw ID of the identifier. If not specified, the 'id' value will be used.
        """
        self.properties = CommunicationUserProperties(id=id)
        raw_id: Optional[str] = kwargs.get("raw_id")
        self.raw_id = raw_id if raw_id is not None else id

    def __eq__(self, other):
        try:
            if other.raw_id:
                return self.raw_id == other.raw_id
            return self.raw_id == other.properties["id"]
        except Exception:  # pylint: disable=broad-except
            return False


class PhoneNumberProperties(TypedDict):
    """Dictionary of properties for a PhoneNumberIdentifier."""

    value: str
    """The phone number in E.164 format."""
    asserted_id: NotRequired[str]
    """The asserted Id set on a phone number to distinguish from other connections made through the same number."""
    is_anonymous: NotRequired[bool]
    """True if the phone number is anonymous, e.g. when used to represent a hidden caller Id."""


class PhoneNumberIdentifier:
    """Represents a phone number."""

    kind: Literal[CommunicationIdentifierKind.PHONE_NUMBER] = CommunicationIdentifierKind.PHONE_NUMBER
    """The type of identifier."""
    properties: PhoneNumberProperties
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(self, value: str, **kwargs: Any) -> None:
        """
        :param str value: The phone number.
        :keyword str raw_id: The raw ID of the identifier. If not specified, this will be constructed from
          the 'value' parameter.
        """

        raw_id: Optional[str] = kwargs.get("raw_id")
        is_anonymous: bool

        if raw_id is not None:
            phone_number = raw_id[len(PHONE_NUMBER_PREFIX):]
            is_anonymous = phone_number == PHONE_NUMBER_ANONYMOUS_SUFFIX
            asserted_id_index = -1 if is_anonymous else phone_number.rfind("_") + 1
            has_asserted_id = 0 < asserted_id_index < len(phone_number)
            props = {"value": value, "is_anonymous": is_anonymous}
            if has_asserted_id:
                props["asserted_id"] = phone_number[asserted_id_index:]
            self.properties = PhoneNumberProperties(**props)  # type: ignore
        else:
            self.properties = PhoneNumberProperties(value=value)
        self.raw_id = raw_id if raw_id is not None else self._format_raw_id(self.properties)

    def __eq__(self, other):
        try:
            if other.raw_id:
                return self.raw_id == other.raw_id
            return self.raw_id == self._format_raw_id(other.properties)
        except Exception:  # pylint:disable=broad-except
            return False

    def _format_raw_id(self, properties: PhoneNumberProperties) -> str:
        # We just assume correct E.164 format here because
        # validation should only happen server-side, not client-side.
        value = properties["value"]
        return f"{PHONE_NUMBER_PREFIX}{value}"

class UnknownIdentifier:
    """Represents an identifier of an unknown type.

    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.

    For checking yet unknown identifiers it is better to rely on the presence of the `raw_id` property,
    as new or existing distinct type identifiers always contain the `raw_id` property.
    It is not advisable to rely on the `kind` property with a value `unknown`,
    as it could become a new or existing distinct type in the future.
    """

    kind: Literal[CommunicationIdentifierKind.UNKNOWN] = CommunicationIdentifierKind.UNKNOWN
    """The type of identifier."""
    properties: Mapping[str, Any]
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(self, identifier: str) -> None:
        """
        :param str identifier: The ID of the identifier.
        """
        self.raw_id = identifier
        self.properties = {}

    def __eq__(self, other):
        try:
            return self.raw_id == other.raw_id
        except AttributeError:
            return False


class MicrosoftTeamsUserProperties(TypedDict):
    """Dictionary of properties for a MicrosoftTeamsUserIdentifier."""

    user_id: str
    """The id of the Microsoft Teams user. If the user isn't anonymous, the id is the AAD object id of the user."""
    is_anonymous: bool
    """Set this to true if the user is anonymous for example when joining a meeting with a share link."""
    cloud: Union[CommunicationCloudEnvironment, str]
    """Cloud environment that this identifier belongs to."""


class MicrosoftTeamsUserIdentifier:
    """Represents an identifier for a Microsoft Teams user."""

    kind: Literal[CommunicationIdentifierKind.MICROSOFT_TEAMS_USER] = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    """The type of identifier."""
    properties: MicrosoftTeamsUserProperties
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(self, user_id: str, **kwargs: Any) -> None:
        """
        :param str user_id: Microsoft Teams user id.
        :keyword bool is_anonymous: `True` if the identifier is anonymous. Default value is `False`.
        :keyword cloud: Cloud environment that the user belongs to. Default value is `PUBLIC`.
        :paramtype cloud: str or ~azure.communication.phonenumbers.CommunicationCloudEnvironment
        :keyword str raw_id: The raw ID of the identifier. If not specified, this value will be constructed from
         the other properties.
        """
        self.properties = MicrosoftTeamsUserProperties(
            user_id=user_id,
            is_anonymous=kwargs.get("is_anonymous", False),
            cloud=kwargs.get("cloud") or CommunicationCloudEnvironment.PUBLIC,
        )
        raw_id: Optional[str] = kwargs.get("raw_id")
        self.raw_id = raw_id if raw_id is not None else self._format_raw_id(self.properties)

    def __eq__(self, other):
        try:
            if other.raw_id:
                return self.raw_id == other.raw_id
            return self.raw_id == self._format_raw_id(other.properties)
        except Exception:  # pylint: disable=broad-except
            return False

    def _format_raw_id(self, properties: MicrosoftTeamsUserProperties) -> str:
        user_id = properties["user_id"]
        if properties["is_anonymous"]:
            return f"{TEAMS_USER_ANONYMOUS_PREFIX}{user_id}"
        cloud = properties["cloud"]
        if cloud == CommunicationCloudEnvironment.DOD:
            return f"{TEAMS_USER_DOD_CLOUD_PREFIX}{user_id}"
        if cloud == CommunicationCloudEnvironment.GCCH:
            return f"{TEAMS_USER_GCCH_CLOUD_PREFIX}{user_id}"
        if cloud == CommunicationCloudEnvironment.PUBLIC:
            return f"{TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"
        return f"{TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"


class MicrosoftTeamsAppProperties(TypedDict):
    """Dictionary of properties for a MicrosoftTeamsAppIdentifier."""

    app_id: str
    """The id of the Microsoft Teams application."""
    cloud: Union[CommunicationCloudEnvironment, str]
    """Cloud environment that this identifier belongs to."""


class _botbackcompatdict(dict):
    """Backwards compatible properties."""

    def __getitem__(self, __key: Any) -> Any:
        try:
            return super().__getitem__(__key)
        except KeyError:
            if __key == "bot_id":
                return super().__getitem__("app_id")
            if __key == "is_resource_account_configured":
                return True
            raise


class MicrosoftTeamsAppIdentifier:
    """Represents an identifier for a Microsoft Teams application."""

    kind: Literal[CommunicationIdentifierKind.MICROSOFT_TEAMS_APP] = CommunicationIdentifierKind.MICROSOFT_TEAMS_APP
    """The type of identifier."""
    properties: MicrosoftTeamsAppProperties
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(self, app_id: str, **kwargs: Any) -> None:
        """
        :param str app_id: Microsoft Teams application id.
        :keyword cloud: Cloud environment that the application belongs to. Default value is `PUBLIC`.
        :paramtype cloud: str or ~azure.communication.phonenumbers.CommunicationCloudEnvironment
        :keyword str raw_id: The raw ID of the identifier. If not specified, this value will be constructed
         from the other properties.
        """
        self.properties = cast(
            MicrosoftTeamsAppProperties,
            _botbackcompatdict(
                app_id=app_id,
                cloud=kwargs.get("cloud") or CommunicationCloudEnvironment.PUBLIC,
            ),
        )
        raw_id: Optional[str] = kwargs.get("raw_id")
        self.raw_id = raw_id if raw_id is not None else self._format_raw_id(self.properties)

    def __eq__(self, other):
        try:
            if other.raw_id:
                return self.raw_id == other.raw_id
            return self.raw_id == self._format_raw_id(other.properties)
        except Exception:  # pylint: disable=broad-except
            return False

    def _format_raw_id(self, properties: MicrosoftTeamsAppProperties) -> str:
        app_id = properties["app_id"]
        cloud = properties["cloud"]
        if cloud == CommunicationCloudEnvironment.DOD:
            return f"{TEAMS_APP_DOD_CLOUD_PREFIX}{app_id}"
        if cloud == CommunicationCloudEnvironment.GCCH:
            return f"{TEAMS_APP_GCCH_CLOUD_PREFIX}{app_id}"
        return f"{TEAMS_APP_PUBLIC_CLOUD_PREFIX}{app_id}"


class _MicrosoftBotIdentifier(MicrosoftTeamsAppIdentifier):
    """Represents an identifier for a Microsoft bot.

    DEPRECATED. Only used in cases of backwards compatibility.
    """

    def __init__(self, bot_id, **kwargs):
        """
        :param str bot_id: Microsoft bot id.
        :keyword bool is_resource_account_configured: `False` if the identifier is global.
         Default value is `True` for tennantzed bots.
        :keyword cloud: Cloud environment that the bot belongs to. Default value is `PUBLIC`.
        :paramtype cloud: str or ~azure.communication.phonenumbers.CommunicationCloudEnvironment
        """
        warnings.warn(
            "The MicrosoftBotIdentifier is deprecated and has been replaced by MicrosoftTeamsAppIdentifier.",
            DeprecationWarning,
        )
        super().__init__(bot_id, **kwargs)


class TeamsExtensionUserProperties(TypedDict):
    """Dictionary of properties for a TeamsExtensionUserIdentifier."""

    user_id: str
    """The id of the Teams extension user."""
    tenant_id: str
    """The tenant id associated with the user."""
    resource_id: str
    """The Communication Services resource id."""
    cloud: Union[CommunicationCloudEnvironment, str]
    """Cloud environment that this identifier belongs to."""


class TeamsExtensionUserIdentifier:
    """Represents an identifier for a Teams Extension user."""

    kind: Literal[CommunicationIdentifierKind.TEAMS_EXTENSION_USER] = CommunicationIdentifierKind.TEAMS_EXTENSION_USER
    """The type of identifier."""
    properties: TeamsExtensionUserProperties
    """The properties of the identifier."""
    raw_id: str
    """The raw ID of the identifier."""

    def __init__(
        self,
        user_id: str,
        tenant_id: str,
        resource_id: str,
        **kwargs: Any
    ) -> None:
        """
        :param str user_id: Teams extension user id.
        :param str tenant_id: Tenant id associated with the user.
        :param str resource_id: The Communication Services resource id.
        :keyword cloud: Cloud environment that the user belongs to. Default value is `PUBLIC`.
        :paramtype cloud: str or ~azure.communication.phonenumbers.CommunicationCloudEnvironment
        :keyword str raw_id: The raw ID of the identifier.
         If not specified, this value will be constructed from the other properties.
        """
        self.properties = TeamsExtensionUserProperties(
            user_id=user_id,
            tenant_id=tenant_id,
            resource_id=resource_id,
            cloud=kwargs.get("cloud") or CommunicationCloudEnvironment.PUBLIC,
        )
        raw_id: Optional[str] = kwargs.get("raw_id")
        self.raw_id = raw_id if raw_id is not None else self._format_raw_id(self.properties)

    def __eq__(self, other):
        try:
            if other.raw_id:
                return self.raw_id == other.raw_id
            return self.raw_id == self._format_raw_id(other.properties)
        except Exception:  # pylint: disable=broad-except
            return False

    def _format_raw_id(self, properties: TeamsExtensionUserProperties) -> str:
        # The prefix depends on the cloud
        cloud = properties["cloud"]
        if cloud == CommunicationCloudEnvironment.DOD:
            prefix = ACS_USER_DOD_CLOUD_PREFIX
        elif cloud == CommunicationCloudEnvironment.GCCH:
            prefix = ACS_USER_GCCH_CLOUD_PREFIX
        else:
            prefix = ACS_USER_PREFIX
        return f"{prefix}{properties['resource_id']}_{properties['tenant_id']}_{properties['user_id']}"

def try_create_teams_extension_user(prefix: str, suffix: str) -> Optional[TeamsExtensionUserIdentifier]:
    segments = suffix.split("_")
    if len(segments) != 3:
        return None
    resource_id, tenant_id, user_id = segments
    if prefix == ACS_USER_PREFIX:
        cloud = CommunicationCloudEnvironment.PUBLIC
    elif prefix == ACS_USER_DOD_CLOUD_PREFIX:
        cloud = CommunicationCloudEnvironment.DOD
    elif prefix == ACS_USER_GCCH_CLOUD_PREFIX:
        cloud = CommunicationCloudEnvironment.GCCH
    else:
        raise ValueError("Invalid MRI")
    return TeamsExtensionUserIdentifier(user_id, tenant_id, resource_id, cloud=cloud)

def identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier:  # pylint: disable=too-many-return-statements
    """
    Creates a CommunicationIdentifier from a given raw ID.

    When storing raw IDs use this function to restore the identifier that was encoded in the raw ID.

    :param str raw_id: A raw ID to construct the CommunicationIdentifier from.
    :return: The CommunicationIdentifier parsed from the raw_id.
    :rtype: CommunicationIdentifier
    """
    if raw_id.startswith(PHONE_NUMBER_PREFIX):
        return PhoneNumberIdentifier(value=raw_id[len(PHONE_NUMBER_PREFIX) :], raw_id=raw_id)

    segments = raw_id.split(":", maxsplit=2)
    if len(segments) < 3:
        return UnknownIdentifier(identifier=raw_id)

    prefix = f"{segments[0]}:{segments[1]}:"
    suffix = segments[2]
    if prefix == TEAMS_USER_ANONYMOUS_PREFIX:
        return MicrosoftTeamsUserIdentifier(user_id=suffix, is_anonymous=True, raw_id=raw_id)
    if prefix == TEAMS_USER_PUBLIC_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.PUBLIC,
            raw_id=raw_id,
        )
    if prefix == TEAMS_USER_DOD_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.DOD,
            raw_id=raw_id,
        )
    if prefix == TEAMS_USER_GCCH_CLOUD_PREFIX:
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud=CommunicationCloudEnvironment.GCCH,
            raw_id=raw_id,
        )
    if prefix == TEAMS_APP_PUBLIC_CLOUD_PREFIX:
        return MicrosoftTeamsAppIdentifier(
            app_id=suffix,
            cloud=CommunicationCloudEnvironment.PUBLIC,
            raw_id=raw_id,
        )
    if prefix == TEAMS_APP_DOD_CLOUD_PREFIX:
        return MicrosoftTeamsAppIdentifier(
            app_id=suffix,
            cloud=CommunicationCloudEnvironment.DOD,
            raw_id=raw_id,
        )
    if prefix == TEAMS_APP_GCCH_CLOUD_PREFIX:
        return MicrosoftTeamsAppIdentifier(
            app_id=suffix,
            cloud=CommunicationCloudEnvironment.GCCH,
            raw_id=raw_id,
        )
    if prefix == SPOOL_USER_PREFIX:
        return CommunicationUserIdentifier(id=raw_id, raw_id=raw_id)

    if prefix in [
        ACS_USER_PREFIX,
        ACS_USER_DOD_CLOUD_PREFIX,
        ACS_USER_GCCH_CLOUD_PREFIX,
    ]:
        identifier = try_create_teams_extension_user(prefix, suffix)
        if identifier is not None:
            return identifier
        return CommunicationUserIdentifier(id=raw_id, raw_id=raw_id)
    return UnknownIdentifier(identifier=raw_id)
