# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
import time

from azure.core.credentials import AccessToken
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultRoleScope, KeyVaultPermission, KeyVaultDataAction
from azure.keyvault.administration.aio import KeyVaultAccessControlClient
from azure.keyvault.administration._internal import HttpChallengeCache
import pytest
from six.moves.urllib_parse import urlparse
from devtools_testutils import AzureTestCase

from _shared.helpers_async import mock
from _shared.test_case_async import KeyVaultTestCase
from test_access_control import assert_role_definitions_equal


@pytest.mark.usefixtures("managed_hsm")
class AccessControlTests(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(AccessControlTests, self).__init__(*args, match_body=False, **kwargs)

    def setUp(self, *args, **kwargs):
        if self.is_live:
            real = urlparse(self.managed_hsm["url"])
            playback = urlparse(self.managed_hsm["playback_url"])
            self.scrubber.register_name_pair(real.netloc, playback.netloc)
        super(AccessControlTests, self).setUp(*args, **kwargs)

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(AccessControlTests, self).tearDown()

    @property
    def credential(self):
        if self.is_live:
            return DefaultAzureCredential()

        async def get_token(*_, **__):
            return AccessToken("secret", time.time() + 3600)

        return mock.Mock(get_token=get_token)

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

    @AzureTestCase.await_prepared_test
    async def test_role_definitions(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        # list initial role definitions
        scope = KeyVaultRoleScope.GLOBAL
        original_definitions = []
        async for definition in client.list_role_definitions(scope):
            original_definitions.append(definition)
        assert len(original_definitions)

        # create custom role definition
        role_name = self.get_resource_name("role-name")
        definition_name = self.get_replayable_uuid("definition-name")
        permissions = [KeyVaultPermission(allowed_data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
        created_definition = await client.set_role_definition(
            role_scope=scope,
            permissions=permissions,
            role_name=role_name,
            role_definition_name=definition_name,
            description="test"
        )
        assert "/" in created_definition.assignable_scopes
        assert created_definition.role_name == role_name
        assert created_definition.name == definition_name
        assert created_definition.description == "test"
        assert len(created_definition.permissions) == 1
        assert created_definition.permissions[0].allowed_data_actions == [KeyVaultDataAction.READ_HSM_KEY]

        # update custom role definition
        permissions = [
            KeyVaultPermission(allowed_data_actions=[], denied_data_actions=[KeyVaultDataAction.READ_HSM_KEY])
        ]
        updated_definition = await client.set_role_definition(
            role_scope=scope, permissions=permissions, role_definition_name=definition_name
        )
        assert updated_definition.role_name == ""
        assert updated_definition.description == ""
        assert len(updated_definition.permissions) == 1
        assert len(updated_definition.permissions[0].allowed_data_actions) == 0
        assert updated_definition.permissions[0].denied_data_actions == [KeyVaultDataAction.READ_HSM_KEY]

        # assert that the created role definition isn't duplicated
        matching_definitions = []
        async for definition in client.list_role_definitions(scope):
            if definition.id == updated_definition.id:
                matching_definitions.append(definition)
        assert len(matching_definitions) == 1

        # get custom role definition
        definition = await client.get_role_definition(role_scope=scope, role_definition_name=definition_name)
        assert_role_definitions_equal(definition, updated_definition)

        # delete custom role definition
        deleted_definition = await client.delete_role_definition(scope, definition_name)
        assert_role_definitions_equal(deleted_definition, definition)

        async for definition in client.list_role_definitions(scope):
            assert (definition.id != deleted_definition.id), "the role definition should have been deleted"

    @AzureTestCase.await_prepared_test
    async def test_role_assignment(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        scope = KeyVaultRoleScope.GLOBAL
        definitions = []
        async for definition in client.list_role_definitions(scope):
            definitions.append(definition)

        # assign an arbitrary role to the service principal authenticating these requests
        definition = definitions[0]
        principal_id = self.get_service_principal_id()
        name = self.get_replayable_uuid("some-uuid")

        created = await client.create_role_assignment(scope, definition.id, principal_id, role_assignment_name=name)
        assert created.name == name
        assert created.principal_id == principal_id
        assert created.role_definition_id == definition.id
        assert created.scope == scope

        # should be able to get the new assignment
        got = await client.get_role_assignment(scope, name)
        assert got.name == name
        assert got.principal_id == principal_id
        assert got.role_definition_id == definition.id
        assert got.scope == scope

        # new assignment should be in the list of all assignments
        matching_assignments = []
        async for assignment in client.list_role_assignments(scope):
            if assignment.role_assignment_id == created.role_assignment_id:
                matching_assignments.append(assignment)
        assert len(matching_assignments) == 1

        # delete the assignment
        deleted = await client.delete_role_assignment(scope, created.name)
        assert deleted.name == created.name
        assert deleted.role_assignment_id == created.role_assignment_id
        assert deleted.scope == scope
        assert deleted.role_definition_id == created.role_definition_id

        async for assignment in client.list_role_assignments(scope):
            assert (
                assignment.role_assignment_id != created.role_assignment_id
            ), "the role assignment should have been deleted"
