# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import codecs
import logging
import json
from dateutil import parser as date_parse

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.keyvault.keys import JsonWebKey, KeyCurveName
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.keys._shared import HttpChallengeCache
from devtools_testutils import PowerShellPreparer

from _shared.test_case_async import KeyVaultTestCase

KeyVaultPreparer = functools.partial(
    PowerShellPreparer,
    "keyvault",
    azure_keyvault_url="https://vaultname.vault.azure.net"
)

# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class KeyVaultKeyTest(KeyVaultTestCase):
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeyVaultKeyTest, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(KeyClient, is_async=True)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _assert_jwks_equal(self, jwk1, jwk2):
        assert jwk1.kid == jwk2.kid
        assert jwk1.kty == jwk2.kty
        assert jwk1.key_ops == jwk2.key_ops
        assert jwk1.n == jwk2.n
        assert jwk1.e == jwk2.e
        assert jwk1.d == jwk2.d
        assert jwk1.dp == jwk2.dp
        assert jwk1.dq == jwk2.dq
        assert jwk1.qi == jwk2.qi
        assert jwk1.p == jwk2.p
        assert jwk1.q == jwk2.q
        assert jwk1.k == jwk2.k
        assert jwk1.t == jwk2.t
        assert jwk1.crv == jwk2.crv
        assert jwk1.x == jwk2.x
        assert jwk1.y == jwk2.y

    def _assert_key_attributes_equal(self, k1, k2):
        self.assertEqual(k1.name, k2.name)
        self.assertEqual(k1.vault_url, k2.vault_url)
        self.assertEqual(k1.enabled, k2.enabled)
        self.assertEqual(k1.not_before, k2.not_before)
        self.assertEqual(k1.expires_on, k2.expires_on)
        self.assertEqual(k1.created_on, k2.created_on)
        self.assertEqual(k1.updated_on, k2.updated_on)
        self.assertEqual(k1.tags, k2.tags)
        self.assertEqual(k1.recovery_level, k2.recovery_level)

    async def _create_rsa_key(self, client, key_name, **kwargs):
        key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        hsm = kwargs.get("hardware_protected") or False
        if self.is_live:
            await asyncio.sleep(2)  # to avoid throttling by the service
        created_key = await client.create_rsa_key(key_name, **kwargs)
        key_type = "RSA-HSM" if hsm else "RSA"
        self._validate_rsa_key_bundle(created_key, client.vault_url, key_name, key_type, key_ops)
        return created_key

    async def _create_ec_key(self, client, key_name, **kwargs):
        key_curve = kwargs.get("curve") or "P-256"
        hsm = kwargs.get("hardware_protected") or False
        if self.is_live:
            await asyncio.sleep(2)  # to avoid throttling by the service
        created_key = await client.create_ec_key(key_name, **kwargs)
        key_type = "EC-HSM" if hsm else "EC"
        self._validate_ec_key_bundle(key_curve, created_key, client.vault_url, key_name, key_type)
        return created_key

    def _validate_ec_key_bundle(self, key_curve, key_attributes, vault, key_name, kty):
        prefix = "/".join(s.strip("/") for s in [vault, "keys", key_name])
        key = key_attributes.key
        kid = key_attributes.id
        self.assertEqual(key_curve, key.crv)
        self.assertTrue(kid.index(prefix) == 0, "Key Id should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(
            key_attributes.properties.created_on and key_attributes.properties.updated_on,
            "Missing required date attributes.",
        )

    def _validate_rsa_key_bundle(self, key_attributes, vault, key_name, kty, key_ops):
        prefix = "/".join(s.strip("/") for s in [vault, "keys", key_name])
        key = key_attributes.key
        kid = key_attributes.id
        self.assertTrue(kid.index(prefix) == 0, "Key Id should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key.n and key.e, "Bad RSA public material.")
        self.assertEqual(key_ops, key.key_ops, "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops))
        self.assertTrue(
            key_attributes.properties.created_on and key_attributes.properties.updated_on,
            "Missing required date attributes.",
        )

    async def _update_key_properties(self, client, key):
        expires = date_parse.parse("2050-01-02T08:00:00.000Z")
        tags = {"foo": "updated tag"}
        key_bundle = await client.update_key_properties(key.name, expires_on=expires, tags=tags)
        self.assertEqual(tags, key_bundle.properties.tags)
        self.assertEqual(key.id, key_bundle.id)
        self.assertNotEqual(key.properties.updated_on, key_bundle.properties.updated_on)
        return key_bundle

    async def _validate_key_list(self, keys, expected):
        async for key in keys:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name].properties, key)
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    async def _import_test_key(self, client, name):
        def _to_bytes(hex):
            if len(hex) % 2:
                hex = "0{}".format(hex)
            return codecs.decode(hex, "hex_codec")

        key = JsonWebKey(
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
        imported_key = await client.import_key(name, key)
        self._validate_rsa_key_bundle(imported_key, client.vault_url, name, "RSA", key.key_ops)
        return imported_key

    @KeyVaultPreparer()
    async def test_key_crud_operations(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        # create ec key
        ec_key_name = self.get_resource_name("crud-ec-key")
        tags = {"purpose": "unit test", "test name": "CreateECKeyTest"}
        ec_key = await self._create_ec_key(
            client, enabled=True, key_name=ec_key_name, hardware_protected=True, tags=tags
        )
        assert ec_key.properties.enabled
        assert tags == ec_key.properties.tags
        # create ec with curve
        ec_key_curve_name = self.get_resource_name("crud-P-256-ec-key")
        created_ec_key_curve = await self._create_ec_key(client, key_name=ec_key_curve_name, curve="P-256")
        self.assertEqual("P-256", created_ec_key_curve.key.crv)

        # import key
        import_test_key_name = self.get_resource_name("import-test-key")
        await self._import_test_key(client, import_test_key_name)

        # create rsa key
        rsa_key_name = self.get_resource_name("crud-rsa-key")
        tags = {"purpose": "unit test", "test name ": "CreateRSAKeyTest"}
        key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        rsa_key = await self._create_rsa_key(
            client, key_name=rsa_key_name, key_operations=key_ops, size=2048, tags=tags
        )
        assert tags == rsa_key.properties.tags

        # get the created key with version
        key = await client.get_key(rsa_key.name, rsa_key.properties.version)
        self.assertEqual(key.properties.version, rsa_key.properties.version)
        self._assert_key_attributes_equal(rsa_key.properties, key.properties)

        # get key without version
        self._assert_key_attributes_equal(
            rsa_key.properties, (await client.get_key(rsa_key.name)).properties
        )

        # update key with version
        if self.is_live:
            # wait to ensure the key's update time won't equal its creation time
            await asyncio.sleep(1)

        await self._update_key_properties(client, rsa_key)

        # delete the new key
        deleted_key = await client.delete_key(rsa_key.name)
        self.assertIsNotNone(deleted_key)
        self._assert_jwks_equal(rsa_key.key, deleted_key.key)
        self.assertEqual(deleted_key.id, rsa_key.id)
        self.assertTrue(
            deleted_key.recovery_id and deleted_key.deleted_date and deleted_key.scheduled_purge_date,
            "Missing required deleted key attributes.",
        )

        # get the deleted key when soft deleted enabled
        deleted_key = await client.get_deleted_key(rsa_key.name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(rsa_key.id, deleted_key.id)

    @KeyVaultPreparer()
    async def test_backup_restore(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        key_name = self.get_resource_name("keybak")

        # create key
        created_bundle = await self._create_rsa_key(client, key_name)

        # backup key
        key_backup = await client.backup_key(created_bundle.name)
        self.assertIsNotNone(key_backup, "key_backup")

        # delete key
        await client.delete_key(created_bundle.name)

        # purge key
        await client.purge_deleted_key(created_bundle.name)

        # restore key
        restore_function = functools.partial(client.restore_key_backup, key_backup)
        restored_key = await self._poll_until_no_exception(restore_function, expected_exception=ResourceExistsError)
        self._assert_key_attributes_equal(created_bundle.properties, restored_key.properties)

    @KeyVaultPreparer()
    async def test_key_list(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(max_keys):
            key_name = self.get_resource_name("key{}".format(x))
            key = await self._create_rsa_key(client, key_name)
            expected[key.name] = key

        # list keys
        result = client.list_properties_of_keys(max_page_size=max_keys - 1)
        async for key in result:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name].properties, key)
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    @KeyVaultPreparer()
    async def test_list_versions(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        key_name = self.get_resource_name("testKey")

        max_keys = self.list_test_size
        expected = {}

        # create many key versions
        for _ in range(max_keys):
            key = await self._create_rsa_key(client, key_name)
            expected[key.id] = key

        result = client.list_properties_of_key_versions(key_name, max_page_size=max_keys - 1)

        # validate list key versions with attributes
        async for key in result:
            if key.id in expected.keys():
                expected_key = expected[key.id]
                del expected[key.id]
                self._assert_key_attributes_equal(expected_key.properties, key)
        self.assertEqual(0, len(expected))

    @KeyVaultPreparer()
    async def test_list_deleted_keys(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        expected = {}

        # create keys to delete
        for i in range(self.list_test_size):
            key_name = self.get_resource_name("key{}".format(i))
            expected[key_name] = await self._create_rsa_key(client, key_name)

        # delete all keys
        for key_name in expected.keys():
            await client.delete_key(key_name)

        # validate list deleted keys with attributes
        async for deleted_key in client.list_deleted_keys():
            self.assertIsNotNone(deleted_key.deleted_date)
            self.assertIsNotNone(deleted_key.scheduled_purge_date)
            self.assertIsNotNone(deleted_key.recovery_id)

        # validate all our deleted keys are returned by list_deleted_keys
        result = client.list_deleted_keys()
        async for key in result:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name].properties, key.properties)
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    @KeyVaultPreparer()
    async def test_recover(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        # create keys
        keys = {}
        for i in range(self.list_test_size):
            key_name = self.get_resource_name("key{}".format(i))
            keys[key_name] = await self._create_rsa_key(client, key_name)

        # delete them
        for key_name in keys.keys():
            await client.delete_key(key_name)

        # recover them
        for key_name in keys.keys():
            recovered_key = await client.recover_deleted_key(key_name)
            expected_key = keys[key_name]
            self._assert_key_attributes_equal(expected_key.properties, recovered_key.properties)

        # validate the recovered keys
        expected = {k: v for k, v in keys.items()}
        actual = {}
        for k in expected.keys():
            actual[k] = await client.get_key(k)

        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @KeyVaultPreparer()
    async def test_purge(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)
        self.assertIsNotNone(client)

        # create keys
        key_names = [self.get_resource_name("key{}".format(i)) for i in range(self.list_test_size)]
        for key_name in key_names:
            await self._create_rsa_key(client, key_name)

        # delete them
        for key_name in key_names:
            await client.delete_key(key_name)

        # purge them
        for key_name in key_names:
            await client.purge_deleted_key(key_name)
        for key_name in key_names:
            await self._poll_until_exception(
                functools.partial(client.get_deleted_key, key_name), expected_exception=ResourceNotFoundError
            )

        # validate none are returned by list_deleted_keys
        async for deleted_key in client.list_deleted_keys():
            assert deleted_key.name not in key_names

    @KeyVaultPreparer()
    async def test_logging_enabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=True)
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        rsa_key_name = self.get_resource_name("rsa-key-name")
        await self._create_rsa_key(client, rsa_key_name, size=2048)

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    if body["kty"] == "RSA":
                        return
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass

        assert False, "Expected request body wasn't logged"

    @KeyVaultPreparer()
    async def test_logging_disabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=False)
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        rsa_key_name = self.get_resource_name("rsa-key-name")
        await self._create_rsa_key(client, rsa_key_name, size=2048)

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    assert body["kty"] != "RSA", "Client request body was logged"
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = KeyClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = KeyClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
