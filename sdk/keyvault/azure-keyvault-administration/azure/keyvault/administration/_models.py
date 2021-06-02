# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from typing import TYPE_CHECKING

from azure.core.exceptions import ODataV4Format

if TYPE_CHECKING:
    from typing import Any, Optional


# pylint:disable=protected-access


class KeyVaultPermission(object):
    """Role definition permissions.

    :keyword list[str] actions: Action permissions that are granted.
    :keyword list[str] not_actions: Action permissions that are excluded but not denied. They may be granted by other
     role definitions assigned to a principal.
    :keyword list[str] data_actions: Data action permissions that are granted.
    :keyword list[str] not_data_actions: Data action permissions that are excluded but not denied. They may be granted
     by other role definitions assigned to a principal.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._actions = kwargs.get("actions", [])
        self._not_actions = kwargs.get("not_actions", [])
        self._data_actions = kwargs.get("data_actions", [])
        self._not_data_actions = kwargs.get("not_data_actions", [])

    @property
    def actions(self):
        # type: () -> list[str]
        """Actions permissions that are granted"""
        return self._actions

    @property
    def not_actions(self):
        # type: () -> list[str]
        """Action permissions that are excluded but not denied. They may be granted by other role definitions assigned
        to a principal"""
        return self._not_actions

    @property
    def data_actions(self):
        # type: () -> list[str]
        """Data action permissions that are granted"""
        return self._data_actions

    @property
    def not_data_actions(self):
        # type: () -> list[str]
        """Data action permissions that are excluded but not denied. They may be granted by other role definitions
        assigned to a principal"""
        return self._not_data_actions

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


class _Operation(object):
    def __init__(self, **kwargs):
        self._status = kwargs.get("status", None)
        self._status_details = kwargs.get("status_details", None)
        self._start_time = kwargs.get("start_time", None)
        self._end_time = kwargs.get("end_time", None)
        self._job_id = kwargs.get("job_id", None)

        error = kwargs.get("error", None)
        # responses can return an empty error object when there's no error
        if error is None or error.code is None:
            self._error = None
        else:
            self._error = ODataV4Format(vars(error))

    @property
    def status(self):
        # type: () -> Optional[str]
        """Status of the operation"""
        return self._status

    @property
    def status_details(self):
        # type: () -> Optional[str]
        """More details of the operation's status"""
        return self._status_details

    @property
    def error(self):
        # type: () -> Optional[ODataV4Format]
        """Error encountered, if any, during the operation"""
        return self._error

    @property
    def start_time(self):
        # type: () -> Optional[datetime.datetime]
        """UTC start time of the operation"""
        return self._start_time

    @property
    def end_time(self):
        # type: () -> Optional[datetime.datetime]
        """UTC end time of the operation"""
        return self._end_time

    @property
    def job_id(self):
        # type: () -> Optional[str]
        """Identifier for the operation"""
        return self._job_id

    @classmethod
    def _wrap_generated(cls, response, deserialized_operation, response_headers):  # pylint:disable=unused-argument
        return cls(**deserialized_operation.__dict__)


class KeyVaultBackupOperation(_Operation):
    """A Key Vault full backup operation."""

    def __init__(self, **kwargs):
        self._folder_url = kwargs.pop("azure_storage_blob_container_uri", None)
        super(KeyVaultBackupOperation, self).__init__(**kwargs)

    @property
    def folder_url(self):
        # type: () -> str
        """URL of the Azure blob storage container which contains the backup"""
        return self._folder_url


class KeyVaultRestoreOperation(_Operation):
    """A Key Vault restore operation."""


class KeyVaultSelectiveKeyRestoreOperation(_Operation):
    """A Key Vault operation restoring a single key."""
