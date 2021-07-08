# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

import unittest
from io import (
    StringIO,
    BytesIO,
)
from json import loads
from os import (
    urandom,
    path,
    remove,
)

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.blob._shared.encryption import (
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _generate_AES_CBC_cipher,
    _ERROR_OBJECT_INVALID,
)
from azure.storage.blob._blob_client import _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION
from cryptography.hazmat.primitives.padding import PKCS7

from azure.storage.blob import BlobType
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from encryption_test_helper import (
    KeyWrapper,
    KeyResolver,
    RSAKeyWrapper,
)
from _shared.testcase import GlobalStorageAccountPreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'encryption_container'
TEST_BLOB_PREFIXES = {'BlockBlob': 'encryption_block_blob',
                      'PageBlob': 'encryption_page_blob',
                      'AppendBlob': 'foo'}
_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = 'The require_encryption flag is set, but encryption is not supported' + \
                                           ' for this method.'


# ------------------------------------------------------------------------------


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageBlobEncryptionTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------

    async def _setup(self, storage_account, key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024,
            max_page_size=4 * 1024,
            max_single_get_size=4 * 1024,
            transport=AiohttpTestTransport())
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.blob_types = (BlobType.BlockBlob, BlobType.PageBlob, BlobType.AppendBlob)
        self.bytes = b'Foo'

        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                await container.create_container()
            except:
                pass

    def _teardown(self, file_name):
        if path.isfile(file_name):
            try:
                remove(file_name)
            except:
                pass

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self, blob_type):
        return self.get_resource_name(TEST_BLOB_PREFIXES[blob_type.value])

    async def _create_small_blob(self, blob_type):
        blob_name = self._get_blob_reference(blob_type)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(self.bytes, blob_type=blob_type)
        return blob

    # --Test cases for blob encryption ----------------------------------------

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_missing_attribute_kek_wrap_async(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # In the shared method _generate_blob_encryption_key
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        self.bsc.key_encryption_key = invalid_key_1
        with self.assertRaises(AttributeError):
            await self._create_small_blob(BlobType.BlockBlob)

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        self.bsc.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            await self._create_small_blob(BlobType.BlockBlob)

        invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        self.bsc.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            await self._create_small_blob(BlobType.BlockBlob)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_invalid_value_kek_wrap_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')

        self.bsc.key_encryption_key.get_key_wrap_algorithm = None
        try:
            await self._create_small_blob(BlobType.BlockBlob)
            self.fail()
        except AttributeError as e:
            self.assertEqual(str(e), _ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm'))

        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.key_encryption_key.get_kid = None
        with self.assertRaises(AttributeError):
            await self._create_small_blob(BlobType.BlockBlob)

        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.key_encryption_key.wrap_key = None
        with self.assertRaises(AttributeError):
            await self._create_small_blob(BlobType.BlockBlob)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_missing_attribute_kek_unwrap_async(self, resource_group, location, storage_account,
                                                      storage_account_key):
        # Shared between all services in decrypt_blob
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        valid_key = KeyWrapper('key1')
        self.bsc.key_encryption_key = valid_key
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        # Note that KeyWrapper has a default value for key_id, so these Exceptions
        # are not due to non_matching kids.
        invalid_key_1 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_1.get_kid = valid_key.get_kid
        #No attribute unwrap_key
        blob.key_encryption_key = invalid_key_1
        with self.assertRaises(HttpResponseError):
            await (await blob.download_blob()).content_as_bytes()

        invalid_key_2 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_2.unwrap_key = valid_key.unwrap_key
        blob.key_encryption_key = invalid_key_2
        #No attribute get_kid
        with self.assertRaises(HttpResponseError):
            await (await blob.download_blob()).content_as_bytes()

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_invalid_value_kek_unwrap_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.key_encryption_key = KeyWrapper('key1')
        blob.key_encryption_key.unwrap_key = None

        with self.assertRaises(HttpResponseError) as e:
            await (await blob.download_blob()).content_as_bytes()
        self.assertEqual(str(e.exception), 'Decryption failed.')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_kek_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        content = await (await blob.download_blob()).content_as_bytes()

        # Assert
        self.assertEqual(content, self.bytes)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_resolver_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        key_resolver = KeyResolver()
        key_resolver.put_key(self.bsc.key_encryption_key)
        self.bsc.key_resolver_function = key_resolver.resolve_key
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        self.bsc.key_encryption_key = None
        content = await (await blob.download_blob()).content_as_bytes()

        # Assert
        self.assertEqual(content, self.bytes)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_kek_RSA_async(self, resource_group, location, storage_account, storage_account_key):
        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.

        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = RSAKeyWrapper('key2')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        content = await blob.download_blob()
        data = b""
        async for d in content.chunks():
            data += d

        # Assert
        self.assertEqual(data, self.bytes)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_nonmatching_kid_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        self.bsc.key_encryption_key.kid = 'Invalid'

        # Assert
        with self.assertRaises(HttpResponseError) as e:
            await (await blob.download_blob()).content_as_bytes()
        self.assertEqual(str(e.exception), 'Decryption failed.')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_invalid_stream_type_async(self, resource_group, location, storage_account,
                                                      storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        small_stream = StringIO(u'small')
        large_stream = StringIO(u'large' * self.config.max_single_put_size)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        # Block blob specific single shot
        with self.assertRaises(TypeError) as e:
            await blob.upload_blob(small_stream, length=5)
        self.assertTrue('Blob data should be of type bytes.' in str(e.exception))

        # Generic blob chunked
        with self.assertRaises(TypeError) as e:
            await blob.upload_blob(large_stream)
        self.assertTrue('Blob data should be of type bytes.' in str(e.exception))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_chnking_reqd_mult_of_block_size_async(self, resource_group, location, storage_account,
                                                                       storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(
            self.config.max_single_put_size + self.config.max_block_size)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content, max_concurrency=3)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=3)

        # Assert
        self.assertEqual(content, blob_content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_chnking_reqd_non_mult_of_block_size_async(self, resource_group, location,
                                                                           storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = urandom(self.config.max_single_put_size + 1)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content, max_concurrency=3)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=3)

        # Assert
        self.assertEqual(content, blob_content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_chunking_required_range_specified_async(self, resource_group, location, storage_account,
                                                                    storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(self.config.max_single_put_size * 2)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(
            content,
            length=self.config.max_single_put_size + 53,
            max_concurrency=3)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=3)

        # Assert
        self.assertEqual(content[:self.config.max_single_put_size + 53], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_blob_single_shot_async(self, resource_group, location, storage_account,
                                                    storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = b'small'
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob()).content_as_bytes()

        # Assert
        self.assertEqual(content, blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_range_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        content = b'Random repeats' * self.config.max_single_put_size * 5

        # All page blob uploads call _upload_chunks, so this will test the ability
        # of that function to handle ranges even though it's a small blob
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(
            content[2:],
            length=self.config.max_single_put_size + 5,
            max_concurrency=1)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=1)

        # Assert
        self.assertEqual(content[2:2 + self.config.max_single_put_size + 5], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_empty_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = b''
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(content, blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_serial_upload_chunking_async(self, resource_group, location, storage_account,
                                                         storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(self.config.max_single_put_size + 1)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content, max_concurrency=1)
        blob_content = await (await blob.download_blob()).content_as_bytes(max_concurrency=1)

        # Assert
        self.assertEqual(content, blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_beginning_to_middle_async(self, resource_group, location, storage_account,
                                                            storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content, max_concurrency=1)
        blob_content = await (await blob.download_blob(offset=0, length=50)).content_as_bytes(max_concurrency=1)

        # Assert
        self.assertEqual(content[:50], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_middle_to_end_async(self, resource_group, location, storage_account,
                                                      storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content, max_concurrency=1)
        blob_content = await (await blob.download_blob(offset=100, length=28)).content_as_bytes()
        blob_content2 = await (await blob.download_blob(offset=100)).content_as_bytes()

        # Assert
        self.assertEqual(content[100:], blob_content)
        self.assertEqual(content[100:], blob_content2)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_middle_to_middle_async(self, resource_group, location, storage_account,
                                                         storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob(offset=5, length=93)).content_as_bytes()

        # Assert
        self.assertEqual(content[5:98], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_aligns_on_16_byte_block_async(self, resource_group, location, storage_account,
                                                                storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob(offset=48, length=16)).content_as_bytes()

        # Assert
        self.assertEqual(content[48:64], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_expnded_to_begin_bloc_align_async(self, resource_group, location,
                                                                          storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob(offset=5, length=50)).content_as_bytes()

        # Assert
        self.assertEqual(content[5:55], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_range_expanded_to_beginning_iv_async(self, resource_group, location, storage_account,
                                                                 storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        self.bsc.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.upload_blob(content)
        blob_content = await (await blob.download_blob(offset=22, length=20)).content_as_bytes()

        # Assert
        self.assertEqual(content[22:42], blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_blob_strict_mode_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        content = urandom(512)

        # Assert
        for service in self.blob_types:
            blob_name = self._get_blob_reference(service)
            blob = self.bsc.get_blob_client(self.container_name, blob_name)

            with self.assertRaises(ValueError):
                await blob.upload_blob(content, blob_type=service)

            stream = BytesIO(content)
            with self.assertRaises(ValueError):
                await blob.upload_blob(stream, length=512, blob_type=service)

            file_name = 'strict_mode_async.temp.dat'
            with open(file_name, 'wb') as stream:
                stream.write(content)
            with open(file_name, 'rb') as stream:
                with self.assertRaises(ValueError):
                    await blob.upload_blob(stream, blob_type=service)

            with self.assertRaises(ValueError):
                await blob.upload_blob('To encrypt', blob_type=service)
            self._teardown(file_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_strict_mode_no_policy_async(self, resource_group, location, storage_account,
                                                        storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.key_encryption_key = None

        # Assert
        with self.assertRaises(ValueError):
            await (await blob.download_blob()).content_as_bytes()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_strict_mode_unencrypted_blob_async(self, resource_group, location, storage_account,
                                                               storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.require_encryption = True
        blob.key_encryption_key = KeyWrapper('key1')

        # Assert
        with self.assertRaises(HttpResponseError):
            await (await blob.download_blob()).content_as_bytes()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_invalid_methods_fail_block_async(self, resource_group, location, storage_account,
                                                    storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.BlockBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with self.assertRaises(ValueError) as e:
            await blob.stage_block('block1', urandom(32))
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        with self.assertRaises(ValueError) as e:
            await blob.commit_block_list(['block1'])
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_invalid_methods_fail_append_async(self, resource_group, location, storage_account,
                                                     storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.AppendBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with self.assertRaises(ValueError) as e:
            await blob.append_block(urandom(32))
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        with self.assertRaises(ValueError) as e:
            await blob.create_append_blob()
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        # All append_from operations funnel into append_from_stream, so testing one is sufficient
        with self.assertRaises(ValueError) as e:
            await blob.upload_blob(b'To encrypt', blob_type=BlobType.AppendBlob)
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_invalid_methods_fail_page_async(self, resource_group, location, storage_account,
                                                   storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference(BlobType.PageBlob)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with self.assertRaises(ValueError) as e:
            await blob.upload_page(urandom(512), offset=0, length=512, blob_type=BlobType.PageBlob)
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        with self.assertRaises(ValueError) as e:
            await blob.create_page_blob(512)
        self.assertEqual(str(e.exception), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_validate_encryption_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        kek = KeyWrapper('key1')
        self.bsc.key_encryption_key = kek
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        blob.require_encryption = False
        blob.key_encryption_key = None
        content = await blob.download_blob()
        data = await content.content_as_bytes()

        encryption_data = _dict_to_encryption_data(loads(content.properties.metadata['encryptiondata']))
        iv = encryption_data.content_encryption_IV
        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)
        cipher = _generate_AES_CBC_cipher(content_encryption_key, iv)
        decryptor = cipher.decryptor()
        unpadder = PKCS7(128).unpadder()

        content = decryptor.update(data) + decryptor.finalize()
        content = unpadder.update(content) + unpadder.finalize()

        self.assertEqual(self.bytes, content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_block_blob_from_star_async(self, resource_group, location, storage_account,
                                                     storage_account_key):
        await self._setup(storage_account, storage_account_key)
        await self._create_blob_from_star(BlobType.BlockBlob, "blob1", self.bytes, self.bytes)

        stream = BytesIO(self.bytes)
        await self._create_blob_from_star(BlobType.BlockBlob, "blob2", self.bytes, stream)

        file_name = 'block_star_async.temp.dat'
        with open(file_name, 'wb') as stream:
            stream.write(self.bytes)
        with open(file_name, 'rb') as stream:
            await self._create_blob_from_star(BlobType.BlockBlob, "blob3", self.bytes, stream)

        await self._create_blob_from_star(BlobType.BlockBlob, "blob4", b'To encrypt', 'To encrypt')
        self._teardown(file_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_page_blob_from_star_async(self, resource_group, location, storage_account,
                                                    storage_account_key):
        await self._setup(storage_account, storage_account_key)
        content = self.get_random_bytes(512)
        await self._create_blob_from_star(BlobType.PageBlob, "blob1", content, content)

        stream = BytesIO(content)
        await self._create_blob_from_star(BlobType.PageBlob, "blob2", content, stream, length=512)

        file_name = 'page_star_async.temp.dat'
        with open(file_name, 'wb') as stream:
            stream.write(content)

        with open(file_name, 'rb') as stream:
            await self._create_blob_from_star(BlobType.PageBlob, "blob3", content, stream)
        self._teardown(file_name)

    async def _create_blob_from_star(self, blob_type, blob_name, content, data, **kwargs):
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.key_encryption_key = KeyWrapper('key1')
        blob.require_encryption = True
        await blob.upload_blob(data, blob_type=blob_type, **kwargs)

        blob_content = await (await blob.download_blob()).content_as_bytes()
        self.assertEqual(content, blob_content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_to_star_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        self.bsc.require_encryption = True
        self.bsc.key_encryption_key = KeyWrapper('key1')
        blob = await self._create_small_blob(BlobType.BlockBlob)

        # Act
        content = await blob.download_blob()
        iter_blob = b""
        async for data in content.chunks():
            iter_blob += data
        bytes_blob = await (await blob.download_blob()).content_as_bytes()
        stream_blob = BytesIO()
        await (await blob.download_blob()).download_to_stream(stream_blob)
        stream_blob.seek(0)
        text_blob = await (await blob.download_blob()).content_as_text()

        # Assert
        self.assertEqual(self.bytes, iter_blob)
        self.assertEqual(self.bytes, bytes_blob)
        self.assertEqual(self.bytes, stream_blob.read())
        self.assertEqual(self.bytes.decode(), text_blob)


# ------------------------------------------------------------------------------
