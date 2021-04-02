# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from enum import Enum, EnumMeta
from six import with_metaclass

import msrest

class CommunicationError(msrest.serialization.Model):
    """The Communication Services error.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param code: Required. The error code.
    :type code: str
    :param message: Required. The error message.
    :type message: str
    :ivar target: The error target.
    :vartype target: str
    :ivar details: Further details about specific errors that led to this error.
    :vartype details: list[~communication.models.CommunicationError]
    :ivar inner_error: The inner error if any.
    :vartype inner_error: ~communication.models.CommunicationError
    """

    _validation = {
        'code': {'required': True},
        'message': {'required': True},
        'target': {'readonly': True},
        'details': {'readonly': True},
        'inner_error': {'readonly': True},
    }

    _attribute_map = {
        'code': {'key': 'code', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
        'target': {'key': 'target', 'type': 'str'},
        'details': {'key': 'details', 'type': '[CommunicationError]'},
        'inner_error': {'key': 'innererror', 'type': 'CommunicationError'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CommunicationError, self).__init__(**kwargs)
        self.code = kwargs['code']
        self.message = kwargs['message']
        self.target = None
        self.details = None
        self.inner_error = None


class CommunicationErrorResponse(msrest.serialization.Model):
    """The Communication Services error.

    All required parameters must be populated in order to send to Azure.

    :param error: Required. The Communication Services error.
    :type error: ~communication.models.CommunicationError
    """

    _validation = {
        'error': {'required': True},
    }

    _attribute_map = {
        'error': {'key': 'error', 'type': 'CommunicationError'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CommunicationErrorResponse, self).__init__(**kwargs)
        self.error = kwargs['error']

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
    :param raw_id: The full id of the phone number.
    :type raw_id: str
    """
    def __init__(self, phone_number, raw_id=None):
        self.phone_number = phone_number
        self.raw_id = raw_id

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

class CommunicationIdentifierModel(msrest.serialization.Model):
    """Communication Identifier Model.
    All required parameters must be populated in order to send to Azure.
    :param kind: Required. Kind of Communication Identifier.
    :type kind: CommunicationIdentifierKind
    :param id: Full id of the identifier.
    :type id: str
    :param phone_number: phone number in case the identifier is a phone number.
    :type phone_number: str
    :param is_anonymous: True if the identifier is anonymous.
    :type is_anonymous: bool
    :param microsoft_teams_user_id: Microsoft Teams user id.
    :type microsoft_teams_user_id: str
    :param communication_cloud_environment: Cloud environment that the user belongs to.
    :type communication_cloud_environment: CommunicationCloudEnvironment
    """

    _validation = {
        'kind': {'required': True},
    }

    _attribute_map = {
        'kind': {'key': 'kind', 'type': 'str'},
        'id': {'key': 'id', 'type': 'str'},
        'phone_number': {'key': 'phoneNumber', 'type': 'str'},
        'is_anonymous': {'key': 'isAnonymous', 'type': 'bool'},
        'microsoft_teams_user_id': {'key': 'microsoftTeamsUserId', 'type': 'str'},
        'communication_cloud_environment': {'key': 'communicationCloudEnvironment', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CommunicationIdentifierModel, self).__init__(**kwargs)
        self.kind = kwargs['kind']
        self.id = kwargs.get('id', None)
        self.phone_number = kwargs.get('phone_number', None)
        self.is_anonymous = kwargs.get('is_anonymous', None)
        self.microsoft_teams_user_id = kwargs.get('microsoft_teams_user_id', None)
        self.communication_cloud_environment = kwargs.get('communication_cloud_environment', None)

class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name):
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
    :ivar raw_id: Raw id of the Microsoft Teams user.
    :vartype raw_id: str
    :ivar cloud: Cloud environment that this identifier belongs to
    :vartype cloud: CommunicationCloudEnvironment
    :ivar is_anonymous: set this to true if the user is anonymous for example when joining a meeting with a share link
    :vartype is_anonymous: bool
    :param is_anonymous: Value to initialize MicrosoftTeamsUserIdentifier.
    :type is_anonymous: bool
    """
    def __init__(self, user_id, raw_id=None, cloud=CommunicationCloudEnvironment.Public, is_anonymous=False):
        self.raw_id = raw_id
        self.user_id = user_id
        self.is_anonymous = is_anonymous
        self.cloud = cloud
