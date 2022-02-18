# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import codecs
from dateutil import parser as date_parse
import functools
import json
import logging
import time

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.keyvault.keys import (
    ApiVersion,
    JsonWebKey,
    KeyClient,
    KeyReleasePolicy,
    KeyRotationLifetimeAction,
    KeyRotationPolicyAction,
)
import pytest
from six import byte2int

from _shared.test_case import KeyVaultTestCase
from _test_case import client_setup, get_attestation_token, get_decorator, get_release_policy, is_public_cloud, KeysTestCase


all_api_versions = get_decorator()
only_hsm = get_decorator(only_hsm=True)
only_hsm_7_3_preview = get_decorator(only_hsm=True, api_versions=[ApiVersion.V7_3_PREVIEW])
only_vault_7_3_preview = get_decorator(only_vault=True, api_versions=[ApiVersion.V7_3_PREVIEW])
only_7_3_preview = get_decorator(api_versions=[ApiVersion.V7_3_PREVIEW])
logging_enabled = get_decorator(logging_enable=True)
logging_disabled = get_decorator(logging_enable=False)


def _assert_rotation_policies_equal(p1, p2):
    assert p1.id == p2.id
    assert p1.expires_in == p2.expires_in
    assert p1.created_on == p2.created_on
    assert p1.updated_on == p2.updated_on
    assert len(p1.lifetime_actions) == len(p2.lifetime_actions)

def _assert_lifetime_actions_equal(a1, a2):
    assert a1.action == a2.action
    assert a1.time_after_create == a2.time_after_create
    assert a1.time_before_expiry == a2.time_before_expiry


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class KeyClientTests(KeysTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(KeyClientTests, self).__init__(*args, match_body=False, **kwargs)

    def _assert_jwks_equal(self, jwk1, jwk2):
        for field in JsonWebKey._FIELDS:
            if field != "key_ops":
                assert getattr(jwk1, field) == getattr(jwk2, field)

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

    def _create_rsa_key(self, client, key_name, **kwargs):
        key_ops = kwargs.get("key_operations") or ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        hsm = kwargs.get("hardware_protected") or False
        if self.is_live:
            time.sleep(2)  # to avoid throttling by the service
        created_key = client.create_rsa_key(key_name, **kwargs)
        kty = "RSA-HSM" if hsm else "RSA"
        self._validate_rsa_key_bundle(created_key, client.vault_url, key_name, kty, key_ops)
        return created_key

    def _create_ec_key(self, client, key_name, **kwargs):
        key_curve = kwargs.get("curve") or "P-256"
        hsm = kwargs.get("hardware_protected") or False
        if self.is_live:
            time.sleep(2)  # to avoid throttling by the service
        created_key = client.create_ec_key(key_name, **kwargs)
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
        self.assertEqual(
            sorted(key_ops), sorted(key.key_ops), "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops)
        )
        self.assertTrue(
            key_attributes.properties.created_on and key_attributes.properties.updated_on,
            "Missing required date attributes.",
        )

    def _update_key_properties(self, client, key, release_policy=None):
        expires = date_parse.parse("2050-01-02T08:00:00.000Z")
        tags = {"foo": "updated tag"}
        key_ops = ["decrypt", "encrypt"]

        # wait before updating the key to make sure updated_on has a different value
        if self.is_live:
            time.sleep(2)
        key_bundle = client.update_key_properties(
            key.name, key_operations=key_ops, expires_on=expires, tags=tags, release_policy=release_policy
        )

        assert tags == key_bundle.properties.tags
        assert key.id == key_bundle.id
        assert key.properties.updated_on != key_bundle.properties.updated_on
        assert sorted(key_ops) == sorted(key_bundle.key_operations)
        if release_policy:
            assert key.properties.release_policy.encoded_policy != key_bundle.properties.release_policy.encoded_policy
        return key_bundle

    def _import_test_key(self, client, name, hardware_protected=False, **kwargs):
        def _to_bytes(hex):
            if len(hex) % 2:
                hex = "0{}".format(hex)
            return codecs.decode(hex, "hex_codec")

        key = JsonWebKey(
            kty="RSA-HSM" if hardware_protected else "RSA",
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
        imported_key = client.import_key(name, key, **kwargs)
        self._validate_rsa_key_bundle(imported_key, client.vault_url, name, key.kty, key.key_ops)
        return imported_key

    @all_api_versions()
    @client_setup
    def test_key_crud_operations(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        # create ec key
        ec_key_name = self.get_resource_name("crud-ec-key")
        tags = {"purpose": "unit test", "test name": "CreateECKeyTest"}
        ec_key = self._create_ec_key(client, enabled=True, key_name=ec_key_name, hardware_protected=is_hsm, tags=tags)
        assert ec_key.properties.enabled
        assert tags == ec_key.properties.tags
        # create ec with curve
        ec_key_curve_name = self.get_resource_name("crud-P-256-ec-key")
        created_ec_key_curve = self._create_ec_key(
            client, key_name=ec_key_curve_name, curve="P-256", hardware_protected=is_hsm
        )
        self.assertEqual("P-256", created_ec_key_curve.key.crv)

        # import key
        import_test_key_name = self.get_resource_name("import-test-key")
        self._import_test_key(client, import_test_key_name, hardware_protected=is_hsm)

        # create rsa key
        rsa_key_name = self.get_resource_name("crud-rsa-key")
        tags = {"purpose": "unit test", "test name ": "CreateRSAKeyTest"}
        key_ops = ["encrypt","decrypt","sign","verify","wrapKey","unwrapKey"]
        rsa_key = self._create_rsa_key(
            client, key_name=rsa_key_name, key_operations=key_ops, size=2048, tags=tags, hardware_protected=is_hsm
        )
        assert tags == rsa_key.properties.tags

        # get the created key with version
        key = client.get_key(rsa_key.name, rsa_key.properties.version)
        self.assertEqual(key.properties.version, rsa_key.properties.version)
        self._assert_key_attributes_equal(rsa_key.properties, key.properties)

        # get key without version
        self._assert_key_attributes_equal(rsa_key.properties, client.get_key(rsa_key.name).properties)

        # update key with version
        if self.is_live:
            # wait to ensure the key's update time won't equal its creation time
            time.sleep(1)

        self._update_key_properties(client, rsa_key)

        # delete the new key
        deleted_key_poller = client.begin_delete_key(rsa_key.name)
        deleted_key = deleted_key_poller.result()
        self.assertIsNotNone(deleted_key)

        # aside from key_ops, the original updated keys should have the same JWKs
        self._assert_jwks_equal(rsa_key.key, deleted_key.key)
        self.assertEqual(deleted_key.id, rsa_key.id)
        self.assertTrue(
            deleted_key.recovery_id and deleted_key.deleted_date and deleted_key.scheduled_purge_date,
            "Missing required deleted key attributes.",
        )
        deleted_key_poller.wait()

        # get the deleted key when soft deleted enabled
        deleted_key = client.get_deleted_key(rsa_key.name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(rsa_key.id, deleted_key.id)

    @only_hsm()
    @client_setup
    def test_rsa_public_exponent(self, client, **kwargs):
        """The public exponent of a Managed HSM RSA key can be specified during creation"""
        self.assertIsNotNone(client)

        key_name = self.get_resource_name("rsa-key")
        key = self._create_rsa_key(client, key_name, hardware_protected=True, public_exponent=17)
        public_exponent = byte2int(key.key.e)
        assert public_exponent == 17

    @all_api_versions()
    @client_setup
    def test_backup_restore(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        key_name = self.get_resource_name("keybak")

        # create key
        created_bundle = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)

        # backup key
        key_backup = client.backup_key(created_bundle.name)
        self.assertIsNotNone(key_backup, "key_backup")

        # delete key
        client.begin_delete_key(created_bundle.name).wait()

        # purge key
        client.purge_deleted_key(created_bundle.name)

        # restore key
        restore_function = functools.partial(client.restore_key_backup, key_backup)
        restored_key = self._poll_until_no_exception(restore_function, ResourceExistsError)
        self._assert_key_attributes_equal(created_bundle.properties, restored_key.properties)

    @all_api_versions()
    @client_setup
    def test_key_list(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(max_keys):
            key_name = self.get_resource_name("key{}".format(x))
            key = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)
            expected[key.name] = key

        # list keys
        result = client.list_properties_of_keys(max_page_size=max_keys - 1)
        for key in result:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name].properties, key)
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    @all_api_versions()
    @client_setup
    def test_list_versions(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        key_name = self.get_resource_name("testKey")

        max_keys = self.list_test_size
        expected = {}

        # create many key versions
        for _ in range(max_keys):
            key = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)
            expected[key.id] = key

        result = client.list_properties_of_key_versions(key_name, max_page_size=max_keys - 1)

        # validate list key versions with attributes
        for key in result:
            if key.id in expected.keys():
                expected_key = expected[key.id]
                del expected[key.id]
                self._assert_key_attributes_equal(expected_key.properties, key)
        self.assertEqual(0, len(expected))

    @all_api_versions()
    @client_setup
    def test_list_deleted_keys(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        expected = {}

        # create keys
        for i in range(self.list_test_size):
            key_name = self.get_resource_name("key{}".format(i))
            expected[key_name] = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)

        # delete them
        for key_name in expected.keys():
            client.begin_delete_key(key_name).wait()

        # validate list deleted keys with attributes
        for deleted_key in client.list_deleted_keys():
            self.assertIsNotNone(deleted_key.deleted_date)
            self.assertIsNotNone(deleted_key.scheduled_purge_date)
            self.assertIsNotNone(deleted_key.recovery_id)

        result = client.list_deleted_keys()
        # validate all the deleted keys are returned by list_deleted_keys
        for key in result:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name].properties, key.properties)
                del expected[key.name]

    @all_api_versions()
    @client_setup
    def test_recover(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        # create keys
        keys = {}
        for i in range(self.list_test_size):
            key_name = self.get_resource_name("key{}".format(i))
            keys[key_name] = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)

        # delete them
        for key_name in keys.keys():
            client.begin_delete_key(key_name).wait()

        # validate the deleted keys are returned by list_deleted_keys
        deleted = [s.name for s in client.list_deleted_keys()]
        self.assertTrue(all(s in deleted for s in keys.keys()))

        # recover the keys
        for key_name in keys.keys():
            recovered_key = client.begin_recover_deleted_key(key_name).result()
            expected_key = keys[key_name]
            self._assert_key_attributes_equal(expected_key.properties, recovered_key.properties)

    @all_api_versions()
    @client_setup
    def test_purge(self, client, is_hsm, **kwargs):
        self.assertIsNotNone(client)

        # create keys
        key_names = [self.get_resource_name("key{}".format(i)) for i in range(self.list_test_size)]
        for name in key_names:
            self._create_rsa_key(client, name, hardware_protected=is_hsm)

        # delete them
        for key_name in key_names:
            client.begin_delete_key(key_name).wait()

        # validate all our deleted keys are returned by list_deleted_keys
        deleted = [k.name for k in client.list_deleted_keys()]
        self.assertTrue(all(n in deleted for n in key_names))

        # purge them
        for key_name in key_names:
            client.purge_deleted_key(key_name)
        for key_name in key_names:
            self._poll_until_exception(
                functools.partial(client.get_deleted_key, key_name), expected_exception=ResourceNotFoundError
            )

        # validate none are returned by list_deleted_keys
        deleted = [s.name for s in client.list_deleted_keys()]
        self.assertTrue(not any(s in deleted for s in key_names))

    @logging_enabled()
    @client_setup
    def test_logging_enabled(self, client, is_hsm, **kwargs):
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        rsa_key_name = self.get_resource_name("rsa-key-name")
        self._create_rsa_key(client, rsa_key_name, size=2048, hardware_protected=is_hsm)

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                request_sections = message.message.split("/n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        expected_kty = "RSA-HSM" if is_hsm else "RSA"
                        if body["kty"] == expected_kty:
                            mock_handler.close()
                            return
                    except (ValueError, KeyError):
                        # this means the request section is not JSON or has no kty property
                        pass

        mock_handler.close()
        assert False, "Expected request body wasn't logged"

    @logging_disabled()
    @client_setup
    def test_logging_disabled(self, client, is_hsm, **kwargs):
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        rsa_key_name = self.get_resource_name("rsa-key-name")
        self._create_rsa_key(client, rsa_key_name, size=2048, hardware_protected=is_hsm)

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                # parts of the request are logged on new lines in a single message
                request_sections = message.message.split("/n")
                for section in request_sections:
                    try:
                        # the body of the request should be JSON
                        body = json.loads(section)
                        expected_kty = "RSA-HSM" if is_hsm else "RSA"
                        if body["kty"] == expected_kty:
                            mock_handler.close()
                            assert False, "Client request body was logged"
                    except (ValueError, KeyError):
                        # this means the request section is not JSON or has no kty property
                        pass

        mock_handler.close()

    @only_hsm_7_3_preview()
    @client_setup
    def test_get_random_bytes(self, client, **kwargs):
        assert client

        generated_random_bytes = []
        for i in range(5):
            # [START get_random_bytes]
            # get eight random bytes from a managed HSM
            random_bytes = client.get_random_bytes(count=8)
            # [END get_random_bytes]
            assert len(random_bytes) == 8
            assert all(random_bytes != rb for rb in generated_random_bytes)
            generated_random_bytes.append(random_bytes)

    @only_7_3_preview()
    @client_setup
    def test_key_release(self, client, **kwargs):
        attestation_uri = self._get_attestation_uri()
        attestation = get_attestation_token(attestation_uri)
        release_policy = get_release_policy(attestation_uri)

        rsa_key_name = self.get_resource_name("rsa-key-name")
        key = self._create_rsa_key(
            client, rsa_key_name, hardware_protected=True, exportable=True, release_policy=release_policy
        )
        assert key.properties.release_policy
        assert key.properties.release_policy.encoded_policy
        assert key.properties.exportable

        release_result = client.release_key(rsa_key_name, attestation)
        assert release_result.value

    @only_hsm_7_3_preview()
    @client_setup
    def test_imported_key_release(self, client, **kwargs):
        attestation_uri = self._get_attestation_uri()
        attestation = get_attestation_token(attestation_uri)
        release_policy = get_release_policy(attestation_uri)

        imported_key_name = self.get_resource_name("imported-key-name")
        key = self._import_test_key(
            client, imported_key_name, hardware_protected=True, exportable=True, release_policy=release_policy
        )
        assert key.properties.release_policy
        assert key.properties.release_policy.encoded_policy
        assert key.properties.exportable

        release_result = client.release_key(imported_key_name, attestation)
        assert release_result.value

    @only_7_3_preview()
    @client_setup
    def test_update_release_policy(self, client, **kwargs):
        attestation_uri = self._get_attestation_uri()
        release_policy = get_release_policy(attestation_uri)
        key_name = self.get_resource_name("key-name")
        key = self._create_rsa_key(
            client, key_name, hardware_protected=True, exportable=True, release_policy=release_policy
        )

        policy = json.loads(key.properties.release_policy.encoded_policy.decode())
        claim_condition = policy["anyOf"][0]["anyOf"][0]["equals"]
        # for some reason, claim_condition may be 'true' here for KV, but should be True here for MHSM
        claim_condition = claim_condition if isinstance(claim_condition, bool) else json.loads(claim_condition)
        assert claim_condition is True

        new_release_policy_json = {
            "anyOf": [
                {
                    "anyOf": [
                        {
                            "claim": "sdk-test",
                            "equals": False
                        }
                    ],
                    "authority": attestation_uri.rstrip("/") + "/"
                }
            ],
            "version": "1.0.0"
        }
        policy_string = json.dumps(new_release_policy_json).encode()
        new_release_policy = KeyReleasePolicy(policy_string)

        updated_key = self._update_key_properties(client, key, new_release_policy)
        updated_policy = json.loads(updated_key.properties.release_policy.encoded_policy.decode())
        claim_condition = updated_policy["anyOf"][0]["anyOf"][0]["equals"]
        claim_condition = claim_condition if isinstance(claim_condition, bool) else json.loads(claim_condition)
        assert claim_condition is False

    # Immutable policies aren't currently supported on Managed HSM
    @only_vault_7_3_preview()
    @client_setup
    def test_immutable_release_policy(self, client, **kwargs):
        attestation_uri = self._get_attestation_uri()
        release_policy = get_release_policy(attestation_uri, immutable=True)
        key_name = self.get_resource_name("key-name")
        key = self._create_rsa_key(
            client, key_name, hardware_protected=True, exportable=True, release_policy=release_policy
        )
        assert key.properties.release_policy.encoded_policy
        assert key.properties.release_policy.immutable

        new_release_policy_json = {
            "anyOf": [
                {
                    "anyOf": [
                        {
                            "claim": "sdk-test",
                            "equals": False
                        }
                    ],
                    "authority": attestation_uri.rstrip("/") + "/"
                }
            ],
            "version": "1.0.0"
        }
        policy_string = json.dumps(new_release_policy_json).encode()
        new_release_policy = KeyReleasePolicy(policy_string, immutable=True)

        with pytest.raises(HttpResponseError):
            self._update_key_properties(client, key, new_release_policy)

    @only_vault_7_3_preview()
    @client_setup
    def test_key_rotation(self, client, **kwargs):
        if (not is_public_cloud() and self.is_live):
            pytest.skip("This test not supprot in usgov/china region. Follow up with service team.")

        key_name = self.get_resource_name("rotation-key")
        key = self._create_rsa_key(client, key_name)
        rotated_key = client.rotate_key(key_name)

        # the rotated key should have a new ID, version, and key material (for RSA, n and e fields)
        assert key.id != rotated_key.id
        assert key.properties.version != rotated_key.properties.version
        assert key.key.n != rotated_key.key.n

    @only_vault_7_3_preview()
    @client_setup
    def test_key_rotation_policy(self, client, **kwargs):
        if (not is_public_cloud() and self.is_live):
            pytest.skip("This test not supprot in usgov/china region. Follow up with service team.")

        key_name = self.get_resource_name("rotation-key")
        self._create_rsa_key(client, key_name)

        actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE, time_after_create="P2M")]
        updated_policy = client.update_key_rotation_policy(key_name, lifetime_actions=actions)
        fetched_policy = client.get_key_rotation_policy(key_name)
        assert updated_policy.expires_in is None
        _assert_rotation_policies_equal(updated_policy, fetched_policy)

        updated_policy_actions = updated_policy.lifetime_actions[0]
        fetched_policy_actions = fetched_policy.lifetime_actions[0]
        assert updated_policy_actions.action == KeyRotationPolicyAction.ROTATE
        assert updated_policy_actions.time_after_create == "P2M"
        assert updated_policy_actions.time_before_expiry is None
        _assert_lifetime_actions_equal(updated_policy_actions, fetched_policy_actions)

        new_actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.NOTIFY, time_before_expiry="P30D")]
        new_policy = client.update_key_rotation_policy(key_name, expires_in="P90D", lifetime_actions=new_actions)
        new_fetched_policy = client.get_key_rotation_policy(key_name)
        assert new_policy.expires_in == "P90D"
        _assert_rotation_policies_equal(new_policy, new_fetched_policy)

        new_policy_actions = new_policy.lifetime_actions[0]
        new_fetched_policy_actions = new_fetched_policy.lifetime_actions[0]
        assert new_policy_actions.action == KeyRotationPolicyAction.NOTIFY
        assert new_policy_actions.time_after_create is None
        assert new_policy_actions.time_before_expiry == "P30D"
        _assert_lifetime_actions_equal(new_policy_actions, new_fetched_policy_actions)

    @all_api_versions()
    @client_setup
    def test_get_cryptography_client(self, client, is_hsm, **kwargs):
        key_name = self.get_resource_name("key-name")
        key = self._create_rsa_key(client, key_name, hardware_protected=is_hsm)

        # try specifying the key version
        crypto_client = client.get_cryptography_client(key_name, key_version=key.properties.version)
        # both clients should use the same generated client
        assert client._client == crypto_client._client

        # the crypto client should successfully perform crypto operations
        plaintext = b"plaintext"
        result = crypto_client.encrypt("RSA-OAEP", plaintext)
        assert result.key_id == key.id

        result = crypto_client.decrypt(result.algorithm, result.ciphertext)
        assert result.key_id == key.id
        assert "RSA-OAEP" == result.algorithm
        assert plaintext == result.plaintext

        # try ommitting the key version
        crypto_client = client.get_cryptography_client(key_name)
        # both clients should use the same generated client
        assert client._client == crypto_client._client

        # the crypto client should successfully perform crypto operations
        result = crypto_client.encrypt("RSA-OAEP", plaintext)
        assert result.key_id == key.id

        result = crypto_client.decrypt(result.algorithm, result.ciphertext)
        assert result.key_id == key.id
        assert "RSA-OAEP" == result.algorithm
        assert plaintext == result.plaintext


def test_positive_bytes_count_required():
    client = KeyClient("...", object())
    with pytest.raises(ValueError):
        client.get_random_bytes(count=0)
    with pytest.raises(ValueError):
        client.get_random_bytes(count=-1)


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = KeyClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = KeyClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
