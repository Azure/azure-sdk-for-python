# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from azure.ai.ml._restclient.v2022_01_01_preview.models import Identity as RestIdentity
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal
from azure.ai.ml.entities._mixins import RestTranslatableMixin

from ._user_assigned_identity import UserAssignedIdentity


class IdentityConfiguration(RestTranslatableMixin):
    """Managed identity specification."""

    def __init__(
        self,
        *,
        type: str, # pylint: disable=redefined-builtin
        user_assigned_identities: List[UserAssignedIdentity] = None
    ):
        """Managed identity specification.

        :param type: Managed identity type, defaults to None
        :type type: str, optional
        :param user_assigned_identities: List of UserAssignedIdentity objects.
        :type user_assigned_identities: list, optional
        """

        self.type = type
        self.user_assigned_identities = user_assigned_identities
        self.principal_id = None
        self.tenant_id = None

    def _to_rest_object(self) -> RestIdentity:
        rest_user_assigned_identities = (
            # pylint: disable=protected-access
            {uai.resource_id: uai._to_rest_object() for uai in self.user_assigned_identities}
            if self.user_assigned_identities
            else None
        )
        return RestIdentity(type=snake_to_pascal(self.type), user_assigned_identities=rest_user_assigned_identities)

    @classmethod
    def _from_rest_object(cls, obj: RestIdentity) -> "IdentityConfiguration":
        from_rest_user_assigned_identities = (
            [
                # pylint: disable=protected-access
                UserAssignedIdentity._from_rest_object(uai, resource_id=resource_id)
                for (resource_id, uai) in obj.user_assigned_identities.items()
            ]
            if obj.user_assigned_identities
            else None
        )
        result = cls(
            type=camel_to_snake(obj.type),
            user_assigned_identities=from_rest_user_assigned_identities,
        )
        result.principal_id = obj.principal_id
        result.tenant_id = obj.tenant_id
        return result
