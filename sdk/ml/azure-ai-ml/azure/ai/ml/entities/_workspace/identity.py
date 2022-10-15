# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2022_05_01.models import UserAssignedIdentity as RestUserAssignedIdentity
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
        user_assigned_identities = None
        if self.user_assigned_identities:
            user_assigned_identities = {}
            for k, v in self.user_assigned_identities.items():
                user_assigned_identities[k] = v._to_rest_object() if v else None

        return RestManagedServiceIdentity(
            type=self.type,
            principal_id=self.principal_id,
            tenant_id=self.tenant_id,
            user_assigned_identities=user_assigned_identities,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestManagedServiceIdentity) -> "ManagedServiceIdentity":
        user_assigned_identities = None
        if obj.user_assigned_identities:
            user_assigned_identities = {}
            for k, v in obj.user_assigned_identities.items():
                metadata = None
                if v and isinstance(v, RestUserAssignedIdentity):
                    metadata = UserAssignedIdentity._from_rest_object(v)
                user_assigned_identities[k] = metadata
        return cls(
            type=obj.type,
            principal_id=obj.principal_id,
            tenant_id=obj.tenant_id,
            user_assigned_identities=user_assigned_identities,
        )


class UserAssignedIdentity:
    """User assigned identity properties."""

    def __init__(
        self,
        *,
        principal_id: str = None,
        client_id: str = None,
    ):
        self.principal_id = principal_id
        self.client_id = client_id

    def _to_rest_object(self) -> RestUserAssignedIdentity:
        return RestUserAssignedIdentity(
            principal_id=self.principal_id,
            client_id=self.client_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestUserAssignedIdentity) -> "UserAssignedIdentity":
        return cls(
            principal_id=obj.principal_id,
            client_id=obj.client_id,
        )
