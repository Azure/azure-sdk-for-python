# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_01_01_preview.models import UserAssignedIdentity as RestUserAssignedIdentity
from typing import Optional


class UserAssignedIdentity(RestUserAssignedIdentity):
    """User Assigned identity specification"""

    def __init__(self, resource_id: Optional[str] = None, **kwargs):
        """User Assigned identity specification

        :param resource_id: The resource ID of the user assigned identity.
        :type resource_id: str
        :param principal_id: The principal ID of the user assigned identity.
        :type principal_id: str
        :param tenant_id: The tenant ID of the user assigned identity.
        :type tenant_id: str
        :param client_id: The clientId(aka appId) of the user assigned identity.
        :type client_id: str
        """
        self.resource_id = resource_id
        super().__init__(**kwargs)

    def _to_rest_object(self) -> RestUserAssignedIdentity:
        return RestUserAssignedIdentity(**self.__dict__)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestUserAssignedIdentity) -> "UserAssignedIdentity":
        result = cls()
        result.__dict__.update(rest_obj.as_dict())
        return result
