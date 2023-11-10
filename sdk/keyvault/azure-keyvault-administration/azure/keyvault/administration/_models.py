# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Dict, Optional, Union

from azure.core.rest import HttpResponse

from ._enums import KeyVaultSettingType
from ._generated.models import (
    FullBackupOperation,
    Permission,
    RoleAssignment,
    RoleAssignmentProperties,
    RoleAssignmentPropertiesWithScope,
    RoleDefinition,
    Setting,
)


class KeyVaultPermission(object):
    """Role definition permissions.

    :ivar list[str] actions: Action permissions that are granted.
    :ivar list[str] not_actions: Action permissions that are excluded but not denied. They may be granted by other role
     definitions assigned to a principal.
    :ivar list[str] data_actions: Data action permissions that are granted.
    :ivar list[str] not_data_actions: Data action permissions that are excluded but not denied. They may be granted by
     other role definitions assigned to a principal.
    """

    def __init__(self, **kwargs) -> None:
        self.actions = kwargs.get("actions")
        self.not_actions = kwargs.get("not_actions")
        self.data_actions = kwargs.get("data_actions")
        self.not_data_actions = kwargs.get("not_data_actions")

    @classmethod
    def _from_generated(cls, permissions: Permission) -> "KeyVaultPermission":
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

    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get("name")
        self.properties = kwargs.get("properties")
        self.role_assignment_id = kwargs.get("role_assignment_id")
        self.type = kwargs.get("assignment_type")

    def __repr__(self) -> str:
        return f"KeyVaultRoleAssignment<{self.role_assignment_id}>"

    @classmethod
    def _from_generated(cls, role_assignment: RoleAssignment) -> "KeyVaultRoleAssignment":
        # pylint:disable=protected-access
        return cls(
            role_assignment_id=role_assignment.id,
            name=role_assignment.name,
            assignment_type=role_assignment.type,
            properties=KeyVaultRoleAssignmentProperties._from_generated(role_assignment.properties)
            if role_assignment.properties
            else KeyVaultRoleAssignmentProperties(),
        )


class KeyVaultRoleAssignmentProperties(object):
    """Properties of a role assignment

    :ivar str principal_id: ID of the principal the assignment applies to. This maps to an Active Directory user,
        service principal, or security group.
    :ivar str role_definition_id: ID of the scope's role definition
    :ivar str scope: the scope of the assignment
    """

    def __init__(self, **kwargs) -> None:
        self.principal_id = kwargs.get("principal_id")
        self.role_definition_id = kwargs.get("role_definition_id")
        self.scope = kwargs.get("scope")

    def __repr__(self) -> str:
        string = (
            f"KeyVaultRoleAssignmentProperties(principal_id={self.principal_id}, "
            + f"role_definition_id={self.role_definition_id}, scope={self.scope})"
        )
        return string[:1024]

    @classmethod
    def _from_generated(
        cls, role_assignment_properties: Union[RoleAssignmentProperties, RoleAssignmentPropertiesWithScope]
    ) -> "KeyVaultRoleAssignmentProperties":
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

    def __init__(self, **kwargs) -> None:
        self.assignable_scopes = kwargs.get("assignable_scopes")
        self.description = kwargs.get("description")
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.permissions = kwargs.get("permissions")
        self.role_name = kwargs.get("role_name")
        self.role_type = kwargs.get("role_type")
        self.type = kwargs.get("type")

    def __repr__(self) -> str:
        return f"KeyVaultRoleDefinition<{self.id}>"

    @classmethod
    def _from_generated(cls, definition: RoleDefinition) -> "KeyVaultRoleDefinition":
        # pylint:disable=protected-access
        return cls(
            assignable_scopes=definition.assignable_scopes,
            description=definition.description,
            id=definition.id,
            name=definition.name,
            permissions=[KeyVaultPermission._from_generated(p) for p in definition.permissions or []],
            role_name=definition.role_name,
            role_type=definition.role_type,
            type=definition.type,
        )


class KeyVaultBackupResult(object):
    """A Key Vault full backup operation result

    :ivar str folder_url: URL of the Azure Blob Storage container containing the backup
    """

    # pylint:disable=unused-argument

    def __init__(self, **kwargs) -> None:
        self.folder_url: Optional[str] = kwargs.get("folder_url")

    @classmethod
    def _from_generated(
        cls, response: HttpResponse, deserialized_operation: FullBackupOperation, response_headers: Dict
    ) -> "KeyVaultBackupResult":
        return cls(folder_url=deserialized_operation.azure_storage_blob_container_uri)


class KeyVaultSetting(object):
    """A Key Vault setting.

    :param str name: The name of the account setting.
    :param str value: The value of the account setting.
    :param setting_type: The type specifier of the value.
    :type setting_type: str or KeyVaultSettingType or None
    """

    def __init__(
        self,
        name: str,
        value: Union[str, bool],
        setting_type: Optional[Union[str, KeyVaultSettingType]] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        self.name = name
        self.value = value if isinstance(value, str) else str(value)  # `value` is stored as a string
        if setting_type == KeyVaultSettingType.BOOLEAN:
            self.setting_type: Optional[Union[str, KeyVaultSettingType]] = KeyVaultSettingType.BOOLEAN
        else:
            self.setting_type = setting_type.lower() if isinstance(setting_type, str) else setting_type

        # If a setting type isn't provided, set it based on `value`'s type (without inferring from the value itself)
        if self.setting_type is None:
            if isinstance(value, bool):
                self.setting_type = KeyVaultSettingType.BOOLEAN

        # If the setting is a boolean, lower-case the string for serialization
        if self.setting_type == KeyVaultSettingType.BOOLEAN:
            self.value = self.value.lower()

    def getboolean(self) -> bool:
        """Gets the account setting value as a boolean if the ``setting_type`` is ``KeyVaultSettingType.BOOLEAN``.

        :returns: The account setting value as a boolean.
        :rtype: bool

        :raises: ValueError if the ``setting_type`` is not boolean or the value cannot be represented as a boolean.
        """
        if self.setting_type == KeyVaultSettingType.BOOLEAN:
            if self.value == "true":
                return True
            if self.value == "false":
                return False
        raise ValueError(
            'The `setting_type` of the setting must be `KeyVaultSettingType.BOOLEAN` and the `value` must be "true" '
            'or "false" in order to use `getboolean`.'
        )

    @classmethod
    def _from_generated(cls, setting: Setting) -> "KeyVaultSetting":
        setting_type = KeyVaultSettingType.BOOLEAN if setting.type == "boolean" else setting.type
        return cls(name=setting.name, value=setting.value, setting_type=setting_type)
