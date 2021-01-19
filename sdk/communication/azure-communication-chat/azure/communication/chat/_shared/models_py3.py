from typing import List, Optional, Union
import msrest

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
        *,
        kind: str,
        id: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_anonymous: Optional[bool] = None,
        microsoft_teams_user_id: Optional[str] = None,
        **kwargs
    ):
        super(CommunicationIdentifierModel, self).__init__(**kwargs)
        self.kind = kind
        self.id = id
        self.phone_number = phone_number
        self.is_anonymous = is_anonymous
        self.microsoft_teams_user_id = microsoft_teams_user_id

