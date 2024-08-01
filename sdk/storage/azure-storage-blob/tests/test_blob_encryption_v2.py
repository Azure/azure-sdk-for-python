# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import os
from io import BytesIO
from json import dumps, loads
from math import ceil
from unittest import mock

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient, BlobType
from azure.storage.blob._encryption import (
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _GCM_NONCE_LENGTH,
    _GCM_TAG_LENGTH,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from encryption_test_helper import KeyResolver, KeyWrapper, mock_urandom, RSAKeyWrapper
from settings.testcase import BlobPreparer

TEST_CONTAINER_PREFIX = 'encryptionv2_container'
TEST_BLOB_PREFIX = 'encryptionv2_blob'
MiB = 1024 * 1024


class TestStorageBlobEncryptionV2(StorageRecordedTestCase):
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
    def test_v2_blocked_for_page_blob_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        self.container_name = self.get_resource_name('utcontainer')
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())

        # Act
        with pytest.raises(ValueError):
            blob.upload_blob(b'Test', blob_type=BlobType.PAGEBLOB)

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_validate_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert '2.0' == encryption_agent.protocol
        assert 'AES_GCM_256' == encryption_agent.encryption_algorithm

        encrypted_region_info = encryption_data.encrypted_region_info
        assert _GCM_NONCE_LENGTH == encrypted_region_info.nonce_length
        assert _GCM_TAG_LENGTH == encrypted_region_info.tag_length

        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)

        nonce_length = encrypted_region_info.nonce_length

        # First bytes are the nonce
        nonce = encrypted_data[:nonce_length]
        ciphertext_with_tag = encrypted_data[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        # Assert
        assert content == decrypted_data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_validate_encryption_chunked_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert '2.0' == encryption_agent.protocol
        assert 'AES_GCM_256' == encryption_agent.encryption_algorithm

        encrypted_region_info = encryption_data.encrypted_region_info
        assert _GCM_NONCE_LENGTH == encrypted_region_info.nonce_length
        assert _GCM_TAG_LENGTH == encrypted_region_info.tag_length

        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)

        nonce_length = encrypted_region_info.nonce_length

        # First bytes are the nonce
        nonce = encrypted_data[:nonce_length]
        ciphertext_with_tag = encrypted_data[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        # Assert
        assert content == decrypted_data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_kek(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_encryption_kek_rsa(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.
        self._setup(storage_account_name, storage_account_key)
        kek = RSAKeyWrapper('key2')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_kek_resolver(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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

        # Set kek to None to test only resolver for download
        blob.key_encryption_key = None
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_with_blob_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        blob.upload_blob(b'', overwrite=True)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        blob.upload_blob(content, overwrite=True, lease=lease)
        with pytest.raises(HttpResponseError):
            blob.download_blob(lease='00000000-1111-2222-3333-444444444445')

        data = blob.download_blob(lease=lease).readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        resp = blob.upload_blob(b'', overwrite=True)
        etag = resp['etag']

        # Act
        resp = blob.upload_blob(content, overwrite=True, etag=etag, match_condition=MatchConditions.IfNotModified)
        etag = resp['etag']

        with pytest.raises(HttpResponseError):
            blob.download_blob(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        data = blob.download_blob(etag=etag, match_condition=MatchConditions.IfNotModified).readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_decryption_on_non_encrypted_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Not Encrypted!'

        blob.upload_blob(content, overwrite=True)

        # Act
        blob.key_encryption_key = KeyWrapper('key1')
        blob.require_encryption = True

        with pytest.raises(HttpResponseError):
            blob.download_blob()

        blob.require_encryption = False
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_v2_v1_downgrade(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Upload blob with encryption V2
        blob.upload_blob(content, overwrite=True)

        # Modify metadata to look like V1
        metadata = blob.get_blob_properties().metadata
        encryption_data = loads(metadata['encryptiondata'])
        encryption_data['EncryptionAgent']['Protocol'] = '1.0'
        encryption_data['EncryptionAgent']['EncryptionAlgorithm'] = 'AES_CBC_256'
        iv = base64.b64encode(os.urandom(16))
        encryption_data['ContentEncryptionIV'] = iv.decode('utf-8')
        metadata = {'encryptiondata': dumps(encryption_data)}

        # Act / Assert
        blob.set_blob_metadata(metadata)
        with pytest.raises(HttpResponseError) as e:
            blob.download_blob()

        assert 'Decryption failed.' in str(e.value)

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_modify_cek(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        blob.upload_blob(content, overwrite=True)

        # Modify cek to not include the version
        metadata = blob.get_blob_properties().metadata
        encryption_data = loads(metadata['encryptiondata'])
        encrypted_key = base64.b64decode(encryption_data['WrappedContentKey']['EncryptedKey'])
        cek = kek.unwrap_key(encrypted_key, 'A256KW')
        encrypted_key = kek.wrap_key(cek[8:])
        encrypted_key = base64.b64encode(encrypted_key).decode()
        encryption_data['WrappedContentKey']['EncryptedKey'] = encrypted_key
        metadata = {'encryptiondata': dumps(encryption_data)}

        # Act / Assert
        blob.set_blob_metadata(metadata)
        with pytest.raises(HttpResponseError) as e:
            blob.download_blob()

        assert 'Decryption failed.' in str(e.value)

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_case_insensitive_metadata_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Upload blob with encryption V2
        blob.upload_blob(content, overwrite=True)

        # Change the case of the metadata key
        metadata = blob.get_blob_properties().metadata
        encryption_data = metadata['encryptiondata']
        metadata = {'Encryptiondata': encryption_data}
        blob.set_blob_metadata(metadata)

        # Act
        data = blob.download_blob().readall()

        # Assert
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_put_blob_empty(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b''

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_put_blob_single_region_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_equal_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_equal_region_concurrent(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True, max_concurrency=3)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_less_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=2 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_multi_region_chunked_size_greater_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            max_block_size=6 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_other_data_types(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())

        content = b'Hello World Encrypted!'
        length = len(content)
        byte_io = BytesIO(content)

        def generator():
            yield b'Hello '
            yield b'World '
            yield b'Encrypted!'

        def text_generator():
            yield 'Hello '
            yield 'World '
            yield 'Encrypted!'

        data_list = [byte_io, generator(), text_generator()]

        # Act
        for data in data_list:
            blob.upload_blob(data, length=length, overwrite=True)
            result = blob.download_blob().readall()

            # Assert
            assert content == result

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_other_data_types_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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

        content = b'abcde' * 1030  # 5 KiB + 30
        byte_io = BytesIO(content)

        def generator():
            for i in range(0, len(content), 500):
                yield content[i: i + 500]

        def text_generator():
            s_content = str(content, encoding='utf-8')
            for i in range(0, len(s_content), 500):
                yield s_content[i: i + 500]

        data_list = [byte_io, generator(), text_generator()]

        # Act
        for data in data_list:
            blob.upload_blob(data, overwrite=True)
            result = blob.download_blob().readall()

            # Assert
            assert content == result

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_single_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 2 * MiB  # 8 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=0, length=4 * MiB).readall()

        # Assert
        assert content[:4 * MiB] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_multiple_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 2 * MiB  # 8 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=0, length=8 * MiB).readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_single_region_beginning_to_middle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * MiB  # 4 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=0, length=100000).readall()

        # Assert
        assert content[:100000] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_single_region_middle_to_middle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * MiB  # 4 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=100000, length=2000000).readall()

        # Assert
        assert content[100000:2100000] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_single_region_middle_to_end(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * MiB  # 4 MiB
        length = len(content)

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=length - 1000000, length=1000000).readall()

        # Assert
        assert content[length - 1000000:] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_cross_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcdef' * MiB  # 6 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=3*1024*1024, length=2*1024*1024).readall()

        # Assert
        assert content[3*1024*1024:5*1024*1024] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_inside_second_region(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcdef' * MiB  # 6 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=5 * MiB, length=MiB).readall()

        # Assert
        assert content[5 * MiB:6 * MiB] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_oversize_length(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcdef' * MiB  # 6 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=1 * MiB, length=7 * MiB).readall()

        # Assert
        assert content[1 * MiB:] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_boundary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcd' * 2 * MiB  # 8 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(offset=4 * MiB - 1, length=4 * MiB + 2).readall()

        # Assert
        assert content[4 * MiB - 1:] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_chunked_size_equal_region_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_range_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB
        blob.upload_blob(content, overwrite=True)

        # Act
        offset, length = 1 * MiB, 5 * MiB
        data = blob.download_blob(offset=offset, length=length).readall()

        # Assert
        assert content[offset:offset + length] == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_chunked_size_equal_region_size_concurrent(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 4 * MiB  # 20 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob(max_concurrency=3).readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_chunked_size_less_than_region_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=2 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_chunked_size_greater_than_region_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=6 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        data = blob.download_blob().readall()

        # Assert
        assert content == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_using_chunks_iter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'abcde' * 3 * MiB  # 15 MiB

        # Act
        blob.upload_blob(content, overwrite=True)
        chunks_iter = blob.download_blob().chunks()

        total = 0
        for chunk in chunks_iter:
            assert content[total:total+len(chunk)] == chunk
            total += len(chunk)

        # Assert
        assert len(content) == total

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_using_read(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        data = b'abcde' * 4 * MiB  # 20 MiB
        blob.upload_blob(data, overwrite=True)

        # Act
        stream = blob.download_blob(max_concurrency=2)

        result = bytearray()
        read_size = 5 * MiB
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_read_with_other_read_operations_ranged(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=4 * MiB,
            max_chunk_get_size=4 * MiB,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        data = b'abcde' * 4 * MiB  # 20 MiB
        blob.upload_blob(data, overwrite=True)

        offset, length = 1 * MiB, 5 * MiB

        # Act / Assert
        read_size = 150000
        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(read_size)  # Read in first chunk
        second = stream.readall()

        assert first == data[offset:offset + read_size]
        assert second == data[offset + read_size:offset + length]

        read_size = 4 * MiB + 100000
        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(read_size)  # Read past first chunk
        second = stream.readall()

        assert first == data[offset:offset + read_size]
        assert second == data[offset + read_size:offset + length]

        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(read_size)  # Read past first chunk
        second_stream = BytesIO()
        read_length = stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data[offset:offset + read_size]
        assert second == data[offset + read_size:offset + length]
        assert read_length == len(second)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_using_read_chars(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        data = '你好世界' * 1024  # 12 KiB
        blob.upload_blob(data, overwrite=True, encoding='utf-8')

        # Act / Assert
        stream = blob.download_blob(max_concurrency=2, encoding='utf-8')
        assert stream.read() == data

        result = ''
        stream = blob.download_blob(encoding='utf-8')
        for _ in range(4):
            chunk = stream.read(chars=300)
            result += chunk
            assert len(chunk) == 300

        result += stream.readall()
        assert result == data

    @pytest.mark.skip(reason="Intended for manual testing due to blob size.")
    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_large_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = (b'abcde' * 100 * MiB) + b'abc'  # 500 MiB + 3

        # Act
        blob.upload_blob(content, overwrite=True, max_concurrency=5)
        data = blob.download_blob(max_concurrency=5).readall()

        # Assert
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_user_agent(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        def assert_user_agent(request):
            assert request.http_request.headers['User-Agent'].startswith('azstorage-clientsideencryption/2.0 ')

        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        content = b'Hello World Encrypted!'

        # Act
        blob.upload_blob(content, overwrite=True, raw_request_hook=assert_user_agent)
        blob.download_blob(raw_request_hook=assert_user_agent).readall()

    @BlobPreparer()
    @recorded_by_proxy
    @mock.patch('os.urandom', mock_urandom)
    def test_encryption_user_agent_app_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        kek = KeyWrapper('key1')
        self.enable_encryption_v2(kek)

        app_id = 'TestAppId'
        content = b'Hello World Encrypted!'

        def assert_user_agent(request):
            start = f'{app_id} azstorage-clientsideencryption/2.0 '
            assert request.http_request.headers['User-Agent'].startswith(start)

        # Test method level keyword
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())

        blob.upload_blob(content, overwrite=True, raw_request_hook=assert_user_agent, user_agent=app_id)
        blob.download_blob(raw_request_hook=assert_user_agent, user_agent=app_id).readall()

        # Test client constructor level keyword
        bsc = BlobServiceClient(
            self.bsc.url,
            credential=storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek,
            user_agent=app_id)

        blob = bsc.get_blob_client(self.container_name, self._get_blob_reference())

        blob.upload_blob(content, overwrite=True, raw_request_hook=assert_user_agent)
        blob.download_blob(raw_request_hook=assert_user_agent).readall()
