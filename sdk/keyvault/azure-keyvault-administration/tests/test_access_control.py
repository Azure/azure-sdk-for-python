# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
import time

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope, KeyVaultPermission, KeyVaultDataAction
from azure.keyvault.administration._internal import HttpChallengeCache
import pytest
from six.moves.urllib_parse import urlparse

from _shared.helpers import mock
from _shared.test_case import KeyVaultTestCase


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
        return mock.Mock(get_token=lambda *_, **__: AccessToken("secret", time.time() + 3600))

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

    def test_role_definitions(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        # list initial role definitions
        scope = KeyVaultRoleScope.GLOBAL
        original_definitions = [d for d in client.list_role_definitions(scope)]
        assert len(original_definitions)

        # create custom role definition
        role_name = self.get_resource_name("role-name")
        definition_name = self.get_replayable_uuid("definition-name")
        permissions = [KeyVaultPermission(allowed_data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
        created_definition = client.set_role_definition(
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
        updated_definition = client.set_role_definition(
            role_scope=scope, permissions=permissions, role_definition_name=definition_name
        )
        assert updated_definition.role_name == ""
        assert updated_definition.description == ""
        assert len(updated_definition.permissions) == 1
        assert len(updated_definition.permissions[0].allowed_data_actions) == 0
        assert updated_definition.permissions[0].denied_data_actions == [KeyVaultDataAction.READ_HSM_KEY]

        # assert that the created role definition isn't duplicated
        matching_definitions = [d for d in client.list_role_definitions(scope) if d.id == updated_definition.id]
        assert len(matching_definitions) == 1

        # get custom role definition
        definition = client.get_role_definition(role_scope=scope, role_definition_name=definition_name)
        assert_role_definitions_equal(definition, updated_definition)

        # delete custom role definition
        deleted_definition = client.delete_role_definition(scope, definition_name)
        assert_role_definitions_equal(deleted_definition, definition)

        assert not any(d.id == deleted_definition.id for d in client.list_role_definitions(scope))

    def test_role_assignment(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        scope = KeyVaultRoleScope.GLOBAL
        definitions = [d for d in client.list_role_definitions(scope)]

        # assign an arbitrary role to the service principal authenticating these requests
        definition = definitions[0]
        principal_id = self.get_service_principal_id()
        name = self.get_replayable_uuid("some-uuid")

        created = client.create_role_assignment(scope, definition.id, principal_id, role_assignment_name=name)
        assert created.name == name
        assert created.principal_id == principal_id
        assert created.role_definition_id == definition.id
        assert created.scope == scope

        # should be able to get the new assignment
        got = client.get_role_assignment(scope, name)
        assert got.name == name
        assert got.principal_id == principal_id
        assert got.role_definition_id == definition.id
        assert got.scope == scope

        # new assignment should be in the list of all assignments
        matching_assignments = [
            a for a in client.list_role_assignments(scope) if a.role_assignment_id == created.role_assignment_id
        ]
        assert len(matching_assignments) == 1

        # delete the assignment
        deleted = client.delete_role_assignment(scope, created.name)
        assert deleted.name == created.name
        assert deleted.role_assignment_id == created.role_assignment_id
        assert deleted.scope == scope
        assert deleted.role_definition_id == created.role_definition_id

        assert not any(a.role_assignment_id == created.role_assignment_id for a in client.list_role_assignments(scope))


def assert_role_definitions_equal(d1, d2):
    assert d1.id == d2.id
    assert d1.name == d2.name
    assert d1.role_name == d2.role_name
    assert d1.description == d2.description
    assert d1.role_type == d2.role_type
    assert d1.type == d2.type
    assert len(d1.permissions) == len(d2.permissions)
    for i in range(len(d1.permissions)):
        assert d1.permissions[i].allowed_actions == d2.permissions[i].allowed_actions
        assert d1.permissions[i].denied_actions == d2.permissions[i].denied_actions
        assert d1.permissions[i].allowed_data_actions == d2.permissions[i].allowed_data_actions
        assert d1.permissions[i].denied_data_actions == d2.permissions[i].denied_data_actions
    assert d1.assignable_scopes == d2.assignable_scopes
