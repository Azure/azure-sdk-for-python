# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
from uuid import uuid4

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._models import KeyVaultRoleAssignment, KeyVaultRoleDefinition
from .._internal import AsyncKeyVaultClientBase

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Union
    from uuid import UUID
    from azure.core.async_paging import AsyncItemPaged
    from .._models import KeyVaultRoleScope


class KeyVaultAccessControlClient(AsyncKeyVaultClientBase):
    """Manages role-based access to Azure Key Vault.

    :param str vault_url: URL of the vault the client will manage. This is also called the vault's "DNS Name".
    :param credential: an object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    """

    # pylint:disable=protected-access

    @distributed_trace_async
    async def create_role_assignment(
        self, role_scope: "Union[str, KeyVaultRoleScope]", role_definition_id: str, principal_id: str, **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Create a role assignment.

        :param role_scope: scope the role assignment will apply over. :class:`KeyVaultRoleScope` defines common broad
            scopes. Specify a narrower scope as a string.
        :type role_scope: str or KeyVaultRoleScope
        :param str role_definition_id: ID of the role's definition
        :param str principal_id: Azure Active Directory object ID of the principal which will be assigned the role. The
            principal can be a user, service principal, or security group.
        :keyword role_assignment_name: a name for the role assignment. Must be a UUID.
        :type role_assignment_name: str or uuid.UUID
        :rtype: KeyVaultRoleAssignment
        """
        create_parameters = self._client.role_assignments.models.RoleAssignmentCreateParameters(
            properties=self._client.role_assignments.models.RoleAssignmentProperties(
                principal_id=principal_id, role_definition_id=str(role_definition_id)
            )
        )
        assignment = await self._client.role_assignments.create(
            vault_base_url=self._vault_url,
            scope=role_scope,
            role_assignment_name=kwargs.pop("role_assignment_name", None) or uuid4(),
            parameters=create_parameters,
            **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace_async
    async def delete_role_assignment(
        self, role_scope: "Union[str, KeyVaultRoleScope]", role_assignment_name: "Union[str, UUID]", **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Delete a role assignment.

        :param role_scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>".
            :class:`KeyVaultRoleScope` defines common broad scopes. Specify a narrower scope as a string.
        :type role_scope: str or KeyVaultRoleScope
        :param role_assignment_name: the assignment's name. Must be a UUID.
        :type role_assignment_name: str or uuid.UUID
        :returns: the deleted assignment
        :rtype: KeyVaultRoleAssignment
        """
        assignment = await self._client.role_assignments.delete(
            vault_base_url=self._vault_url, scope=role_scope, role_assignment_name=str(role_assignment_name), **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace_async
    async def get_role_assignment(
        self, role_scope: "Union[str, KeyVaultRoleScope]", role_assignment_name: "Union[str, UUID]", **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Get a role assignment.

        :param role_scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>".
            :class:`KeyVaultRoleScope` defines common broad scopes. Specify a narrower scope as a string.
        :type role_scope: str or KeyVaultRoleScope
        :param role_assignment_name: the assignment's name. Must be a UUID.
        :type role_assignment_name: str or uuid.UUID
        :rtype: KeyVaultRoleAssignment
        """
        assignment = await self._client.role_assignments.get(
            vault_base_url=self._vault_url, scope=role_scope, role_assignment_name=str(role_assignment_name), **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace
    def list_role_assignments(
        self, role_scope: "Union[str, KeyVaultRoleScope]", **kwargs: "Any"
    ) -> "AsyncItemPaged[KeyVaultRoleAssignment]":
        """List all role assignments for a scope.

        :param role_scope: scope of the role assignments. :class:`KeyVaultRoleScope` defines common broad
            scopes. Specify a narrower scope as a string.
        :type role_scope: str or KeyVaultRoleScope
        :rtype: ~azure.core.async_paging.AsyncItemPaged[KeyVaultRoleAssignment]
        """
        return self._client.role_assignments.list_for_scope(
            self._vault_url,
            role_scope,
            cls=lambda result: [KeyVaultRoleAssignment._from_generated(a) for a in result],
            **kwargs
        )

    @distributed_trace_async
    async def set_role_definition(self, **kwargs):
        # type: (...) -> "_models.RoleDefinition"
        """Creates or updates a custom role definition.

        :param vault_base_url: The vault name, for example https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param scope: The scope of the role definition to create or update. Managed HSM only supports
         '/'.
        :type scope: str
        :param role_definition_name: The name of the role definition to create or update. It can be any
         valid GUID.
        :type role_definition_name: str
        :param parameters: Parameters for the role definition.
        :type parameters: ~key_vault_client.models.RoleDefinitionCreateParameters
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: RoleDefinition, or the result of cls(response)
        :rtype: ~key_vault_client.models.RoleDefinition
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        role_definition_operations = self._client.role_definitions

    @distributed_trace_async
    async def get_role_definition(self, **kwargs):
        # type: (...) -> "_models.RoleDefinition"
        """Get the specified role definition.

        :param vault_base_url: The vault name, for example https://myvault.vault.azure.net.
        :type vault_base_url: str
        :param scope: The scope of the role definition to get. Managed HSM only supports '/'.
        :type scope: str
        :param role_definition_name: The name of the role definition to get.
        :type role_definition_name: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: RoleDefinition, or the result of cls(response)
        :rtype: ~key_vault_client.models.RoleDefinition
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        role_definition_operations = self._client.role_definitions

    @distributed_trace_async
    async def delete_role_definition(self, role_scope, role_definition_name, **kwargs):
        # type: (...) -> "_models.RoleDefinition"
        """Deletes a custom role definition.

        :param role_scope: scope of the role definitions. :class:`KeyVaultRoleScope` defines common broad scopes.
            Specify a narrower scope as a string. Managed HSM only supports '/', or KeyVaultRoleScope.global_value.
        :type role_scope: str or KeyVaultRoleScope
        :param role_definition_name: the definition's name. Must be a UUID.
        :type role_definition_name: str or uuid.UUID
        :returns: the deleted definition
        :rtype: KeyVaultRoleDefinition
        """
        definition = self._client.role_definitions.delete(
            vault_base_url=self._vault_url, scope=role_scope, role_definition_name=str(role_definition_name), **kwargs
        )
        return definition

    @distributed_trace
    def list_role_definitions(
        self, role_scope: "Union[str, KeyVaultRoleScope]", **kwargs: "Any"
    ) -> "AsyncItemPaged[KeyVaultRoleDefinition]":
        """List all role definitions applicable at and above a scope.

        :param role_scope: scope of the role definitions. :class:`KeyVaultRoleScope` defines common broad
            scopes. Specify a narrower scope as a string.
        :type role_scope: str or KeyVaultRoleScope
        :rtype: ~azure.core.async_paging.AsyncItemPaged[KeyVaultRoleDefinition]
        """
        return self._client.role_definitions.list(
            self._vault_url,
            role_scope,
            cls=lambda result: [KeyVaultRoleDefinition._from_generated(d) for d in result],
            **kwargs
        )
