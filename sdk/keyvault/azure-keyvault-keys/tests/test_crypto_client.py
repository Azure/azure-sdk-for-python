# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import codecs
import hashlib
import os

from azure.keyvault.keys import JsonWebKey, KeyCurveName, KeyVaultKey
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
from azure.mgmt.keyvault.models import KeyPermissions, Permissions
from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from keys_preparer import VaultClientPreparer
from keys_test_case import KeyVaultTestCase

# without keys/get, a CryptographyClient created with a key ID performs all ops remotely
NO_GET = Permissions(keys=[p.value for p in KeyPermissions if p.value != "get"])


class CryptoClientTests(KeyVaultTestCase):
    plaintext = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"

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

    def _import_test_key(self, client, name):
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
        imported_key = client.import_key(name, key)
        self._validate_rsa_key_bundle(imported_key, client.vault_url, name, key.kty, key.key_ops)
        return imported_key

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer(permissions=NO_GET)
    @VaultClientPreparer()
    def test_encrypt_and_decrypt(self, vault_client, **kwargs):
        # TODO: use iv, authentication_data
        key_name = self.get_resource_name("keycrypt")
        key_client = vault_client.keys

        imported_key = self._import_test_key(key_client, key_name)
        crypto_client = vault_client.get_cryptography_client(imported_key.id)

        result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, self.plaintext)
        self.assertEqual(result.key_id, imported_key.id)

        result = crypto_client.decrypt(result.algorithm, result.ciphertext)
        self.assertEqual(result.key_id, imported_key.id)
        self.assertEqual(EncryptionAlgorithm.rsa_oaep, result.algorithm)
        self.assertEqual(self.plaintext, result.plaintext)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer(permissions=NO_GET)
    @VaultClientPreparer()
    def test_sign_and_verify(self, vault_client, **kwargs):
        key_client = vault_client.keys

        key_name = self.get_resource_name("keysign")

        md = hashlib.sha256()
        md.update(self.plaintext)
        digest = md.digest()

        imported_key = self._import_test_key(key_client, key_name)
        crypto_client = vault_client.get_cryptography_client(imported_key.id)

        result = crypto_client.sign(SignatureAlgorithm.rs256, digest)
        self.assertEqual(result.key_id, imported_key.id)

        verified = crypto_client.verify(result.algorithm, digest, result.signature)
        self.assertEqual(result.key_id, imported_key.id)
        self.assertEqual(result.algorithm, SignatureAlgorithm.rs256)
        self.assertTrue(verified.is_valid)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer(permissions=NO_GET)
    @VaultClientPreparer()
    def test_wrap_and_unwrap(self, vault_client, **kwargs):
        key_name = self.get_resource_name("keywrap")
        key_client = vault_client.keys

        created_key = key_client.create_key(key_name, "RSA")
        self.assertIsNotNone(created_key)
        crypto_client = vault_client.get_cryptography_client(created_key.id)

        # Wrap a key with the created key, then unwrap it. The wrapped key's bytes should round-trip.
        key_bytes = self.plaintext
        result = crypto_client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
        self.assertEqual(result.key_id, created_key.id)

        result = crypto_client.unwrap_key(result.algorithm, result.encrypted_key)
        self.assertEqual(key_bytes, result.key)

    def test_symmetric_wrap_and_unwrap_local(self, **kwargs):
        jwk = {"k": os.urandom(32), "kty": "oct", "key_ops": ("unwrapKey", "wrapKey")}
        key = KeyVaultKey(key_id="http://fake.test.vault/keys/key/version", jwk=jwk)

        crypto_client = CryptographyClient(key, credential=lambda *_: None)

        # Wrap a key with the created key, then unwrap it. The wrapped key's bytes should round-trip.
        key_bytes = os.urandom(32)
        wrap_result = crypto_client.wrap_key(KeyWrapAlgorithm.aes_256, key_bytes)
        unwrap_result = crypto_client.unwrap_key(wrap_result.algorithm, wrap_result.encrypted_key)
        self.assertEqual(unwrap_result.key, key_bytes)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_encrypt_local(self, vault_client, **kwargs):
        """Encrypt locally, decrypt with Key Vault"""

        key_client = vault_client.keys
        key = key_client.create_rsa_key("encrypt-local", size=4096)
        crypto_client = vault_client.get_cryptography_client(key)

        for encrypt_algorithm in EncryptionAlgorithm:
            result = crypto_client.encrypt(encrypt_algorithm, self.plaintext)
            self.assertEqual(result.key_id, key.id)

            result = crypto_client.decrypt(result.algorithm, result.ciphertext)
            self.assertEqual(result.plaintext, self.plaintext)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_wrap_local(self, vault_client, **kwargs):
        """Wrap locally, unwrap with Key Vault"""

        key_client = vault_client.keys
        key = key_client.create_rsa_key("wrap-local", size=4096)
        crypto_client = vault_client.get_cryptography_client(key)

        for wrap_algorithm in (algo for algo in KeyWrapAlgorithm if algo.value.startswith("RSA")):
            result = crypto_client.wrap_key(wrap_algorithm, self.plaintext)
            self.assertEqual(result.key_id, key.id)

            result = crypto_client.unwrap_key(result.algorithm, result.encrypted_key)
            self.assertEqual(result.key, self.plaintext)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_rsa_verify_local(self, vault_client, **kwargs):
        """Sign with Key Vault, verify locally"""

        key_client = vault_client.keys

        for size in (2048, 3072, 4096):
            key = key_client.create_rsa_key("rsa-verify-{}".format(size), size=size)
            crypto_client = vault_client.get_cryptography_client(key)
            for signature_algorithm, hash_function in (
                (SignatureAlgorithm.ps256, hashlib.sha256),
                (SignatureAlgorithm.ps384, hashlib.sha384),
                (SignatureAlgorithm.ps512, hashlib.sha512),
                (SignatureAlgorithm.rs256, hashlib.sha256),
                (SignatureAlgorithm.rs384, hashlib.sha384),
                (SignatureAlgorithm.rs512, hashlib.sha512),
            ):
                digest = hash_function(self.plaintext).digest()

                result = crypto_client.sign(signature_algorithm, digest)
                self.assertEqual(result.key_id, key.id)

                result = crypto_client.verify(result.algorithm, digest, result.signature)
                self.assertTrue(result.is_valid)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_ec_verify_local(self, vault_client, **kwargs):
        """Sign with Key Vault, verify locally"""

        key_client = vault_client.keys

        matrix = {
            KeyCurveName.p_256: (SignatureAlgorithm.es256, hashlib.sha256),
            KeyCurveName.p_256_k: (SignatureAlgorithm.es256_k, hashlib.sha256),
            KeyCurveName.p_384: (SignatureAlgorithm.es384, hashlib.sha384),
            KeyCurveName.p_521: (SignatureAlgorithm.es512, hashlib.sha512),
        }

        for curve, (signature_algorithm, hash_function) in matrix.items():
            key = key_client.create_ec_key("ec-verify-{}".format(curve.value), curve=curve)
            crypto_client = vault_client.get_cryptography_client(key)

            digest = hash_function(self.plaintext).digest()

            result = crypto_client.sign(signature_algorithm, digest)
            self.assertEqual(result.key_id, key.id)

            result = crypto_client.verify(result.algorithm, digest, result.signature)
            self.assertTrue(result.is_valid)
