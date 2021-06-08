# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# pylint:disable=protected-access


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
    """Represents the assignment to a principal of a role over a scope"""

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._role_assignment_id = kwargs.get("role_assignment_id")
        self._name = kwargs.get("name")
        self._properties = kwargs.get("properties")
        self._type = kwargs.get("assignment_type")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleAssignment<{}>".format(self._role_assignment_id)

    @property
    def role_assignment_id(self):
        # type: () -> str
        """Unique identifier for this assignment"""
        return self._role_assignment_id

    @property
    def name(self):
        # type: () -> str
        """Name of the assignment"""
        return self._name

    @property
    def properties(self):
        # type: () -> KeyVaultRoleAssignmentProperties
        """Properties of the assignment"""
        return self._properties

    @property
    def type(self):
        # type: () -> str
        """The type of this assignment"""
        return self._type

    @classmethod
    def _from_generated(cls, role_assignment):
        return cls(
            role_assignment_id=role_assignment.id,
            name=role_assignment.name,
            assignment_type=role_assignment.type,
            properties=KeyVaultRoleAssignmentProperties._from_generated(role_assignment.properties),
        )


class KeyVaultRoleAssignmentProperties(object):
    """Properties of a role assignment."""

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._principal_id = kwargs.get("principal_id")
        self._role_definition_id = kwargs.get("role_definition_id")
        self._scope = kwargs.get("scope")

    @property
    def principal_id(self):
        # type: () -> str
        """ID of the principal this assignment applies to.

        This maps to the ID inside the Active Directory. It can point to a user, service principal, or security group.
        """
        return self._principal_id

    @property
    def role_definition_id(self):
        # type: () -> str
        """ID of the role's definition"""
        return self._role_definition_id

    @property
    def scope(self):
        # type: () -> str
        """Scope of the assignment"""
        return self._scope

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
    """Represents the definition of a role over a scope."""

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._id = kwargs.get("id")
        self._name = kwargs.get("name")
        self._role_name = kwargs.get("role_name")
        self._description = kwargs.get("description")
        self._role_type = kwargs.get("role_type")
        self._type = kwargs.get("type")
        self._permissions = kwargs.get("permissions")
        self._assignable_scopes = kwargs.get("assignable_scopes")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleDefinition<{}>".format(self._id)

    @property
    def id(self):
        # type: () -> str
        """Unique identifier for this role definition"""
        return self._id

    @property
    def name(self):
        # type: () -> str
        """Name of the role definition"""
        return self._name

    @property
    def role_name(self):
        # type: () -> str
        """Name of the role"""
        return self._role_name

    @property
    def description(self):
        # type: () -> str
        """Description of the role definition"""
        return self._description

    @property
    def role_type(self):
        # type: () -> str
        """Type of the role"""
        return self._role_type

    @property
    def type(self):
        # type: () -> str
        """Type of the role definition"""
        return self._type

    @property
    def permissions(self):
        # type: () -> list[KeyVaultPermission]
        """Permissions defined for the role"""
        return self._permissions

    @property
    def assignable_scopes(self):
        # type: () -> list[str]
        """Scopes that can be assigned to the role"""
        return self._assignable_scopes

    @classmethod
    def _from_generated(cls, definition):
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


class KeyVaultBackupOperation(object):
    """A Key Vault full backup operation"""

    def __init__(self, folder_url, **kwargs):
        # type: (str, **Any) -> None
        self._folder_url = folder_url

    @property
    def folder_url(self):
        # type: () -> str
        """URL of the Azure Blob Storage container containing the backup"""
        return self._folder_url

    @classmethod
    def _from_generated(cls, response, deserialized_operation, response_headers):  # pylint:disable=unused-argument
        return cls(deserialized_operation.azure_storage_blob_container_uri)
