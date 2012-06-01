#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
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
from azure.storage import Metrics, BlockList
from azure import WindowsAzureError
from azuretest.util import *
from azure.http import HTTPRequest, HTTPResponse

import unittest
import time

#------------------------------------------------------------------------------
class BlobServiceTest(unittest.TestCase):

    def setUp(self):
        self.bc = BlobService(account_name=credentials.getStorageServicesName(), 
                                  account_key=credentials.getStorageServicesKey())

        # TODO: it may be overkill to use the machine name from 
        #       getUniqueTestRunID, current time may be unique enough
        __uid = getUniqueTestRunID()

        container_base_name = u'mytestcontainer%s' % (__uid)

        self.container_name = getUniqueNameBasedOnCurrentTime(container_base_name)

    def tearDown(self):
        self.cleanup()
        return super(BlobServiceTest, self).tearDown()

    def cleanup(self):
        try:
            self.bc.delete_container(self.container_name)
        except: pass

    #--Helpers-----------------------------------------------------------------

    # TODO: move this function out of here so other tests can use them
    # TODO: find out how to import/use safe_repr instead repr
    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = '%s not found in %s' % (repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    # TODO: move this function out of here so other tests can use them
    # TODO: find out how to import/use safe_repr instead repr
    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '%s unexpectedly found in %s' % (repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

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
        self.assertNamedItemInContainer(containers, self.container_name)

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

        # Act
        md = self.bc.get_container_metadata(self.container_name)

        # Assert
        self.assertIsNotNone(md)

    def test_get_container_metadata_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.bc.get_container_metadata(self.container_name)

        # Assert

    def test_get_container_properties(self):
        # Arrange
        self.bc.create_container(self.container_name)

        # Act
        props = self.bc.get_container_properties(self.container_name)

        # Assert
        self.assertIsNotNone(props)

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
        resp = self.bc.put_blob(self.container_name, 'blob1', data, 'BlockBlob')
        resp = self.bc.put_blob(self.container_name, 'blob2', data, 'BlockBlob')

        # Act
        blobs = self.bc.list_blobs(self.container_name)
        for blob in blobs:
            name = blob.name

        # Assert
        self.assertIsNotNone(blobs)
        self.assertNamedItemInContainer(blobs, 'blob1')
        self.assertNamedItemInContainer(blobs, 'blob2')

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

    def test_get_blob_with_existing_blob(self):
        # Arrange
        self._create_container_and_block_blob(self.container_name, 'blob1', 'hello world')

        # Act
        blob = self.bc.get_blob(self.container_name, 'blob1')

        # Assert
        self.assertEqual(type(blob), str)
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
        self.assertEquals(props['Content-Language'], 'spanish')

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
        self.assertIsNone(resp)

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
            self.assertIsInstance(request.uri, (str, unicode))
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
