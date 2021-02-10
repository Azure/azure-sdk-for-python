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
    :ivar identifier: Unknown communication identifier.
    :vartype identifier: str
    :param identifier: Value to initialize UnknownIdentifier.
    :type identifier: str
    """
    def __init__(self, identifier):
        self.identifier = identifier

class CommunicationIdentifierModel(msrest.serialization.Model):
    """Identifies a participant in Azure Communication services. A participant is, for example, a phone number or an Azure communication user. This model must be interpreted as a union: Apart from rawId, at most one further property may be set.

    :param raw_id: Raw Id of the identifier. Optional in requests, required in responses.
    :type raw_id: str
    :param communication_user: The communication user.
    :type communication_user: ~communication.models.CommunicationUserIdentifierModel
    :param phone_number: The phone number.
    :type phone_number: ~communication.models.PhoneNumberIdentifierModel
    :param microsoft_teams_user: The Microsoft Teams user.
    :type microsoft_teams_user: ~communication.models.MicrosoftTeamsUserIdentifierModel
    """

    _attribute_map = {
        'raw_id': {'key': 'rawId', 'type': 'str'},
        'communication_user': {'key': 'communicationUser', 'type': 'CommunicationUserIdentifierModel'},
        'phone_number': {'key': 'phoneNumber', 'type': 'PhoneNumberIdentifierModel'},
        'microsoft_teams_user': {'key': 'microsoftTeamsUser', 'type': 'MicrosoftTeamsUserIdentifierModel'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CommunicationIdentifierModel, self).__init__(**kwargs)
        self.raw_id = kwargs.get('raw_id', None)
        self.communication_user = kwargs.get('communication_user', None)
        self.phone_number = kwargs.get('phone_number', None)
        self.microsoft_teams_user = kwargs.get('microsoft_teams_user', None)

class CommunicationUserIdentifierModel(msrest.serialization.Model):
    """A user that got created with an Azure Communication Services resource.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. The Id of the communication user.
    :type id: str
    """

    _validation = {
        'id': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CommunicationUserIdentifierModel, self).__init__(**kwargs)
        self.id = kwargs['id']


class MicrosoftTeamsUserIdentifierModel(msrest.serialization.Model):
    """A Microsoft Teams user.

    All required parameters must be populated in order to send to Azure.

    :param user_id: Required. The Id of the Microsoft Teams user. If not anonymous, this is the AAD
     object Id of the user.
    :type user_id: str
    :param is_anonymous: True if the Microsoft Teams user is anonymous. By default false if
     missing.
    :type is_anonymous: bool
    :param cloud: The cloud that the Microsoft Teams user belongs to. By default 'public' if
     missing. Possible values include: "public", "dod", "gcch".
    :type cloud: str or ~communication.models.CommunicationCloudEnvironmentModel
    """

    _validation = {
        'user_id': {'required': True},
    }

    _attribute_map = {
        'user_id': {'key': 'userId', 'type': 'str'},
        'is_anonymous': {'key': 'isAnonymous', 'type': 'bool'},
        'cloud': {'key': 'cloud', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(MicrosoftTeamsUserIdentifierModel, self).__init__(**kwargs)
        self.user_id = kwargs['user_id']
        self.is_anonymous = kwargs.get('is_anonymous', None)
        self.cloud = kwargs.get('cloud', None)


class PhoneNumberIdentifierModel(msrest.serialization.Model):
    """A phone number.

    All required parameters must be populated in order to send to Azure.

    :param value: Required. The phone number in E.164 format.
    :type value: str
    """

    _validation = {
        'value': {'required': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(PhoneNumberIdentifierModel, self).__init__(**kwargs)
        self.value = kwargs['value']

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

class CommunicationCloudEnvironmentModel(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The cloud that the identifier belongs to.
    """

    PUBLIC = "public"
    DOD = "dod"
    GCCH = "gcch"

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
    :ivar rawId: Raw id of the Microsoft Teams user.
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
