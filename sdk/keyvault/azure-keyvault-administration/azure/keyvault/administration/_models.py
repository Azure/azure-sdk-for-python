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

    :ivar list[str] allowed_actions:
    :ivar list[str] denied_actions:
    :ivar list[str] allowed_data_actions:
    :ivar list[str] denied_data_actions:
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.allowed_actions = kwargs.get("allowed_actions")
        self.denied_actions = kwargs.get("denied_actions")
        self.allowed_data_actions = kwargs.get("allowed_data_actions")
        self.denied_data_actions = kwargs.get("denied_data_actions")

    @classmethod
    def _from_generated(cls, permissions):
        return cls(
            allowed_actions=permissions.actions,
            denied_actions=permissions.not_actions,
            allowed_data_actions=permissions.data_actions,
            denied_data_actions=permissions.not_data_actions,
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
        """unique identifier for this assignment"""
        return self._role_assignment_id

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
            role_assignment_id=role_assignment.id,
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
        """unique identifier for this role definition"""
        return self._id

    @property
    def name(self):
        # type: () -> str
        """name of the role definition"""
        return self._name

    @property
    def role_name(self):
        # type: () -> str
        """name of the role"""
        return self._role_name

    @property
    def description(self):
        # type: () -> str
        """description of the role definition"""
        return self._description

    @property
    def role_type(self):
        # type: () -> str
        """type of the role"""
        return self._role_type

    @property
    def type(self):
        # type: () -> str
        """type of the role definition"""
        return self._type

    @property
    def permissions(self):
        # type: () -> list[KeyVaultPermission]
        """permissions defined for the role"""
        return self._permissions

    @property
    def assignable_scopes(self):
        # type: () -> list[str]
        """scopes that can be assigned to the role"""
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
        self.status = kwargs.get("status", None)
        self.status_details = kwargs.get("status_details", None)
        self.error = kwargs.get("error", None)
        self.start_time = kwargs.get("start_time", None)
        self.end_time = kwargs.get("end_time", None)
        self.job_id = kwargs.get("job_id", None)

    @classmethod
    def _wrap_generated(cls, response, deserialized_operation, response_headers):  # pylint:disable=unused-argument
        return cls(**deserialized_operation.__dict__)


class BackupOperation(_Operation):
    """A Key Vault full backup operation.

    :ivar str status: status of the backup operation
    :ivar str status_details: more details of the operation's status
    :ivar error: Error encountered, if any, during the operation
    :type error: ~key_vault_client.models.Error
    :ivar datetime.datetime start_time: UTC start time of the operation
    :ivar datetime.datetime end_time: UTC end time of the operation
    :ivar str job_id: identifier for the operation
    :ivar str folder_url: URL of the Azure blob storage container which contains the backup
    """

    def __init__(self, **kwargs):
        self.folder_url = kwargs.pop("azure_storage_blob_container_uri", None)
        super(BackupOperation, self).__init__(**kwargs)


class RestoreOperation(_Operation):
    """A Key Vault restore operation.

    :ivar str status: status of the operation
    :ivar str status_details: more details of the operation's status
    :ivar error: Error encountered, if any, during the operation
    :type error: ~key_vault_client.models.Error
    :ivar datetime.datetime start_time: UTC start time of the operation
    :ivar datetime.datetime end_time: UTC end time of the operation
    :ivar str job_id: identifier for the operation
    """


class SelectiveKeyRestoreOperation(_Operation):
    """A Key Vault operation restoring a single key.

    :ivar str status: status of the operation
    :ivar str status_details: more details of the operation's status
    :ivar error: Error encountered, if any, during the operation
    :type error: ~key_vault_client.models.Error
    :ivar datetime.datetime start_time: UTC start time of the operation
    :ivar datetime.datetime end_time: UTC end time of the operation
    :ivar str job_id: identifier for the operation
    """
