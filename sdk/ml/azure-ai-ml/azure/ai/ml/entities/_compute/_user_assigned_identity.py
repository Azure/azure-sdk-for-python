# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2022_01_01_preview.models import UserAssignedIdentity as RestUserAssignedIdentity
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class UserAssignedIdentity(RestTranslatableMixin):
    """User Assigned identity specification."""

    def __init__(self, *, resource_id: Optional[str] = None):
        """User Assigned identity specification.

        :param resource_id: The resource ID of the user assigned identity.
        :type resource_id: str
        """
        self.resource_id = resource_id
        self.principal_id = None
        self.tenant_id = None
        self.client_id = None

    def _to_rest_object(self) -> RestUserAssignedIdentity:
        return RestUserAssignedIdentity()

    @classmethod
    def _from_rest_object(cls, obj: RestUserAssignedIdentity, **kwargs) -> "UserAssignedIdentity":
        result = cls(resource_id=kwargs["resource_id"])
        result.__dict__.update(obj.as_dict())
        return result
