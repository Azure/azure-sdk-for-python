# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from typing import Dict, Optional, Union

import msrest.serialization
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta


class ManagedServiceIdentity(msrest.serialization.Model):
    """Managed service identity (system assigned and/or user assigned identities)."""

    _validation = {
        "principal_id": {"readonly": True},
        "tenant_id": {"readonly": True},
        "type": {"required": True},
    }

    _attribute_map = {
        "principal_id": {"key": "principalId", "type": "str"},
        "tenant_id": {"key": "tenantId", "type": "str"},
        "type": {"key": "type", "type": "str"},
        "user_assigned_identities": {"key": "userAssignedIdentities", "type": "{UserAssignedIdentity}"},
    }

    def __init__(
        self,
        *,
        type: Union[str, "ManagedServiceIdentityType"],
        user_assigned_identities: Optional[Dict[str, "UserAssignedIdentity"]] = None,
        **kwargs
    ):
        super(ManagedServiceIdentity, self).__init__(**kwargs)
        self.principal_id = None
        self.tenant_id = None
        self.type = type
        self.user_assigned_identities = user_assigned_identities


class UserAssignedIdentity(msrest.serialization.Model):
    """User assigned identity properties."""

    _validation = {
        "principal_id": {"readonly": True},
        "client_id": {"readonly": True},
    }

    _attribute_map = {
        "principal_id": {"key": "principalId", "type": "str"},
        "client_id": {"key": "clientId", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(UserAssignedIdentity, self).__init__(**kwargs)
        self.principal_id = None
        self.client_id = None


class ManagedServiceIdentityType(str, Enum):
    """Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed)."""

    NONE = "None"
    SYSTEM_ASSIGNED = "SystemAssigned"
    USER_ASSIGNED = "UserAssigned"
    SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
