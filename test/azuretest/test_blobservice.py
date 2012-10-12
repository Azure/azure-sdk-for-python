#-------------------------------------------------------------------------
# Copyright 2011-2012 Microsoft Corporation
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

from azure.storage.blobservice import *
from azure.storage import Metrics
from azure.storage.storageclient import AZURE_STORAGE_ACCESS_KEY, AZURE_STORAGE_ACCOUNT, EMULATED, DEV_ACCOUNT_NAME, DEV_ACCOUNT_KEY
from azure import WindowsAzureError
from azuretest.util import *
from azure.http import HTTPRequest, HTTPResponse

import unittest

#------------------------------------------------------------------------------
class BlobServiceTest(AzureTestCase):

    def setUp(self):
        self.bc = BlobService(account_name=credentials.getStorageServicesName(), 
                                  account_key=credentials.getStorageServicesKey())

        proxy_host = credentials.getProxyHost()
        proxy_port = credentials.getProxyPort()
        if proxy_host:
            self.bc.set_proxy(proxy_host, proxy_port)

        __uid = getUniqueTestRunID()

        container_base_name = u'mytestcontainer%s' % (__uid)

        self.container_name = getUniqueNameBasedOnCurrentTime(container_base_name)
        self.additional_container_names = []

    def tearDown(self):
        self.cleanup()
        return super(BlobServiceTest, self).tearDown()

    def cleanup(self):
        try:
            self.bc.delete_container(self.container_name)
        except: pass

        for name in self.additional_container_names:
            try:
                self.bc.delete_container(name)
            except: pass

    #--Helpers-----------------------------------------------------------------
    def _create_container(self, container_name):
        self.bc.create_container(container_name, None, None, True)

    def _create_container_and_block_blob(self, container_name, blob_name, blob_data):
        self._create_container(container_name)
        resp = self.bc.put_blob(container_name, blob_name, blob_data, 'BlockBlob')
        self.assertIsNone(resp)

    def _create_container_and_page_blob(self, container_name, blob_name, content_length):
        self._create_container(container_name)
        resp = self.bc.put_blob(self.container_name, blob_name, '', 'PageBlob', x_ms_blob_content_length=str(content_length))
        self.assertIsNone(resp)

    #--Test cases for blob service --------------------------------------------
    def test_create_blob_service_missing_arguments(self):
        # Arrange
        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]
        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        # Assert

    def test_create_blob_service_env_variables(self):
        # Arrange
        os.environ[AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, credentials.getStorageServicesName())
        self.assertEquals(bs.account_key, credentials.getStorageServicesKey())
        self.assertEquals(bs.is_emulated, False)

    def test_create_blob_service_emulated_true(self):
        # Arrange
        os.environ[EMULATED] = 'true'

        # Act
        bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, DEV_ACCOUNT_NAME)
        self.assertEquals(bs.account_key, DEV_ACCOUNT_KEY)
        self.assertEquals(bs.is_emulated, True)

    def test_create_blob_service_emulated_false(self):
        # Arrange
        os.environ[EMULATED] = 'false'

        # Act
        with self.assertRaises(WindowsAzureError):
            bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]

        # Assert

    def test_create_blob_service_emulated_false_env_variables(self):
        # Arrange
        os.environ[EMULATED] = 'false'
        os.environ[AZURE_STORAGE_ACCOUNT] = credentials.getStorageServicesName()
        os.environ[AZURE_STORAGE_ACCESS_KEY] = credentials.getStorageServicesKey()

        # Act
        bs = BlobService()

        if os.environ.has_key(EMULATED):
            del os.environ[EMULATED]
        if os.environ.has_key(AZURE_STORAGE_ACCOUNT):
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if os.environ.has_key(AZURE_STORAGE_ACCESS_KEY):
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(bs)
        self.assertEquals(bs.account_name, credentials.getStorageServicesName())
        self.assertEquals(bs.account_key, credentials.getStorageServicesKey())
        self.assertEquals(bs.is_emulated, False)

    #--Test cases for containers -----------------------------------------
    def test_create_container_no_options(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name)

        # Assert
        self.assertTrue(created)

    def test_create_container_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_already_existing_container(self):
        # Arrange

        # Act
        created1 = self.bc.create_container(self.container_name)
        created2 = self.bc.create_container(self.container_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_container_with_already_existing_container_fail_on_exist(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name)
        with self.assertRaises(WindowsAzureError):
            self.bc.create_container(self.container_name, None, None, True)

        # Assert
        self.assertTrue(created)

    def test_create_container_with_public_access_container(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, 'container')

        # Assert
        self.assertTrue(created)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_public_access_blob(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, None, 'blob')

        # Assert
        self.assertTrue(created)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_create_container_with_metadata(self):
        # Arrange

        # Act
        created = self.bc.create_container(self.container_name, {'hello':'world', 'foo':'42'})

        # Assert
        self.assertTrue(created)
        md = self.bc.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_list_containers_no_options(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        containers = self.bc.list_containers()
        for container in containers:
            name = container.name

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)

    def test_list_containers_with_prefix(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        containers = self.bc.list_containers(self.container_name)

        # Assert
        self.assertIsNotNone(containers)
        self.assertEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertEqual(containers[0].name, self.container_name)
        self.assertIsNone(containers[0].metadata);

    def test_list_containers_with_include_metadata(self):
        # Arrange
        self.bc.create_container(self.container_name)
        resp = self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Act
        containers = self.bc.list_containers(self.container_name, None, None, 'metadata')

        # Assert
        self.assertIsNotNone(containers)
        self.assertGreaterEqual(len(containers), 1)
        self.assertIsNotNone(containers[0])
        self.assertNamedItemInContainer(containers, self.container_name)
        self.assertEqual(containers[0].metadata['hello'], 'world')
        self.assertEqual(containers[0].metadata['bar'], '43')

    def test_list_containers_with_maxresults_and_marker(self):
        # Arrange
        self.additional_container_names = [self.container_name + 'a', 
                                           self.container_name + 'b', 
                                           self.container_name + 'c', 
                                           self.container_name + 'd']
        for name in self.additional_container_names:
            self.bc.create_container(name)

        # Act
        containers1 = self.bc.list_containers(self.container_name, None, 2)
        containers2 = self.bc.list_containers(self.container_name, containers1.next_marker, 2)

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
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_container_metadata(self.container_name)
        self.assertIsNotNone(md)
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-bar'], '43')

    def test_set_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_container_metadata(self.container_name, {'hello':'world', 'bar':'43'})

        # Assert

    def test_get_container_metadata(self):
        # Arrange
        self.bc.create_container(self.container_name)
        self.bc.set_container_acl(self.container_name, None, 'container')
        self.bc.set_container_metadata(self.container_name, {'hello':'world','foo':'42'})

        # Act
        md = self.bc.get_container_metadata(self.container_name)

        # Assert
        self.assertIsNotNone(md)
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')
        # TODO:
        # get_container_properties returns container lease information whereas get_container_metadata doesn't
        # we should lease the container in the arrange section and verify that we do not receive that info

    def test_get_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_metadata(self.container_name)

        # Assert

    def test_get_container_properties(self):
        # Arrange
        self.bc.create_container(self.container_name)
        self.bc.set_container_acl(self.container_name, None, 'container')
        self.bc.set_container_metadata(self.container_name, {'hello':'world','foo':'42'})

        # Act
        props = self.bc.get_container_properties(self.container_name)

        # Assert
        self.assertIsNotNone(props)
        self.assertEquals(props['x-ms-meta-hello'], 'world')
        self.assertEquals(props['x-ms-meta-foo'], '42')
        # TODO:
        # get_container_properties returns container lease information whereas get_container_metadata doesn't
        # we should lease the container in the arrange section and verify that we receive that info

    def test_get_container_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_properties(self.container_name)

        # Assert

    def test_get_container_acl(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        acl = self.bc.get_container_acl(self.container_name)

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_container_acl_iter(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        acl = self.bc.get_container_acl(self.container_name)
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)
        self.assertEqual(len(acl), 0)

    def test_get_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_acl(self.container_name)

        # Assert

    def test_set_container_acl(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_public_access_container(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name, None, 'container')

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_public_access_blob(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        resp = self.bc.set_container_acl(self.container_name, None, 'blob')

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)

    def test_set_container_acl_with_empty_signed_identifiers(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        identifiers = SignedIdentifiers()

        resp = self.bc.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_set_container_acl_with_signed_identifiers(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2011-10-12'
        si.access_policy.permission = 'r'
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.bc.set_container_acl(self.container_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.bc.get_container_acl(self.container_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 1)
        self.assertEqual(len(acl), 1)
        self.assertEqual(acl.signed_identifiers[0].id, 'testid')
        self.assertEqual(acl[0].id, 'testid')

    def test_set_container_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_container_acl(self.container_name, None, 'container')

        # Assert

    def test_delete_container_with_existing_container(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        deleted = self.bc.delete_container(self.container_name)

        # Assert
        self.assertTrue(deleted)
        containers = self.bc.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_existing_container_fail_not_exist(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        deleted = self.bc.delete_container(self.container_name, True)

        # Assert
        self.assertTrue(deleted)
        containers = self.bc.list_containers()
        self.assertNamedItemNotInContainer(containers, self.container_name)

    def test_delete_container_with_non_existing_container(self):
        # Arrange

        # Act
        deleted = self.bc.delete_container(self.container_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_container_with_non_existing_container_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.delete_container(self.container_name, True)

        # Assert

    #--Test cases for blob service ---------------------------------------
    def test_set_blob_service_properties(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.metrics.enabled = False
        resp = self.bc.set_blob_service_properties(props)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bc.get_blob_service_properties()
        self.assertFalse(received_props.metrics.enabled)

    def test_set_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = StorageServiceProperties()
        props.logging.write = True
        resp = self.bc.set_blob_service_properties(props, 5)

        # Assert
        self.assertIsNone(resp)
        received_props = self.bc.get_blob_service_properties()
        self.assertTrue(received_props.logging.write)

    def test_get_blob_service_properties(self):
        # Arrange

        # Act
        props = self.bc.get_blob_service_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.metrics, Metrics)

    def test_get_blob_service_properties_with_timeout(self):
        # Arrange

        # Act
        props = self.bc.get_blob_service_properties(5)

        # Assert
        self.assertIsNotNone(props)
        self.assertIsInstance(props.logging, Logging)
        self.assertIsInstance(props.metrics, Metrics)

    #--Test cases for blobs ----------------------------------------------
    def test_list_blobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob')

        # Act
        blobs = self.bc.list_blobs(self.container_name)
        for blob in blobs:
            name = blob.name

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 2)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, 'blob1')
        self.assertNamedItemInContainer(blobs, 'blob2')
        self.assertEqual(blobs[0].properties.content_length, 11)
        self.assertEqual(blobs[1].properties.content_type, 'application/octet-stream Charset=UTF-8')

    def test_list_blobs_with_prefix(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs = self.bc.list_blobs(self.container_name, 'bloba')

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(blobs, 'bloba1')
        self.assertNamedItemInContainer(blobs, 'bloba2')

    def test_list_blobs_with_maxresults(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs = self.bc.list_blobs(self.container_name, None, None, 2)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertEqual(len(blobs), 2)
        self.assertNamedItemInContainer(blobs, 'bloba1')
        self.assertNamedItemInContainer(blobs, 'bloba2')

    def test_list_blobs_with_maxresults_and_marker(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'bloba1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba2', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'bloba3', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blobb1', data, 'BlockBlob')

        # Act
        blobs1 = self.bc.list_blobs(self.container_name, None, None, 2)
        blobs2 = self.bc.list_blobs(self.container_name, None, blobs1.next_marker, 2)

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
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob')
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='snapshots')

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
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'foo':'1','bar':'bob'})
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='metadata')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[0].metadata['foo'], '1')
        self.assertEqual(blobs[0].metadata['bar'], 'bob')
        self.assertEqual(blobs[1].name, 'blob2')
        self.assertEqual(blobs[1].metadata['foo'], '2')
        self.assertEqual(blobs[1].metadata['bar'], 'car')

    def test_list_blobs_with_include_uncommittedblobs(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='uncommittedblobs')

        # Assert
        self.assertEqual(len(blobs), 2)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertEqual(blobs[1].name, 'blob2')

    #def test_list_blobs_with_include_copy(self):
    #    # Arrange
    #    self._create_container(self.container_name)
    #    data = 'hello world'
    #    self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'status':'original'})
    #    sourceblob = '/%s/%s/%s' % (credentials.getStorageServicesName(),
    #                                self.container_name,
    #                                'blob1')
    #    self.bc.copy_blob(self.container_name, 'blob1copy', sourceblob, {'status':'copy'})

    #    # Act
    #    blobs = self.bc.list_blobs(self.container_name, include='copy')

    #    # Assert
    #    self.assertEqual(len(blobs), 2)
    #    self.assertEqual(blobs[0].name, 'blob1')
    #    self.assertEqual(blobs[1].name, 'blob2')
    #    #TODO: check for metadata related to copy blob

    def test_list_blobs_with_include_multiple(self):
        # Arrange
        self._create_container(self.container_name)
        data = 'hello world'
        self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'foo':'1','bar':'bob'})
        self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob', x_ms_meta_name_values={'foo':'2','bar':'car'})
        self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blobs = self.bc.list_blobs(self.container_name, include='snapshots,metadata')

        # Assert
        self.assertEqual(len(blobs), 3)
        self.assertEqual(blobs[0].name, 'blob1')
        self.assertNotEqual(blobs[0].snapshot, '')
        self.assertEqual(blobs[0].metadata['foo'], '1')
        self.assertEqual(blobs[0].metadata['bar'], 'bob')
        self.assertEqual(blobs[1].name, 'blob1')
        self.assertEqual(blobs[1].snapshot, '')
        self.assertEqual(blobs[1].metadata['foo'], '1')
        self.assertEqual(blobs[1].metadata['bar'], 'bob')
        self.assertEqual(blobs[2].name, 'blob2')
        self.assertEqual(blobs[2].snapshot, '')
        self.assertEqual(blobs[2].metadata['foo'], '2')
        self.assertEqual(blobs[2].metadata['bar'], 'car')

    def test_put_blob_block_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = 'hello world'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_page_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        resp = self.bc.put_blob(self.container_name, 'blob1', '', 'PageBlob', x_ms_blob_content_length='1024')

        # Assert
        self.assertIsNone(resp)

    def test_put_blob_with_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        lease = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        data = 'hello world again'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_lease_id=lease_id)

        # Assert
        self.assertIsNone(resp)
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.assertEqual(blob, 'hello world again')

    def test_put_blob_with_metadata(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        data = 'hello world'
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob', x_ms_meta_name_values={'hello':'world','foo':'42'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_get_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_snapshot(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        snapshot = self.bc.snapshot_blob(self.container_name, 'blob1')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', snapshot['x-ms-snapshot'])

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_snapshot_previous(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        snapshot = self.bc.snapshot_blob(self.container_name, 'blob1')
        self.bc.put_blob(self.container_name, 'blob1', 'hello world again', 'BlockBlob')

        # Act
        blob_previous = self.bc.get_blob(self.container_name, 'blob1', snapshot['x-ms-snapshot'])
        blob_latest = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsInstance(blob_previous, BlobResult)
        self.assertIsInstance(blob_latest, BlobResult)
        self.assertEquals(blob_previous, 'hello world')
        self.assertEquals(blob_latest, 'hello world again')

    def test_get_blob_with_range(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_range='bytes=0-5')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello ')

    def test_get_blob_with_range_and_get_content_md5(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_range='bytes=0-5', x_ms_range_get_content_md5='true')

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello ')
        self.assertEquals(blob.properties['content-md5'], '+BSJN3e8wilf/wXwDlCNpg==')

    def test_get_blob_with_lease(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        lease = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        lease_id = lease['x-ms-lease-id']

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1', x_ms_lease_id=lease_id)
        self.bc.lease_blob(self.container_name, 'blob1', 'release', lease_id)

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_on_leased_blob_without_lease_id(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        self.bc.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1') # get_blob is allowed without lease id

        # Assert
        self.assertIsInstance(blob, BlobResult)
        self.assertEquals(blob, 'hello world')

    def test_get_blob_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob(self.container_name, 'blob1')

        # Assert

    def test_get_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob(self.container_name, 'blob1')

        # Assert

    def test_set_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert
        self.assertIsNone(resp)
        props = self.bc.get_blob_properties(self.container_name, 'blob1')
        self.assertEquals(props['content-language'], 'spanish')

    def test_set_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert

    def test_set_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.set_blob_properties(self.container_name, 'blob1', x_ms_blob_content_language='spanish')

        # Assert

    def test_get_blob_properties_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        props = self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(props)
        self.assertEquals(props['x-ms-blob-type'], 'BlockBlob')
        self.assertEquals(props['x-ms-lease-status'], 'unlocked')
        self.assertEquals(props['content-length'], '11')

    def test_get_blob_properties_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_properties_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_blob_properties(self.container_name, 'blob1')

        # Assert

    def test_get_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(md)

    def test_set_blob_metadata_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.set_blob_metadata(self.container_name, 'blob1', {'hello':'world', 'foo':'42'})

        # Assert
        self.assertIsNone(resp)
        md = self.bc.get_blob_metadata(self.container_name, 'blob1')
        self.assertEquals(md['x-ms-meta-hello'], 'world')
        self.assertEquals(md['x-ms-meta-foo'], '42')

    def test_delete_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.delete_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNone(resp)

    def test_delete_blob_with_non_existing_blob(self):
        # Arrange
        self._create_container(self.container_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.delete_blob(self.container_name, 'blob1')

        # Assert

    def test_copy_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        sourceblob = '/%s/%s/%s' % (credentials.getStorageServicesName(),
                                    self.container_name,
                                    'blob1')
        resp = self.bc.copy_blob(self.container_name, 'blob1copy', sourceblob)

        # Assert
        self.assertIsNone(resp)
        copy = self.bc.get_blob(self.container_name, 'blob1copy')
        self.assertEquals(copy, 'hello world')

    def test_snapshot_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp = self.bc.snapshot_blob(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['x-ms-snapshot'])

    def test_lease_blob_acquire_and_release(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        resp1 = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bc.lease_blob(self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_lease_blob_acquire_twice_fails(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')
        resp1 = self.bc.lease_blob(self.container_name, 'blob1', 'acquire')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.lease_blob(self.container_name, 'blob1', 'acquire')
        resp2 = self.bc.lease_blob(self.container_name, 'blob1', 'release', resp1['x-ms-lease-id'])

        # Assert
        self.assertIsNotNone(resp1)
        self.assertIsNotNone(resp2)

    def test_put_block(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')

        # Act
        for i in xrange(5):
            resp = self.bc.put_block(self.container_name, 
                                     'blob1',
                                     'block %d' % (i),
                                     str(i))
            self.assertIsNone(resp)

        # Assert

    def test_put_block_list(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')

        # Act
        resp = self.bc.put_block_list(self.container_name, 'blob1', ['1', '2', '3'])

        # Assert
        self.assertIsNone(resp)
        blob = self.bc.get_blob(self.container_name, 'blob1')
        self.assertEqual(blob, 'AAABBBCCC')

    def test_get_block_list_no_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 0)
        self.assertEquals(len(block_list.committed_blocks), 0)

    def test_get_block_list_uncommitted_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 3)
        self.assertEquals(len(block_list.committed_blocks), 0)

    def test_get_block_list_committed_blocks(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', '')
        self.bc.put_block(self.container_name, 'blob1', 'AAA', '1')
        self.bc.put_block(self.container_name, 'blob1', 'BBB', '2')
        self.bc.put_block(self.container_name, 'blob1', 'CCC', '3')
        self.bc.put_block_list(self.container_name, 'blob1', ['1', '2', '3'])

        # Act
        block_list = self.bc.get_block_list(self.container_name, 'blob1', None, 'all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertIsInstance(block_list, BlobBlockList)
        self.assertEquals(len(block_list.uncommitted_blocks), 0)
        self.assertEquals(len(block_list.committed_blocks), 3)

    def test_put_page_update(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        data = 'abcdefghijklmnop' * 32
        resp = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')

        # Assert
        self.assertIsNone(resp)

    def test_put_page_clear(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        resp = self.bc.put_page(self.container_name, 'blob1', '', 'bytes=0-511', 'clear')

        # Assert
        self.assertIsNone(resp)

    def test_get_page_ranges_no_pages(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 1024)

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEquals(len(ranges.page_ranges), 0)

    def test_get_page_ranges_2_pages(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 2048)
        data = 'abcdefghijklmnop' * 32
        resp1 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, PageList)
        self.assertEquals(len(ranges.page_ranges), 2)
        self.assertEquals(ranges.page_ranges[0].start, 0)
        self.assertEquals(ranges.page_ranges[0].end, 511)
        self.assertEquals(ranges.page_ranges[1].start, 1024)
        self.assertEquals(ranges.page_ranges[1].end, 1535)

    def test_get_page_ranges_iter(self):
        # Arrange
        self._create_container_and_page_blob(self.container_name, 'blob1', 2048)
        data = 'abcdefghijklmnop' * 32
        resp1 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=0-511', 'update')
        resp2 = self.bc.put_page(self.container_name, 'blob1', data, 'bytes=1024-1535', 'update')

        # Act
        ranges = self.bc.get_page_ranges(self.container_name, 'blob1')
        for range in ranges:
            pass

        # Assert
        self.assertEquals(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    def test_with_filter(self):
        # Single filter
        called = []
        def my_filter(request, next):
            called.append(True)
            self.assertIsInstance(request, HTTPRequest)
            for header in request.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, (str, unicode, type(None)))
            self.assertIsInstance(request.host, (str, unicode))
            self.assertIsInstance(request.method, (str, unicode))
            self.assertIsInstance(request.path, (str, unicode))
            self.assertIsInstance(request.query, list)
            self.assertIsInstance(request.body, (str, unicode))
            response = next(request)
                
            self.assertIsInstance(response, HTTPResponse)
            self.assertIsInstance(response.body, (str, type(None)))
            self.assertIsInstance(response.headers, list)
            for header in response.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, (str, unicode))
            self.assertIsInstance(response.status, int)
            return response

        bc = self.bc.with_filter(my_filter)
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

        bc = self.bc.with_filter(filter_a).with_filter(filter_b)
        bc.create_container(self.container_name + '1', None, None, False)

        self.assertEqual(called, ['b', 'a'])
        
        bc.delete_container(self.container_name + '1')

        self.assertEqual(called, ['b', 'a', 'b', 'a'])

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
