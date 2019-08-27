# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

import pytest
import os
import unittest
from datetime import datetime, timedelta
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobProperties,
    BlobPermissions,
    BlobType,
    PremiumPageBlobTier,
    SequenceNumberAction,
    StorageErrorCode)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from testcase import (
    StorageTestCase
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024 + 512
EIGHT_TB = 8 * 1024 * 1024 * 1024 * 1024
#------------------------------------------------------------------------------s

class StoragePageBlobTest(StorageTestCase):
    #--Helpers-----------------------------------------------------------------

    def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            bsc.create_container(self.container_name)

    def _get_blob_reference(self, bsc):
        return bsc.get_blob_client(
            self.container_name,
            self.get_resource_name(TEST_BLOB_PREFIX))

    def _create_blob(self, bsc, length=512):
        blob = self._get_blob_reference(bsc)
        blob.create_page_blob(size=length)
        return blob

    def _wait_for_async_copy(self, blob):
        count = 0
        props = blob.get_blob_properties()
        while props.copy.status == 'pending':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            props = blob.get_blob_properties()
        return props

    def assertBlobEqual(self, container_name, blob_name, expected_data, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), expected_data)

    def assertRangeEqual(self, container_name, blob_name, expected_data, start_range, end_range, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob(offset=start_range, length=end_range)
        self.assertEqual(b"".join(list(actual_data)), expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for page blobs --------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)

        # Act
        resp = blob.create_page_blob(1024)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertTrue(blob.get_blob_properties())

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        metadata = {'hello': 'world', 'number': '42'}
        
        # Act
        resp = blob.create_page_blob(512, metadata=metadata)

        # Assert
        md = blob.get_blob_properties()
        self.assertDictEqual(md.metadata, metadata)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_put_page_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)
        lease = blob.acquire_lease()

        # Act        
        data = self.get_random_bytes(512)
        blob.upload_page(data, 0, 511, lease=lease)

        # Assert
        content = blob.download_blob(lease=lease)
        self.assertEqual(b"".join(list(content)), data)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = blob.upload_page(data, 0, 511)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_8tb_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)

        # Act
        resp = blob.create_page_blob(EIGHT_TB)
        props = blob.get_blob_properties()
        page_ranges, cleared = blob.get_page_ranges()

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.size, EIGHT_TB)
        self.assertEqual(0, len(page_ranges))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_larger_than_8tb_blob_fail(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.create_page_blob(EIGHT_TB + 1)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_8tb_blob_page(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        blob.create_page_blob(EIGHT_TB)

        # Act
        data = self.get_random_bytes(512)
        start_range = EIGHT_TB - 512
        end_range = EIGHT_TB - 1
        resp = blob.upload_page(data, start_range, end_range)
        props = blob.get_blob_properties()
        page_ranges, cleared = blob.get_page_ranges()
        
        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertRangeEqual(self.container_name, blob.blob_name, data, start_range, end_range, bsc)
        self.assertEqual(props.size, EIGHT_TB)
        self.assertEqual(1, len(page_ranges))
        self.assertEqual(page_ranges[0]['start'], start_range)
        self.assertEqual(page_ranges[0]['end'], end_range)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_with_md5(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = blob.upload_page(data, 0, 511, validate_content=True)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_clear_page(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)

        # Act
        resp = blob.clear_page(0, 511)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertBlobEqual(self.container_name, blob.blob_name, b'\x00' * 512)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_put_page_if_sequence_number_lt_success(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)       
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)

        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, 0, 511, if_sequence_number_lt=start_sequence + 1)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_if_sequence_number_lt_failure(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_sequence_number_lt=start_sequence)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_if_sequence_number_lte_success(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, 0, 511, if_sequence_number_lte=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_if_sequence_number_lte_failure(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_sequence_number_lte=start_sequence - 1)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_if_sequence_number_eq_success(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, 0, 511, if_sequence_number_eq=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_if_sequence_number_eq_failure(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc) 
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_sequence_number_eq=start_sequence - 1)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_update_page_unicode(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)

        # Act
        data = u'abcdefghijklmnop' * 32
        resp = blob.upload_page(data, 0, 511)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_page_ranges_no_pages(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)

        # Act
        ranges, cleared = blob.get_page_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(len(ranges), 0)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_page_ranges_2_pages(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = blob.upload_page(data, 0, 511)
        resp2 = blob.upload_page(data, 1024, 1535)

        # Act
        ranges, cleared = blob.get_page_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]['start'], 0)
        self.assertEqual(ranges[0]['end'], 511)
        self.assertEqual(ranges[1]['start'], 1024)
        self.assertEqual(ranges[1]['end'], 1535)


    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_get_page_ranges_diff(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc, 2048)
        data = self.get_random_bytes(1536)
        snapshot1 = blob.create_snapshot()
        blob.upload_page(data, 0, 1535)
        snapshot2 = blob.create_snapshot()
        blob.clear_page(512, 1023)

        # Act
        ranges1, cleared1 = blob.get_page_ranges(previous_snapshot_diff=snapshot1)
        ranges2, cleared2 = blob.get_page_ranges(previous_snapshot_diff=snapshot2['snapshot'])

        # Assert
        self.assertIsNotNone(ranges1)
        self.assertIsInstance(ranges1, list)
        self.assertEqual(len(ranges1), 2)
        self.assertIsInstance(cleared1, list)
        self.assertEqual(len(cleared1), 1)
        self.assertEqual(ranges1[0]['start'], 0)
        self.assertEqual(ranges1[0]['end'], 511)
        self.assertEqual(cleared1[0]['start'], 512)
        self.assertEqual(cleared1[0]['end'], 1023)
        self.assertEqual(ranges1[1]['start'], 1024)
        self.assertEqual(ranges1[1]['end'], 1535)

        self.assertIsNotNone(ranges2)
        self.assertIsInstance(ranges2, list)
        self.assertEqual(len(ranges2), 0)
        self.assertIsInstance(cleared2, list)
        self.assertEqual(len(cleared2), 1)
        self.assertEqual(cleared2[0]['start'], 512)
        self.assertEqual(cleared2[0]['end'], 1023)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')   
    def test_update_page_fail(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = blob.upload_page(data, 0, 511)

        # Act
        try:
            blob.upload_page(data, 1024, 1536)
        except ValueError as e:
            self.assertEqual(str(e), 'end_range must be an integer that aligns with 512 page size')
            return

        # Assert
        raise Exception('Page range validation failed to throw on failure case')


    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_resize_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(1024)
        
        # Act
        resp = blob.resize_blob(512)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        props = blob.get_blob_properties()
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.size, 512)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_set_sequence_number_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._create_blob(bsc)
        
        # Act
        resp = blob.set_sequence_number(SequenceNumberAction.Update, 6)     

        #Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        props = blob.get_blob_properties()
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.page_blob_sequence_number, 6)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_page_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'BlobData': 'Data1'})

        with self.assertRaises(ResourceExistsError):
            blob.upload_blob(
                data2,
                overwrite=False,
                blob_type=BlobType.PageBlob,
                metadata={'BlobData': 'Data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data1, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'BlobData': 'Data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE)
        self.assertEqual(props.blob_type, BlobType.PageBlob)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_page_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'BlobData': 'Data1'})
        update_resp = blob.upload_blob(
            data2,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'BlobData': 'Data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data2, bsc)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'BlobData': 'Data2'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)
        self.assertEqual(props.blob_type, BlobType.PageBlob)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_bytes(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = blob.upload_blob(data, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_0_bytes(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(0)

        # Act
        create_resp = blob.upload_blob(data, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_bytes_with_progress_first(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        create_resp = blob.upload_blob(
            data, blob_type=BlobType.PageBlob, raw_response_hook=callback)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assert_upload_progress(LARGE_BLOB_SIZE, self.config.max_page_size, progress)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_bytes_with_index(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 1024

        # Act
        blob.upload_blob(data[index:], blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[1024:])

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_bytes_with_index_and_count(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 512
        count = 1024

        # Act
        create_resp = blob.upload_blob(data[index:], length=count, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[index:index + count])
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)          
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_input.temp.dat'
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_path_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)          
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assert_upload_progress(len(data), self.config.max_page_size, progress)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)          
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream_with_empty_pages(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        # data is almost all empty (0s) except two ranges
        blob = self._get_blob_reference(bsc)
        data = bytearray(LARGE_BLOB_SIZE)
        data[512: 1024] = self.get_random_bytes(512)
        data[8192: 8196] = self.get_random_bytes(4)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        # the uploader should have skipped the empty ranges
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        page_ranges, cleared = list(blob.get_page_ranges())
        self.assertEqual(len(page_ranges), 2)
        self.assertEqual(page_ranges[0]['start'], 0)
        self.assertEqual(page_ranges[0]['end'], 4095)
        self.assertEqual(page_ranges[1]['start'], 8192)
        self.assertEqual(page_ranges[1]['end'], 12287)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream_non_seekable(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)        
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StoragePageBlobTest.NonSeekableFile(stream)
            blob.upload_blob(
                non_seekable_file,
                length=blob_size,
                max_connections=1,
                blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)        
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(
                stream, length=blob_size, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self.assert_upload_progress(len(data), self.config.max_page_size, progress)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream_truncated(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)         
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_from_stream_with_progress_truncated(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)         
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(
                stream, length=blob_size, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self.assert_upload_progress(blob_size, self.config.max_page_size, progress)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_md5_small(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)

        # Act
        blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_create_blob_with_md5_large(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_incremental_copy_blob(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)  
        source_blob = self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = source_blob.upload_page(data, 0, 511)
        resp2 = source_blob.upload_page(data, 1024, 1535)
        source_snapshot_blob = source_blob.create_snapshot()

        snapshot_blob = BlobClient(
            source_blob.url, credential=source_blob.credential, snapshot=source_snapshot_blob)
        sas_token = snapshot_blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient(snapshot_blob.url, credential=sas_token)


        # Act
        dest_blob = bsc.get_blob_client(self.container_name, 'dest_blob')
        copy = dest_blob.start_copy_from_url(sas_blob.url, incremental_copy=True)

        # Assert
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy['copy_id'])
        self.assertEqual(copy['copy_status'], 'pending')

        copy_blob = self._wait_for_async_copy(dest_blob)
        self.assertEqual(copy_blob.copy.status, 'success')
        self.assertIsNotNone(copy_blob.copy.destination_snapshot)

        # strip off protocol
        self.assertTrue(copy_blob.copy.source.endswith(sas_blob.url[5:]))

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_tier_on_create(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self._get_premium_account_url()
        credential = self._get_premium_shared_key_credential()
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)
            if self.is_live:
                container.create_container()

            # test create_blob API
            blob = self._get_blob_reference(bsc)
            pblob = pbs.get_blob_client(container_name, blob.blob_name)
            pblob.create_page_blob(1024, premium_page_blob_tier=PremiumPageBlobTier.P4)

            props = pblob.get_blob_properties()
            self.assertEqual(props.blob_tier, PremiumPageBlobTier.P4)
            self.assertFalse(props.blob_tier_inferred)

            # test create_blob_from_bytes API
            blob2 = self._get_blob_reference(bsc)
            pblob2 = pbs.get_blob_client(container_name, blob2.blob_name)
            byte_data = self.get_random_bytes(1024)
            pblob2.upload_blob(
                byte_data,
                premium_page_blob_tier=PremiumPageBlobTier.P6,
                blob_type=BlobType.PageBlob)

            props2 = pblob2.get_blob_properties()
            self.assertEqual(props2.blob_tier, PremiumPageBlobTier.P6)
            self.assertFalse(props2.blob_tier_inferred)

            # test create_blob_from_path API
            blob3 = self._get_blob_reference(bsc)
            pblob3 = pbs.get_blob_client(container_name, blob3.blob_name)
            with open(FILE_PATH, 'wb') as stream:
                stream.write(byte_data)
            with open(FILE_PATH, 'rb') as stream:
                pblob3.upload_blob(
                    stream,
                    blob_type=BlobType.PageBlob,
                    premium_page_blob_tier=PremiumPageBlobTier.P10)

            props3 = pblob3.get_blob_properties()
            self.assertEqual(props3.blob_tier, PremiumPageBlobTier.P10)
            self.assertFalse(props3.blob_tier_inferred)

        finally:
            container.delete_container()

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_tier_set_tier_api(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self._get_premium_account_url()
        credential = self._get_premium_shared_key_credential()
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if self.is_live:
                try:
                    container.create_container()
                except ResourceExistsError:
                    pass

            blob = self._get_blob_reference(bsc)
            pblob = pbs.get_blob_client(container_name, blob.blob_name)
            pblob.create_page_blob(1024)
            blob_ref = pblob.get_blob_properties()
            self.assertEqual(PremiumPageBlobTier.P10, blob_ref.blob_tier)
            self.assertIsNotNone(blob_ref.blob_tier)
            self.assertTrue(blob_ref.blob_tier_inferred)

            pcontainer = pbs.get_container_client(container_name)
            blobs = list(pcontainer.list_blobs())

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)

            pblob.set_premium_page_blob_tier(PremiumPageBlobTier.P50)

            blob_ref2 = pblob.get_blob_properties()
            self.assertEqual(PremiumPageBlobTier.P50, blob_ref2.blob_tier)
            self.assertFalse(blob_ref2.blob_tier_inferred)

            blobs = list(pcontainer.list_blobs())

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            self.assertEqual(blobs[0].blob_tier, PremiumPageBlobTier.P50)
            self.assertFalse(blobs[0].blob_tier_inferred)
        finally:
            container.delete_container()

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_blob_tier_copy_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self._account_url(storage_account.name), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self._get_premium_account_url()
        credential = self._get_premium_shared_key_credential()
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if self.is_live:
                try:
                    container.create_container()
                except ResourceExistsError:
                    pass
  
            source_blob = pbs.get_blob_client(
                container_name,
                self.get_resource_name(TEST_BLOB_PREFIX))
            source_blob.create_page_blob(1024, premium_page_blob_tier=PremiumPageBlobTier.P10)

            # Act
            source_blob_url = '{0}/{1}/{2}'.format(
                self._get_premium_account_url(), container_name, source_blob.blob_name)

            copy_blob = pbs.get_blob_client(container_name, 'blob1copy')
            copy = copy_blob.start_copy_from_url(source_blob_url, premium_page_blob_tier=PremiumPageBlobTier.P30)

            # Assert
            self.assertIsNotNone(copy)
            self.assertEqual(copy['copy_status'], 'success')
            self.assertIsNotNone(copy['copy_id'])

            copy_ref = copy_blob.get_blob_properties()
            self.assertEqual(copy_ref.blob_tier, PremiumPageBlobTier.P30)

            source_blob2 = pbs.get_blob_client(
               container_name,
               self.get_resource_name(TEST_BLOB_PREFIX))

            source_blob2.create_page_blob(1024)
            source_blob2_url = '{0}/{1}/{2}'.format(
                self._get_premium_account_url(), source_blob2.container_name, source_blob2.blob_name)

            copy_blob2 = pbs.get_blob_client(container_name, 'blob2copy')
            copy2 = copy_blob2.start_copy_from_url(source_blob2_url, premium_page_blob_tier=PremiumPageBlobTier.P60)
            self.assertIsNotNone(copy2)
            self.assertEqual(copy2['copy_status'], 'success')
            self.assertIsNotNone(copy2['copy_id'])

            copy_ref2 = copy_blob2.get_blob_properties()
            self.assertEqual(copy_ref2.blob_tier, PremiumPageBlobTier.P60)
            self.assertFalse(copy_ref2.blob_tier_inferred)

            copy_blob3 = pbs.get_blob_client(container_name, 'blob3copy')
            copy3 = copy_blob3.start_copy_from_url(source_blob2_url)
            self.assertIsNotNone(copy3)
            self.assertEqual(copy3['copy_status'], 'success')
            self.assertIsNotNone(copy3['copy_id'])

            copy_ref3 = copy_blob3.get_blob_properties()
            self.assertEqual(copy_ref3.blob_tier, PremiumPageBlobTier.P10)
            self.assertTrue(copy_ref3.blob_tier_inferred)
        finally:
            container.delete_container()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
