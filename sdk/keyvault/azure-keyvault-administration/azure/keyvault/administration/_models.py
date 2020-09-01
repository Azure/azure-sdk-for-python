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

    :ivar list[str] actions: allowed actions
    :ivar list[str] not_actions: denied actions
    :ivar list[str] data_actions: allowed data actions
    :ivar list[str] not_data_actions: denied data actions
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
        self._assignment_id = kwargs.get("assignment_id")
        self._name = kwargs.get("name")
        self._properties = kwargs.get("properties")
        self._type = kwargs.get("assignment_type")

    def __repr__(self):
        # type: () -> str
        return "KeyVaultRoleAssignment<{}>".format(self._assignment_id)

    @property
    def assignment_id(self):
        # type: () -> str
        """unique identifier for this assignment"""
        return self._assignment_id

    @property
    def name(self):
        # type: () -> str
        """name of the assignment"""
        return self._name

    @property
    def principal_id(self):
        # type: () -> str
        """ID of the principal this assignment applies to.

        This maps to the ID inside the Active Directory. It can point to a user, service principal, or security group.
        """
        return self._properties.principal_id

    @property
    def role_definition_id(self):
        # type: () -> str
        """ID of the role's definition"""
        return self._properties.role_definition_id

    @property
    def scope(self):
        # type: () -> str
        """scope of the assignment"""
        return self._properties.scope

    @property
    def type(self):
        # type: () -> str
        """the type of this assignment"""
        return self._type

    @classmethod
    def _from_generated(cls, role_assignment):
        return cls(
            assignment_id=role_assignment.id,
            name=role_assignment.name,
            assignment_type=role_assignment.type,
            properties=KeyVaultRoleAssignmentProperties._from_generated(role_assignment.properties),
        )


class KeyVaultRoleAssignmentProperties(object):
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
    """Role definition.

    :ivar str id: The role definition ID.
    :ivar str name: The role definition name.
    :ivar str type: The role definition type.
    :ivar str role_name: The role name.
    :ivar str description: The role definition description.
    :ivar str role_type: The role type.
    :ivar permissions: Role definition permissions.
    :vartype permissions: list[KeyVaultPermission]
    :ivar list[str] assignable_scopes: Role definition assignable scopes.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.role_name = kwargs.get("role_name")
        self.description = kwargs.get("description")
        self.role_type = kwargs.get("role_type")
        self.type = kwargs.get("type")
        self.permissions = kwargs.get("permissions")
        self.assignable_scopes = kwargs.get("assignable_scopes")

    def __repr__(self):
        # type: () -> str
        return "<KeyVaultRoleDefinition {}>".format(self.role_name)[:1024]

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
