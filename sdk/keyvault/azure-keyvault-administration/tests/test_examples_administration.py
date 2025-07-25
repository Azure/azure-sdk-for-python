# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

import pytest
from azure.keyvault.administration import KeyVaultDataAction, KeyVaultPermission, KeyVaultRoleScope, KeyVaultSetting, KeyVaultSettingType
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultBackupClientPreparer, KeyVaultAccessControlClientPreparer, KeyVaultSettingsClientPreparer, get_decorator

all_api_versions = get_decorator()
only_default = get_decorator(api_versions=[DEFAULT_VERSION])


class TestExamplesTests(KeyVaultTestCase):
    def create_key_client(self, vault_uri, **kwargs):
        from azure.keyvault.keys import KeyClient
        credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs )

    def get_service_principal_id(self):
        """Helper method to get a service principal ID for testing"""
        import os
        replay_value = "service-principal-id"
        if self.is_live:
            value = os.environ.get("CLIENT_OBJECTID")
            return value or replay_value
        return replay_value

    @pytest.mark.parametrize("api_version", only_default)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy
    def test_example_backup_and_restore(self, client, **kwargs):
        set_bodiless_matcher()
        backup_client = client
        container_uri = kwargs.pop("container_uri")

        # [START begin_backup]
        # begin a vault backup
        backup_poller = backup_client.begin_backup(container_uri, use_managed_identity=True)

        # check if the backup completed
        done = backup_poller.done()

        # block until the backup completes
        # result() returns an object with a URL of the backup
        backup_operation = backup_poller.result()
        # [END begin_backup]

        folder_url = backup_operation.folder_url

        if self.is_live:
            time.sleep(15)  # Additional waiting to ensure backup will be available for restore

        # [START begin_restore]
        # begin a full vault restore
        restore_poller = backup_client.begin_restore(folder_url, use_managed_identity=True)

        # check if the restore completed
        done = restore_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_restore]

        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.parametrize("api_version", only_default)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy
    def test_example_selective_key_restore(self, client,**kwargs):
        set_bodiless_matcher()
        # create a key to selectively restore
        managed_hsm_url = kwargs.pop("managed_hsm_url")
        key_client = self.create_key_client(managed_hsm_url)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        backup_client = client
        container_uri = kwargs.pop("container_uri")
        backup_poller = backup_client.begin_backup(container_uri, use_managed_identity=True)
        backup_operation = backup_poller.result()
        folder_url = backup_operation.folder_url

        if self.is_live:
            time.sleep(15)  # Additional waiting to ensure backup will be available for restore

        # [START begin_selective_restore]
        # begin a restore of a single key from a backed up vault
        restore_poller = backup_client.begin_restore(folder_url, use_managed_identity=True, key_name=key_name)

        # check if the restore completed
        done = restore_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_selective_restore]

        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.parametrize("api_version", only_default)
    @KeyVaultAccessControlClientPreparer()
    @recorded_by_proxy
    def test_example_role_assignments(self, client, **kwargs):
        set_bodiless_matcher()
        access_control_client = client

        # [START list_role_definitions]
        # List all role definitions
        role_definitions = [d for d in access_control_client.list_role_definitions(KeyVaultRoleScope.GLOBAL)]
        
        for definition in role_definitions:
            print(f"Role definition: {definition.name}")
        # [END list_role_definitions]

        # Get the first available role definition for the example
        first_definition = role_definitions[0]
        definition_id = first_definition.id
        
        # Get a service principal ID for testing
        principal_id = self.get_service_principal_id()

        # [START create_role_assignment]
        # Create a role assignment
        role_assignment = access_control_client.create_role_assignment(
            scope=KeyVaultRoleScope.GLOBAL,
            definition_id=definition_id,
            principal_id=principal_id
        )
        
        print(f"Created role assignment: {role_assignment.name}")
        # [END create_role_assignment]

        assignment_name = role_assignment.name

        # [START get_role_assignment]
        # Get a specific role assignment
        retrieved_assignment = access_control_client.get_role_assignment(
            scope=KeyVaultRoleScope.GLOBAL,
            name=assignment_name
        )
        
        print(f"Retrieved role assignment: {retrieved_assignment.name}")
        # [END get_role_assignment]

        # [START list_role_assignments]
        # List all role assignments for a scope
        role_assignments = access_control_client.list_role_assignments(KeyVaultRoleScope.GLOBAL)
        
        for assignment in role_assignments:
            print(f"Role assignment: {assignment.name}")
        # [END list_role_assignments]

        # [START delete_role_assignment]
        # Delete a role assignment
        access_control_client.delete_role_assignment(
            scope=KeyVaultRoleScope.GLOBAL,
            name=assignment_name
        )
        
        print("Role assignment deleted")
        # [END delete_role_assignment]

    @pytest.mark.parametrize("api_version", only_default)
    @KeyVaultAccessControlClientPreparer()
    @recorded_by_proxy
    def test_example_role_definitions(self, client, **kwargs):
        set_bodiless_matcher()
        access_control_client = client

        # [START set_role_definition]
        # Create or update a custom role definition
        permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
        role_definition = access_control_client.set_role_definition(
            scope=KeyVaultRoleScope.GLOBAL,
            role_name="Custom Key Reader",
            description="Can read HSM keys",
            permissions=permissions
        )
        
        print(f"Created role definition: {role_definition.name}")
        # [END set_role_definition]

        definition_name = role_definition.name

        # [START get_role_definition]
        # Get a specific role definition
        retrieved_definition = access_control_client.get_role_definition(
            scope=KeyVaultRoleScope.GLOBAL,
            name=definition_name
        )
        
        print(f"Retrieved role definition: {retrieved_definition.role_name}")
        # [END get_role_definition]

        # [START delete_role_definition]
        # Delete a custom role definition
        access_control_client.delete_role_definition(
            scope=KeyVaultRoleScope.GLOBAL,
            name=definition_name
        )
        
        print("Role definition deleted")
        # [END delete_role_definition]

    @pytest.mark.parametrize("api_version", only_default)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_example_settings(self, client, **kwargs):
        set_bodiless_matcher()
        settings_client = client

        # [START list_settings]
        # List all account settings
        settings = settings_client.list_settings()
        
        for setting in settings:
            print(f"Setting: {setting.name} = {setting.value}")
        # [END list_settings]

        # [START get_setting]
        # Get a specific setting
        setting = settings_client.get_setting("AllowKeyManagementOperationsThroughARM")
        
        print(f"Setting value: {setting.value}")
        # [END get_setting]

        # [START update_setting]
        # Update a setting
        updated_setting = KeyVaultSetting(
            name=setting.name,
            value=not setting.getboolean(),
            setting_type=KeyVaultSettingType.BOOLEAN
        )
        
        result = settings_client.update_setting(updated_setting)
        print(f"Updated setting: {result.name} = {result.value}")
        
        # Restore original value
        original_setting = KeyVaultSetting(
            name=setting.name,
            value=setting.value,
            setting_type=setting.setting_type
        )
        settings_client.update_setting(original_setting)
        # [END update_setting]
