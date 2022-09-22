# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2022_10_01_preview.models import UserAssignedIdentity as RestUserAssignedIdentity
from azure.ai.ml.constants._workspace import ManagedServiceIdentityType


class ManagedServiceIdentity:
    """Managed service identity (system assigned and/or user assigned identities)."""

    def __init__(
        self,
        *,
        type: Union[str, "ManagedServiceIdentityType"],
        principal_id: str = None,
        tenant_id: str = None,
        user_assigned_identities: Optional[Dict[str, "UserAssignedIdentity"]] = None,
    ):
        self.type = type
        self.principal_id = principal_id
        self.tenant_id = tenant_id
        self.user_assigned_identities = user_assigned_identities

    def _to_rest_object(self) -> RestManagedServiceIdentity:
        return RestManagedServiceIdentity(
            type=self.type,
            principal_id=self.principal_id,
            tenant_id=self.tenant_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestManagedServiceIdentity) -> "ManagedServiceIdentity":
        return cls(
            type=obj.type,
            principal_id=obj.principal_id,
            tenant_id=obj.tenant_id,
        )
