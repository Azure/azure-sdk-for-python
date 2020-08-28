# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._models import KeyVaultRoleAssignment, KeyVaultRoleDefinition
from .._internal import AsyncKeyVaultClientBase

if TYPE_CHECKING:
    from typing import Any, Union
    from uuid import UUID
    from azure.core.async_paging import AsyncItemPaged


class KeyVaultAccessControlClient(AsyncKeyVaultClientBase):
    """Manages role-based access to Azure Key Vault.

    :param str vault_url: URL of the vault the client will manage. This is also called the vault's "DNS Name".
    :param credential: an object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    """

    # pylint:disable=protected-access

    @distributed_trace_async
    async def create_role_assignment(
        self,
        role_scope: str,
        role_assignment_name: "Union[str, UUID]",
        role_definition_id: str,
        principal_id: str,
        **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Create a role assignment.

        :param str role_scope: scope the role assignment will apply over
        :param role_assignment_name: a name for the role assignment. Must be a UUID.
        :type role_assignment_name: str or uuid.UUID
        :param str role_definition_id: ID of the role's definition
        :param str principal_id: Azure Active Directory object ID of the principal which will be assigned the role. The
            principal can be a user, service principal, or security group.
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
            role_assignment_name=role_assignment_name,
            parameters=create_parameters,
            **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace_async
    async def delete_role_assignment(
        self, role_scope: str, role_assignment_name: "Union[str, UUID]", **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Delete a role assignment.

        :param str role_scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>"
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
        self, role_scope: str, role_assignment_name: "Union[str, UUID]", **kwargs: "Any"
    ) -> KeyVaultRoleAssignment:
        """Get a role assignment.

        :param str role_scope: the assignment's scope, for example "/", "/keys", or "/keys/<specific key identifier>"
        :param role_assignment_name: the assignment's name. Must be a UUID.
        :type role_assignment_name: str or uuid.UUID
        :rtype: KeyVaultRoleAssignment
        """
        assignment = await self._client.role_assignments.get(
            vault_base_url=self._vault_url, scope=role_scope, role_assignment_name=str(role_assignment_name), **kwargs
        )
        return KeyVaultRoleAssignment._from_generated(assignment)

    @distributed_trace
    def list_role_assignments(self, role_scope: str, **kwargs: "Any") -> "AsyncItemPaged[KeyVaultRoleAssignment]":
        """List all role assignments for a scope.

        :param str role_scope: scope of the role assignments
        :rtype: ~azure.core.async_paging.AsyncItemPaged[KeyVaultRoleAssignment]
        """
        return self._client.role_assignments.list_for_scope(
            self._vault_url,
            role_scope,
            cls=lambda result: [KeyVaultRoleAssignment._from_generated(a) for a in result],
            **kwargs
        )

    @distributed_trace
    def list_role_definitions(self, role_scope: str, **kwargs: "Any") -> "AsyncItemPaged[KeyVaultRoleDefinition]":
        """List all role definitions applicable at and above a scope.

        :param str role_scope: scope of the role definitions
        :rtype: ~azure.core.async_paging.AsyncItemPaged[KeyVaultRoleDefinition]
        """
        return self._client.role_definitions.list(
            self._vault_url,
            role_scope,
            cls=lambda result: [KeyVaultRoleDefinition._from_generated(d) for d in result],
            **kwargs
        )
