# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import uuid
import time

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope
from devtools_testutils import CachedResourceGroupPreparer
import pytest
from six.moves.urllib_parse import urlparse

from _shared.helpers import mock
from _shared.test_case import KeyVaultTestCase


@pytest.mark.usefixtures("managed_hsm")
class AccessControlTests(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(AccessControlTests, self).__init__(*args, **kwargs)

    def setUp(self, *args, **kwargs):
        if self.is_live:
            real = urlparse(self.managed_hsm["url"])
            playback = urlparse(self.managed_hsm["playback_url"])
            self.scrubber.register_name_pair(real.netloc, playback.netloc)
        super(AccessControlTests, self).setUp(*args, **kwargs)

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

    def test_a_rest_api(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        properties = None
        definition = client.set_role_definition(role_scope="/", role_definition_properties=properties)
        print(definition)

    def test_list_role_definitions(self):
        client = KeyVaultAccessControlClient(self.managed_hsm["url"], self.credential)

        definitions = [d for d in client.list_role_definitions(KeyVaultRoleScope.global_value)]
        assert len(definitions)

        for definition in definitions:
            assert "/" in definition.assignable_scopes
            assert definition.description is not None
            assert definition.id is not None
            assert definition.name is not None
            assert len(definition.permissions)
            assert definition.role_name is not None
            assert definition.role_type is not None
            assert definition.type is not None

    def test_role_assignment(self):
        client = KeyVaultAccessControlClient("https://mcpatinotesthsm.azure.net", self.credential)

        scope = KeyVaultRoleScope.global_value
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

        assert not any(
            a for a in client.list_role_assignments(scope) if a.role_assignment_id == created.role_assignment_id
        )
