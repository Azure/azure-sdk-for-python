# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
import uuid

import pytest
from azure.keyvault.administration import KeyVaultDataAction, KeyVaultPermission, KeyVaultRoleScope
from devtools_testutils import add_general_regex_sanitizer, recorded_by_proxy, set_bodiless_matcher

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultAccessControlClientPreparer, get_decorator

all_api_versions = get_decorator()


class TestAccessControl(KeyVaultTestCase):
    def get_replayable_uuid(self, replay_value):
        if self.is_live:
            value = str(uuid.uuid4())
            return value
        return replay_value

    def get_service_principal_id(self):
        replay_value = "service-principal-id"
        if self.is_live:
            value = os.environ["AZURE_CLIENT_ID"]
            return value
        return replay_value

    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultAccessControlClientPreparer()
    @recorded_by_proxy
    def test_role_definitions(self, client, **kwargs):
        set_bodiless_matcher()
        # list initial role definitions
        scope = KeyVaultRoleScope.GLOBAL
        original_definitions = [d for d in client.list_role_definitions(scope)]
        assert len(original_definitions)

        # create custom role definition
        role_name = self.get_resource_name("role-name")
        definition_name = self.get_replayable_uuid("definition-name")
        add_general_regex_sanitizer(regex=definition_name, value = "definition-name")
        permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
        created_definition = client.set_role_definition(
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
        updated_definition = client.set_role_definition(
            scope=scope, name=definition_name, permissions=permissions
        )
        assert updated_definition.role_name == ""
        assert updated_definition.description == ""
        assert len(updated_definition.permissions) == 1
        assert len(updated_definition.permissions[0].data_actions) == 0
        assert updated_definition.permissions[0].not_data_actions == [KeyVaultDataAction.READ_HSM_KEY]
        assert updated_definition.assignable_scopes == [KeyVaultRoleScope.GLOBAL]

        # assert that the created role definition isn't duplicated
        matching_definitions = [d for d in client.list_role_definitions(scope) if d.id == updated_definition.id]
        assert len(matching_definitions) == 1

        # get custom role definition
        definition = client.get_role_definition(scope=scope, name=definition_name)
        assert_role_definitions_equal(definition, updated_definition)

        # delete custom role definition
        client.delete_role_definition(scope, definition_name)

        assert not any(d.id == definition.id for d in client.list_role_definitions(scope))
        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultAccessControlClientPreparer()
    @recorded_by_proxy
    def test_role_assignment(self, client, **kwargs):
        set_bodiless_matcher()
        scope = KeyVaultRoleScope.GLOBAL
        definitions = [d for d in client.list_role_definitions(scope)]

        # assign an arbitrary role to the service principal authenticating these requests
        definition = definitions[0]
        principal_id = self.get_service_principal_id()
        name = self.get_replayable_uuid("some-uuid")
        add_general_regex_sanitizer(regex=name, value = "some-uuid")

        created = client.create_role_assignment(scope, definition.id, principal_id, name=name)
        assert created.name == name
        #assert created.properties.principal_id == principal_id
        assert created.properties.role_definition_id == definition.id
        assert created.properties.scope == scope

        # should be able to get the new assignment
        got = client.get_role_assignment(scope, name)
        assert got.name == name
        #assert got.properties.principal_id == principal_id
        assert got.properties.role_definition_id == definition.id
        assert got.properties.scope == scope

        # new assignment should be in the list of all assignments
        matching_assignments = [
            a for a in client.list_role_assignments(scope) if a.role_assignment_id == created.role_assignment_id
        ]
        assert len(matching_assignments) == 1

        # delete the assignment
        client.delete_role_assignment(scope, created.name)

        assert not any(a.role_assignment_id == created.role_assignment_id for a in client.list_role_assignments(scope))
        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests


def assert_role_definitions_equal(d1, d2):
    assert d1.id == d2.id
    assert d1.name == d2.name
    assert d1.role_name == d2.role_name
    assert d1.description == d2.description
    assert d1.role_type == d2.role_type
    assert d1.type == d2.type
    assert len(d1.permissions) == len(d2.permissions)
    for i in range(len(d1.permissions)):
        assert d1.permissions[i].actions == d2.permissions[i].actions
        assert d1.permissions[i].not_actions == d2.permissions[i].not_actions
        assert d1.permissions[i].data_actions == d2.permissions[i].data_actions
        assert d1.permissions[i].not_data_actions == d2.permissions[i].not_data_actions
    assert d1.assignable_scopes == d2.assignable_scopes
