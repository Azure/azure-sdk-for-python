# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum
from six import with_metaclass
from typing import Mapping, Optional, Union, Dict, Any
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

from .._generated.models import (
    CommunicationIdentifierModel,
    PhoneNumberIdentifierModel
)
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
    :paramtype cloud: str or ~azure.communication.callautomation.CommunicationCloudEnvironment
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
            value = raw_id[len('4:'):]
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

def serialize_identifier(identifier):
    # type: (CommunicationIdentifier) -> Dict[str, Any]
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: Identifier object
    :type identifier: CommunicationIdentifier
    :return: CommunicationIdentifierModel
    """
    try:
        request_model = {'raw_id': identifier.raw_id}

        if identifier.kind and identifier.kind != CommunicationIdentifierKind.UNKNOWN:
            request_model[identifier.kind] = dict(identifier.properties)
        return request_model
    except AttributeError:
        raise TypeError("Unsupported identifier type " +
                        identifier.__class__.__name__)

def serialize_phone_identifier(identifier):
    # type: (PhoneNumberIdentifier) -> PhoneNumberIdentifierModel
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: PhoneNumberIdentifier
    :type identifier: PhoneNumberIdentifier
    :return: PhoneNumberIdentifierModel
    """
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.PHONE_NUMBER:
            request_model = PhoneNumberIdentifierModel(
                value=identifier.properties['value'])
            return request_model
        else:
            raise AttributeError
    except AttributeError:
        raise TypeError("Unsupported identifier type " +
                        identifier.__class__.__name__)

def deserialize_identifier(identifier_model):
    # type: (CommunicationIdentifierModel) -> CommunicationIdentifier
    """
    Deserialize the CommunicationIdentifierModel into Communication Identifier

    :param identifier_model: CommunicationIdentifierModel
    :type identifier_model: CommunicationIdentifierModel
    :return: CommunicationIdentifier
    """
    raw_id = identifier_model.raw_id

    if identifier_model.communication_user:
        return CommunicationUserIdentifier(raw_id, raw_id=raw_id)
    if identifier_model.phone_number:
        return PhoneNumberIdentifier(identifier_model.phone_number.value, raw_id=raw_id)
    if identifier_model.microsoft_teams_user:
        return MicrosoftTeamsUserIdentifier(
            raw_id=raw_id,
            user_id=identifier_model.microsoft_teams_user.user_id,
            is_anonymous=identifier_model.microsoft_teams_user.is_anonymous,
            cloud=identifier_model.microsoft_teams_user.cloud
        )
    return UnknownIdentifier(raw_id)

def deserialize_phone_identifier(identifier_model) -> Union[PhoneNumberIdentifier, None]:
    """
    Deserialize the PhoneNumberIdentifierModel into PhoneNumberIdentifier

    :param identifier_model: PhoneNumberIdentifierModel
    :type identifier_model: PhoneNumberIdentifierModel
    :return: PhoneNumberIdentifier
    """
    if identifier_model:
        return PhoneNumberIdentifier(identifier_model.value)
    else:
        return None
