# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
from uuid import uuid4

from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace

from ._models import KeyVaultRoleAssignment, KeyVaultRoleDefinition
from ._internal import KeyVaultClientBase

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Union
    from uuid import UUID
    from azure.core.paging import ItemPaged
    from ._enums import KeyVaultRoleScope


class KeyVaultAccessControlClient(KeyVaultClientBase):
    """Manages role-based access to Azure Key Vault.

    :param str vault_url: URL of the vault the client will manage. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :type credential: :class:`~azure.core.credentials.TokenCredential`

    :keyword api_version: Version of the service API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion or str
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    # pylint:disable=protected-access

    @distributed_trace
    def create_role_assignment(
        self, scope: "Union[str, KeyVaultRoleScope]", definition_id: str, principal_id: str, **kwargs
    ) -> KeyVaultRoleAssignment:
        """Create a role assignment.

        :param scope: scope the role assignment will apply over. :class:`KeyVaultRoleScope` defines common
            broad scopes. Specify a narrower scope as a string.
        :type scope: str or KeyVaultRoleScope
        :param str definition_id: ID of the role's definition
        :param str principal_id: Azure Active Directory object ID of the principal which will be assigned the role. The
            principal can be a user, service principal, or security group.

        :keyword name: a name for the role assignment. Must be a UUID.
        :paramtype name: str or uuid.UUID or None

        :returns: The created role assignment.
        :rtype: ~azure.keyvault.administration.KeyVaultRoleAssignment
        """
        name = kwargs.pop("name", None) or uuid4()

        create_parameters = self._client.role_assignments.models.RoleAssignmentCreateParameters(
            properties=self._client.role_assignments.models.RoleAssignmentProperties(
                principal_id=principal_id, role_definition_id=str(definition_id)
            )
        )
        assignment = self._client.role_assignments.create(
            vault_base_url=self._vault_url,
            scope=scope,
            role_assignment_name=str(name),
            parameters=create_parameters,
            **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace
    def delete_role_assignment(
        self, scope: "Union[str, KeyVaultRoleScope]", name: "Union[str, UUID]", **kwargs
    ) -> None:
        """Delete a role assignment.

        :param scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>"
            :class:`KeyVaultRoleScope` defines common broad scopes. Specify a narrower scope as a string.
        :type scope: str or KeyVaultRoleScope
        :param name: the role assignment's name.
        :type name: str or uuid.UUID

        :returns: None
        :rtype: None
        """
        try:
            self._client.role_assignments.delete(
                vault_base_url=self._vault_url, scope=scope, role_assignment_name=str(name), **kwargs
            )
        except ResourceNotFoundError:
            pass

    @distributed_trace
    def get_role_assignment(
        self, scope: "Union[str, KeyVaultRoleScope]", name: "Union[str, UUID]", **kwargs
    ) -> KeyVaultRoleAssignment:
        """Get a role assignment.

        :param scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>"
            :class:`KeyVaultRoleScope` defines common broad scopes. Specify a narrower scope as a string.
        :type scope: str or KeyVaultRoleScope
        :param name: the role assignment's name.
        :type name: str or uuid.UUID

        :returns: The fetched role assignment.
        :rtype: ~azure.keyvault.administration.KeyVaultRoleAssignment
        """
        assignment = self._client.role_assignments.get(
            vault_base_url=self._vault_url, scope=scope, role_assignment_name=str(name), **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace
    def list_role_assignments(
        self, scope: "Union[str, KeyVaultRoleScope]", **kwargs
    ) -> "ItemPaged[KeyVaultRoleAssignment]":
        """List all role assignments for a scope.

        :param scope: scope of the role assignments. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string.
        :type scope: str or KeyVaultRoleScope

        :returns: A paged response containing the role assignments for the specified scope.
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.administration.KeyVaultRoleAssignment]
        """
        return self._client.role_assignments.list_for_scope(
            vault_base_url=self._vault_url,
            scope=scope,
            cls=lambda result: [KeyVaultRoleAssignment._from_generated(a) for a in result],
            **kwargs
        )

    @distributed_trace
    def set_role_definition(
        self, scope: "Union[str, KeyVaultRoleScope]", **kwargs
    ) -> "KeyVaultRoleDefinition":
        """Creates or updates a custom role definition.

        To update a role definition, specify the definition's ``name``.

        :param scope: scope of the role definition. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string. Managed HSM only supports '/', or KeyVaultRoleScope.GLOBAL.
        :type scope: str or KeyVaultRoleScope

        :keyword name: the role definition's name, a UUID. When this argument has a value, the client will create a new
            role definition with this name or update an existing role definition, if one exists with the given name.
            When this argument has no value, a new role definition will be created with a generated name.
        :paramtype name: str or uuid.UUID or None
        :keyword role_name: the role's display name. If unspecified when creating or updating a role definition, the
            role name will be set to an empty string.
        :paramtype role_name: str or None
        :keyword description: a description of the role definition. If unspecified when creating or updating a role
            definition, the description will be set to an empty string.
        :paramtype description: str or None
        :keyword permissions: the role definition's permissions. If unspecified when creating or updating a role
            definition, the role definition will have no action permissions.
        :paramtype permissions: list[KeyVaultPermission] or None
        :keyword assignable_scopes: the scopes for which the role definition can be assigned.
        :paramtype assignable_scopes: list[str] or list[KeyVaultRoleScope] or None

        :returns: The created or updated role definition
        :rtype: ~azure.keyvault.administration.KeyVaultRoleDefinition
        """
        permissions = [
            self._client.role_definitions.models.Permission(
                actions=p.actions,
                not_actions=p.not_actions,
                data_actions=p.data_actions,
                not_data_actions=p.not_data_actions,
            )
            for p in kwargs.pop("permissions", None) or []
        ]

        properties = self._client.role_definitions.models.RoleDefinitionProperties(
            role_name=kwargs.pop("role_name", None),
            description=kwargs.pop("description", None),
            permissions=permissions,
            assignable_scopes=kwargs.pop("assignable_scopes", None),
        )
        parameters = self._client.role_definitions.models.RoleDefinitionCreateParameters(properties=properties)

        definition = self._client.role_definitions.create_or_update(
            vault_base_url=self._vault_url,
            scope=scope,
            role_definition_name=str(kwargs.pop("name", None) or uuid4()),
            parameters=parameters,
            **kwargs
        )
        return KeyVaultRoleDefinition._from_generated(definition)

    @distributed_trace
    def get_role_definition(
        self, scope: "Union[str, KeyVaultRoleScope]", name: "Union[str, UUID]", **kwargs
    ) -> "KeyVaultRoleDefinition":
        """Get the specified role definition.

        :param scope: scope of the role definition. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string. Managed HSM only supports '/', or KeyVaultRoleScope.GLOBAL.
        :type scope: str or KeyVaultRoleScope
        :param name: the role definition's name.
        :type name: str or uuid.UUID

        :returns: The fetched role definition.
        :rtype: ~azure.keyvault.administration.KeyVaultRoleDefinition
        """
        definition = self._client.role_definitions.get(
            vault_base_url=self._vault_url, scope=scope, role_definition_name=str(name), **kwargs
        )
        return KeyVaultRoleDefinition._from_generated(definition)

    @distributed_trace
    def delete_role_definition(
        self, scope: "Union[str, KeyVaultRoleScope]", name: "Union[str, UUID]", **kwargs
    ) -> None:
        """Deletes a custom role definition.

        :param scope: scope of the role definition. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string. Managed HSM only supports '/', or KeyVaultRoleScope.GLOBAL.
        :type scope: str or KeyVaultRoleScope
        :param name: the role definition's name.
        :type name: str or uuid.UUID

        :returns: None
        :rtype: None
        """
        try:
            self._client.role_definitions.delete(
                vault_base_url=self._vault_url, scope=scope, role_definition_name=str(name), **kwargs
            )
        except ResourceNotFoundError:
            pass

    @distributed_trace
    def list_role_definitions(
        self, scope: "Union[str, KeyVaultRoleScope]", **kwargs
    ) -> "ItemPaged[KeyVaultRoleDefinition]":
        """List all role definitions applicable at and above a scope.

        :param scope: scope of the role definitions. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string.
        :type scope: str or KeyVaultRoleScope

        :returns: A paged response containing the role definitions for the specified scope.
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.administration.KeyVaultRoleDefinition]
        """
        return self._client.role_definitions.list(
            vault_base_url=self._vault_url,
            scope=scope,
            cls=lambda result: [KeyVaultRoleDefinition._from_generated(d) for d in result],
            **kwargs
        )
