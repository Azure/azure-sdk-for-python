import time
import codecs
import copy
import hashlib
from dateutil import parser as date_parse
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault import KeyVaultId
from azure.keyvault.models import (
    JsonWebKey
)

class KeyVaultKeyTest(KeyvaultTestCase):
    def setUp(self):
        super(KeyVaultKeyTest, self).setUp()
        self.plain_text = b'5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd'

    def tearDown(self):
        super(KeyVaultKeyTest, self).tearDown()

    def _import_test_key(self, vault, key_id, import_to_hardware=False):

        def _to_bytes(hex):
            if len(hex) % 2:
                hex = '0{}'.format(hex)
            return codecs.decode(hex, 'hex_codec')

        key = JsonWebKey(
            kty='RSA',
            key_ops=['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey'],
            n=_to_bytes(
                '00a0914d00234ac683b21b4c15d5bed887bdc959c2e57af54ae734e8f00720d775d275e455207e3784ceeb60a50a4655dd72a7a94d271e8ee8f7959a669ca6e775bf0e23badae991b4529d978528b4bd90521d32dd2656796ba82b6bbfc7668c8f5eeb5053747fd199319d29a8440d08f4412d527ff9311eda71825920b47b1c46b11ab3e91d7316407e89c7f340f7b85a34042ce51743b27d4718403d34c7b438af6181be05e4d11eb985d38253d7fe9bf53fc2f1b002d22d2d793fa79a504b6ab42d0492804d7071d727a06cf3a8893aa542b1503f832b296371b6707d4dc6e372f8fe67d8ded1c908fde45ce03bc086a71487fa75e43aa0e0679aa0d20efe35'),
            e=_to_bytes('10001'),
            d=_to_bytes(
                '627c7d24668148fe2252c7fa649ea8a5a9ed44d75c766cda42b29b660e99404f0e862d4561a6c95af6a83d213e0a2244b03cd28576473215073785fb067f015da19084ade9f475e08b040a9a2c7ba00253bb8125508c9df140b75161d266be347a5e0f6900fe1d8bbf78ccc25eeb37e0c9d188d6e1fc15169ba4fe12276193d77790d2326928bd60d0d01d6ead8d6ac4861abadceec95358fd6689c50a1671a4a936d2376440a41445501da4e74bfb98f823bd19c45b94eb01d98fc0d2f284507f018ebd929b8180dbe6381fdd434bffb7800aaabdd973d55f9eaf9bb88a6ea7b28c2a80231e72de1ad244826d665582c2362761019de2e9f10cb8bcc2625649'),
            p=_to_bytes(
                '00d1deac8d68ddd2c1fd52d5999655b2cf1565260de5269e43fd2a85f39280e1708ffff0682166cb6106ee5ea5e9ffd9f98d0becc9ff2cda2febc97259215ad84b9051e563e14a051dce438bc6541a24ac4f014cf9732d36ebfc1e61a00d82cbe412090f7793cfbd4b7605be133dfc3991f7e1bed5786f337de5036fc1e2df4cf3'),
            q=_to_bytes(
                '00c3dc66b641a9b73cd833bc439cd34fc6574465ab5b7e8a92d32595a224d56d911e74624225b48c15a670282a51c40d1dad4bc2e9a3c8dab0c76f10052dfb053bc6ed42c65288a8e8bace7a8881184323f94d7db17ea6dfba651218f931a93b8f738f3d8fd3f6ba218d35b96861a0f584b0ab88ddcf446b9815f4d287d83a3237'),
            dp=_to_bytes(
                '00c9a159be7265cbbabc9afcc4967eb74fe58a4c4945431902d1142da599b760e03838f8cbd26b64324fea6bdc9338503f459793636e59b5361d1e6951e08ddb089e1b507be952a81fbeaf7e76890ea4f536e25505c3f648b1e88377dfc19b4c304e738dfca07211b792286a392a704d0f444c0a802539110b7f1f121c00cff0a9'),
            dq=_to_bytes(
                '00a0bd4c0a3d9f64436a082374b5caf2488bac1568696153a6a5e4cd85d186db31e2f58f024c617d29f37b4e6b54c97a1e25efec59c4d1fd3061ac33509ce8cae5c11f4cd2e83f41a8264f785e78dc0996076ee23dfdfc43d67c463afaa0180c4a718357f9a6f270d542479a0f213870e661fb950abca4a14ca290570ba7983347'),
            qi=_to_bytes(
                '009fe7ae42e92bc04fcd5780464bd21d0c8ac0c599f9af020fde6ab0a7e7d1d39902f5d8fb6c614184c4c1b103fb46e94cd10a6c8a40f9991a1f28269f326435b6c50276fda6493353c650a833f724d80c7d522ba16c79f0eb61f672736b68fb8be3243d10943c4ab7028d09e76cfb5892222e38bc4d35585bf35a88cd68c73b07')
        )
        imported_key = self.client.import_key(key_id.vault, key_id.name, key, import_to_hardware)
        self._validate_rsa_key_bundle(imported_key, vault.properties.vault_uri, key_id.name,
                                      'RSA-HSM' if import_to_hardware else 'RSA', key.key_ops)
        return imported_key

    def _validate_rsa_key_bundle(self, bundle, vault, key_name, kty, key_ops=None):
        prefix = '{}keys/{}/'.format(vault, key_name)
        key_ops = key_ops or ['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey']
        key = bundle.key
        kid = key.kid
        self.assertTrue(kid.index(prefix) == 0,
                        "String should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key.n and key.e, 'Bad RSA public material.')
        self.assertEqual(key_ops, key.key_ops,
                         "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops))
        self.assertTrue(bundle.attributes.created and bundle.attributes.updated,
                        'Missing required date attributes.')

    def _validate_key_list(self, keys, expected):
        for key in keys:
            if key.kid in expected.keys():
                del expected[key.kid]
            else:
                self.assertTrue(False)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_crud_operations(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('key')

        # create key
        created_bundle = self.client.create_key(vault_uri, key_name, 'RSA')
        self._validate_rsa_key_bundle(created_bundle, vault_uri, key_name, 'RSA')
        key_id = KeyVaultId.parse_key_id(created_bundle.key.kid)

        # get key without version
        self.assertEqual(created_bundle, self.client.get_key(key_id.vault, key_id.name, ''))

        # get key with version
        self.assertEqual(created_bundle, self.client.get_key(key_id.vault, key_id.name, key_id.version))

        def _update_key(key_uri):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.key.key_ops = ['encrypt', 'decrypt']
            updating_bundle.tags = {'foo': 'updated tag'}
            kid = KeyVaultId.parse_key_id(key_uri)
            key_bundle = self.client.update_key(
                kid.vault, kid.name, kid.version, updating_bundle.key.key_ops, updating_bundle.attributes,
                updating_bundle.tags)
            self.assertEqual(updating_bundle.tags, key_bundle.tags)
            self.assertEqual(updating_bundle.key.kid, key_bundle.key.kid)
            return key_bundle

        # update key without version
        created_bundle = _update_key(key_id.base_id)

        # update key with version
        created_bundle = _update_key(key_id.id)

        # delete key
        self.client.delete_key(key_id.vault, key_id.name)

        # get key returns not found
        try:
            self.client.get_key(key_id.vault, key_id.name, '')
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_list(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(0, max_keys):
            key_name = self.get_resource_name('key{}-'.format(x))
            key_bundle = None
            error_count = 0
            while not key_bundle:
                try:
                    key_bundle = self.client.create_key(vault_uri, key_name, 'RSA')
                    kid = KeyVaultId.parse_key_id(key_bundle.key.kid).base_id.strip('/')
                    expected[kid] = key_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

                        # list keys
        result = list(self.client.get_keys(vault_uri, self.list_test_size))
        self._validate_key_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_list_versions(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('key')

        max_keys = self.list_test_size
        expected = {}

        # create many key versions
        for x in range(0, max_keys):
            key_bundle = None
            error_count = 0
            while not key_bundle:
                try:
                    key_bundle = self.client.create_key(vault_uri, key_name, 'RSA')
                    kid = KeyVaultId.parse_key_id(key_bundle.key.kid).id.strip('/')
                    expected[kid] = key_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list key versions
        self._validate_key_list(list(self.client.get_key_versions(vault_uri, key_name)), expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_backup_and_restore(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('keybak')

        # create key
        created_bundle = self.client.create_key(vault_uri, key_name, 'RSA')
        key_id = KeyVaultId.parse_key_id(created_bundle.key.kid)

        # backup key
        key_backup = self.client.backup_key(key_id.vault, key_id.name).value

        # delete key
        self.client.delete_key(key_id.vault, key_id.name)

        # restore key
        self.assertEqual(created_bundle, self.client.restore_key(vault_uri, key_backup))

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_key_recover_and_purge(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        keys = {}

        # create keys to recover
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name('keyrec{}'.format(str(i)))
            keys[key_name] = self.client.create_key(vault_uri, key_name, 'RSA')

        # create keys to purge
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name('keyprg{}'.format(str(i)))
            keys[key_name] = self.client.create_key(vault_uri, key_name, 'RSA')

        # delete all keys
        for key_name in keys.keys():
            self.client.delete_key(vault_uri, key_name)

        if not self.is_playback():
            time.sleep(20)

        # validate all our deleted keys are returned by get_deleted_keys
        deleted = [KeyVaultId.parse_key_id(s.kid).name for s in self.client.get_deleted_keys(vault_uri)]
        self.assertTrue(all(s in deleted for s in keys.keys()))

        # recover select keys
        for key_name in [s for s in keys.keys() if s.startswith('keyrec')]:
            self.client.recover_deleted_key(vault_uri, key_name)

        # purge select keys
        for key_name in [s for s in keys.keys() if s.startswith('keyprg')]:
            self.client.purge_deleted_key(vault_uri, key_name)

        if not self.is_playback():
            time.sleep(20)

        # validate none of our deleted keys are returned by get_deleted_keys
        deleted = [KeyVaultId.parse_key_id(s.kid).name for s in self.client.get_deleted_keys(vault_uri)]
        self.assertTrue(not any(s in deleted for s in keys.keys()))

        # validate the recovered keys
        expected = {k: v for k, v in keys.items() if k.startswith('key-') and k.endswith('-recover')}
        actual = {k: self.client.get_key(vault_uri, k) for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_import(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('keyimp')

        key_id = KeyVaultId.create_key_id(vault_uri, key_name)

        # import to software
        self._import_test_key(vault, key_id, False)

        # import to hardware
        self._import_test_key(vault, key_id, True)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_encrypt_and_decrypt(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('keycrypt')

        key_id = KeyVaultId.create_key_id(vault_uri, key_name)
        plain_text = self.plain_text

        # import key
        imported_key = self._import_test_key(vault, key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # encrypt without version
        result = self.client.encrypt(key_id.vault, key_id.name, '', 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # decrypt without version
        result = self.client.decrypt(key_id.vault, key_id.name, '', 'RSA-OAEP', cipher_text)
        self.assertEqual(plain_text, result.result)

        # encrypt with version
        result = self.client.encrypt(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # decrypt with version
        result = self.client.decrypt(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', cipher_text)
        self.assertEqual(plain_text, result.result)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_wrap_and_unwrap(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('keywrap')

        key_id = KeyVaultId.create_key_id(vault_uri, key_name)
        plain_text = self.plain_text

        # import key
        imported_key = self._import_test_key(vault, key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # wrap without version
        result = self.client.wrap_key(key_id.vault, key_id.name, '', 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # unwrap without version
        result = self.client.unwrap_key(key_id.vault, key_id.name, '', 'RSA-OAEP', cipher_text)
        self.assertEqual(plain_text, result.result)

        # wrap with version
        result = self.client.wrap_key(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # unwrap with version
        result = self.client.unwrap_key(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', cipher_text)
        self.assertEqual(plain_text, result.result)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_sign_and_verify(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        key_name = self.get_resource_name('keysign')

        key_id = KeyVaultId.create_key_id(vault_uri, key_name)
        plain_text = self.plain_text
        md = hashlib.sha256()
        md.update(plain_text);
        digest = md.digest();

        # import key
        imported_key = self._import_test_key(vault, key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # sign without version
        signature = self.client.sign(key_id.vault, key_id.name, '', 'RS256', digest).result

        # verify without version
        result = self.client.verify(key_id.vault, key_id.name, '', 'RS256', digest, signature)
        self.assertTrue(result.value)

        # sign with version
        signature = self.client.sign(key_id.vault, key_id.name, '', 'RS256', digest).result

        # verify with version
        result = self.client.verify(key_id.vault, key_id.name, key_id.version, 'RS256', digest, signature)
        self.assertTrue(result.value)
