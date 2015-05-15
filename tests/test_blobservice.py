# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import base64
import datetime
import os
import random
import requests
import sys
import time
import unittest
if sys.version_info < (3,):
    from httplib import HTTPConnection
else:
    from http.client import HTTPConnection

from azure import (
    WindowsAzureError,
    WindowsAzureConflictError,
    WindowsAzureMissingResourceError,
    BLOB_SERVICE_HOST_BASE,
    )
from azure.http import (
    HTTPRequest,
    HTTPResponse,
    )
from azure.storage import (
    AccessPolicy,
    BlobBlockList,
    BlobResult,
    BlobSharedAccessPermissions,
    ContainerSharedAccessPermissions,
    Logging,
    HourMetrics,
    MinuteMetrics,
    PageList,
    PageRange,
    SignedIdentifier,
    SignedIdentifiers,
    StorageServiceProperties,
    )
from azure.storage.blobservice import BlobService
from azure.storage.storageclient import (
    AZURE_STORAGE_ACCESS_KEY,
    AZURE_STORAGE_ACCOUNT,
    EMULATED,
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY,
    )
from azure.storage.sharedaccesssignature import SharedAccessPolicy
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
    )


#------------------------------------------------------------------------------


class BlobServiceTest(AzureTestCase):

    def setUp(self):
        self.bs = BlobService(credentials.getStorageServicesName(),
                              credentials.getStorageServicesKey())
        set_service_options(self.bs)

        remote_storage_service_name = credentials.getRemoteStorageServicesName()
        remote_storage_service_key = credentials.getRemoteStorageServicesKey()
        if remote_storage_service_key and remote_storage_service_name:
            self.bs2 = BlobService(credentials.getRemoteStorageServicesName(),
                                   credentials.getRemoteStorageServicesKey())
            set_service_options(self.bs2)
        else:
            print("Remote Storage Account not configured. Add " \
                  "'remotestorageserviceskey' and 'remotestorageservicesname'" \
                  " to windowsazurecredentials.json to test functionality " \
                  "involving multiple storage accounts.")

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bs._BLOB_MAX_DATA_SIZE = 64 * 1024
        self.bs._BLOB_MAX_CHUNK_DATA_SIZE = 4 * 1024

        self.container_name = getUniqueName('utcontainer')
        self.container_lease_id = None
        self.additional_container_names = []
        self.remote_container_name = None

    def tearDown(self):
        self.cleanup()
        return super(BlobServiceTest, self).tearDown()

    def cleanup(self):
        if self.container_lease_id:
            try:
                self.bs.lease_container(
                    self.container_name, 'release', self.container_lease_id)
            except:
                pass
        try:
            self.bs.delete_container(self.container_name)
        except:
            pass

        for name in self.additional_container_names:
            try:
                self.bs.delete_container(name)
            except:
                pass

        if self.remote_container_name:
            try:
                self.bs2.delete_container(self.remote_container_name)
            except:
                pass

        for tmp_file in ['blob_input.temp.dat', 'blob_output.temp.dat']:
            if os.path.isfile(tmp_file):
                try:
                    os.remove(tmp_file)
                except:
                    pass

    #--Helpers-----------------------------------------------------------------
    def _create_container(self, container_name):
        self.bs.create_container(container_name, None, None, True)

    def _create_container_and_block_blob(self, container_name, blob_name,
                                         blob_data):
        self._create_container(container_name)
        resp = self.bs.put_blob(
            container_name, blob_name, blob_data, 'BlockBlob')
        self.assertIsNone(resp)

    def _create_container_and_page_blob(self, container_name, blob_name,
                                        content_length):
        self._create_container(container_name)
        resp = self.bs.put_blob(self.container_name, blob_name, b'',
                                'PageBlob',
                                x_ms_blob_content_length=str(content_length))
        self.assertIsNone(resp)

    def _create_container_and_block_blob_with_random_data(self, container_name,
                                                          blob_name,
                                                          block_count,
                                                          block_size):
        self._create_container_and_block_blob(container_name, blob_name, '')
        block_list = []
        for i in range(0, block_count):
            block_id = '{0:04d}'.format(i)
            block_data = os.urandom(block_size)
            self.bs.put_block(container_name, blob_name, block_data, block_id)
            block_list.append(block_id)
        self.bs.put_block_list(container_name, blob_name, block_list)

    def _blob_exists(self, container_name, blob_name):
        resp = self.bs.list_blobs(container_name)
        for blob in resp:
            if blob.name == blob_name:
                return True
        return False

    def _create_remote_container_and_block_blob(self, source_blob_name, data,
                                                x_ms_blob_public_access):
        self.remote_container_name = getUniqueName('remotectnr')
        self.bs2.create_container(
            self.remote_container_name,
            x_ms_blob_public_access=x_ms_blob_public_access)
        self.bs2.put_block_blob_from_bytes(
            self.remote_container_name, source_blob_name, data)
        source_blob_url = self.bs2.make_blob_url(
            self.remote_container_name, source_blob_name)
        return source_blob_url

    def _wait_for_async_copy(self, container_name, blob_name):
        count = 0
        props = self.bs.get_blob_properties(container_name, blob_name)
        while props['x-ms-copy-status'] != 'success':
            count = count + 1
            if count > 5:
                self.assertTrue(
                    False, 'Timed out waiting for async copy to complete.')
            time.sleep(5)
            props = self.bs.get_blob_properties(container_name, blob_name)
        self.assertEqual(props['x-ms-copy-status'], 'success')

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        actual_data = self.bs.get_blob(container_name, blob_name)
        self.assertEqual(actual_data, expected_data)

    def assertBlobLengthEqual(self, container_name, blob_name, expected_length):
        props = self.bs.get_blob_properties(container_name, blob_name)
        self.assertEqual(int(props['content-length']), expected_length)

    def _get_oversized_binary_data(self):
        '''Returns random binary data exceeding the size threshold for
        chunking blob upload.'''
        size = self.bs._BLOB_MAX_DATA_SIZE + 12345
        return os.urandom(size)

    def _get_expected_progress(self, blob_size, unknown_size=False):
        result = []
        index = 0
        total = None if unknown_size else blob_size
        while (index < blob_size):
            result.append((index, total))
            index += self.bs._BLOB_MAX_CHUNK_DATA_SIZE
        result.append((blob_size, total))
        return result

    def _get_oversized_page_blob_binary_data(self):
        '''Returns random binary data exceeding the size threshold for
        chunking blob upload.'''
        size = self.bs._BLOB_MAX_DATA_SIZE + 16384
        return os.urandom(size)

    def _get_oversized_text_data(self):
        '''Returns random unicode text data exceeding the size threshold for
        chunking blob upload.'''
        size = self.bs._BLOB_MAX_DATA_SIZE + 12345
        text = u''
        words = [u'hello', u'world', u'python', u'啊齄丂狛狜']
        while (len(text) < size):
            index = random.randint(0, len(words) - 1)
            text = text + u' ' + words[index]

        return text

    def _get_shared_access_policy(self, permission):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        expiry = start + datetime.timedelta(hours=1)
        return SharedAccessPolicy(
            AccessPolicy(
                start.strftime(date_format),
                expiry.strftime(date_format),
                permission
            )
        )

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for blob service --------------------------------------------
    def test_create_blob_service_missing_arguments(self):
        # Arrange
        if AZURE_STORAGE_ACCOUNT in os.environ:
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if AZURE_STORAGE_ACCESS_KEY in os.environ:
            del os.environ[AZURE_STORAGE_ACCESS_KEY]
        if EMULATED in os.environ:
            del os.environ[EMULATED]

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        # Assert

    def test_create_blob_service_env_variables(self):
        # Arrange
        os.environ[
            AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[
            AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if AZURE_STORAGE_ACCOUNT in os.environ:
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if AZURE_STORAGE_ACCESS_KEY in os.environ:
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEqual(bs.account_name, credentials.getStorageServicesName())
        self.assertEqual(bs.account_key, credentials.getStorageServicesKey())
        self.assertEqual(bs.is_emulated, False)

    def test_create_blob_service_emulated_true(self):
        # Arrange
        os.environ[EMULATED] = 'true'

        # Act
        bs = BlobService()

        if EMULATED in os.environ:
            del os.environ[EMULATED]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEqual(bs.account_name, DEV_ACCOUNT_NAME)
        self.assertEqual(bs.account_key, DEV_ACCOUNT_KEY)
        self.assertEqual(bs.is_emulated, True)

    def test_create_blob_service_emulated_false(self):
        # Arrange
        os.environ[EMULATED] = 'false'

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        if EMULATED in os.environ:
            del os.environ[EMULATED]

        # Assert

    def test_create_blob_service_emulated_false_env_variables(self):
        # Arrange
        os.environ[EMULATED] = 'false'
        os.environ[
            AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[
            AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if EMULATED in os.environ:
            del os.environ[EMULATED]
        if AZURE_STORAGE_ACCOUNT in os.environ:
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if AZURE_STORAGE_ACCESS_KEY in os.environ:
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEqual(bs.account_name, credentials.getStorageServicesName())
        self.assertEqual(bs.account_key, credentials.getStorageServicesKey())
        self.assertEqual(bs.is_emulated, False)

    def test_create_blob_service_connection_string(self):
        # Arrange
        connection_string = 'DefaultEndpointsProtocol={};AccountName={};AccountKey={}'.format(
                            'http', credentials.getStorageServicesName(),
                            credentials.getStorageServicesKey())
        
        # Act
        bs = BlobService(connection_string = connection_string)
        
        # Assert
        self.assertIsNotNone(bs)
        self.assertEqual(bs.account_name, credentials.getStorageServicesName())
        self.assertEqual(bs.account_key, credentials.getStorageServicesKey())
        self.assertEqual(bs.protocol, 'http')
        self.assertEqual(bs.host_base, BLOB_SERVICE_HOST_BASE)
        self.assertFalse(bs.is_emulated)
        
    #--Test cases for containers -----------------------------------------
    def test_create_container_no_options(self):
        # Arrange

        # Act
        created = self.bs.create_container(self.container_name)

        # Assert
        self.assertTrue(created)

    def test_create_container_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bs.create_container(
            self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_already_existing_container(self):
        # Arrange

        # Act
        created1 = self.bs.create_container(self.container_name)
        created2 = self.bs.create_container(self.container_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_container_with_already_existing_container_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bs.create_container(self.container_name)
        with self.assertRaises(WindowsAzureError):
            self.bs.create_container(self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_public_access_container(self):
        # Arrange

        # Act
        created = self.bs.create_container(
            self.container_name, None, 'container')

        # Assert
        self.assertTrue(created)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_public_access_blob(self):
        # Arrange

        # Act
        created = self.bs.create_container(self.container_name, None, 'blob')

        # Assert
        self.assertTrue(created)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_metadata(self):
        # Arrange

        # Act
        created = self.bs.create_container(
            self.container_name, {'hello': 'world', 'number': '42'})

        # Assert
        self.assertTrue(created)
        md = self.bs.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    def test_list_containers_no_options(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        containers = self.bs.list_containers()
        for container in containers:
            name = container.name

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)

    def test_list_containers_with_prefix(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        containers = self.bs.list_containers(self.container_name)

        # Assert
        self.assertIsNotNone(containers)
        self.assertEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertEqual(containers[0].name, self.container_name)
        self.assertIsNone(containers[0].metadata)

    def test_list_containers_with_include_metadata(self):
        # Arrange
        self.bs.create_container(self.container_name)
        resp = self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '43'})

        # Act
        containers = self.bs.list_containers(
            self.container_name, None, None, 'metadata')

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)
        self.assertEqual(containers[0].metadata['hello'], 'world')
        self.assertEqual(containers[0].metadata['number'], '43')

    def test_list_containers_with_maxresults_and_marker(self):
        # Arrange
        self.additional_container_names = [self.container_name + 'a',
                                           self.container_name + 'b',
                                           self.container_name + 'c',
                                           self.container_name + 'd']
        for name in self.additional_container_names:
            self.bs.create_container(name)

        # Act
        containers1 = self.bs.list_containers(self.container_name, None, 2)
        containers2 = self.bs.list_containers(
            self.container_name, containers1.next_marker, 2)

        # Assert
        self.assertIsNotNone(containers1)
        self.assertEqual(len(containers1), 2)
        self.assertNamedItemInContainer(containers1, self.container_name + 'a')
        self.assertNamedItemInContainer(containers1, self.container_name + 'b')
        self.assertIsNotNone(containers2)
        self.assertEqual(len(containers2), 2)
        self.assertNamedItemInContainer(containers2, self.container_name + 'c')
        self.assertNamedItemInContainer(containers2, self.container_name + 'd')

    def test_set_container_metadata(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        resp = self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '43'})

        # Assert
        self.assertIsNone(resp)
        md = self.bs.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '43')

    def test_set_container_metadata_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        resp = self.bs.set_container_metadata(
            self.container_name,
            {'hello': 'world', 'number': '43'},
            lease['x-ms-lease-id'])

        # Assert
        self.assertIsNone(resp)
        md = self.bs.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '43')

    def test_set_container_metadata_with_non_matching_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        non_matching_lease_id = '00000000-1111-2222-3333-444444444444'
        with self.assertRaises(WindowsAzureError):
            self.bs.set_container_metadata(
                self.container_name,
                {'hello': 'world', 'number': '43'},
                non_matching_lease_id)

        # Assert

    def test_set_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.set_container_metadata(
                self.container_name, {'hello': 'world', 'number': '43'})

        # Assert

    def test_get_container_metadata(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        md = self.bs.get_container_metadata(self.container_name)

        # Assert
        self.assertIsNotNone(md)
        self.assertEqual(2, len(md))
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    def test_get_container_metadata_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        md = self.bs.get_container_metadata(
            self.container_name, lease['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(md)
        self.assertEqual(2, len(md))
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    def test_get_container_metadata_with_non_matching_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        non_matching_lease_id = '00000000-1111-2222-3333-444444444444'
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_metadata(
                self.container_name, non_matching_lease_id)

        # Assert

    def test_get_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_metadata(self.container_name)

        # Assert

    def test_get_container_properties(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        props = self.bs.get_container_properties(self.container_name)

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['x-ms-meta-hello'], 'world')
        self.assertEqual(props['x-ms-meta-number'], '42')
        self.assertEqual(props['x-ms-lease-duration'], 'fixed')
        self.assertEqual(props['x-ms-lease-state'], 'leased')
        self.assertEqual(props['x-ms-lease-status'], 'locked')

    def test_get_container_properties_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        props = self.bs.get_container_properties(
            self.container_name, lease['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['x-ms-meta-hello'], 'world')
        self.assertEqual(props['x-ms-meta-number'], '42')
        self.assertEqual(props['x-ms-lease-duration'], 'fixed')
        self.assertEqual(props['x-ms-lease-status'], 'locked')
        self.assertEqual(props['x-ms-lease-state'], 'leased')

    def test_get_container_properties_with_non_matching_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        self.bs.set_container_acl(self.container_name, None, 'container')
        self.bs.set_container_metadata(
            self.container_name, {'hello': 'world', 'number': '42'})
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        non_matching_lease_id = '00000000-1111-2222-3333-444444444444'
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_properties(
                self.container_name, non_matching_lease_id)

        # Assert

    def test_get_container_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_properties(self.container_name)

        # Assert

    def test_get_container_acl(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        acl = self.bs.get_container_acl(self.container_name)

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_container_acl_iter(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        acl = self.bs.get_container_acl(self.container_name)
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)
        self.assertEqual(len(acl), 0)

    def test_get_container_acl_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        acl = self.bs.get_container_acl(
            self.container_name, lease['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_container_acl_with_non_matching_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        non_matching_lease_id = '00000000-1111-2222-3333-444444444444'
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_acl(
                self.container_name, non_matching_lease_id)

        # Assert

    def test_get_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_container_acl(self.container_name)

        # Assert

    def test_set_container_acl(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        resp = self.bs.set_container_acl(self.container_name)

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        resp = self.bs.set_container_acl(
            self.container_name, x_ms_lease_id=lease['x-ms-lease-id'])

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_non_matching_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        non_matching_lease_id = '00000000-1111-2222-3333-444444444444'
        with self.assertRaises(WindowsAzureError):
            self.bs.set_container_acl(
                self.container_name, x_ms_lease_id=non_matching_lease_id)

        # Assert

    def test_set_container_acl_with_public_access_container(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        resp = self.bs.set_container_acl(
            self.container_name, None, 'container')

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_public_access_blob(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        resp = self.bs.set_container_acl(self.container_name, None, 'blob')

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_empty_signed_identifiers(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        identifiers = SignedIdentifiers()

        resp = self.bs.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_set_container_acl_with_signed_identifiers(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2011-10-12'
        si.access_policy.permission = ContainerSharedAccessPermissions.READ
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.bs.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bs.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 1)
        self.assertEqual(len(acl), 1)
        self.assertEqual(acl.signed_identifiers[0].id, 'testid')
        self.assertEqual(acl[0].id, 'testid')

    def test_set_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.set_container_acl(self.container_name, None, 'container')

        # Assert

    def test_lease_container_acquire_and_release(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']
        lease = self.bs.lease_container(
            self.container_name,
            'release',
            x_ms_lease_id=lease['x-ms-lease-id'])
        self.container_lease_id = None

        # Assert

    def test_lease_container_renew(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_lease_duration=15)
        self.container_lease_id = lease['x-ms-lease-id']
        time.sleep(10)

        # Act
        renewed_lease = self.bs.lease_container(
            self.container_name, 'renew', x_ms_lease_id=lease['x-ms-lease-id'])

        # Assert
        self.assertEqual(lease['x-ms-lease-id'],
                         renewed_lease['x-ms-lease-id'])
        time.sleep(5)
        with self.assertRaises(WindowsAzureError):
            self.bs.delete_container(self.container_name)
        time.sleep(10)
        self.bs.delete_container(self.container_name)

    def test_lease_container_break_period(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_lease_duration=15)
        self.container_lease_id = lease['x-ms-lease-id']

        # Assert
        self.bs.lease_container(self.container_name,
                                'break',
                                x_ms_lease_id=lease['x-ms-lease-id'],
                                x_ms_lease_break_period=5)
        time.sleep(5)
        with self.assertRaises(WindowsAzureError):
            self.bs.delete_container(
                self.container_name, x_ms_lease_id=lease['x-ms-lease-id'])

    def test_lease_container_break_released_lease_fails(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']
        self.bs.lease_container(
            self.container_name, 'release', lease['x-ms-lease-id'])

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.lease_container(
                self.container_name, 'break', lease['x-ms-lease-id'])

        # Assert

    def test_lease_container_acquire_after_break_fails(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']
        self.bs.lease_container(
            self.container_name, 'break', lease['x-ms-lease-id'])

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.lease_container(self.container_name, 'acquire')

        # Assert

    def test_lease_container_with_duration(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_lease_duration=15)
        self.container_lease_id = lease['x-ms-lease-id']

        # Assert
        with self.assertRaises(WindowsAzureError):
            self.bs.lease_container(self.container_name, 'acquire')
        time.sleep(15)
        lease = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease['x-ms-lease-id']

    def test_lease_container_with_proposed_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        lease_id = '55e97f64-73e8-4390-838d-d9e84a374321'
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_proposed_lease_id=lease_id)
        self.container_lease_id = lease['x-ms-lease-id']

        # Assert
        self.assertIsNotNone(lease)
        self.assertEqual(lease['x-ms-lease-id'], lease_id)

    def test_lease_container_change_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        lease_id = '29e0b239-ecda-4f69-bfa3-95f6af91464c'
        lease1 = self.bs.lease_container(self.container_name, 'acquire')
        self.container_lease_id = lease1['x-ms-lease-id']
        lease2 = self.bs.lease_container(self.container_name,
                                         'change',
                                         x_ms_lease_id=lease1['x-ms-lease-id'],
                                         x_ms_proposed_lease_id=lease_id)
        self.container_lease_id = lease2['x-ms-lease-id']

        # Assert
        self.assertIsNotNone(lease1)
        self.assertIsNotNone(lease2)
        self.assertNotEqual(lease1['x-ms-lease-id'], lease_id)
        self.assertEqual(lease2['x-ms-lease-id'], lease_id)

    def test_delete_container_with_existing_container(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        deleted = self.bs.delete_container(self.container_name)

        # Assert
        self.assertTrue(deleted)
        containers = self.bs.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_existing_container_fail_not_exist(self):
        # Arrange
        self.bs.create_container(self.container_name)

        # Act
        deleted = self.bs.delete_container(self.container_name, True)

        # Assert
        self.assertTrue(deleted)
        containers = self.bs.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_non_existing_container(self):
        # Arrange

        # Act
        deleted = self.bs.delete_container(self.container_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_container_with_non_existing_container_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.delete_container(self.container_name, True)

        # Assert

    def test_delete_container_with_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_lease_duration=15)
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        deleted = self.bs.delete_container(
            self.container_name, x_ms_lease_id=lease['x-ms-lease-id'])

        # Assert
        self.assertTrue(deleted)
        containers = self.bs.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_without_lease_id(self):
        # Arrange
        self.bs.create_container(self.container_name)
        lease = self.bs.lease_container(
            self.container_name, 'acquire', x_ms_lease_duration=15)
        self.container_lease_id = lease['x-ms-lease-id']

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.delete_container(self.container_name)

        # Assert

    #--Test cases for blob service ---------------------------------------
    def test_set_blob_service_properties(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.hour_metrics.enabled = False
        resp = self.bs.set_blob_service_properties(props)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bs.get_blob_service_properties()
        self.assertFalse(received_props.hour_metrics.enabled)

    def test_set_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.logging.write = True
        resp = self.bs.set_blob_service_properties(props, 5)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bs.get_blob_service_properties()
        self.assertTrue(received_props.logging.write)

    def test_get_blob_service_properties(self):
        # Arrange

        # Act
        props = self.bs.get_blob_service_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.minute_metrics, MinuteMetrics)
        self.assertIsInstance(props.hour_metrics, HourMetrics)

    def test_get_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = self.bs.get_blob_service_properties(5)

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.minute_metrics, MinuteMetrics)
        self.assertIsInstance(props.hour_metrics, HourMetrics)

    #--Test cases for blobs ----------------------------------------------
    def test_make_blob_url(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd')

        # Assert
        self.assertEqual(res, 'https://' + credentials.getStorageServicesName()
                         + '.blob.core.windows.net/vhds/my.vhd')

    def test_make_blob_url_with_account_name(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd', account_name='myaccount')

        # Assert
        self.assertEqual(
            res, 'https://myaccount.blob.core.windows.net/vhds/my.vhd')

    def test_make_blob_url_with_protocol(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url('vhds', 'my.vhd', protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + credentials.getStorageServicesName()
                         + '.blob.core.windows.net/vhds/my.vhd')

    def test_make_blob_url_with_host_base(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url(
            'vhds', 'my.vhd', host_base='.blob.internal.net')

        # Assert
        self.assertEqual(res, 'https://' + credentials.getStorageServicesName()
                         + '.blob.internal.net/vhds/my.vhd')

    def test_make_blob_url_with_all(self):
        # Arrange

        # Act
        res = self.bs.make_blob_url(
            'vhds', 'my.vhd', account_name='myaccount', protocol='http',
            host_base='.blob.internal.net')

        # Assert
        self.assertEqual(res, 'http://myaccount.blob.internal.net/vhds/my.vhd')

    def test_list_blobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'blob2', data, 'BlockBlob')

        # Act
        resp = self.bs.list_blobs(self.container_name)
        for blob in resp:
            name = blob.name

        # Assert
        self.assertIsNotNone(resp)
        self.assertGreaterEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'blob1')
        self.assertNamedItemInContainer(resp, 'blob2')
        self.assertEqual(resp[0].properties.content_length, 11)
        self.assertEqual(resp[1].properties.content_type,
                         'application/octet-stream Charset=UTF-8')

    def test_list_blobs_leased_blob(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        resp = self.bs.list_blobs(self.container_name)
        for blob in resp:
            name = blob.name

        # Assert
        self.assertIsNotNone(resp)
        self.assertGreaterEqual(len(resp), 1)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'blob1')
        self.assertEqual(resp[0].properties.content_length, 11)
        self.assertEqual(resp[0].properties.lease_duration, 'fixed')
        self.assertEqual(resp[0].properties.lease_status, 'locked')
        self.assertEqual(resp[0].properties.lease_state, 'leased')

    def test_list_blobs_with_prefix(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        resp = self.bs.list_blobs(self.container_name, 'bloba')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertEqual(len(resp.blobs), 2)
        self.assertEqual(len(resp.prefixes), 0)
        self.assertEqual(resp.prefix, 'bloba')
        self.assertNamedItemInContainer(resp, 'bloba1')
        self.assertNamedItemInContainer(resp, 'bloba2')

    def test_list_blobs_with_prefix_and_delimiter(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name,
                         'documents/music/pop/thriller.mp3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/music/rock/stairwaytoheaven.mp3', data,
                         'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/music/rock/hurt.mp3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/music/rock/metallica/one.mp3', data,
                         'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/music/unsorted1.mp3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/music/unsorted2.mp3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/pictures/birthday/kid.jpg', data,
                         'BlockBlob')
        self.bs.put_blob(self.container_name,
                         'documents/pictures/birthday/cake.jpg', data,
                         'BlockBlob')

        # Act
        resp = self.bs.list_blobs(
            self.container_name, 'documents/music/', delimiter='/')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertEqual(len(resp.blobs), 2)
        self.assertEqual(len(resp.prefixes), 2)
        self.assertEqual(resp.prefix, 'documents/music/')
        self.assertEqual(resp.delimiter, '/')
        self.assertNamedItemInContainer(resp, 'documents/music/unsorted1.mp3')
        self.assertNamedItemInContainer(resp, 'documents/music/unsorted2.mp3')
        self.assertNamedItemInContainer(
            resp.blobs, 'documents/music/unsorted1.mp3')
        self.assertNamedItemInContainer(
            resp.blobs, 'documents/music/unsorted2.mp3')
        self.assertNamedItemInContainer(resp.prefixes, 'documents/music/pop/')
        self.assertNamedItemInContainer(resp.prefixes, 'documents/music/rock/')

    def test_list_blobs_with_maxresults(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs = self.bs.list_blobs(self.container_name, None, None, 2)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(blobs, 'bloba1')
        self.assertNamedItemInContainer(blobs, 'bloba2')

    def test_list_blobs_with_maxresults_and_marker(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs1 = self.bs.list_blobs(self.container_name, None, None, 2)
        blobs2 = self.bs.list_blobs(
            self.container_name, None, blobs1.next_marker, 2)

        # Assert
        self.assertEqual(len(blobs1), 2)
        self.assertEqual(len(blobs2), 2)
        self.assertNamedItemInContainer(blobs1, 'bloba1')
        self.assertNamedItemInContainer(blobs1, 'bloba2')
        self.assertNamedItemInContainer(blobs2, 'bloba3')
        self.assertNamedItemInContainer(blobs2, 'blobb1')

    def test_list_blobs_with_include_snapshots(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bs.put_blob(self.container_name, 'blob2', data, 'BlockBlob')
        self.bs.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertNotEqual(blobs[0].snapshot, '')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertEqual(blobs[1].snapshot, '')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertEqual(blobs[2].snapshot, '')

    def test_list_blobs_with_include_metadata(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data, 'BlockBlob',
                         x_ms_meta_name_values={'number': '1', 'name': 'bob'})
        self.bs.put_blob(self.container_name, 'blob2', data, 'BlockBlob',
                         x_ms_meta_name_values={'number': '2', 'name': 'car'})
        self.bs.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bs.list_blobs(self.container_name, include='metadata')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[0].metadata['number'], '1')
        self.assertEqual(blobs[0].metadata['name'], 'bob')
        self.assertEqual(blobs[1].name, 'blob2')
        self.assertEqual(blobs[1].metadata['number'], '2')
        self.assertEqual(blobs[1].metadata['name'], 'car')

    def test_list_blobs_with_include_uncommittedblobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        self.bs.put_blob(self.container_name, 'blob2', data, 'BlockBlob',
                         x_ms_meta_name_values={'number': '2', 'name': 'car'})

        # Act
        blobs = self.bs.list_blobs(
            self.container_name, include='uncommittedblobs')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob2')

    def test_list_blobs_with_include_copy(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data,
                         'BlockBlob',
                         x_ms_meta_name_values={'status': 'original'})
        sourceblob = 'https://{0}.blob.core.windows.net/{1}/{2}'.format(
            credentials.getStorageServicesName(),
            self.container_name,
            'blob1')
        self.bs.copy_blob(self.container_name, 'blob1copy',
                          sourceblob, {'status': 'copy'})

        # Act
        blobs = self.bs.list_blobs(self.container_name, include='copy')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob1copy')
        self.assertEqual(blobs[1].properties.content_length, 11)
        self.assertEqual(blobs[1].properties.content_type,
                         'application/octet-stream Charset=UTF-8')
        self.assertEqual(blobs[1].properties.content_encoding, '')
        self.assertEqual(blobs[1].properties.content_language, '')
        self.assertNotEqual(blobs[1].properties.content_md5, '')
        self.assertEqual(blobs[1].properties.blob_type, 'BlockBlob')
        self.assertEqual(blobs[1].properties.lease_status, 'unlocked')
        self.assertEqual(blobs[1].properties.lease_state, 'available')
        self.assertNotEqual(blobs[1].properties.copy_id, '')
        self.assertEqual(blobs[1].properties.copy_source, sourceblob)
        self.assertEqual(blobs[1].properties.copy_status, 'success')
        self.assertEqual(blobs[1].properties.copy_progress, '11/11')
        self.assertNotEqual(blobs[1].properties.copy_completion_time, '')

    def test_list_blobs_with_include_multiple(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'hello world'
        self.bs.put_blob(self.container_name, 'blob1', data, 'BlockBlob',
                         x_ms_meta_name_values={'number': '1', 'name': 'bob'})
        self.bs.put_blob(self.container_name, 'blob2', data, 'BlockBlob',
                         x_ms_meta_name_values={'number': '2', 'name': 'car'})
        self.bs.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bs.list_blobs(
            self.container_name, include='snapshots,metadata')

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertNotEqual(blobs[0].snapshot, '')
        self.assertEqual(blobs[0].metadata['number'], '1')
        self.assertEqual(blobs[0].metadata['name'], 'bob')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertEqual(blobs[1].snapshot, '')
        self.assertEqual(blobs[1].metadata['number'], '1')
        self.assertEqual(blobs[1].metadata['name'], 'bob')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertEqual(blobs[2].snapshot, '')
        self.assertEqual(blobs[2].metadata['number'], '2')
        self.assertEqual(blobs[2].metadata['name'], 'car')

    def test_put_blob_block_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'hello world'
        resp = self.bs.put_blob(
            self.container_name, 'blob1', data, 'BlockBlob')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_block_blob_unicode_python_27(self):
        '''Test for auto-encoding of unicode text (backwards compatibility).'''
        if sys.version_info >= (3,):
            return

        # Arrange
        self._create_container(self.container_name)

        # Act
        data = u'啊齄丂狛狜'
        resp = self.bs.put_blob(
            self.container_name, 'blob1', data, 'BlockBlob')

        # Assert
        self.assertIsNone(resp)
        blob = self.bs.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, data.encode('utf-8'))

    def test_put_blob_block_blob_unicode_python_33(self):
        if sys.version_info < (3,):
            return

        # Arrange
        self._create_container(self.container_name)

        # Act
        data = u'hello world'
        with self.assertRaises(TypeError):
            resp = self.bs.put_blob(
                self.container_name, 'blob1', data, 'BlockBlob')

        # Assert

    def test_put_blob_page_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        resp = self.bs.put_blob(self.container_name, 'blob1',
                                b'', 'PageBlob',
                                x_ms_blob_content_length='1024')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_with_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        data = b'hello world again'
        resp = self.bs.put_blob(
            self.container_name, 'blob1', data, 'BlockBlob',
            x_ms_lease_id=lease_id)

        # Assert
        self.assertIsNone(resp)
        blob = self.bs.get_blob(
            self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.assertEqual(blob, b'hello world again')

    def test_put_blob_with_metadata(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'hello world'
        resp = self.bs.put_blob(
            self.container_name, 'blob1', data, 'BlockBlob',
            x_ms_meta_name_values={'hello': 'world', 'number': '42'})

        # Assert
        self.assertIsNone(resp)
        md = self.bs.get_blob_metadata(self.container_name, 'blob1')
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    def test_get_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bs.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello world')

    def test_get_blob_with_snapshot(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        snapshot = self.bs.snapshot_blob(self.container_name, 'blob1')

        # Act
        blob = self.bs.get_blob(
            self.container_name, 'blob1', snapshot['x-ms-snapshot'])

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello world')

    def test_get_blob_with_snapshot_previous(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        snapshot = self.bs.snapshot_blob(self.container_name, 'blob1')
        self.bs.put_blob(self.container_name, 'blob1',
                         b'hello world again', 'BlockBlob')

        # Act
        blob_previous = self.bs.get_blob(
            self.container_name, 'blob1', snapshot['x-ms-snapshot'])
        blob_latest = self.bs.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob_previous, BlobResult)
        self.assertIsInstance(blob_latest, BlobResult)
        self.assertEqual(blob_previous, b'hello world')
        self.assertEqual(blob_latest, b'hello world again')

    def test_get_blob_with_range(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bs.get_blob(
            self.container_name, 'blob1', x_ms_range='bytes=0-5')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello ')

    def test_get_blob_with_range_and_get_content_md5(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bs.get_blob(self.container_name, 'blob1',
                                x_ms_range='bytes=0-5',
                                x_ms_range_get_content_md5='true')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello ')
        self.assertEqual(
            blob.properties['content-md5'], '+BSJN3e8wilf/wXwDlCNpg==')

    def test_get_blob_with_lease(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        blob = self.bs.get_blob(
            self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.bs.lease_blob(self.container_name, 'blob1', 'release', lease_id)

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello world')

    def test_get_blob_on_leased_blob_without_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        # get_blob is allowed without lease id
        blob = self.bs.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello world')

    def test_get_blob_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_blob(self.container_name, 'blob1')

        # Assert

    def test_get_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_blob(self.container_name, 'blob1')

        # Assert

    def test_set_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp = self.bs.set_blob_properties(
            self.container_name,
            'blob1',
            x_ms_blob_content_language='spanish',
            x_ms_blob_content_disposition='inline',
        )

        # Assert
        self.assertIsNone(resp)
        props = self.bs.get_blob_properties(self.container_name, 'blob1')
        self.assertEqual(props['content-language'], 'spanish')
        self.assertEqual(props['content-disposition'], 'inline')

    def test_set_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.set_blob_properties(
                self.container_name, 'blob1',
                x_ms_blob_content_language='spanish')

        # Assert

    def test_set_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.set_blob_properties(
                self.container_name, 'blob1',
                x_ms_blob_content_language='spanish')

        # Assert

    def test_get_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        props = self.bs.get_blob_properties(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['x-ms-blob-type'], 'BlockBlob')
        self.assertEqual(props['content-length'], '11')
        self.assertEqual(props['x-ms-lease-status'], 'unlocked')

    def test_get_blob_properties_with_leased_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        props = self.bs.get_blob_properties(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['x-ms-blob-type'], 'BlockBlob')
        self.assertEqual(props['content-length'], '11')
        self.assertEqual(props['x-ms-lease-status'], 'locked')
        self.assertEqual(props['x-ms-lease-state'], 'leased')
        self.assertEqual(props['x-ms-lease-duration'], 'fixed')

    def test_get_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        md = self.bs.get_blob_metadata(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(md)

    def test_set_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp = self.bs.set_blob_metadata(
            self.container_name,
            'blob1',
            {'hello': 'world', 'number': '42', 'UP': 'UPval'})

        # Assert
        self.assertIsNone(resp)
        md = self.bs.get_blob_metadata(self.container_name, 'blob1')
        self.assertEqual(3, len(md))
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')
        self.assertEqual(md['x-ms-meta-up'], 'UPval')

    def test_delete_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp = self.bs.delete_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNone(resp)

    def test_delete_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.delete_blob (self.container_name, 'blob1')

        # Assert

    def test_delete_blob_snapshot(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = b'hello world'
        self.bs.put_blob(self.container_name, blob_name, data, 'BlockBlob')
        res = self.bs.snapshot_blob(self.container_name, blob_name)
        snapshot = res['x-ms-snapshot']
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 2)

        # Act
        self.bs.delete_blob(self.container_name, blob_name, snapshot=snapshot)

        # Assert
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].name, blob_name)
        self.assertEqual(blobs[0].snapshot, '')

    def test_delete_blob_snapshots(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = b'hello world'
        self.bs.put_blob(self.container_name, blob_name, data, 'BlockBlob')
        self.bs.snapshot_blob(self.container_name, blob_name)
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 2)

        # Act
        self.bs.delete_blob(self.container_name, blob_name,
                            x_ms_delete_snapshots='only')

        # Assert
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].snapshot, '')

    def test_delete_blob_with_snapshots(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = b'hello world'
        self.bs.put_blob(self.container_name, blob_name, data, 'BlockBlob')
        self.bs.snapshot_blob(self.container_name, blob_name)
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 2)

        # Act
        self.bs.delete_blob(self.container_name, blob_name,
                            x_ms_delete_snapshots='include')

        # Assert
        blobs = self.bs.list_blobs(self.container_name, include='snapshots')
        self.assertEqual(len(blobs), 0)

    def test_copy_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        sourceblob = '/{0}/{1}/{2}'.format(credentials.getStorageServicesName(),
                                           self.container_name,
                                           'blob1')
        resp = self.bs.copy_blob(self.container_name, 'blob1copy', sourceblob)

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp['x-ms-copy-status'], 'success')
        self.assertIsNotNone(resp['x-ms-copy-id'])
        copy = self.bs.get_blob(self.container_name, 'blob1copy')
        self.assertEqual(copy, b'hello world')

    def test_copy_blob_async_public_blob(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'12345678' * 1024 * 1024
        source_blob_name = 'sourceblob'
        source_blob_url = self._create_remote_container_and_block_blob(
            source_blob_name, data, 'container')

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)

        # Assert
        self.assertEqual(copy_resp['x-ms-copy-status'], 'pending')
        self._wait_for_async_copy(self.container_name, target_blob_name)
        self.assertBlobEqual(self.container_name, target_blob_name, data)

    def test_copy_blob_async_private_blob(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'12345678' * 1024 * 1024
        source_blob_name = 'sourceblob'
        source_blob_url = self._create_remote_container_and_block_blob(
            source_blob_name, data, None)

        # Act
        target_blob_name = 'targetblob'
        with self.assertRaises(WindowsAzureMissingResourceError):
            self.bs.copy_blob(self.container_name,
                              target_blob_name, source_blob_url)

        # Assert

    def test_copy_blob_async_private_blob_with_sas(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'12345678' * 1024 * 1024
        source_blob_name = 'sourceblob'
        self._create_remote_container_and_block_blob(
            source_blob_name, data, None)
        sas_token = self.bs2.generate_shared_access_signature(
            self.remote_container_name,
            source_blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.READ),
        )
        source_blob_url = self.bs2.make_blob_url(
            self.remote_container_name,
            source_blob_name,
            sas_token=sas_token,
        )

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)

        # Assert
        self.assertEqual(copy_resp['x-ms-copy-status'], 'pending')
        self._wait_for_async_copy(self.container_name, target_blob_name)
        self.assertBlobEqual(self.container_name, target_blob_name, data)

    def test_abort_copy_blob(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'12345678' * 1024 * 1024
        source_blob_name = 'sourceblob'
        source_blob_url = self._create_remote_container_and_block_blob(
            source_blob_name, data, 'container')

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)
        self.assertEqual(copy_resp['x-ms-copy-status'], 'pending')
        self.bs.abort_copy_blob(
            self.container_name, 'targetblob', copy_resp['x-ms-copy-id'])

        # Assert
        target_blob = self.bs.get_blob(self.container_name, target_blob_name)
        self.assertEqual(target_blob, b'')
        self.assertEqual(target_blob.properties['x-ms-copy-status'], 'aborted')

    def test_abort_copy_blob_with_synchronous_copy_fails(self):
        # Arrange
        source_blob_name = 'sourceblob'
        self._create_container_and_block_blob(
            self.container_name, source_blob_name, b'hello world')
        source_blob_url = self.bs.make_blob_url(
            self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        copy_resp = self.bs.copy_blob(
            self.container_name, target_blob_name, source_blob_url)
        with self.assertRaises(WindowsAzureError):
            self.bs.abort_copy_blob(
                self.container_name,
                target_blob_name,
                copy_resp['x-ms-copy-id'])

        # Assert
        self.assertEqual(copy_resp['x-ms-copy-status'], 'success')

    def test_snapshot_blob(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp = self.bs.snapshot_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['x-ms-snapshot'])

    def test_lease_blob_acquire_and_release(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bs.lease_blob(
            self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])
        resp3 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)
        self.assertIsNotNone(resp3)

    def test_lease_blob_with_duration(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp1 = self.bs.lease_blob(
            self.container_name, 'blob1', 'acquire', x_ms_lease_duration=15)
        resp2 = self.bs.put_blob(self.container_name, 'blob1', b'hello 2',
                                 'BlockBlob',
                                 x_ms_lease_id=resp1['x-ms-lease-id'])
        time.sleep(15)
        with self.assertRaises(WindowsAzureError):
            self.bs.put_blob(self.container_name, 'blob1', b'hello 3',
                             'BlockBlob', x_ms_lease_id=resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNone(resp2)

    def test_lease_blob_with_proposed_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        resp1 = self.bs.lease_blob(
            self.container_name, 'blob1', 'acquire',
            x_ms_proposed_lease_id=lease_id)

        # Assert
        self.assertIsNotNone(resp1)
        self.assertEqual(resp1['x-ms-lease-id'], lease_id)

    def test_lease_blob_change_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bs.lease_blob(self.container_name, 'blob1', 'change',
                                   x_ms_lease_id=resp1['x-ms-lease-id'],
                                   x_ms_proposed_lease_id=lease_id)

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)
        self.assertNotEqual(resp1['x-ms-lease-id'], lease_id)
        self.assertEqual(resp2['x-ms-lease-id'], lease_id)

    def test_lease_blob_renew_released_lease_fails(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bs.lease_blob(
            self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])
        with self.assertRaises(WindowsAzureConflictError):
            self.bs.lease_blob(self.container_name, 'blob1',
                               'renew', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_lease_blob_break_period(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire',
                                   x_ms_lease_duration=15)
        resp2 = self.bs.lease_blob(self.container_name, 'blob1',
                                   'break', resp1['x-ms-lease-id'],
                                   x_ms_lease_break_period=5)
        resp3 = self.bs.put_blob(self.container_name, 'blob1', b'hello 2',
                                 'BlockBlob',
                                 x_ms_lease_id=resp1['x-ms-lease-id'])
        time.sleep(5)
        with self.assertRaises(WindowsAzureError):
            self.bs.put_blob(self.container_name, 'blob1', b'hello 3',
                             'BlockBlob', x_ms_lease_id=resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)
        self.assertIsNone(resp3)

    def test_lease_blob_break_released_lease_fails(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        self.bs.lease_blob(self.container_name, 'blob1',
                           'release', lease['x-ms-lease-id'])

        # Act
        with self.assertRaises(WindowsAzureConflictError):
            self.bs.lease_blob(self.container_name, 'blob1',
                               'break', lease['x-ms-lease-id'])

        # Assert

    def test_lease_blob_acquire_after_break_fails(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        lease = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        self.bs.lease_blob(self.container_name, 'blob1',
                           'break', lease['x-ms-lease-id'])

        # Act
        with self.assertRaises(WindowsAzureConflictError):
            self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Assert

    def test_lease_blob_acquire_and_renew(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bs.lease_blob(
            self.container_name, 'blob1', 'renew', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_lease_blob_acquire_twice_fails(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        resp1 = self.bs.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bs.lease_blob(
            self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_put_block(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')

        # Act
        for i in range(5):
            resp = self.bs.put_block(self.container_name,
                                     'blob1',
                                     u'block {0}'.format(i).encode('utf-8'),
                                     str(i))
            self.assertIsNone(resp)

        # Assert

    def test_put_block_unicode_python_27(self):
        '''Test for auto-encoding of unicode text (backwards compatibility).'''
        if sys.version_info >= (3,):
            return

        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')

        # Act
        resp = self.bs.put_block(self.container_name, 'blob1', u'啊齄', '1')
        self.assertIsNone(resp)
        resp = self.bs.put_block(self.container_name, 'blob1', u'丂狛狜', '2')
        self.assertIsNone(resp)
        resp = self.bs.put_block_list(self.container_name, 'blob1', ['1', '2'])
        self.assertIsNone(resp)

        # Assert
        blob = self.bs.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, u'啊齄丂狛狜'.encode('utf-8'))

    def test_put_block_unicode_python_33(self):
        if sys.version_info < (3,):
            return

        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')

        # Act
        with self.assertRaises(TypeError):
            resp = self.bs.put_block(self.container_name, 'blob1', u'啊齄', '1')

        # Assert

    def test_put_block_list(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')

        # Act
        resp = self.bs.put_block_list(
            self.container_name, 'blob1', ['1', '2', '3'])

        # Assert
        self.assertIsNone(resp)
        blob = self.bs.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, b'AAABBBCCC')

    def test_put_block_list_invalid_block_id(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')

        # Act
        try:
            resp = self.bs.put_block_list(
                self.container_name, 'blob1', ['1', '2', '4'])
            self.assertTrue(False)
        except WindowsAzureError as e:
            self.assertGreaterEqual(
                str(e).find('specified block list is invalid'), 0)

        # Assert

    def test_get_block_list_no_blocks(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')

        # Act
        block_list = self.bs.get_block_list(
            self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEqual(len(block_list.uncommitted_blocks), 0)
        self.assertEqual(len(block_list.committed_blocks), 0)

    def test_get_block_list_uncommitted_blocks(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')

        # Act
        block_list = self.bs.get_block_list(
            self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEqual(len(block_list.uncommitted_blocks), 3)
        self.assertEqual(len(block_list.committed_blocks), 0)
        self.assertEqual(block_list.uncommitted_blocks[0].id, '1')
        self.assertEqual(block_list.uncommitted_blocks[0].size, 3)
        self.assertEqual(block_list.uncommitted_blocks[1].id, '2')
        self.assertEqual(block_list.uncommitted_blocks[1].size, 3)
        self.assertEqual(block_list.uncommitted_blocks[2].id, '3')
        self.assertEqual(block_list.uncommitted_blocks[2].size, 3)

    def test_get_block_list_committed_blocks(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        self.bs.put_block_list(self.container_name, 'blob1', ['1', '2', '3'])

        # Act
        block_list = self.bs.get_block_list(
            self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEqual(len(block_list.uncommitted_blocks), 0)
        self.assertEqual(len(block_list.committed_blocks), 3)
        self.assertEqual(block_list.committed_blocks[0].id, '1')
        self.assertEqual(block_list.committed_blocks[0].size, 3)
        self.assertEqual(block_list.committed_blocks[1].id, '2')
        self.assertEqual(block_list.committed_blocks[1].size, 3)
        self.assertEqual(block_list.committed_blocks[2].id, '3')
        self.assertEqual(block_list.committed_blocks[2].size, 3)

    def test_put_page_update(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)

        # Act
        data = b'abcdefghijklmnop' * 32
        resp = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=0-511', 'update')

        # Assert
        self.assertIsNone(resp)

    def test_put_page_clear(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)

        # Act
        resp = self.bs.put_page(
            self.container_name, 'blob1', b'', 'bytes=0-511', 'clear')

        # Assert
        self.assertIsNone(resp)

    def test_put_page_if_sequence_number_lt_success(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                         'update',
                         x_ms_if_sequence_number_lt=start_sequence + 1)

        # Assert
        self.assertBlobEqual(self.container_name, 'blob1', data)

    def test_put_page_if_sequence_number_lt_failure(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                             'update',
                             x_ms_if_sequence_number_lt=start_sequence)

        # Assert

    def test_put_page_if_sequence_number_lte_success(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                         'update', x_ms_if_sequence_number_lte=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, 'blob1', data)

    def test_put_page_if_sequence_number_lte_failure(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                             'update',
                             x_ms_if_sequence_number_lte=start_sequence - 1)

        # Assert

    def test_put_page_if_sequence_number_eq_success(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                         'update', x_ms_if_sequence_number_eq=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, 'blob1', data)

    def test_put_page_if_sequence_number_eq_failure(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'ab' * 256
        start_sequence = 10
        self.bs.put_blob(self.container_name, 'blob1', None, 'PageBlob',
                         x_ms_blob_content_length=512,
                         x_ms_blob_sequence_number=start_sequence)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bs.put_page(self.container_name, 'blob1', data, 'bytes=0-511',
                             'update',
                             x_ms_if_sequence_number_eq=start_sequence - 1)

        # Assert

    def test_put_page_unicode_python_27(self):
        '''Test for auto-encoding of unicode text (backwards compatibility).'''
        if sys.version_info >= (3,):
            return

        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 512)

        # Act
        data = u'abcdefghijklmnop' * 32
        resp = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=0-511', 'update')

        # Assert
        self.assertIsNone(resp)
        blob = self.bs.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, data.encode('utf-8'))

    def test_put_page_unicode_python_33(self):
        '''Test for auto-encoding of unicode text (backwards compatibility).'''
        if sys.version_info < (3,):
            return

        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 512)

        # Act
        data = u'abcdefghijklmnop' * 32
        with self.assertRaises(TypeError):
            self.bs.put_page(self.container_name, 'blob1',
                             data, 'bytes=0-511', 'update')

        # Assert

    def test_get_page_ranges_no_pages(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)

        # Act
        ranges = self.bs.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEqual(len(ranges.page_ranges), 0)

    def test_get_page_ranges_2_pages(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bs.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEqual(len(ranges.page_ranges), 2)
        self.assertEqual(ranges.page_ranges[0].start, 0)
        self.assertEqual(ranges.page_ranges[0].end, 511)
        self.assertEqual(ranges.page_ranges[1].start, 1024)
        self.assertEqual(ranges.page_ranges[1].end, 1535)

    def test_get_page_ranges_iter(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bs.put_page(
            self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bs.get_page_ranges(self.container_name, 'blob1')
        for range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    def test_with_filter(self):
        # Single filter
        if sys.version_info < (3,):
            strtype = (str, unicode)
            strornonetype = (str, unicode, type(None))
        else:
            strtype = str
            strornonetype = (str, type(None))

        called = []

        def my_filter(request, next):
            called.append(True)
            self.assertIsInstance(request, HTTPRequest)
            for header in request.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, strornonetype)
            self.assertIsInstance(request.host, strtype)
            self.assertIsInstance(request.method, strtype)
            self.assertIsInstance(request.path, strtype)
            self.assertIsInstance(request.query, list)
            self.assertIsInstance(request.body, strtype)
            response = next(request)

            self.assertIsInstance(response, HTTPResponse)
            self.assertIsInstance(response.body, (bytes, type(None)))
            self.assertIsInstance(response.headers, list)
            for header in response.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, strtype)
            self.assertIsInstance(response.status, int)
            return response

        bc = self.bs.with_filter(my_filter)
        bc.create_container(self.container_name + '0', None, None, False)

        self.assertTrue(called)

        del called[:]

        bc.delete_container(self.container_name + '0')

        self.assertTrue(called)
        del called[:]

        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)

        def filter_b(request, next):
            called.append('b')
            return next(request)

        bc = self.bs.with_filter(filter_a).with_filter(filter_b)
        bc.create_container(self.container_name + '1', None, None, False)

        self.assertEqual(called, ['b', 'a'])

        bc.delete_container(self.container_name + '1')

        self.assertEqual(called, ['b', 'a', 'b', 'a'])

    def test_unicode_create_container_unicode_name(self):
        # Arrange
        self.container_name = self.container_name + u'啊齄丂狛狜'

        # Act
        with self.assertRaises(WindowsAzureError):
            # not supported - container name must be alphanumeric, lowercase
            self.bs.create_container(self.container_name)

        # Assert

    def test_unicode_get_blob_unicode_name(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, '啊齄丂狛狜', b'hello world')

        # Act
        blob = self.bs.get_blob(self.container_name, '啊齄丂狛狜')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, b'hello world')

    def test_put_blob_block_blob_unicode_data(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        resp = self.bs.put_blob(
            self.container_name, 'blob1', data, 'BlockBlob')

        # Assert
        self.assertIsNone(resp)

    def test_unicode_get_blob_unicode_data(self):
        # Arrange
        blob_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        self._create_container_and_block_blob(
            self.container_name, 'blob1', blob_data)

        # Act
        blob = self.bs.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, blob_data)

    def test_unicode_get_blob_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        self._create_container_and_block_blob(
            self.container_name, 'blob1', binary_data)

        # Act
        blob = self.bs.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEqual(blob, binary_data)

    def test_no_sas_private_blob(self):
        # Arrange
        data = b'a private blob cannot be read without a shared access signature'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )

        # Act
        url = self.bs.make_blob_url(self.container_name, blob_name)
        response = requests.get(url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))

    def test_no_sas_public_blob(self):
        # Arrange
        data = b'a public blob can be read without a shared access signature'
        blob_name = 'blob1.txt'
        self.bs.create_container(self.container_name, None, 'blob')
        self.bs.put_blob(self.container_name, blob_name, data, 'BlockBlob')

        # Act
        url = self.bs.make_blob_url(self.container_name, blob_name)
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    def test_public_access_blob(self):
        # Arrange
        data = b'public access blob'
        blob_name = 'blob1.txt'
        self.bs.create_container(self.container_name, None, 'blob')
        self.bs.put_blob(self.container_name, blob_name, data, 'BlockBlob')

        # Act
        service = BlobService(credentials.getStorageServicesName())
        set_service_options(service)
        result = service.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(data, result)

    def test_sas_access_blob(self):
        # Arrange
        data = b'shared access signature with read permission on blob'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.READ),
        )

        # Act
        service = BlobService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(data, result)

    def test_sas_signed_identifier(self):
        # Arrange
        data = b'shared access signature with signed identifier'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )

        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2018-10-12'
        si.access_policy.permission = BlobSharedAccessPermissions.READ
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.bs.set_container_acl(self.container_name, identifiers)

        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            SharedAccessPolicy(signed_identifier=si.id),
        )

        # Act
        service = BlobService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(data, result)

    def test_shared_read_access_blob(self):
        # Arrange
        data = b'shared access signature with read permission on blob'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.READ),
        )

        # Act
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    def test_shared_read_access_blob_with_content_query_params(self):
        # Arrange
        data = b'shared access signature with read permission on blob'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.READ),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        response = requests.get(url)

        # Assert
        self.assertEqual(data, response.content)
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        self.assertEqual(response.headers['content-disposition'], 'inline')
        self.assertEqual(response.headers['content-encoding'], 'utf-8')
        self.assertEqual(response.headers['content-language'], 'fr')
        self.assertEqual(response.headers['content-type'], 'text')

    def test_shared_write_access_blob(self):
        # Arrange
        data = b'shared access signature with write permission on blob'
        updated_data = b'updated blob data'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.WRITE),
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        headers = {'x-ms-blob-type': 'BlockBlob'}
        response = requests.put(url, headers=headers, data=updated_data)

        # Assert
        self.assertTrue(response.ok)
        blob = self.bs.get_blob(self.container_name, 'blob1.txt')
        self.assertEqual(updated_data, blob)

    def test_shared_delete_access_blob(self):
        # Arrange
        data = b'shared access signature with delete permission on blob'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            blob_name,
            self._get_shared_access_policy(BlobSharedAccessPermissions.DELETE),
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        response = requests.delete(url)

        # Assert
        self.assertTrue(response.ok)
        with self.assertRaises(WindowsAzureMissingResourceError):
            blob = self.bs.get_blob(self.container_name, blob_name)

    def test_shared_access_container(self):
        # Arrange
        data = b'shared access signature with read permission on container'
        blob_name = 'blob1.txt'
        self._create_container_and_block_blob(
            self.container_name,
            blob_name,
            data,
        )
        token = self.bs.generate_shared_access_signature(
            self.container_name,
            None,
            self._get_shared_access_policy(ContainerSharedAccessPermissions.READ),
        )
        url = self.bs.make_blob_url(
            self.container_name,
            blob_name,
            sas_token=token,
        )

        # Act
        response = requests.get(url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    def test_get_blob_to_bytes(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(data, resp)

    def test_get_blob_to_bytes_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(data, resp)

    def test_get_blob_to_bytes_chunked_download_parallel(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_bytes(self.container_name, blob_name,
                                         max_connections=10)

        # Assert
        self.assertEqual(data, resp)

    def test_get_blob_to_bytes_with_progress(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_bytes(
            self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(data, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_bytes_with_progress_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_bytes(
            self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(data, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_file(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_file_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_file_chunked_download_parallel(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_file_non_seekable_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            non_seekable_stream = BlobServiceTest.NonSeekableFile(stream)
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, non_seekable_stream,
                max_connections=1)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_file_non_seekable_chunked_download_parallel(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            non_seekable_stream = BlobServiceTest.NonSeekableFile(stream)

            # Parallel downloads require that the file be seekable
            with self.assertRaises(AttributeError):
                resp = self.bs.get_blob_to_file(
                    self.container_name, blob_name, non_seekable_stream,
                    max_connections=10)

        # Assert

    def test_get_blob_to_file_with_progress(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_file_with_progress_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_file_with_progress_chunked_download_parallel(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.bs.get_blob_to_file(
                self.container_name, blob_name, stream,
                progress_callback=callback,
                max_connections=5)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, sorted(progress))
        self.assertGreater(len(progress), 0)

    def test_get_blob_to_path(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_path_chunked_downlad(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_path_chunked_downlad_parallel(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_blob_to_path_with_progress(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_path_with_progress_chunked_downlad(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_path_with_mode(self):
        # Arrange
        blob_name = 'blob1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)
        with open(file_path, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path, 'a+b')

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + data, actual)

    def test_get_blob_to_path_with_mode_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_output.temp.dat'
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)
        with open(file_path, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        resp = self.bs.get_blob_to_path(
            self.container_name, blob_name, file_path, 'a+b')

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + data, actual)

    def test_get_blob_to_text(self):
        # Arrange
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_text(self.container_name, blob_name)

        # Assert
        self.assertEqual(text, resp)

    def test_get_blob_to_text_with_encoding(self):
        # Arrange
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_text(
            self.container_name, blob_name, 'utf-16')

        # Assert
        self.assertEqual(text, resp)

    def test_get_blob_to_text_chunked_download(self):
        # Arrange
        blob_name = 'blob1'
        text = self._get_oversized_text_data()
        data = text.encode('utf-8')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_text(self.container_name, blob_name)

        # Assert
        self.assertEqual(text, resp)

    def test_get_blob_to_text_chunked_download_parallel(self):
        # Arrange
        blob_name = 'blob1'
        text = self._get_oversized_text_data()
        data = text.encode('utf-8')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        resp = self.bs.get_blob_to_text(self.container_name, blob_name,
                                        max_connections=10)

        # Assert
        self.assertEqual(text, resp)

    def test_get_blob_to_text_with_progress(self):
        # Arrange
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_text(
            self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(text, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_blob_to_text_with_encoding_and_progress(self):
        # Arrange
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        self._create_container_and_block_blob(
            self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.get_blob_to_text(
            self.container_name, blob_name, 'utf-16',
            progress_callback=callback)

        # Assert
        self.assertEqual(text, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_block_blob_from_bytes(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, 'blob1', data)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_block_blob_from_bytes_with_progress(self):
        # Arrange
        self._create_container(self.container_name)
        data = b'abcdefghijklmnopqrstuvwxyz'

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, 'blob1', data, progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.bs.get_blob(self.container_name, 'blob1'))
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_block_blob_from_bytes_with_index(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, 'blob1', data, 3)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(b'defghijklmnopqrstuvwxyz',
                         self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_block_blob_from_bytes_with_index_and_count(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, 'blob1', data, 3, 5)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(
            b'defgh', self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_block_blob_from_bytes_with_index_and_count_and_properties(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, 'blob1', data, 3, 5,
            x_ms_blob_content_type='image/png',
            x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(
            b'defgh', self.bs.get_blob(self.container_name, 'blob1'))
        props = self.bs.get_blob_properties(self.container_name, 'blob1')
        self.assertEqual(props['content-type'], 'image/png')
        self.assertEqual(props['content-language'], 'spanish')

    def test_put_block_blob_from_bytes_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()

        # Act
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, blob_name, data)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_bytes_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()

        # Act
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, blob_name, data,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_bytes_chunked_upload_with_properties(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()

        # Act
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, blob_name, data,
            x_ms_blob_content_type='image/png',
            x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        props = self.bs.get_blob_properties(self.container_name, 'blob1')
        self.assertEqual(props['content-type'], 'image/png')
        self.assertEqual(props['content-language'], 'spanish')

    def test_put_block_blob_from_bytes_with_progress_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, blob_name, data, progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_block_blob_from_bytes_chunked_upload_with_index_and_count(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        index = 33
        blob_size = len(data) - 66

        # Act
        resp = self.bs.put_block_blob_from_bytes(
            self.container_name, blob_name, data, index, blob_size)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name,
                             data[index:index + blob_size])

    def test_put_block_blob_from_path_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.bs.put_block_blob_from_path(
            self.container_name, blob_name, file_path)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_path_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.bs.put_block_blob_from_path(
            self.container_name, blob_name, file_path,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_path_with_progress_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.put_block_blob_from_path(
            self.container_name, blob_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_block_blob_from_path_chunked_upload_with_properties(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.bs.put_block_blob_from_path(
            self.container_name, blob_name, file_path,
            x_ms_blob_content_type='image/png',
            x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        props = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(props['content-type'], 'image/png')
        self.assertEqual(props['content-language'], 'spanish')

    def test_put_block_blob_from_file_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_file_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_file_non_seekable_chunked_upload_known_size(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)
        blob_size = len(data) - 66

        # Act
        with open(file_path, 'rb') as stream:
            non_seekable_file = BlobServiceTest.NonSeekableFile(stream)
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, non_seekable_file,
                count=blob_size, max_connections=1)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_block_blob_from_file_non_seekable_chunked_upload_unknown_size(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        with open(file_path, 'rb') as stream:
            non_seekable_file = BlobServiceTest.NonSeekableFile(stream)
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, non_seekable_file,
                max_connections=1)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_file_non_seekable_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        with open(file_path, 'rb') as stream:
            non_seekable_file = BlobServiceTest.NonSeekableFile(stream)

            # Parallel uploads require that the file be seekable
            with self.assertRaises(AttributeError):
                resp = self.bs.put_block_blob_from_file(
                    self.container_name, blob_name, non_seekable_file,
                    max_connections=10)

        # Assert

    def test_put_block_blob_from_file_with_progress_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(
            progress,
            self._get_expected_progress(len(data), unknown_size=True))

    def test_put_block_blob_from_file_with_progress_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream,
                progress_callback=callback,
                max_connections=5)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(progress, sorted(progress))
        self.assertGreater(len(progress), 0)

    def test_put_block_blob_from_file_chunked_upload_with_count(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_block_blob_from_file_chunked_upload_with_count_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_block_blob_from_file_chunked_upload_with_count_and_properties(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                x_ms_blob_content_type='image/png',
                x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        props = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(props['content-type'], 'image/png')
        self.assertEqual(props['content-language'], 'spanish')

    def test_put_block_blob_from_file_chunked_upload_with_properties(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_block_blob_from_file(
                self.container_name, blob_name, stream,
                x_ms_blob_content_type='image/png',
                x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        props = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(props['content-type'], 'image/png')
        self.assertEqual(props['content-language'], 'spanish')

    def test_put_block_blob_from_text(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        resp = self.bs.put_block_blob_from_text(
            self.container_name, blob_name, text)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_text_with_encoding(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        resp = self.bs.put_block_blob_from_text(
            self.container_name, blob_name, text, 'utf-16')

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_block_blob_from_text_with_encoding_and_progress(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.put_block_blob_from_text(
            self.container_name, blob_name, text, 'utf-16',
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_block_blob_from_text_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_text_data()
        encoded_data = data.encode('utf-8')

        # Act
        resp = self.bs.put_block_blob_from_text(
            self.container_name, blob_name, data)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(
            self.container_name, blob_name, len(encoded_data))
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    def test_put_block_blob_from_text_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_text_data()
        encoded_data = data.encode('utf-8')

        # Act
        resp = self.bs.put_block_blob_from_text(
            self.container_name, blob_name, data,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(
            self.container_name, blob_name, len(encoded_data))
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    def test_put_page_blob_from_bytes(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = os.urandom(2048)
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, 'blob1', data)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_page_blob_from_bytes_with_progress(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        data = os.urandom(2048)
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, 'blob1', data, progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.bs.get_blob(self.container_name, 'blob1'))
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_page_blob_from_bytes_with_index(self):
        # Arrange
        self._create_container(self.container_name)
        index = 1024

        # Act
        data = os.urandom(2048)
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, 'blob1', data, index)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data[index:],
                         self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_page_blob_from_bytes_with_index_and_count(self):
        # Arrange
        self._create_container(self.container_name)
        index = 512
        count = 1024

        # Act
        data = os.urandom(2048)
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, 'blob1', data, index, count)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data[index:index + count],
                         self.bs.get_blob(self.container_name, 'blob1'))

    def test_put_page_blob_from_bytes_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()

        # Act
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, blob_name, data)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_page_blob_from_bytes_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()

        # Act
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, blob_name, data,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_page_blob_from_bytes_chunked_upload_with_index_and_count(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        index = 512
        count = len(data) - 1024

        # Act
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, blob_name, data, index, count)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, count)
        self.assertBlobEqual(self.container_name,
                             blob_name, data[index:index + count])

    def test_put_page_blob_from_bytes_chunked_upload_with_index_and_count_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        index = 512
        count = len(data) - 1024

        # Act
        resp = self.bs.put_page_blob_from_bytes(
            self.container_name, blob_name, data, index, count,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, count)
        self.assertBlobEqual(self.container_name,
                             blob_name, data[index:index + count])

    def test_put_page_blob_from_path_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.bs.put_page_blob_from_path(
            self.container_name, blob_name, file_path)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_page_blob_from_path_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.bs.put_page_blob_from_path(
            self.container_name, blob_name, file_path,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_put_page_blob_from_path_with_progress_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.bs.put_page_blob_from_path(
            self.container_name, blob_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, len(data))
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_page_blob_from_file_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_page_blob_from_file_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_page_blob_from_file_non_seekable_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            non_seekable_file = BlobServiceTest.NonSeekableFile(stream)
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, non_seekable_file, blob_size,
                max_connections=1)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_page_blob_from_file_non_seekable_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            non_seekable_file = BlobServiceTest.NonSeekableFile(stream)

            # Parallel uploads require that the file be seekable
            with self.assertRaises(AttributeError):
                resp = self.bs.put_page_blob_from_file(
                    self.container_name, blob_name, non_seekable_file, blob_size,
                    max_connections=10)

        # Assert

    def test_put_page_blob_from_file_with_progress_chunked_upload(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_page_blob_from_file_with_progress_chunked_upload_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                progress_callback=callback,
                max_connections=5)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assertEqual(progress, sorted(progress))
        self.assertGreater(len(progress), 0)

    def test_put_page_blob_from_file_chunked_upload_truncated(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_page_blob_from_file_chunked_upload_truncated_parallel(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_put_page_blob_from_file_with_progress_chunked_upload_truncated(self):
        # Arrange
        self._create_container(self.container_name)
        blob_name = 'blob1'
        data = self._get_oversized_page_blob_binary_data()
        file_path = 'blob_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.bs.put_page_blob_from_file(
                self.container_name, blob_name, stream, blob_size,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertBlobLengthEqual(self.container_name, blob_name, blob_size)
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assertEqual(progress, self._get_expected_progress(blob_size))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
