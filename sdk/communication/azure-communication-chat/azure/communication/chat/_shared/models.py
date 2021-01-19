# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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
    :ivar value: Value for a phone number.
    :vartype value: str
    :param value: Value to initialize PhoneNumberIdentifier.
    :type value: str
    """
    def __init__(self, value):
        self.value = value

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

class MicrosoftTeamsUserIdentifier(object):
    """
    Represents an identifier for a Microsoft Teams user.
    :ivar user_id: the string identifier representing the identity
    :vartype user_id: str
    :param user_id: Value to initialize MicrosoftTeamsUserIdentifier.
    :type user_id: str
    :ivar is_anonymous: set this to true if the user is anonymous for example when joining a meeting with a share link
    :vartype is_anonymous: bool
    :param is_anonymous: Value to initialize MicrosoftTeamsUserIdentifier.
    :type is_anonymous: bool
    """
    def __init__(self, user_id, is_anonymous=False):
        self.user_id = user_id
        self.is_anonymous = is_anonymous

class CommunicationIdentifierModel(msrest.serialization.Model):
    """Test.

    All required parameters must be populated in order to send to Azure.

    :param kind: Required. Test.
    :type kind: str
    :param id: Test.
    :type id: str
    :param phone_number: Test.
    :type phone_number: str
    :param is_anonymous: Test.
    :type is_anonymous: bool
    :param microsoft_teams_user_id: Test.
    :type microsoft_teams_user_id: str
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

