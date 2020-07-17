# # coding: utf-8
#
# # -------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for
# # license information.
# # --------------------------------------------------------------------------
#
# import unittest
#
# import pytest
# from datetime import datetime
#
# from azure.common import AzureException
# from azure.core.exceptions import ResourceExistsError
# from azure.table import TableServiceClient
# from azure.table._entity import EntityProperty, EdmType, Entity
# from azure.table._models import TablePayloadFormat, AccessPolicy, TableSasPermissions, TableServices
# from azure.table._shared._common_conversion import _encode_base64
# from azure.table._shared.encryption import _dict_to_encryption_data, _generate_AES_CBC_cipher
# from dateutil.tz import tzutc
# from os import urandom
# from json import loads
# from copy import deepcopy
#
# # from encryption_test_helper import KeyWrapper, KeyResolver, RSAKeyWrapper
# from testutils.common_recordingtestcase import TestMode
#
# pytestmark = pytest.mark.skip
#
# # from testcase import (
# #     TableTestCase,
# #     TestMode,
# #     record,
# # )
# # from azure.table import (
# #     Entity,
# #     EntityProperty,
# #     TableService,
# #     EdmType,
# #     TableBatch,
# # )
# # from azure.storage.models import(
# #     AccessPolicy,
# # )
# # from tests.test_encryption_helper import(
# #     KeyWrapper,
# #     KeyResolver,
# #     RSAKeyWrapper,
# # )
# # from azure.storage.table.models import(
# #     TablePayloadFormat,
# #     TablePermissions,
# # )
# from azure.table._shared._error import (
#     _ERROR_UNSUPPORTED_TYPE_FOR_ENCRYPTION,
# )
# from azure.table._shared._error import (
#     _ERROR_OBJECT_INVALID,
#     _ERROR_DECRYPTION_FAILURE,
# )
# #Encyption not supported yet
# # from cryptography.hazmat.backends import default_backend
# # from cryptography.hazmat.primitives.ciphers.algorithms import AES
# # from cryptography.hazmat.primitives.ciphers.modes import CBC
# # from cryptography.hazmat.primitives.padding import PKCS7
# # from cryptography.hazmat.primitives.ciphers import Cipher
# # from cryptography.hazmat.primitives.hashes import (
# #     Hash,
# #     SHA256,
# # )
#
# from _shared.testcase import GlobalStorageAccountPreparer, TableTestCase, LogCaptured
#
#
# class StorageTableEncryptionTest(TableTestCase):
#
#     def _set_up(self, storage_account, storage_account_key):
#         self.ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
#         self.table_name = self.get_resource_name('uttable')
#         self.table = self.ts.get_table_client(self.table_name)
#         if self.is_live:
#             try:
#                 self.ts.create_table(table_name=self.table_name)
#             except ResourceExistsError:
#                 pass
#
#         self.query_tables = []
#
#     def _tear_down(self):
#         if self.is_live:
#             try:
#                 self.ts.delete_table(self.table_name)
#             except:
#                 pass
#
#             for table_name in self.query_tables:
#                 try:
#                     self.ts.delete_table(table_name)
#                 except:
#                     pass
#
#     # --Helpers-----------------------------------------------------------------
#
#     def _create_query_table_encrypted(self, entity_count):
#         '''
#         Creates a table with the specified name and adds entities with the
#         default set of values. PartitionKey is set to 'MyPartition' and RowKey
#         is set to a unique counter value starting at 1 (as a string). The
#         'sex' attribute is set to be encrypted.
#         '''
#         table_name = self.get_resource_name('querytable')
#         self.ts.create_table(table_name, True)
#         self.query_tables.append(table_name)
#         self.ts.require_encryption = True
#
#         entity = self._create_default_entity_for_encryption()
#         self.table.create_entity(table_entity_properties=entity)
#        # with self.ts.batch(table_name) as batch:
#         #    for i in range(1, entity_count + 1):
#        #         entity['RowKey'] = entity['RowKey'] + str(i)
#         #        batch.insert_entity(entity)
#         return table_name
#
#     def _create_random_base_entity_class(self):
#         '''
#         Creates a class-based entity with only pk and rk.
#         '''
#         partition = self.get_resource_name('pk')
#         row = self.get_resource_name('rk')
#         entity = Entity()
#         entity.PartitionKey = partition
#         entity.RowKey = row
#         return entity
#
#     def _create_random_base_entity_dict(self):
#         '''
#         Creates a dict-based entity with only pk and rk.
#         '''
#         partition = self.get_resource_name('pk')
#         row = self.get_resource_name('rk')
#         return {'PartitionKey': partition,
#                 'RowKey': row,
#                 }
#
#     def _create_random_entity_class(self, pk=None, rk=None):
#         '''
#         Creates a class-based entity with fixed values, using all
#         of the supported data types.
#         '''
#         partition = pk if pk is not None else self.get_resource_name('pk')
#         row = rk if rk is not None else self.get_resource_name('rk')
#         entity = Entity()
#         entity.PartitionKey = partition
#         entity.RowKey = row
#         entity.age = 39
#         entity.sex = 'male'
#         entity.name = 'John Doe'
#         entity.married = True
#         entity.deceased = False
#         entity.optional = None
#         entity.evenratio = 3.0
#         entity.ratio = 3.1
#         entity.large = 933311100
#         entity.Birthday = datetime(1973, 10, 4)
#         entity.birthday = datetime(1970, 10, 4)
#         entity.binary = EntityProperty(EdmType.BINARY, b'binary')
#         entity.other = EntityProperty(EdmType.INT32, 20)
#         entity.clsid = EntityProperty(
#             EdmType.GUID, 'c9da6455-213d-42c9-9a79-3e9149a57833')
#         return entity
#
#     def _create_default_entity_for_encryption(self):
#         entity = self._create_random_entity_class()
#         entity['sex'] = EntityProperty(EdmType.STRING, entity['sex'], True)
#         entity['name'] = EntityProperty(EdmType.STRING, entity['name'], True)
#         return entity
#
#     def _create_default_entity_dict(self, pk=None, rk=None):
#         '''
#         Creates a dictionary-based entity with fixed values, using all
#         of the supported data types.
#         '''
#         partition = pk if pk is not None else self.get_resource_name('pk')
#         row = rk if rk is not None else self.get_resource_name('rk')
#         return {'PartitionKey': partition,
#                 'RowKey': row,
#                 'age': 39,
#                 'sex': 'male',
#                 'name': 'John Doe',
#                 'married': True,
#                 'deceased': False,
#                 'optional': None,
#                 'ratio': 3.1,
#                 'evenratio': 3.0,
#                 'large': 933311100,
#                 'Birthday': datetime(1973, 10, 4),
#                 'birthday': datetime(1970, 10, 4),
#                 'binary': EntityProperty(EdmType.BINARY, b'binary'),
#                 'other': EntityProperty(EdmType.INT32, 20),
#                 'clsid': EntityProperty(
#                     EdmType.GUID,
#                     'c9da6455-213d-42c9-9a79-3e9149a57833')}
#
#     def _assert_default_entity(self, entity):
#         '''
#         Asserts that the entity passed in matches the default entity.
#         '''
#         self.assertEqual(entity.age, 39)
#         self.assertEqual(entity.sex, 'male')
#         self.assertEqual(entity.name, 'John Doe')
#         self.assertEqual(entity.married, True)
#         self.assertEqual(entity.deceased, False)
#         self.assertFalse(hasattr(entity, "optional"))
#         self.assertFalse(hasattr(entity, "aquarius"))
#         self.assertEqual(entity.ratio, 3.1)
#         self.assertEqual(entity.evenratio, 3.0)
#         self.assertEqual(entity.large, 933311100)
#         self.assertEqual(entity.Birthday, datetime(1973, 10, 4, tzinfo=tzutc()))
#         self.assertEqual(entity.birthday, datetime(1970, 10, 4, tzinfo=tzutc()))
#         self.assertIsInstance(entity.binary, EntityProperty)
#         self.assertEqual(entity.binary.type, EdmType.BINARY)
#         self.assertEqual(entity.binary.value, b'binary')
#         self.assertIsInstance(entity.other, EntityProperty)
#         self.assertEqual(entity.other.type, EdmType.INT32)
#         self.assertEqual(entity.other.value, 20)
#         self.assertIsInstance(entity.clsid, EntityProperty)
#         self.assertEqual(entity.clsid.type, EdmType.GUID)
#         self.assertEqual(entity.clsid.value,
#                          'c9da6455-213d-42c9-9a79-3e9149a57833')
#         self.assertTrue(hasattr(entity, "Timestamp"))
#         self.assertIsInstance(entity.Timestamp, datetime)
#         self.assertIsNotNone(entity.etag)
#
#     def _assert_default_entity_json_no_metadata(self, entity):
#         '''
#         Asserts that the entity passed in matches the default entity.
#         '''
#         self.assertEqual(entity.age, '39')
#         self.assertEqual(entity.sex, 'male')
#         self.assertEqual(entity.name, 'John Doe')
#         self.assertEqual(entity.married, True)
#         self.assertEqual(entity.deceased, False)
#         self.assertFalse(hasattr(entity, "optional"))
#         self.assertFalse(hasattr(entity, "aquarius"))
#         self.assertEqual(entity.ratio, 3.1)
#         self.assertEqual(entity.evenratio, 3.0)
#         self.assertEqual(entity.large, '933311100')
#         self.assertEqual(entity.Birthday, '1973-10-04T00:00:00Z')
#         self.assertEqual(entity.birthday, '1970-10-04T00:00:00Z')
#         self.assertEqual(entity.binary, _encode_base64(b'binary'))
#         self.assertIsInstance(entity.other, EntityProperty)
#         self.assertEqual(entity.other.type, EdmType.INT32)
#         self.assertEqual(entity.other.value, 20)
#         self.assertEqual(entity.clsid, 'c9da6455-213d-42c9-9a79-3e9149a57833')
#         self.assertTrue(hasattr(entity, "Timestamp"))
#         self.assertIsInstance(entity.Timestamp, datetime)
#         self.assertIsNotNone(entity.etag)
#
#     def _default_encryption_resolver(self, x, y, property):
#         return (property == 'sex' or property == 'name')
#
#     # @record
#     def test_get_encrypted_dict(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_dict()
#         entity['sex'] = EntityProperty(EdmType.STRING, entity['sex'], True)
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.table.create_entity(table_entity_properties=entity)
#
#         # Act
#         new_entity = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_encrypted_entity(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         # Only want to encrypt one property in this test
#         entity['name'] = 'John Doe'
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.table.insert_entity(self.table_name, entity)
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_encrypt_multiple_properties(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.create_entity(table_entity_properties=entity)
#
#         # Act
#         new_entity = self.ts.get_entity(entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_encrypted_entity_key_resolver(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         key_resolver = KeyResolver()
#         key_resolver.put_key(self.ts.key_encryption_key)
#         self.ts.key_resolver_function = key_resolver.resolve_key
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.key_encryption_key = None
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_encrypted_entity_encryption_resolver(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_random_entity_class()
#         self.ts.encryption_resolver_function = self._default_encryption_resolver
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#         self.ts.key_encryption_key = None
#         self.ts.require_encryption = False
#         # Retrive a second copy without decrypting to ensure properties were encrypted.
#         new_entity2 = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#         self.assertEqual(EdmType.BINARY, new_entity2['sex'].type)
#         self.assertEqual(EdmType.BINARY, new_entity2['name'].type)
#
#     # @record
#     def test_get_encrypted_entity_properties_and_resolver(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.encryption_resolver_function = self._default_encryption_resolver
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     def _get_with_payload_format(self, format):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         entity['RowKey'] = entity['RowKey'] + format[len('application/json;odata='):]
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'],
#                                         accept=format)
#
#         # Assert
#         if format == TablePayloadFormat.JSON_NO_METADATA:
#             self._assert_default_entity_json_no_metadata(new_entity)
#         else:
#             self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_payload_formats(self):
#         self._get_with_payload_format(TablePayloadFormat.JSON_FULL_METADATA)
#         self._get_with_payload_format(TablePayloadFormat.JSON_MINIMAL_METADATA)
#         self._get_with_payload_format(TablePayloadFormat.JSON_NO_METADATA)
#
#     def test_get_entity_kek_RSA(self):
#         # We can only generate random RSA keys, so this must be run live or
#         # the playback test will fail due to a change in kek values.
#         if TestMode.need_recording_file(self.test_mode):
#             return
#
#             # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = RSAKeyWrapper('key2')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_entity_nonmatching_kid(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_random_entity_class()
#         self.ts.encryption_resolver_function = self._default_encryption_resolver
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.key_encryption_key.kid = 'Invalid'
#
#         # Assert
#         try:
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#             self.fail()
#         except AzureException as e:
#             self.assertEqual(str(e), _ERROR_DECRYPTION_FAILURE)
#
#     # @record
#     def test_get_entity_invalid_value_kek_wrap(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         self.ts.key_encryption_key.get_key_wrap_algorithm = None
#         try:
#             self.ts.insert_entity(self.table_name, entity)
#             self.fail()
#         except AttributeError as e:
#             self.assertEqual(str(e), _ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm'))
#
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         self.ts.key_encryption_key.get_kid = None
#         with self.assertRaises(AttributeError):
#             self.ts.insert_entity(self.table_name, entity)
#
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         self.ts.key_encryption_key.wrap_key = None
#         with self.assertRaises(AttributeError):
#             self.ts.insert_entity(self.table_name, entity)
#
#     # @record
#     def test_get_entity_invalid_value_kek_unwrap(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         self.ts.key_encryption_key.unwrap_key = None
#         try:
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#             self.fail()
#         except AzureException as e:
#             self.assertEqual(str(e), _ERROR_DECRYPTION_FAILURE)
#
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         self.ts.key_encryption_key.get_kid = None
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#     # @record
#     def test_insert_entity_missing_attribute_kek_wrap(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         valid_key = KeyWrapper('key1')
#
#         # Act
#         invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
#         invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
#         invalid_key_1.get_kid = valid_key.get_kid
#         # No attribute wrap_key
#         self.ts.key_encryption_key = invalid_key_1
#         with self.assertRaises(AttributeError):
#             self.ts.insert_entity(self.table_name, entity)
#
#         invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
#         invalid_key_2.wrap_key = valid_key.wrap_key
#         invalid_key_2.get_kid = valid_key.get_kid
#         # No attribute get_key_wrap_algorithm
#         self.ts.key_encryption_key = invalid_key_2
#         with self.assertRaises(AttributeError):
#             self.ts.insert_entity(self.table_name, entity)
#
#         invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
#         invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
#         invalid_key_3.wrap_key = valid_key.wrap_key
#         # No attribute get_kid
#         self.ts.key_encryption_key = invalid_key_3
#         with self.assertRaises(AttributeError):
#             self.ts.insert_entity(self.table_name, entity)
#
#     # @record
#     def test_get_entity_missing_attribute_kek_unwrap(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         valid_key = KeyWrapper('key1')
#         self.ts.key_encryption_key = valid_key
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
#         invalid_key_1.get_kid = valid_key.get_kid
#         # No attribute unwrap_key
#         self.ts.key_encryption_key = invalid_key_1
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
#         invalid_key_2.unwrap_key = valid_key.unwrap_key
#         # No attribute get_kid
#         self.ts.key_encryption_key = invalid_key_2
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#     # @record
#     def test_get_entity_no_decryption(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.key_encryption_key = None
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         # Access the properties to ensure they are still on the entity
#         new_entity['_ClientEncryptionMetadata1']
#         new_entity['_ClientEncryptionMetadata2']
#
#         value = new_entity['sex']
#         self.assertEqual(value.type, EdmType.BINARY)
#
#     # @record
#     def test_replace_entity(self):
#         # Arrange
#         entity = self._create_random_entity_class()
#         self.ts.insert_entity(self.table_name, entity)
#         entity['sex'] = EntityProperty(EdmType.STRING, 'female', True)
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         # Act
#         self.ts.require_encryption = True
#         self.ts.update_entity(self.table_name, entity)
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self.assertEqual(new_entity['sex'], entity['sex'].value)
#
#     # @record
#     def test_insert_strict_mode(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         self.ts.require_encryption = True
#
#         # Assert
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity)
#
#     # @record
#     def test_strict_mode_policy_no_encrypted_properties(self):
#         # Arrange
#         entity = self._create_random_entity_class()
#         self.ts.require_encryption = True
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         # Act
#         # Even when require encryption is true, it should be possilbe to insert
#         # an entity that happens to not have any properties marked for encyrption.
#         self.ts.insert_entity(self.table_name, entity)
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Assert
#         self._assert_default_entity(new_entity)
#
#     # @record
#     def test_get_strict_mode_no_key(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.key_encryption_key = None
#         self.ts.require_encryption = True
#
#         # Assert
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#     # @record
#     def test_get_strict_mode_unencrypted_entity(self):
#         # Arrange
#         entity = self._create_random_base_entity_class()
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.require_encryption = True
#         self.ts.key_encryption_key = KeyWrapper('key1')
#
#         # Assert
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#     # @record
#     @pytest.mark.skip("pending")
#     def test_batch_entity_inserts_context_manager(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity1 = self._create_random_entity_class()
#         entity2 = self._create_random_entity_class(rk='Entity2')
#         entity3 = self._create_random_entity_class(rk='Entity3')
#         entity2['PartitionKey'] = entity1['PartitionKey']
#         entity3['PartitionKey'] = entity1['PartitionKey']
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.require_encryption = True
#         self.ts.encryption_resolver_function = self._default_encryption_resolver
#         self.ts.insert_entity(self.table_name, entity3)
#         entity3['sex'] = 'female'
#
#         # Act
#         with self.ts.batch(self.table_name) as batch:
#             batch.insert_entity(entity1)
#             batch.insert_or_replace_entity(entity2)
#             batch.update_entity(entity3)
#
#         new_entity1 = self.ts.get_entity(self.table_name, entity1['PartitionKey'], entity1['RowKey'])
#         new_entity2 = self.ts.get_entity(self.table_name, entity2['PartitionKey'], entity2['RowKey'])
#         new_entity3 = self.ts.get_entity(self.table_name, entity3['PartitionKey'], entity3['RowKey'])
#
#         # Assert
#         self.assertEqual(new_entity1['sex'], entity1['sex'])
#         self.assertEqual(new_entity2['sex'], entity2['sex'])
#         self.assertEqual(new_entity3['sex'], entity3['sex'])
#
#     # @record
#     @pytest.mark.skip("pending")
#     def test_batch_strict_mode(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#
#         # Act
#         batch = TableBatch(require_encryption=True)
#
#         # Assert
#         with self.assertRaises(ValueError):
#             batch.insert_entity(entity)
#
#     # @record
#     def test_property_resolver_decrypt_conflict(self):
#         # Tests that the encrypted properties list is given priorty
#         # over the property resolver when deserializng (i.e. the
#         # EdmType should be binary, not the result of the resolver)
#
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         property_resolver = lambda x, y, name, a, b: EdmType.STRING if name == 'sex' else None
#
#         # Act
#         new_entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'],
#                                         property_resolver=property_resolver)
#
#         # Assert
#         # If the encrypted property list correctly took priority, this field will have been
#         # properly decrypted
#         self.assertEqual(new_entity['sex'], 'male')
#
#     # @record
#     def test_validate_encryption(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         key_encryption_key = KeyWrapper('key1')
#         self.ts.key_encryption_key = key_encryption_key
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         self.ts.key_encryption_key = None
#         entity = self.ts.get_entity(self.table_name, entity['PartitionKey'], entity['RowKey'])
#
#         # Note the minor discrepancy from the normal decryption process: because the entity was retrieved
#         # without being decrypted, the encrypted_properties list is now stored in an EntityProperty object
#         # and is already raw bytes.
#         encrypted_properties_list = entity['_ClientEncryptionMetadata2'].value
#         encryption_data = entity['_ClientEncryptionMetadata1']
#         encryption_data = _dict_to_encryption_data(loads(encryption_data))
#
#         content_encryption_key = key_encryption_key.unwrap_key(encryption_data.wrapped_content_key.encrypted_key,
#                                                                encryption_data.wrapped_content_key.algorithm)
#
#         digest = Hash(SHA256(), default_backend())
#         digest.update(encryption_data.content_encryption_IV +
#                       (entity['RowKey'] + entity['PartitionKey'] + '_ClientEncryptionMetadata2').encode('utf-8'))
#         metadataIV = digest.finalize()
#         metadataIV = metadataIV[:16]
#
#         cipher = _generate_AES_CBC_cipher(content_encryption_key, metadataIV)
#
#         # Decrypt the data.
#         decryptor = cipher.decryptor()
#         encrypted_properties_list = decryptor.update(encrypted_properties_list) + decryptor.finalize()
#
#         # Unpad the data.
#         unpadder = PKCS7(128).unpadder()
#         encrypted_properties_list = unpadder.update(encrypted_properties_list) + unpadder.finalize()
#
#         encrypted_properties_list = encrypted_properties_list.decode('utf-8')
#
#         # Strip the square braces from the ends and split string into list.
#         encrypted_properties_list = loads(encrypted_properties_list)
#
#         entity_iv, encrypted_properties, content_encryption_key = \
#             (encryption_data.content_encryption_IV, encrypted_properties_list, content_encryption_key)
#
#         decrypted_entity = deepcopy(entity)
#
#         for property in encrypted_properties_list:
#             value = entity[property]
#
#             digest = Hash(SHA256(), default_backend())
#             digest.update(entity_iv +
#                           (entity['RowKey'] + entity['PartitionKey'] + property).encode('utf-8'))
#             propertyIV = digest.finalize()
#             propertyIV = propertyIV[:16]
#
#             cipher = _generate_AES_CBC_cipher(content_encryption_key,
#                                               propertyIV)
#
#             # Decrypt the property.
#             decryptor = cipher.decryptor()
#             decrypted_data = (decryptor.update(value.value) + decryptor.finalize())
#
#             # Unpad the data.
#             unpadder = PKCS7(128).unpadder()
#             decrypted_data = (unpadder.update(decrypted_data) + unpadder.finalize())
#
#             decrypted_data = decrypted_data.decode('utf-8')
#
#             decrypted_entity[property] = decrypted_data
#
#         decrypted_entity.pop('_ClientEncryptionMetadata1')
#         decrypted_entity.pop('_ClientEncryptionMetadata2')
#
#         # Assert
#         self.assertEqual(decrypted_entity['sex'], 'male')
#
#     # @record
#     def test_insert_encrypt_invalid_types(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity_binary = self._create_random_entity_class()
#         entity_binary['bytes'] = EntityProperty(EdmType.BINARY, urandom(10), True)
#         entity_boolean = self._create_random_entity_class()
#         entity_boolean['married'] = EntityProperty(EdmType.BOOLEAN, True, True)
#         entity_date_time = self._create_random_entity_class()
#         entity_date_time['birthday'] = EntityProperty(EdmType.DATETIME, entity_date_time['birthday'], True)
#         entity_double = self._create_random_entity_class()
#         entity_double['ratio'] = EntityProperty(EdmType.DATETIME, entity_double['ratio'], True)
#         entity_guid = self._create_random_entity_class()
#         entity_guid['clsid'].encrypt = True
#         entity_int32 = self._create_random_entity_class()
#         entity_int32['other'].encrypt = True
#         entity_int64 = self._create_random_entity_class()
#         entity_int64['large'] = EntityProperty(EdmType.INT64, entity_int64['large'], True)
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         entity_none_str = self._create_random_entity_class()
#         entity_none_str['none_str'] = EntityProperty(EdmType.STRING, None, True)
#
#         # Act
#
#         # Assert
#         try:
#             self.ts.insert_entity(self.table_name, entity_binary)
#             self.fail()
#         except ValueError as e:
#             self.assertEqual(str(e), _ERROR_UNSUPPORTED_TYPE_FOR_ENCRYPTION)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_boolean)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_date_time)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_double)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_guid)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_int32)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_int64)
#         with self.assertRaises(ValueError):
#             self.ts.insert_entity(self.table_name, entity_none_str)
#
#     # @record
#     def test_invalid_encryption_operations_fail(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Assert
#         with self.assertRaises(ValueError):
#             self.ts.merge_entity(self.table_name, entity)
#
#         with self.assertRaises(ValueError):
#             self.ts.insert_or_merge_entity(self.table_name, entity)
#
#         self.ts.require_encryption = True
#         self.ts.key_encryption_key = None
#
#         with self.assertRaises(ValueError):
#             self.ts.merge_entity(self.table_name, entity)
#
#         with self.assertRaises(ValueError):
#             self.ts.insert_or_merge_entity(self.table_name, entity)
#
#     # @record
#     @pytest.mark.skip("pending")
#     def test_invalid_encryption_operations_fail_batch(self):
#         # Arrange
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         batch = TableBatch(require_encryption=True, key_encryption_key=self.ts.key_encryption_key)
#
#         # Assert
#         with self.assertRaises(ValueError):
#             batch.merge_entity(entity)
#
#         with self.assertRaises(ValueError):
#             batch.insert_or_merge_entity(entity)
#
#     # @record
#     def test_query_entities_all_properties(self):
#         # Arrange
#         self.ts.require_encryption = True
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         table_name = self._create_query_table_encrypted(5)
#         default_entity = self._create_random_entity_class()
#
#         # Act
#         resp = self.ts.query_entities(table_name, num_results=5)
#
#         # Assert
#         self.assertEqual(len(resp.items), 5)
#         for entity in resp.items:
#             self.assertEqual(default_entity['sex'], entity['sex'])
#
#     # @record
#     def test_query_entities_projection(self):
#         # Arrange
#         self.ts.require_encryption = True
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         table_name = self._create_query_table_encrypted(5)
#         default_entity = self._create_random_entity_class()
#
#         # Act
#         resp = self.ts.query_entities(table_name, num_results=5, select='PartitionKey,RowKey,sex')
#
#         # Assert
#         for entity in resp.items:
#             self.assertEqual(default_entity['sex'], entity['sex'])
#             self.assertFalse(hasattr(entity, '_ClientEncryptionMetadata1'))
#             self.assertFalse(hasattr(entity, '_ClientEncryptionMetadata2'))
#
#     # @record
#     def test_query_entities_mixed_mode(self):
#         # Arrange
#         entity = self._create_random_entity_class(rk='unencrypted')
#         entity['RowKey'] += 'unencrypted'
#         self.ts.insert_entity(self.table_name, entity)
#         entity = self._create_default_entity_for_encryption()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         self.ts.insert_entity(self.table_name, entity)
#
#         # Act
#         # Pass with out encryption_required
#         self.ts.query_entities(self.table_name)
#
#         # Assert
#         # Fail with encryption_required because not all returned entities
#         # will be encrypted.
#         self.ts.require_encryption = True
#         with self.assertRaises(AzureException):
#             self.ts.query_entities(self.table_name)
#
#     # @record
#     def test_insert_entity_too_many_properties(self):
#         # Arrange
#         self.ts.require_encryption = True
#         entity = self._create_random_base_entity_dict()
#         self.ts.key_encryption_key = KeyWrapper('key1')
#         for i in range(251):
#             entity['key{0}'.format(i)] = 'value{0}'.format(i)
#
#         # Act
#         with self.assertRaises(ValueError):
#             resp = self.ts.insert_entity(self.table_name, entity)
#
#     # @record
#     def test_validate_swapping_properties_fails(self):
#         # Arrange
#         entity1 = self._create_random_entity_class(rk='entity1')
#         entity2 = self._create_random_entity_class(rk='entity2')
#         kek = KeyWrapper('key1')
#         self.ts.key_encryption_key = kek
#         self.ts.encryption_resolver_function = self._default_encryption_resolver
#         self.ts.insert_entity(self.table_name, entity1)
#         self.ts.insert_entity(self.table_name, entity2)
#
#         # Act
#         self.ts.key_encryption_key = None
#         new_entity1 = self.ts.get_entity(self.table_name, entity1['PartitionKey'], entity1['RowKey'])
#         new_entity2 = deepcopy(new_entity1)
#         new_entity2['PartitionKey'] = entity2['PartitionKey']
#         new_entity2['RowKey'] = entity2['RowKey']
#         self.ts.update_entity(self.table_name, new_entity2)
#         self.ts.key_encryption_key = kek
#
#         # Assert
#         with self.assertRaises(AzureException):
#             self.ts.get_entity(self.table_name, new_entity2['PartitionKey'], new_entity2['RowKey'])
#
#     # @record
#     def test_table_ops_ignore_encryption(self):
#         table_name = self.get_resource_name('EncryptionTableOps')
#         try:
#             # Arrange
#             self.ts.require_encryption = True
#             self.ts.key_encryption_key = KeyWrapper('key1')
#
#             # Act
#             self.assertTrue(self.ts.create_table(table_name))
#
#             self.assertTrue(self.ts.exists(table_name))
#
#             list_tables = self.ts.list_tables()
#             test_table_exists = False
#             for table in list_tables:
#                 if table.name == table_name:
#                     test_table_exists = True
#             self.assertTrue(test_table_exists)
#
#             permissions = self.ts.get_table_acl(table_name)
#             new_policy = AccessPolicy(TableSasPermissions(_str='r'), expiry=datetime(2017, 9, 9))
#             permissions['samplePolicy'] = new_policy
#             self.ts.set_table_acl(table_name, permissions)
#             permissions = self.ts.get_table_acl(table_name)
#             permissions['samplePolicy']
#             self.ts.key_encryption_key = None
#             permissions = self.ts.get_table_acl(table_name)
#             permissions['samplePolicy']
#
#             self.ts.delete_table(table_name)
#             self.assertFalse(self.ts.exists(table_name))
#         finally:
#             self.ts.delete_table(table_name)
#
#
# # ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     unittest.main()
