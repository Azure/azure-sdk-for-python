# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional
from azure.ai.ml._restclient.v2022_01_01_preview.models import Identity as RestIdentity
from ._user_assigned_identity import UserAssignedIdentity
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal


class IdentityConfiguration(RestIdentity):
    """Managed identity specification"""

    def __init__(self, **kwargs):
        """Managed identity specification

        :param type: Managed identity type, defaults to None
        :type type: str, optional
        :param user_assigned_identities: List of UserAssignedIdentity objects.
        :type user_assigned_identities: list, optional
        """

        super().__init__(**kwargs)

    @property
    def type(self) -> str:
        return camel_to_snake(self.__dict__["type"])

    @type.setter
    def type(self, value: str) -> None:
        self.__dict__["type"] = snake_to_pascal(value)

    @property
    def user_assigned_identities(self) -> Optional[List[UserAssignedIdentity]]:
        if self.__dict__.get("user_assigned_identities", None):
            uai_list = []
            uai_dict = self.__dict__["user_assigned_identities"]
            for resource_id, assigned_identity in uai_dict.items():
                if isinstance(assigned_identity, dict):
                    principal_id = assigned_identity.get("principal_id")
                    client_id = assigned_identity.get("client_id")
                    assigned_identity = UserAssignedIdentity(resource_id)
                    assigned_identity.client_id = client_id
                    assigned_identity.principal_id = principal_id
                uai_list.append(assigned_identity)
            return uai_list

    @user_assigned_identities.setter
    def user_assigned_identities(self, value: List[UserAssignedIdentity]) -> None:
        if value:
            uai_dict = {item.resource_id: item for item in value}
            self.__dict__["user_assigned_identities"] = uai_dict

    def _to_rest_object(self) -> RestIdentity:
        return RestIdentity(**self.__dict__)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestIdentity) -> "IdentityConfiguration":
        result = cls()
        result.__dict__.update(rest_obj.as_dict())
        return result
