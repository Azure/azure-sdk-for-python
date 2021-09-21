# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
import uuid

from azure.keyvault.administration import KeyVaultRoleScope, KeyVaultPermission, KeyVaultDataAction

from _shared.test_case_async import KeyVaultTestCase
from test_access_control import assert_role_definitions_equal
from _test_case import AdministrationTestCase, access_control_client_setup, get_decorator


all_api_versions = get_decorator(is_async=True)


class AccessControlTests(AdministrationTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(AccessControlTests, self).__init__(*args, match_body=False, **kwargs)

    def get_replayable_uuid(self, replay_value):
        if self.is_live:
            value = str(uuid.uuid4())
            self.scrubber.register_name_pair(value, replay_value)
            return value
        return replay_value

    def get_service_principal_id(self):
        replay_value = "service-principal-id"
        if self.is_live:
            value = os.environ["AZURE_CLIENT_ID"]
            self.scrubber.register_name_pair(value, replay_value)
            return value
        return replay_value

    @all_api_versions()
    @access_control_client_setup
    async def test_role_definitions(self, client):
        # list initial role definitions
        scope = KeyVaultRoleScope.GLOBAL
        original_definitions = []
        async for definition in client.list_role_definitions(scope):
            original_definitions.append(definition)
        assert len(original_definitions)

        # create custom role definition
        role_name = self.get_resource_name("role-name")
        definition_name = self.get_replayable_uuid("definition-name")
        permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
        created_definition = await client.set_role_definition(
            scope=scope,
            name=definition_name,
            role_name=role_name,
            description="test",
            permissions=permissions
        )
        assert "/" in created_definition.assignable_scopes
        assert created_definition.role_name == role_name
        assert created_definition.name == definition_name
        assert created_definition.description == "test"
        assert len(created_definition.permissions) == 1
        assert created_definition.permissions[0].data_actions == [KeyVaultDataAction.READ_HSM_KEY]
        assert created_definition.assignable_scopes == [KeyVaultRoleScope.GLOBAL]

        # update custom role definition
        permissions = [
            KeyVaultPermission(data_actions=[], not_data_actions=[KeyVaultDataAction.READ_HSM_KEY])
        ]
        updated_definition = await client.set_role_definition(
            scope=scope, name=definition_name, permissions=permissions
        )
        assert updated_definition.role_name == ""
        assert updated_definition.description == ""
        assert len(updated_definition.permissions) == 1
        assert len(updated_definition.permissions[0].data_actions) == 0
        assert updated_definition.permissions[0].not_data_actions == [KeyVaultDataAction.READ_HSM_KEY]
        assert updated_definition.assignable_scopes == [KeyVaultRoleScope.GLOBAL]

        # assert that the created role definition isn't duplicated
        matching_definitions = []
        async for definition in client.list_role_definitions(scope):
            if definition.id == updated_definition.id:
                matching_definitions.append(definition)
        assert len(matching_definitions) == 1

        # get custom role definition
        definition = await client.get_role_definition(scope=scope, name=definition_name)
        assert_role_definitions_equal(definition, updated_definition)

        # delete custom role definition
        await client.delete_role_definition(scope, definition_name)

        async for d in client.list_role_definitions(scope):
            assert (d.id != definition.id), "the role definition should have been deleted"
        await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @access_control_client_setup
    async def test_role_assignment(self, client):
        scope = KeyVaultRoleScope.GLOBAL
        definitions = []
        async for definition in client.list_role_definitions(scope):
            definitions.append(definition)

        # assign an arbitrary role to the service principal authenticating these requests
        definition = definitions[0]
        principal_id = self.get_service_principal_id()
        name = self.get_replayable_uuid("some-uuid")

        created = await client.create_role_assignment(scope, definition.id, principal_id, name=name)
        assert created.name == name
        assert created.properties.principal_id == principal_id
        assert created.properties.role_definition_id == definition.id
        assert created.properties.scope == scope

        # should be able to get the new assignment
        got = await client.get_role_assignment(scope, name)
        assert got.name == name
        assert got.properties.principal_id == principal_id
        assert got.properties.role_definition_id == definition.id
        assert got.properties.scope == scope

        # new assignment should be in the list of all assignments
        matching_assignments = []
        async for assignment in client.list_role_assignments(scope):
            if assignment.role_assignment_id == created.role_assignment_id:
                matching_assignments.append(assignment)
        assert len(matching_assignments) == 1

        # delete the assignment
        await client.delete_role_assignment(scope, created.name)

        async for assignment in client.list_role_assignments(scope):
            assert (
                assignment.role_assignment_id != created.role_assignment_id
            ), "the role assignment should have been deleted"
