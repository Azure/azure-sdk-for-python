# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum, EnumMeta
from six import with_metaclass

import msrest

class CommunicationUserIdentifier(object):
    """
    Represents a user in Azure Communication Service.
    :ivar identifier: Communication user identifier.
    :vartype identifier: str
    :param identifier: Identifier to initialize CommunicationUserIdentifier.
    :type identifier: str
    """
    def __init__(self, identifier):
        self.identifier = identifier

class PhoneNumberIdentifier(object):
    """
    Represents a phone number.
    :param phone_number: The phone number in E.164 format.
    :type phone_number: str
    :param identifier: The full id of the phone number.
    :type identifier: str
    """
    def __init__(self, phone_number, identifier=None):
        self.phone_number = phone_number
        self.identifier = identifier

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
    def __init__(self, identifier):
        self.raw_id = identifier

class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(cls, name):
        return super().__getitem__(name.upper())

    def __getattr__(cls, name):
        """Return the enum member matching `name`
        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        try:
            return cls._member_map_[name.upper()]
        except KeyError:
            raise AttributeError(name)

class CommunicationIdentifierKind(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Communication Identifier Kind.
    """
    Unknown = "UNKNOWN"
    CommunicationUser = "COMMUNICATIONUSER"
    PhoneNumber = "PHONENUMBER"
    CallingApplication = "CALLINGAPPLICATION"
    MicrosoftTeamsUser = "MICROSOFTTEAMSUSER"

class CommunicationCloudEnvironment(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """
    The cloud enviornment that the identifier belongs to
    """
    
    Public = "PUBLIC"
    Dod = "DOD"
    Gcch = "GCCH"

class MicrosoftTeamsUserIdentifier(object):
    """
    Represents an identifier for a Microsoft Teams user.
    :ivar user_id: The id of the Microsoft Teams user. If the user isn't anonymous, the id is the AAD object id of the user.
    :vartype user_id: str
    :param user_id: Value to initialize MicrosoftTeamsUserIdentifier.
    :type user_id: str
    :ivar identifier: The full id of the Microsoft Teams User identifier.
    :vartype identifier: str
    :ivar cloud: Cloud environment that this identifier belongs to
    :vartype cloud: CommunicationCloudEnvironment
    :ivar is_anonymous: set this to true if the user is anonymous for example when joining a meeting with a share link
    :vartype is_anonymous: bool
    :param is_anonymous: Value to initialize MicrosoftTeamsUserIdentifier.
    :type is_anonymous: bool
    """
    def __init__(self, user_id, identifier=None, cloud=CommunicationCloudEnvironment.Public, is_anonymous=False):
        self.identifier = identifier
        self.user_id = user_id
        self.is_anonymous = is_anonymous
        self.cloud = cloud