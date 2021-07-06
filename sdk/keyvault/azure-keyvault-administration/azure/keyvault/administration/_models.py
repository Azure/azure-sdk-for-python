# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class KeyVaultPermission(object):
    """Role definition permissions.

    :ivar list[str] actions: Action permissions that are granted.
    :ivar list[str] not_actions: Action permissions that are excluded but not denied. They may be granted by other role
     definitions assigned to a principal.
    :ivar list[str] data_actions: Data action permissions that are granted.
    :ivar list[str] not_data_actions: Data action permissions that are excluded but not denied. They may be granted by
     other role definitions assigned to a principal.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.actions = kwargs.get("actions")
        self.not_actions = kwargs.get("not_actions")
        self.data_actions = kwargs.get("data_actions")
        self.not_data_actions = kwargs.get("not_data_actions")

    @classmethod
    def _from_generated(cls, permissions):
        return cls(
            actions=permissions.actions,
            not_actions=permissions.not_actions,
            data_actions=permissions.data_actions,
            not_data_actions=permissions.not_data_actions,
        )


class KeyVaultRoleAssignment(object):
    """Represents the assignment to a principal of a role over a scope

    :ivar str name: the assignment's name
    :ivar KeyVaultRoleAssignmentProperties properties: the assignment's properties
    :ivar str role_assignment_id: unique identifier for the assignment
    :ivar str type: type of the assignment
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.name = kwargs.get("name")
        self.properties = kwargs.get("properties")
        self.role_assignment_id = kwargs.get("role_assignment_id")
        self.type = kwargs.get("assignment_type")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleAssignment<{}>".format(self.role_assignment_id)

    @classmethod
    def _from_generated(cls, role_assignment):
        # pylint:disable=protected-access
        return cls(
            role_assignment_id=role_assignment.id,
            name=role_assignment.name,
            assignment_type=role_assignment.type,
            properties=KeyVaultRoleAssignmentProperties._from_generated(role_assignment.properties),
        )


class KeyVaultRoleAssignmentProperties(object):
    """Properties of a role assignment

    :ivar str principal_id: ID of the principal the assignment applies to. This maps to an Active Directory user,
        service principal, or security group.
    :ivar str role_definition_id: ID of the scope's role definition
    :ivar str scope: the scope of the assignment
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.principal_id = kwargs.get("principal_id")
        self.role_definition_id = kwargs.get("role_definition_id")
        self.scope = kwargs.get("scope")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleAssignmentProperties(principal_id={}, role_definition_id={}, scope={})".format(
            self.principal_id, self.role_definition_id, self.scope
        )[:1024]

    @classmethod
    def _from_generated(cls, role_assignment_properties):
        # the generated RoleAssignmentProperties and RoleAssignmentPropertiesWithScope
        # models differ only in that the latter has a "scope" attribute
        return cls(
            principal_id=role_assignment_properties.principal_id,
            role_definition_id=role_assignment_properties.role_definition_id,
            scope=getattr(role_assignment_properties, "scope", None),
        )


class KeyVaultRoleDefinition(object):
    """The definition of a role over one or more scopes

    :ivar list[str] assignable_scopes: scopes the role can be assigned over
    :ivar str description: description of the role definition
    :ivar str id: unique identifier for this role definition
    :ivar str name: the role definition's name
    :ivar list[KeyVaultPermission] permissions: permissions defined for the role
    :ivar str role_name: the role's name
    :ivar str role_type: type of the role
    :ivar str type: type of the role definition
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.assignable_scopes = kwargs.get("assignable_scopes")
        self.description = kwargs.get("description")
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.permissions = kwargs.get("permissions")
        self.role_name = kwargs.get("role_name")
        self.role_type = kwargs.get("role_type")
        self.type = kwargs.get("type")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleDefinition<{}>".format(self.id)

    @classmethod
    def _from_generated(cls, definition):
        # pylint:disable=protected-access
        return cls(
            assignable_scopes=definition.assignable_scopes,
            description=definition.description,
            id=definition.id,
            name=definition.name,
            permissions=[KeyVaultPermission._from_generated(p) for p in definition.permissions],
            role_name=definition.role_name,
            role_type=definition.role_type,
            type=definition.type,
        )


class KeyVaultBackupResult(object):
    """A Key Vault full backup operation result

    :ivar str folder_url: URL of the Azure Blob Storage container containing the backup
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.folder_url = kwargs.get("folder_url")

    @classmethod
    def _from_generated(cls, response, deserialized_operation, response_headers):  # pylint:disable=unused-argument
        return cls(folder_url=deserialized_operation.azure_storage_blob_container_uri)
