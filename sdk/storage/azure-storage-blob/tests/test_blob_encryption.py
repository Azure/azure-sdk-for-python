# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import tempfile
from io import StringIO, BytesIO
from json import loads
from math import ceil
from os import path, remove, unlink, urandom
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient, BlobType
from azure.storage.blob._encryption import (
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _generate_AES_CBC_cipher,
    _ERROR_OBJECT_INVALID,
)
from cryptography.hazmat.primitives.padding import PKCS7

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from encryption_test_helper import KeyResolver, KeyWrapper, mock_urandom, RSAKeyWrapper
from settings.testcase import BlobPreparer


# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'encryption_container'
TEST_BLOB_PREFIXES = {'BlockBlob': 'encryption_block_blob',
                      'PageBlob': 'encryption_page_blob',
                      'AppendBlob': 'foo'}
_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = 'The require_encryption flag is set, but encryption is not supported' + \
                                           ' for this method.'
# ------------------------------------------------------------------------------


@mock.patch('os.urandom', mock_urandom)
class TestStorageBlobEncryption(StorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024,
            max_page_size=4 * 1024,
            max_single_get_size=1024,
            max_chunk_get_size=1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.blob_types = (BlobType.BlockBlob, BlobType.PageBlob, BlobType.AppendBlob)
        self.bytes = b'Foo'

        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container()
            except:
                pass

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self, blob_type):
        return self.get_resource_name(TEST_BLOB_PREFIXES[blob_type.value])

    def _create_small_blob(self, blob_type):
        blob_name = self._get_blob_reference(blob_type)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(self.bytes, blob_type=blob_type)
        return blob

    # --Test cases for blob encryption ----------------------------------------

    @BlobPreparer()
    def test_missing_attribute_kek_wrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self.bsc.require_encryption = True
        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        self.bsc.key_encryption_key = invalid_key_1
        with pytest.raises(AttributeError):
            self._create_small_blob(BlobType.BlockBlob)

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        self.bsc.key_encryption_key = invalid_key_2
        with pytest.raises(AttributeError):
            self._create_small_blob(BlobType.BlockBlob)

        invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        self.bsc.key_encryption_key = invalid_key_2
        with pytest.raises(AttributeError):
            self._create_small_blob(BlobType.BlockBlob)

    @BlobPreparer()
    def test_invalid_value_kek_wrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')

        self.bsc.key_encryption_key.get_key_wrap_algorithm = None
        try:
            self._create_small_blob(BlobType.BlockBlob)
            self.fail()
        except AttributeError as e:
            assert str(e), _ERROR_OBJECT_INVALID.format('key encryption key' == 'get_key_wrap_algorithm')

        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.key_encryption_key.get_kid = None
        with pytest.raises(AttributeError):
            self._create_small_blob(BlobType.BlockBlob)

        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.key_encryption_key.wrap_key = None
        with pytest.raises(AttributeError):
            self._create_small_blob(BlobType.BlockBlob)

    @BlobPreparer()
    @recorded_by_proxy
    def test_missing_attribute_kek_unwrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        valid_key = KeyWrapper('key1')
        self.bsc.key_encryption_key = valid_key
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        # Note that KeyWrapper has a default value for key_id, so these Exceptions
        # are not due to non_matching kids.
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute unwrap_key
        blob.key_encryption_key = invalid_key_1
        with pytest.raises(HttpResponseError):
            blob.download_blob().readall()

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.unwrap_key = valid_key.unwrap_key
        blob.key_encryption_key = invalid_key_2
        # No attribute get_kid
        with pytest.raises(HttpResponseError):
            blob.download_blob().readall()

    @BlobPreparer()
    @recorded_by_proxy
    def test_invalid_value_kek_unwrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = self._create_small_blob(BlobType.BLOCKBLOB)

        # Act
        blob.key_encryption_key = KeyWrapper('key1')
        blob.key_encryption_key.unwrap_key = None

        with pytest.raises(HttpResponseError) as e:
            blob.download_blob().readall()
        assert 'Decryption failed.' in str(e.value.message)

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_kek(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        content = blob.download_blob()

        # Assert
        assert b"".join(list(content.chunks())) == self.bytes

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_resolver(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        key_resolver = KeyResolver()
        key_resolver.put_key(self.bsc.key_encryption_key)
        self.bsc.key_resolver_function = key_resolver.resolve_key
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        self.bsc.key_encryption_key = None
        content = blob.download_blob().readall()

        # Assert
        assert content == self.bytes

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_kek_RSA(self, **kwargs):
        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = RSAKeyWrapper('key2')
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        content = blob.download_blob()

        # Assert
        assert b"".join(list(content.chunks())) == self.bytes

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_nonmatching_kid(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = self._create_small_blob(BlobType.BLOCKBLOB)

        # Act
        self.bsc.key_encryption_key.kid = 'Invalid'

        # Assert
        with pytest.raises(HttpResponseError) as e:
            blob.download_blob().readall()
        assert 'Decryption failed.' in str(e.value.message)

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_invalid_stream_type(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        small_stream = StringIO(u'small')
        large_stream = StringIO(u'large' * self.config.max_single_put_size)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        # Block blob specific single shot
        with pytest.raises(TypeError) as e:
            blob.upload_blob(small_stream, length=5)
        assert 'Blob data should be of type bytes.' in str(e.value)

        # Generic blob chunked
        with pytest.raises(TypeError) as e:
            blob.upload_blob(large_stream)
        assert 'Blob data should be of type bytes.' in str(e.value)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_chunking_required_mult_of_block_size(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(
            self.config.max_single_put_size + self.config.max_block_size)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content, max_concurrency=3)
        blob_content = blob.download_blob(max_concurrency=3).readall()

        # Assert
        assert content == blob_content

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_chunking_required_non_mult_of_block_size(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = urandom(self.config.max_single_put_size + 1)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content, max_concurrency=3)
        blob_content = blob.download_blob(max_concurrency=3).readall()

        # Assert
        assert content == blob_content

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_blob_chunking_required_range_specified(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(self.config.max_single_put_size * 2)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(
            content,
            length=self.config.max_single_put_size + 53,
            max_concurrency=3)
        blob_content = blob.download_blob(max_concurrency=3).readall()

        # Assert
        assert content[:self.config.max_single_put_size + 53] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_blob_single_shot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = b'small'
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob().readall()

        # Assert
        assert content == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        content = b'Random repeats' * self.config.max_single_put_size * 5

        # All page blob uploads call _upload_chunks, so this will test the ability
        # of that function to handle ranges even though it's a small blob
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(
            content[2:],
            length=self.config.max_single_put_size + 5,
            max_concurrency=1)
        blob_content = blob.download_blob().readall()

        # Assert
        assert content[2:2 + self.config.max_single_put_size + 5] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_empty(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = b''
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob(max_concurrency=2).readall()

        # Assert
        assert content == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_serial_upload_chunking(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(self.config.max_single_put_size + 1)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content, max_concurrency=1)
        blob_content = blob.download_blob().readall()

        # Assert
        assert content == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_beginning_to_middle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content, max_concurrency=1)
        blob_content = blob.download_blob(offset=0, length=50).readall()

        # Assert
        assert content[:50] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_middle_to_end(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content, max_concurrency=1)
        blob_content = blob.download_blob(offset=100, length=28).readall()
        blob_content2 = blob.download_blob(offset=100).readall()

        # Assert
        assert content[100:] == blob_content
        assert content[100:] == blob_content2

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_middle_to_middle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob(offset=5, length=93).readall()

        # Assert
        assert content[5:98] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_aligns_on_16_byte_block(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob(offset=48, length=16).readall()

        # Assert
        assert content[48:64] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_expanded_to_beginning_block_align(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob(offset=5, length=50).readall()

        # Assert
        assert content[5:55] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_expanded_to_beginning_iv(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.upload_blob(content)
        blob_content = blob.download_blob(offset=22, length=20).readall()

        # Assert
        assert content[22:42] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_range_cross_chunk(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True

        data = b'12345' * 205 * 3  # 3075 bytes
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(data, overwrite=True)

        # Act
        offset, length = 501, 2500
        blob_content = blob.download_blob(offset=offset, length=length).readall()

        # Assert
        assert data[offset:offset + length] == blob_content

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_strict_mode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        content = b'Hello world'

        # Assert
        for service in self.blob_types:
            blob_name = self._get_blob_reference(service)
            blob = self.bsc.get_blob_client(self.container_name, blob_name)

            with pytest.raises(ValueError):
                blob.upload_blob(content, blob_type=service)

            stream = BytesIO(content)
            with pytest.raises(ValueError):
                blob.upload_blob(stream, length=512, blob_type=service)

            with tempfile.TemporaryFile() as temp_file:
                temp_file.write(content)
                temp_file.seek(0)
                with pytest.raises(ValueError):
                    blob.upload_blob(temp_file, blob_type=service)

                with pytest.raises(ValueError):
                    blob.upload_blob('To encrypt', blob_type=service)

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_strict_mode_no_policy(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.key_encryption_key = None

        # Assert
        with pytest.raises(ValueError):
            blob.download_blob().readall()

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_strict_mode_unencrypted_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.require_encryption = True
        blob.key_encryption_key = KeyWrapper('key1')

        # Assert
        with pytest.raises(HttpResponseError):
            blob.download_blob().readall()

    @BlobPreparer()
    @recorded_by_proxy
    def test_invalid_methods_fail_block(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with pytest.raises(ValueError) as e:
            blob.stage_block('block1', b'hello world')
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

        with pytest.raises(ValueError) as e:
            blob.commit_block_list(['block1'])
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    @recorded_by_proxy
    def test_invalid_methods_fail_append(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.AppendBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with pytest.raises(ValueError) as e:
            blob.append_block(b'hello world')
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

        with pytest.raises(ValueError) as e:
            blob.create_append_blob()
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

        # All append_from operations funnel into append_from_stream, so testing one is sufficient
        with pytest.raises(ValueError) as e:
            blob.upload_blob(b'To encrypt', blob_type=BlobType.AppendBlob)
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    @recorded_by_proxy
    def test_invalid_methods_fail_page(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.PageBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with pytest.raises(ValueError) as e:
            blob.upload_page(b'a' * 512, offset=0, length=512)
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

        with pytest.raises(ValueError) as e:
            blob.create_page_blob(512)
        assert str(e.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    @recorded_by_proxy
    def test_validate_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        kek = KeyWrapper('key1')
        self.bsc.key_encryption_key = kek
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.require_encryption = False
        blob.key_encryption_key = None
        content = blob.download_blob()
        data = content.readall()

        encryption_data = _dict_to_encryption_data(loads(content.properties.metadata['encryptiondata']))
        iv = encryption_data.content_encryption_IV
        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)
        cipher = _generate_AES_CBC_cipher(content_encryption_key, iv)
        decryptor = cipher.decryptor()
        unpadder = PKCS7(128).unpadder()

        content = decryptor.update(data) + decryptor.finalize()
        content = unpadder.update(content) + unpadder.finalize()

        assert self.bytes == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_block_blob_from_star(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self._create_blob_from_star(BlobType.BlockBlob, self.bytes, self.bytes)

        stream = BytesIO(self.bytes)
        self._create_blob_from_star(BlobType.BlockBlob, self.bytes, stream)

        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(self.bytes)
            temp_file.seek(0)
            self._create_blob_from_star(BlobType.BlockBlob, self.bytes, temp_file)

        self._create_blob_from_star(BlobType.BlockBlob, b'To encrypt', 'To encrypt')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_page_blob_from_star(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        content = self.get_random_bytes(512)
        self._create_blob_from_star(BlobType.PageBlob, content, content)

        stream = BytesIO(content)
        self._create_blob_from_star(BlobType.PageBlob, content, stream, length=512)

        stream = tempfile.NamedTemporaryFile(delete=False)
        path_name = stream.name
        stream.write(content)
        stream.close()

        with open(path_name, 'rb') as stream:
            self._create_blob_from_star(BlobType.PageBlob, content, stream)

        unlink(stream.name)

    def _create_blob_from_star(self, blob_type, content, data, **kwargs):
        blob_name = self._get_blob_reference(blob_type)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.key_encryption_key = KeyWrapper('key1')
        blob.require_encryption = True
        blob.upload_blob(data, blob_type=blob_type, **kwargs)

        blob_content = blob.download_blob().readall()
        assert content == blob_content
        blob.delete_blob()

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_to_star(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = self._create_small_blob(BlobType.BlockBlob)

        # Act
        iter_blob = b"".join(list(blob.download_blob().chunks()))
        bytes_blob = blob.download_blob().readall()
        stream_blob = BytesIO()
        blob.download_blob().download_to_stream(stream_blob)
        stream_blob.seek(0)
        text_blob = blob.download_blob(encoding='UTF-8').readall()

        # Assert
        assert self.bytes == iter_blob
        assert self.bytes == bytes_blob
        assert self.bytes == stream_blob.read()
        assert self.bytes.decode() == text_blob

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_blob_read(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')

        data = b'12345' * 205 * 25  # 25625 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference(BlobType.BLOCKBLOB))
        blob.upload_blob(data, overwrite=True)
        stream = blob.download_blob(max_concurrency=3)

        # Act
        result = bytearray()
        read_size = 3000
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_read_with_other_read_operations_ranged(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')

        data = b'12345' * 205 * 10  # 10250 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference(BlobType.BLOCKBLOB))
        blob.upload_blob(data, overwrite=True)
        offset, length = 501, 5000

        # Act / Assert
        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(100)  # Read in first chunk
        second = stream.readall()

        assert first == data[offset:offset + 100]
        assert second == data[offset + 100:offset + length]

        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(3000)  # Read past first chunk
        second = stream.readall()

        assert first == data[offset:offset + 3000]
        assert second == data[offset + 3000:offset + length]

        stream = blob.download_blob(offset=offset, length=length)
        first = stream.read(3000)  # Read past first chunk
        second_stream = BytesIO()
        read_size = stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data[offset:offset + 3000]
        assert second == data[offset + 3000:offset + length]
        assert read_size == len(second)

# ------------------------------------------------------------------------------
