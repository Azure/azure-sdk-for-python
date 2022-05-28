# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from json import loads

from azure.storage.blob import (
    BlobServiceClient
)
from azure.storage.blob._shared.encryption import (
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _GCM_NONCE_LENGTH,
    _GCM_TAG_LENGTH,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from devtools_testutils.storage import StorageTestCase
from encryption_test_helper import (
    KeyWrapper,
    KeyResolver,
    RSAKeyWrapper,
)
from settings.testcase import BlobPreparer

TEST_CONTAINER_PREFIX = 'encryptionv2_container'
TEST_BLOB_PREFIX = 'encryptionv2_blob'


class StorageBlobEncryptionV2Test(StorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key)
        self.container_name = self.get_resource_name('utcontainer')

        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container()
            except:
                pass

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def enable_encryption_v2(self, kek):
        self.bsc.require_encryption = True
        self.bsc.encryption_version = '2.0'
        self.bsc.key_encryption_key = kek
    # --------------------------------------------------------------------------

    @BlobPreparer()
    def test_validate_encryption(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True)

        blob.require_encryption = False
        blob.key_encryption_key = None
        metadata = blob.get_blob_properties().metadata
        encrypted_data = blob.download_blob().readall()

        encryption_data = _dict_to_encryption_data(loads(metadata['encryptiondata']))

        encryption_agent = encryption_data.encryption_agent
        self.assertEqual('2.0', encryption_agent.protocol)
        self.assertEqual('AES_GCM_256', encryption_agent.encryption_algorithm)

        encrypted_region_info = encryption_data.encrypted_region_info
        self.assertEqual(_GCM_NONCE_LENGTH, encrypted_region_info.nonce_length)
        self.assertEqual(_GCM_TAG_LENGTH, encrypted_region_info.tag_length)

        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)

        nonce_length = encrypted_region_info.nonce_length

        # First bytes are the nonce
        nonce = encrypted_data[:nonce_length]
        ciphertext_with_tag = encrypted_data[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        # Assert
        self.assertEqual(content, decrypted_data)

    @BlobPreparer()
    def test_validate_encryption_chunked_upload(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'a' * 5 * 1024

        # Act
        blob.upload_blob(content, overwrite=True)

        blob.require_encryption = False
        blob.key_encryption_key = None
        metadata = blob.get_blob_properties().metadata
        encrypted_data = blob.download_blob().readall()

        encryption_data = _dict_to_encryption_data(loads(metadata['encryptiondata']))

        encryption_agent = encryption_data.encryption_agent
        self.assertEqual('2.0', encryption_agent.protocol)
        self.assertEqual('AES_GCM_256', encryption_agent.encryption_algorithm)

        encrypted_region_info = encryption_data.encrypted_region_info
        self.assertEqual(_GCM_NONCE_LENGTH, encrypted_region_info.nonce_length)
        self.assertEqual(_GCM_TAG_LENGTH, encrypted_region_info.tag_length)

        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)

        nonce_length = encrypted_region_info.nonce_length

        # First bytes are the nonce
        nonce = encrypted_data[:nonce_length]
        ciphertext_with_tag = encrypted_data[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        # Assert
        self.assertEqual(content, decrypted_data)

    @BlobPreparer()
    def test_encryption_kek(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_encryption_kek_rsa(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = RSAKeyWrapper('key2')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_encryption_kek_resolver(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)
        key_resolver = KeyResolver()
        key_resolver.put_key(self.bsc.key_encryption_key)
        self.bsc.key_resolver_function = key_resolver.resolve_key

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        self.bsc.key_encryption_key = None
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_put_blob_empty(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b''

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_put_blob_single_region_chunked(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 1024

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_equal_region(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=4 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_equal_region_concurrent(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=4 * 1024 * 1024,
            max_concurrency=3,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_less_region(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=2 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_greater_region(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=6 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(content, data)

    @BlobPreparer()
    def test_get_blob_range_single_region_beginning_to_middle(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 1024 * 1024

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=0, length=100000).readall()

        # Assert
        self.assertEqual(content[:100000], data)

    @BlobPreparer()
    def test_get_blob_range_single_region_middle_to_middle(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 1024 * 1024

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=100000, length=2000000).readall()

        # Assert
        self.assertEqual(content[100000:2100000], data)

    @BlobPreparer()
    def test_get_blob_range_single_region_middle_to_end(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 1024 * 1024
        length = len(content)

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=length - 1000000, length=1000000).readall()

        # Assert
        self.assertEqual(content[length - 1000000:], data)

    @BlobPreparer()
    def test_get_blob_range_cross_region(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcdef' * 1024 * 1024

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=3*1024*1024, length=2*1024*1024).readall()

        # Assert
        self.assertEqual(content[3*1024*1024:5*1024*1024], data)

    @BlobPreparer()
    def test_get_blob_range_inside_second_region(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcdef' * 1024 * 1024

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=5 * 1024 * 1024, length=1024 * 1024).readall()

        # Assert
        self.assertEqual(content[5 * 1024 * 1024:6 * 1024 * 1024], data)

    @BlobPreparer()
    def test_get_blob_chunked_size_equal_region_size(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * 1024 * 1024,
            max_chunk_get_size=4 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(len(content), len(data))

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_chunked_size_equal_region_size_concurrent(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * 1024 * 1024,
            max_chunk_get_size=4 * 1024 * 1024,
            max_concurrency=3,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 4 * 1024 * 1024  # 20 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(len(content), len(data))

    @BlobPreparer()
    def test_get_blob_chunked_size_less_than_region_size(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * 1024 * 1024,
            max_chunk_get_size=2 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(len(content), len(data))

    @BlobPreparer()
    def test_get_blob_chunked_size_greater_than_region_size(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * 1024 * 1024,
            max_chunk_get_size=6 * 1024 * 1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * 1024 * 1024  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        self.assertEqual(len(content), len(data))
