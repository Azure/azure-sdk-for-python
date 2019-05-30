# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
import asyncio
import functools
import codecs

from azure.security.keyvault._generated.v7_0.models import JsonWebKey
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, HttpResponseError
from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase
from azure.security.keyvault.aio import VaultClient


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
       upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        # TODO: this is a workaround for VaultClientPreparer creating a sync client; let's obviate it
        vault_client = kwargs.get("vault_client")
        credentials = test_class_instance.settings.get_credentials(resource="https://vault.azure.net")
        aio_client = VaultClient(vault_client.vault_url, credentials)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, vault_client=aio_client))

    return run

def create_vault_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_vault_client]
    from azure.security.keyvault.aio import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # [END create_vault_client]
    return vault_client


def create_key_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_key_client]
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault.aio.keys import KeyClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new key client using Azure credentials
    key_client = KeyClient(vault_url=vault_url, credentials=credentials)
    # [END create_key_client]
    return key_client


class TestExamplesKeyVault(KeyVaultTestCase):
    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_example_key_crud_operations(self, vault_client, **kwargs):
        from dateutil import parser as date_parse

        key_client = vault_client.keys
        try:
            # [START create_key]
            from dateutil import parser as date_parse

            key_size = 2048
            key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
            expires = date_parse.parse("2050-02-02T08:00:00.000Z")

            # create a key with optional arguments
            key = await key_client.create_key(
                "key-name", "RSA", size=key_size, key_ops=key_ops, enabled=True, expires=expires
            )

            print(key.id)
            print(key.version)
            print(key.key_material.kty)
            print(key.enabled)
            print(key.expires)

            # [END create_key]
            # [START create_rsa_key]

            key_size = 2048
            key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]

            # create an rsa key with size specification
            # RSA key can be created with default size of '2048'
            key = await key_client.create_rsa_key("key-name", hsm=True, size=key_size, enabled=True, key_ops=key_ops)

            print(key.id)
            print(key.version)
            # when hsm=True, key_type = RSA-HSM
            print(key.key_material.kty)
            print(key.key_material.key_ops)

            # [END create_rsa_key]

            # [START create_ec_key]
            from dateutil import parser as date_parse

            key_curve = "P-256"

            # create an ec (Elliptic curve) key with curve specification
            # EC key can be created with default curve of 'P-256'
            ec_key = await key_client.create_ec_key("key-name", hsm=False, curve=key_curve)

            print(ec_key.id)
            print(ec_key.version)
            # when hsm=False, key_type = EC
            print(ec_key.key_material.kty)
            print(ec_key.key_material.crv)

            # [END create_ec_key]
        except HttpResponseError:
            pass

        try:
            # [START get_key]

            # if no version is specified the latest
            # version of the key will be returned
            key = await key_client.get_key("key-name")

            # get key with version
            key_version = key.version
            key = await key_client.get_key("key-name", key_version)

            print(key.id)
            print(key.name)
            print(key.version)
            print(key.key_material.kty)
            print(key.vault_url)
            # [END get_key]

            # [START import_key]
            def _to_bytes(hex):
                if len(hex) % 2:
                    hex = "0{}".format(hex)
                return codecs.decode(hex, "hex_codec")

            json_web_key = JsonWebKey(
                kty="RSA",
                key_ops=["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"],
                n=_to_bytes(
                    "00a0914d00234ac683b21b4c15d5bed887bdc959c2e57af54ae734e8f00720d775d275e455207e3784ceeb60a50a4655dd72a7a94d271e8ee8f7959a669ca6e775bf0e23badae991b4529d978528b4bd90521d32dd2656796ba82b6bbfc7668c8f5eeb5053747fd199319d29a8440d08f4412d527ff9311eda71825920b47b1c46b11ab3e91d7316407e89c7f340f7b85a34042ce51743b27d4718403d34c7b438af6181be05e4d11eb985d38253d7fe9bf53fc2f1b002d22d2d793fa79a504b6ab42d0492804d7071d727a06cf3a8893aa542b1503f832b296371b6707d4dc6e372f8fe67d8ded1c908fde45ce03bc086a71487fa75e43aa0e0679aa0d20efe35"
                ),
                e=_to_bytes("10001"),
                d=_to_bytes(
                    "627c7d24668148fe2252c7fa649ea8a5a9ed44d75c766cda42b29b660e99404f0e862d4561a6c95af6a83d213e0a2244b03cd28576473215073785fb067f015da19084ade9f475e08b040a9a2c7ba00253bb8125508c9df140b75161d266be347a5e0f6900fe1d8bbf78ccc25eeb37e0c9d188d6e1fc15169ba4fe12276193d77790d2326928bd60d0d01d6ead8d6ac4861abadceec95358fd6689c50a1671a4a936d2376440a41445501da4e74bfb98f823bd19c45b94eb01d98fc0d2f284507f018ebd929b8180dbe6381fdd434bffb7800aaabdd973d55f9eaf9bb88a6ea7b28c2a80231e72de1ad244826d665582c2362761019de2e9f10cb8bcc2625649"
                ),
                p=_to_bytes(
                    "00d1deac8d68ddd2c1fd52d5999655b2cf1565260de5269e43fd2a85f39280e1708ffff0682166cb6106ee5ea5e9ffd9f98d0becc9ff2cda2febc97259215ad84b9051e563e14a051dce438bc6541a24ac4f014cf9732d36ebfc1e61a00d82cbe412090f7793cfbd4b7605be133dfc3991f7e1bed5786f337de5036fc1e2df4cf3"
                ),
                q=_to_bytes(
                    "00c3dc66b641a9b73cd833bc439cd34fc6574465ab5b7e8a92d32595a224d56d911e74624225b48c15a670282a51c40d1dad4bc2e9a3c8dab0c76f10052dfb053bc6ed42c65288a8e8bace7a8881184323f94d7db17ea6dfba651218f931a93b8f738f3d8fd3f6ba218d35b96861a0f584b0ab88ddcf446b9815f4d287d83a3237"
                ),
                dp=_to_bytes(
                    "00c9a159be7265cbbabc9afcc4967eb74fe58a4c4945431902d1142da599b760e03838f8cbd26b64324fea6bdc9338503f459793636e59b5361d1e6951e08ddb089e1b507be952a81fbeaf7e76890ea4f536e25505c3f648b1e88377dfc19b4c304e738dfca07211b792286a392a704d0f444c0a802539110b7f1f121c00cff0a9"
                ),
                dq=_to_bytes(
                    "00a0bd4c0a3d9f64436a082374b5caf2488bac1568696153a6a5e4cd85d186db31e2f58f024c617d29f37b4e6b54c97a1e25efec59c4d1fd3061ac33509ce8cae5c11f4cd2e83f41a8264f785e78dc0996076ee23dfdfc43d67c463afaa0180c4a718357f9a6f270d542479a0f213870e661fb950abca4a14ca290570ba7983347"
                ),
                qi=_to_bytes(
                    "009fe7ae42e92bc04fcd5780464bd21d0c8ac0c599f9af020fde6ab0a7e7d1d39902f5d8fb6c614184c4c1b103fb46e94cd10a6c8a40f9991a1f28269f326435b6c50276fda6493353c650a833f724d80c7d522ba16c79f0eb61f672736b68fb8be3243d10943c4ab7028d09e76cfb5892222e38bc4d35585bf35a88cd68c73b07"
                ),
            )
            # import key
            # If the named key already exists in the Key Vault
            # creates a new version of the key
            imported_key = await key_client.import_key("key-name", json_web_key)

            print(imported_key.id)
            print(imported_key.name)
            print(imported_key.version)
            print(imported_key.key_material.kty)
            print(imported_key.vault_url)
            # [END import_key]

            # [START update_key]

            # update attributes of an existing key
            expires = date_parse.parse("2050-01-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            key_version = key.version
            updated_key = await key_client.update_key(key.name, key_version, expires=expires, tags=tags)

            print(updated_key.version)
            print(updated_key.updated)
            print(updated_key.expires)
            print(updated_key.tags)
            print(key.key_material.kty)

            # [END update_key]
        except ResourceNotFoundError:
            pass

        try:
            # [START delete_key]

            # delete a key
            deleted_key = await key_client.delete_key("key-name")

            print(deleted_key.name)
            # when vault has soft-delete enabled, deleted_key exposes the purge date, recover id
            # and deleted date of the key
            print(deleted_key.deleted_date)
            print(deleted_key.recovery_id)
            print(deleted_key.scheduled_purge_date)

            # [END delete_key]
        except ResourceNotFoundError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_key_list_operations(self, vault_client, **kwargs):
        key_client = vault_client.keys
        try:
            # [START list_keys]

            # list keys
            keys = await key_client.list_keys()

            async for key in keys:
                print(key.id)
                print(key.name)
                print(key.key_material.kty)

            # [END list_keys]
        except HttpResponseError:
            pass

        try:
            # [START list_key_versions]
            # get an iterator of all versions of a key
            key_versions = await key_client.list_key_versions("key-name")

            async for key in key_versions:
                print(key.id)
                print(key.version)
                print(key.key_material.kty)

            # [END list_key_versions]
        except HttpResponseError:
            pass

        try:
            # [START list_deleted_keys]

            # get an iterator of DeletedKey (requires soft-delete enabled for the vault)
            deleted_keys = await key_client.list_deleted_keys()

            async for key in deleted_keys:
                print(key.id)
                print(key.name)

            # [END list_deleted_keys]
        except HttpResponseError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_example_keys_backup_restore(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = await key_client.create_key("keyrec", "RSA")
        key_name = created_key.name
        try:
            # [START backup_key]
            # backup key
            key_backup = await key_client.backup_key(key_name)

            # returns the raw bytes of the backed up key
            print(key_backup)

            # [END backup_key]

            await key_client.delete_key("keyrec")
            if self.is_live:
                # wait a second to ensure the key has been deleted
                time.sleep(20)
            # [START restore_key]

            # restores a backed up key
            restored_key = await key_client.restore_key(key_backup)
            print(restored_key.id)
            print(restored_key.version)

            # [END restore_key]
        except ResourceExistsError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_keys_recover_purge(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = await key_client.create_key("key-name", "RSA")
        if self.is_live:
            # wait a second to ensure the key has been created
            time.sleep(20)
        await key_client.delete_key(created_key.name)
        if self.is_live:
            # wait a second to ensure the key has been deleted
            time.sleep(30)

        try:
            # [START get_deleted_key]
            # gets a deleted key (requires soft-delete enabled for the vault)
            deleted_key = await key_client.get_deleted_key("key-name")
            print(deleted_key.name)

            # [END get_deleted_key]
        except ResourceNotFoundError:
            pass

        try:
            # [START recover_deleted_key]

            # recover deleted key to its latest version
            recover_deleted_key = await key_client.recover_deleted_key("key-name")
            print(recover_deleted_key.id)
            print(recover_deleted_key.name)

            # [END recover_deleted_key]
        except HttpResponseError:
            pass

        try:
            if self.is_live:
                # wait a second to ensure the key has been recovered
                time.sleep(20)
            await key_client.delete_key("key-name")
            if self.is_live:
                # wait a second to ensure the key has been deleted
                time.sleep(20)
            # [START purge_deleted_key]

            # if the vault has soft-delete enabled, purge permanently deletes the key
            # (without soft-delete, an ordinary delete is permanent)
            # key must be deleted prior to be purged
            await key_client.purge_deleted_key("key-name")

            # [END purge_deleted_key]
        except HttpResponseError:
            pass