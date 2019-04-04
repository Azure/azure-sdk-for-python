from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault.keys import KeyClient
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from time import sleep, time
import copy
from dateutil import parser as date_parse
from azure.keyvault._internal import _VaultId as KeyVaultId


class KeyClientTests(KeyvaultTestCase):
    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_new_client(self, vault_client, **kwargs):
        client = vault_client.keys

        # get all the vault's keys
        key_ids_at_start = {key.kid for key in client.get_all_keys()}

        # create a key
        key_name = "crud-test-key"
        new_key = client.create_key(key_name, "RSA")
        assert new_key.name == key_name

        # get the created key by its name
        key = client.get_key(key_name)
        assert key.version == new_key.version
        assert len(list(client.get_key_versions(key_name))) == 1

        # get all the vault's keys again
        all_keys = list(client.get_all_keys())
        # the vault should have exactly one more now
        assert len(all_keys) - len(key_ids_at_start) == 1

        # update the new key
        client.update_key(key_name, "", key_ops=["decrypt"], tags={"spam": "eggs"})
        updated_key = client.get_key(key_name)
        assert updated_key.tags["spam"] == "eggs"

        # delete the new key
        delete_result = client.delete_key(key_name)
        assert delete_result.key.kid == new_key.id

        # verify deletion
        deleted_key = client.get_deleted_key(key_name)
        assert deleted_key.key.kid == key.id
        keys_after_delete = client.get_all_keys()
        key_ids_after_delete = {key.kid for key in keys_after_delete}
        assert len(key_ids_after_delete.symmetric_difference(key_ids_at_start)) == 0
        all_deleted_keys = client.get_all_deleted_keys()
        recovery_ids = {key.recovery_id for key in all_deleted_keys}
        assert delete_result.recovery_id in recovery_ids

        # recover the deleted key
        recovered_key = client.recover_deleted_key(key_name)
        assert recovered_key.id == key.id

        # purge the key
        second_delete_result = client.delete_key(key_name)
        client.purge_deleted_key(key_name)
        # verify the purge
        recovery_ids_after_purge = {
            key.recovery_id for key in client.get_all_deleted_keys()
        }
        assert second_delete_result.recovery_id not in recovery_ids_after_purge

        return
