# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

pytestmark = pytest.mark.skip

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

from azure.common import AzureException
from azure.storage.common._encryption import (
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _generate_AES_CBC_cipher,
)
from azure.storage.common._error import (
    _ERROR_OBJECT_INVALID,
    _ERROR_DECRYPTION_FAILURE,
    _ERROR_VALUE_SHOULD_BE_BYTES,
    _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION,
)
from cryptography.hazmat.primitives.padding import PKCS7

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from tests.encryption_test_helper import (
    KeyWrapper,
    KeyResolver,
    RSAKeyWrapper,
)
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'encryption_container'
TEST_BLOB_PREFIXES = {'block_blob':'encryption_block_blob',
                      'page_blob':'encryption_page_blob'}
FILE_PATH = 'blob_input.temp.dat'
#------------------------------------------------------------------------------

class StorageBlobEncryptionTest(StorageTestCase):

    def setUp(self):
        super(StorageBlobEncryptionTest, self).setUp()

        self.bbs = self._create_storage_service(BlockBlobService, self.settings)
        self.pbs = self._create_storage_service(PageBlobService, self.settings)
        self.service_dict = {'block_blob':self.bbs,
                             'page_blob':self.pbs}
        self.container_name = self.get_resource_name('utcontainer')
        self.bytes = b'Foo'

        if not self.is_playback():
            self.bbs.create_container(self.container_name)

        self.bbs.MAX_BLOCK_SIZE = 4 * 1024
        self.bbs.MAX_SINGLE_PUT_SIZE = 32 * 1024
        self.pbs.MAX_PAGE_SIZE = 4 * 1024

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bbs.delete_container(self.container_name)
            except:
                pass
        if path.isfile(FILE_PATH):
            try:
                remove(FILE_PATH)
            except:
                pass

        return super(StorageBlobEncryptionTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self, type):
        return self.get_resource_name(TEST_BLOB_PREFIXES[type])

    def _create_small_blob(self, type):
        blob_name = self._get_blob_reference(type)
        self.service_dict[type].create_blob_from_bytes(self.container_name, blob_name, self.bytes)
        return blob_name
        
    #--Test cases for blob encryption ----------------------------------------

    @record
    def test_missing_attribute_kek_wrap(self):
        # In the shared method _generate_blob_encryption_key
        # Arrange
        self.bbs.require_encryption = True
        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        self.bbs.key_encryption_key = invalid_key_1
        with self.assertRaises(AttributeError):
            self._create_small_blob('block_blob')

        invalid_key_2 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        self.bbs.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            self._create_small_blob('block_blob')
        
        invalid_key_3 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        self.bbs.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            self._create_small_blob('block_blob')

    @record
    def test_invalid_value_kek_wrap(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')

        self.bbs.key_encryption_key.get_key_wrap_algorithm = None
        try:
            self._create_small_blob('block_blob')
            self.fail()
        except AttributeError as e:
            self.assertEqual(str(e), _ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm'))

        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.key_encryption_key.get_kid = None
        with self.assertRaises(AttributeError):
            self._create_small_blob('block_blob')

        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.key_encryption_key.wrap_key = None
        with self.assertRaises(AttributeError):
            self._create_small_blob('block_blob')

    @record
    def test_missing_attribute_kek_unwrap(self):
        # Shared between all services in _decrypt_blob
        # Arrange
        self.bbs.require_encryption = True
        valid_key = KeyWrapper('key1')
        self.bbs.key_encryption_key = valid_key
        blob_name = self._create_small_blob('block_blob')

        # Act
        # Note that KeyWrapper has a default value for key_id, so these Exceptions
        # are not due to non_matching kids.
        invalid_key_1 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_1.get_kid = valid_key.get_kid
        #No attribute unwrap_key
        self.bbs.key_encryption_key = invalid_key_1
        with self.assertRaises(AzureException):
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        invalid_key_2 = lambda: None #functions are objects, so this effectively creates an empty object
        invalid_key_2.unwrap_key = valid_key.unwrap_key
        #No attribute get_kid
        with self.assertRaises(AzureException):
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)

    @record
    def test_invalid_value_kek_unwrap(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.key_encryption_key.unwrap_key = None
        try:
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)
            self.fail()
        except AzureException as e:
            self.assertEqual(str(e), _ERROR_DECRYPTION_FAILURE)

    @record
    def test_get_blob_kek(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._create_small_blob('block_blob')

        # Act
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(blob.content, self.bytes)
        

    @record
    def test_get_blob_resolver(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        key_resolver = KeyResolver()
        key_resolver.put_key(self.bbs.key_encryption_key)
        self.bbs.key_resolver_function = key_resolver.resolve_key
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.key_encryption_key = None
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(blob.content, self.bytes)

    def test_get_blob_kek_RSA(self):
        # We can only generate random RSA keys, so this must be run live or 
        # the playback test will fail due to a change in kek values.
        if TestMode.need_recording_file(self.test_mode):
            return 

        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = RSAKeyWrapper('key2')
        blob_name = self._create_small_blob('block_blob')

        # Act
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(blob.content, self.bytes)

    @record
    def test_get_blob_nonmatching_kid(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.key_encryption_key.kid = 'Invalid'

        # Assert
        try:
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)
            self.fail()
        except AzureException as e:
            self.assertEqual(str(e), _ERROR_DECRYPTION_FAILURE)

    @record
    def test_put_blob_invalid_stream_type(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        small_stream = StringIO(u'small')
        large_stream = StringIO(u'large' * self.bbs.MAX_SINGLE_PUT_SIZE)
        blob_name = self._get_blob_reference('block_blob')

        # Assert
        # Block blob specific single shot
        try:
            self.bbs.create_blob_from_stream(self.container_name, blob_name, small_stream, count=5)
            self.fail()
        except TypeError as e:
            self.assertEqual(str(e), _ERROR_VALUE_SHOULD_BE_BYTES.format('blob'))

        # Generic blob chunked
        with self.assertRaises(TypeError):
            self.bbs.create_blob_from_stream(self.container_name, blob_name, large_stream)

    def test_put_blob_chunking_required_mult_of_block_size(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(self.bbs.MAX_SINGLE_PUT_SIZE + self.bbs.MAX_BLOCK_SIZE)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content, max_connections=3)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content, blob.content)

    def test_put_blob_chunking_required_non_mult_of_block_size(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = urandom(self.bbs.MAX_SINGLE_PUT_SIZE + 1)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content, max_connections=3)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content, blob.content)

    def test_put_blob_chunking_required_range_specified(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(self.bbs.MAX_SINGLE_PUT_SIZE * 2)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content, max_connections=3,
                                        count=self.bbs.MAX_SINGLE_PUT_SIZE+53)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content[:self.bbs.MAX_SINGLE_PUT_SIZE+53], blob.content)

    @record
    def test_put_block_blob_single_shot(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = b'small'
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content, blob.content)

    @record
    def test_put_blob_range(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        content = b'Random repeats' * self.bbs.MAX_SINGLE_PUT_SIZE * 5

        # All page blob uploads call _upload_chunks, so this will test the ability
        # of that function to handle ranges even though it's a small blob
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content, index=2,
                                        count=self.bbs.MAX_SINGLE_PUT_SIZE + 5,
                                        max_connections=1)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content[2:2 + self.bbs.MAX_SINGLE_PUT_SIZE + 5], blob.content)

    @record
    def test_put_blob_empty(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = b''
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(content, blob.content)

    @record
    def test_put_blob_serial_upload_chunking(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(self.bbs.MAX_SINGLE_PUT_SIZE + 1)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content, max_connections=1)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, max_connections=1)

        # Assert
        self.assertEqual(content, blob.content)

    @record
    def test_get_blob_range_beginning_to_middle(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=0, end_range=50)

        # Assert
        self.assertEqual(content[:51], blob.content)

    @record
    def test_get_blob_range_middle_to_end(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=50, end_range=127)
        blob2 = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=50)

        # Assert
        self.assertEqual(content[50:], blob.content)
        self.assertEqual(content[50:], blob.content)

    @record
    def test_get_blob_range_middle_to_middle(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=50, end_range=93)

        # Assert
        self.assertEqual(content[50:94], blob.content)

    @record
    def test_get_blob_range_aligns_on_16_byte_block(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=48, end_range=63,
                                          max_connections=1)

        # Assert
        self.assertEqual(content[48:64], blob.content)

    @record
    def test_get_blob_range_expanded_to_beginning_block_align(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=5, end_range=50)

        # Assert
        self.assertEqual(content[5:51], blob.content)

    @record
    def test_get_blob_range_expanded_to_beginning_iv(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        self.bbs.require_encryption = True
        content = self.get_random_bytes(128)
        blob_name = self._get_blob_reference('block_blob')

        # Act
        self.bbs.create_blob_from_bytes(self.container_name, blob_name, content)
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name, start_range=22, end_range=42)

        # Assert
        self.assertEqual(content[22:43], blob.content)

    @record
    def test_put_blob_strict_mode(self):
        # Arrange
        blob_name = self._get_blob_reference('block_blob')
        for service in self.service_dict.values():
            service.require_encryption = True
        content = urandom(512)

        # Assert
        for service in self.service_dict.values():
            with self.assertRaises(ValueError):
                service.create_blob_from_bytes(self.container_name, blob_name, content)

            stream = BytesIO(content)
            with self.assertRaises(ValueError):
                service.create_blob_from_stream(self.container_name, blob_name, stream, count=512)

            FILE_PATH = 'blob_input.temp.dat'
            with open(FILE_PATH, 'wb') as stream:
                stream.write(content)
            with self.assertRaises(ValueError):
                service.create_blob_from_path(self.container_name, blob_name, FILE_PATH)

            if not isinstance(service, PageBlobService):
                with self.assertRaises(ValueError):
                    service.create_blob_from_text(self.container_name, blob_name, 'To encrypt')


    @record
    def test_get_blob_strict_mode_no_policy(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.key_encryption_key = None

        # Assert
        with self.assertRaises(ValueError):
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)


    @record
    def test_get_blob_strict_mode_unencrypted_blob(self):
        # Arrange
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')

        # Assert
        with self.assertRaises(AzureException):
            self.bbs.get_blob_to_bytes(self.container_name, blob_name)

    @record
    def test_invalid_methods_fail_block(self):
        # Arrange
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference('block_blob')

        # Assert
        try:
            self.bbs.put_block(self.container_name, blob_name, urandom(32), 'block1')
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        try:
            self.bbs.put_block_list(self.container_name, blob_name, ['block1'])
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

    @record
    def test_invalid_methods_fail_append(self):
        # Arrange
        abs = self._create_storage_service(AppendBlobService, self.settings)
        abs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference('block_blob')

        # Assert
        try:
            abs.append_block(self.container_name, blob_name, urandom(32), 'block1')
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        try:
            abs.create_blob(self.container_name, blob_name)
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        # All append_from operations funnel into append_from_stream, so testing one is sufficient
        with self.assertRaises(ValueError):
            abs.append_blob_from_bytes(self.container_name, blob_name, b'To encrypt')

    @record
    def test_invalid_methods_fail_page(self):
        # Arrange
        self.pbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._get_blob_reference('page_blob')

        # Assert
        try:
            self.pbs.update_page(self.container_name, blob_name, urandom(512), 0, 511)
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        try:
            self.pbs.create_blob(self.container_name, blob_name, 512)
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

    @record
    def test_validate_encryption(self):
        # Arrange
        self.bbs.require_encryption = True
        kek = KeyWrapper('key1')
        self.bbs.key_encryption_key = kek
        blob_name = self._create_small_blob('block_blob')

        # Act
        self.bbs.require_encryption = False
        self.bbs.key_encryption_key = None
        blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)

        encryption_data = _dict_to_encryption_data(loads(blob.metadata['encryptiondata']))
        iv = encryption_data.content_encryption_IV
        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)
        cipher = _generate_AES_CBC_cipher(content_encryption_key, iv)
        decryptor = cipher.decryptor()
        unpadder = PKCS7(128).unpadder()

        content = decryptor.update(blob.content) + decryptor.finalize()
        content = unpadder.update(content) + unpadder.finalize()
        
        self.assertEqual(self.bytes, content)

    @record
    def test_create_block_blob_from_star(self):
        self._create_blob_from_star('block_blob', self.bytes, self.bbs.create_blob_from_bytes, self.bytes)

        stream = BytesIO(self.bytes)
        self._create_blob_from_star('block_blob', self.bytes, self.bbs.create_blob_from_stream, stream)

        FILE_PATH = 'blob_input.temp.dat'
        with open(FILE_PATH, 'wb') as stream:
            stream.write(self.bytes)
        self._create_blob_from_star('block_blob', self.bytes, self.bbs.create_blob_from_path, FILE_PATH)

        self._create_blob_from_star('block_blob', b'To encrypt', self.bbs.create_blob_from_text, 'To encrypt')

    @record
    def test_create_page_blob_from_star(self):
        content = self.get_random_bytes(512)
        self._create_blob_from_star('page_blob', content, self.pbs.create_blob_from_bytes, content)

        stream = BytesIO(content)
        self._create_blob_from_star('page_blob', content, self.pbs.create_blob_from_stream, stream, count=512)

        FILE_PATH = 'blob_input.temp.dat'
        with open(FILE_PATH, 'wb') as stream:
            stream.write(content)
        self._create_blob_from_star('page_blob', content, self.pbs.create_blob_from_path, FILE_PATH)
            
    def _create_blob_from_star(self, type, content, create_method, data, **kwargs):
        self.service_dict[type].key_encryption_key = KeyWrapper('key1')
        self.service_dict[type].require_encryption = True
        blob_name = self._get_blob_reference(type)

        create_method(self.container_name, blob_name, data, **kwargs)

        blob = self.service_dict[type].get_blob_to_bytes(self.container_name, blob_name)

        self.assertEqual(content, blob.content)

    @record
    def test_get_blob_to_star(self):
        # Arrange
        self.bbs.require_encryption = True
        self.bbs.key_encryption_key = KeyWrapper('key1')
        blob_name = self._create_small_blob('block_blob')

        # Act
        bytes_blob = self.bbs.get_blob_to_bytes(self.container_name, blob_name)
        stream = BytesIO()
        self.bbs.get_blob_to_stream(self.container_name, blob_name, stream)
        stream.seek(0)
        text_blob = self.bbs.get_blob_to_text(self.container_name, blob_name, encoding='utf-8')
        self.bbs.get_blob_to_path(self.container_name, blob_name, FILE_PATH)

        # Assert
        self.assertEqual(self.bytes, bytes_blob.content)
        self.assertEqual(self.bytes, stream.read())
        self.assertEqual(self.bytes.decode(), text_blob.content)
        with open(FILE_PATH, 'rb') as stream:
            self.assertEqual(self.bytes, stream.read()) 

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()