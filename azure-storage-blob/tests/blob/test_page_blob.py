# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import unittest
from datetime import datetime, timedelta
from azure.common import AzureHttpError
#from azure.storage.blob import BlobPermissions
#from azure.storage.blob.models import PremiumPageBlobTier

from azure.storage.blob import (
    #Blob,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    #SequenceNumberAction,
    #PageRange,
)

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)
from azure.common import (
    AzureException,
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024 + 512
EIGHT_TB = 8 * 1024 * 1024 * 1024 * 1024
#------------------------------------------------------------------------------s

class StoragePageBlobTest(StorageTestCase):

    def setUp(self):
        super(StoragePageBlobTest, self).setUp()

        self.bs = self._create_storage_service(PageBlobService, self.settings)
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bs.MAX_PAGE_SIZE = 4 * 1024

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StoragePageBlobTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self, length=512):
        blob_name = self._get_blob_reference()
        self.bs.create_blob(self.container_name, blob_name, length)
        return blob_name

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        actual_data = self.bs.get_blob_to_bytes(container_name, blob_name)
        self.assertEqual(actual_data.content, expected_data)

    def assertRangeEqual(self, container_name, blob_name, expected_data, start_range, end_range):
        actual_data = self.bs.get_blob_to_bytes(container_name, blob_name, None, start_range, end_range)
        self.assertEqual(actual_data.content, expected_data)

    def _wait_for_async_copy(self, container_name, blob_name):
        count = 0
        blob = self.bs.get_blob_properties(container_name, blob_name)
        while blob.properties.copy.status != 'success':
            count = count + 1
            if count > 5:
                self.assertTrue(
                    False, 'Timed out waiting for async copy to complete.')
            self.sleep(5)
            blob = self.bs.get_blob_properties(container_name, blob_name)
        self.assertEqual(blob.properties.copy.status, 'success')

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for page blobs --------------------------------------------
    @record
    def test_create_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        resp = self.bs.create_blob(self.container_name, blob_name, 1024)

        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertTrue(self.bs.exists(self.container_name, blob_name))

    @record
    def test_create_blob_with_metadata(self):
        # Arrange
        blob_name = self._get_blob_reference()
        metadata = {'hello': 'world', 'number': '42'}
        
        # Act
        resp = self.bs.create_blob(self.container_name, blob_name, 512, metadata=metadata)

        # Assert
        md = self.bs.get_blob_metadata(self.container_name, blob_name)
        self.assertDictEqual(md, metadata)

    @record
    def test_put_page_with_lease_id(self):
        # Arrange
        blob_name = self._create_blob()
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act        
        data = self.get_random_bytes(512)
        self.bs.update_page(self.container_name, blob_name, data, 0, 511, lease_id=lease_id)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, lease_id=lease_id)
        self.assertEqual(blob.content, data)

    @record
    def test_update_page(self):
        # Arrange
        blob_name = self._create_blob()

        # Act
        data = self.get_random_bytes(512)
        resp = self.bs.update_page(self.container_name, blob_name, data, 0, 511)

        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsNotNone(resp.sequence_number)
        self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_8tb_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        resp = self.bs.create_blob(self.container_name, blob_name, EIGHT_TB)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        ranges = self.bs.get_page_ranges(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.properties.content_length, EIGHT_TB)
        self.assertEqual(0, len(ranges))

    @record
    def test_create_larger_than_8tb_blob_fail(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.create_blob(self.container_name, blob_name, EIGHT_TB + 1)

    @record
    def test_update_8tb_blob_page(self):
        # Arrange
        blob_name = self._get_blob_reference()
        self.bs.create_blob(self.container_name, blob_name, EIGHT_TB)

        # Act
        data = self.get_random_bytes(512)
        start_range = EIGHT_TB - 512
        end_range = EIGHT_TB - 1
        resp = self.bs.update_page(self.container_name, blob_name, data, start_range, end_range)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        ranges = self.bs.get_page_ranges(self.container_name, blob_name)
        
        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsNotNone(resp.sequence_number)
        self.assertRangeEqual(self.container_name, blob_name, data, start_range, end_range)
        self.assertEqual(blob.properties.content_length, EIGHT_TB)
        self.assertEqual(1, len(ranges))
        self.assertEqual(ranges[0].start, start_range)
        self.assertEqual(ranges[0].end, end_range)

    @record
    def test_update_page_with_md5(self):
        # Arrange
        blob_name = self._create_blob()

        # Act
        data = self.get_random_bytes(512)
        resp = self.bs.update_page(self.container_name, blob_name, data, 0, 511, 
                                   validate_content=True)

        # Assert

    @record
    def test_clear_page(self):
        # Arrange
        blob_name = self._create_blob()

        # Act
        resp = self.bs.clear_page(self.container_name, blob_name, 0, 511)

        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsNotNone(resp.sequence_number)
        self.assertBlobEqual(self.container_name, blob_name, b'\x00' * 512)

    @record
    def test_put_page_if_sequence_number_lt_success(self):
        # Arrange     
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)

        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512, sequence_number=start_sequence)

        # Act
        self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                         if_sequence_number_lt=start_sequence + 1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_update_page_if_sequence_number_lt_failure(self):
        # Arrange
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)
        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                             if_sequence_number_lt=start_sequence)

        # Assert

    @record
    def test_update_page_if_sequence_number_lte_success(self):
        # Arrange
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)
        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512, sequence_number=start_sequence)

        # Act
        self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                            if_sequence_number_lte=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_update_page_if_sequence_number_lte_failure(self):
        # Arrange
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)
        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                                if_sequence_number_lte=start_sequence - 1)

        # Assert

    @record
    def test_update_page_if_sequence_number_eq_success(self):
        # Arrange
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)
        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512, sequence_number=start_sequence)

        # Act
        self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                            if_sequence_number_eq=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_update_page_if_sequence_number_eq_failure(self):
        # Arrange
        blob_name = self._get_blob_reference() 
        data = self.get_random_bytes(512)
        start_sequence = 10
        self.bs.create_blob(self.container_name, blob_name, 512,
                            sequence_number=start_sequence)

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.update_page(self.container_name, blob_name, data, 0, 511,
                                if_sequence_number_eq=start_sequence - 1)

        # Assert

    @record
    def test_update_page_unicode(self):
        # Arrange
        blob_name = self._create_blob()

        # Act
        data = u'abcdefghijklmnop' * 32
        with self.assertRaises(TypeError):
            self.bs.update_page(self.container_name, blob_name, data, 0, 511)

        # Assert

    @record
    def test_get_page_ranges_no_pages(self):
        # Arrange
        blob_name = self._create_blob()

        # Act
        ranges = self.bs.get_page_ranges(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(len(ranges), 0)

    @record
    def test_get_page_ranges_2_pages(self):
        # Arrange
        blob_name = self._create_blob(2048)
        data = self.get_random_bytes(512)
        resp1 = self.bs.update_page(self.container_name, blob_name, data, 0, 511)
        resp2 = self.bs.update_page(self.container_name, blob_name, data, 1024, 1535)

        # Act
        ranges = self.bs.get_page_ranges(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0].start, 0)
        self.assertEqual(ranges[0].end, 511)
        self.assertEqual(ranges[1].start, 1024)
        self.assertEqual(ranges[1].end, 1535)


    @record
    def test_get_page_ranges_diff(self):
        # Arrange
        blob_name = self._create_blob(2048)
        data = self.get_random_bytes(1536)
        snapshot1 = self.bs.snapshot_blob(self.container_name, blob_name)
        self.bs.update_page(self.container_name, blob_name, data, 0, 1535)
        snapshot2 = self.bs.snapshot_blob(self.container_name, blob_name)
        self.bs.clear_page(self.container_name, blob_name, 512, 1023)

        # Act
        ranges1 = self.bs.get_page_ranges_diff(self.container_name, blob_name, snapshot1.snapshot)
        ranges2 = self.bs.get_page_ranges_diff(self.container_name, blob_name, snapshot2.snapshot)

        # Assert
        self.assertIsNotNone(ranges1)
        self.assertIsInstance(ranges1, list)
        self.assertEqual(len(ranges1), 3)
        self.assertEqual(ranges1[0].is_cleared, False)
        self.assertEqual(ranges1[0].start, 0)
        self.assertEqual(ranges1[0].end, 511)
        self.assertEqual(ranges1[1].is_cleared, True)
        self.assertEqual(ranges1[1].start, 512)
        self.assertEqual(ranges1[1].end, 1023)
        self.assertEqual(ranges1[2].is_cleared, False)
        self.assertEqual(ranges1[2].start, 1024)
        self.assertEqual(ranges1[2].end, 1535)

        self.assertIsNotNone(ranges2)
        self.assertIsInstance(ranges2, list)
        self.assertEqual(len(ranges2), 1)
        self.assertEqual(ranges2[0].is_cleared, True)
        self.assertEqual(ranges2[0].start, 512)
        self.assertEqual(ranges2[0].end, 1023)

    @record    
    def test_update_page_fail(self):
        # Arrange
        blob_name = self._create_blob(2048)
        data = self.get_random_bytes(512)
        resp1 = self.bs.update_page(self.container_name, blob_name, data, 0, 511)

        # Act
        try:
            self.bs.update_page(self.container_name, blob_name, data, 1024, 1536)
        except ValueError as e:
            self.assertEqual(str(e), 'end_range must align with 512 page size')
            return

        # Assert
        raise Exception('Page range validation failed to throw on failure case')


    @record
    def test_resize_blob(self):
        # Arrange
        blob_name = self._create_blob(1024)
        
        # Act
        resp = self.bs.resize_blob(self.container_name, blob_name, 512)

        # Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsNotNone(resp.sequence_number)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.properties.content_length, 512)

    @record
    def test_set_sequence_number_blob(self):
        # Arrange
        blob_name = self._create_blob()
        
        # Act
        resp = self.bs.set_sequence_number(self.container_name, blob_name, SequenceNumberAction.Update, 6)     

        #Assert
        self.assertIsNotNone(resp.etag)
        self.assertIsNotNone(resp.last_modified)
        self.assertIsNotNone(resp.sequence_number)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.properties.page_blob_sequence_number, 6)

    def test_create_blob_from_bytes(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_0_bytes(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(0)

        # Act
        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_bytes_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data, progress_callback=callback)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_bytes_with_index(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 1024

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, index)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[1024:])

    @record
    def test_create_blob_from_bytes_with_index_and_count(self):
        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 512
        count = 1024

        # Act
        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data, index, count)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[index:index + count])
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange        
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_input.temp.dat'
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        create_resp = self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange        
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH, 
                                      progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_PAGE_SIZE, progress)

    def test_create_blob_from_stream(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange        
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = self.bs.create_blob_from_stream(self.container_name, blob_name, stream, blob_size)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_stream_with_empty_pages(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        # data is almost all empty (0s) except two ranges
        blob_name = self._get_blob_reference()
        data = bytearray(LARGE_BLOB_SIZE)
        data[512: 1024] = self.get_random_bytes(512)
        data[8192: 8196] = self.get_random_bytes(4)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = self.bs.create_blob_from_stream(self.container_name, blob_name, stream, blob_size)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        # the uploader should have skipped the empty ranges
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        page_ranges = list(self.bs.get_page_ranges(self.container_name, blob_name))
        self.assertEqual(len(page_ranges), 2)
        self.assertEqual(page_ranges[0].start, 0)
        self.assertEqual(page_ranges[0].end, 4095)
        self.assertEqual(page_ranges[1].start, 8192)
        self.assertEqual(page_ranges[1].end, 12287)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_stream_non_seekable(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange      
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StoragePageBlobTest.NonSeekableFile(stream)
            self.bs.create_blob_from_stream(self.container_name, blob_name, 
                                            non_seekable_file, blob_size, 
                                            max_connections=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_blob_from_stream_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange      
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream, 
                                            blob_size, progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assert_upload_progress(len(data), self.bs.MAX_PAGE_SIZE, progress)

    def test_create_blob_from_stream_truncated(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange       
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_blob_from_stream_with_progress_truncated(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange       
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream, 
                                            blob_size, progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self.assert_upload_progress(blob_size, self.bs.MAX_PAGE_SIZE, progress)

    @record
    def test_create_blob_with_md5_small(self):
        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(512)

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, 
                                       validate_content=True)

        # Assert

    def test_create_blob_with_md5_large(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, 
                                       validate_content=True)

        # Assert

    def test_incremental_copy_blob(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        source_blob_name = self._create_blob(2048)
        data = self.get_random_bytes(512)
        resp1 = self.bs.update_page(self.container_name, source_blob_name, data, 0, 511)
        resp2 = self.bs.update_page(self.container_name, source_blob_name, data, 1024, 1535)
        source_snapshot_blob = self.bs.snapshot_blob(self.container_name, source_blob_name)

        sas_token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            source_blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        source_blob_url = self.bs.make_blob_url(
            self.container_name,
            source_blob_name, # + '?snapshot=' + source_snapshot_blob.snapshot,
            sas_token=sas_token,
            snapshot=source_snapshot_blob.snapshot)

        dest_blob_name = 'dest_blob'
        copy = self.bs.incremental_copy_blob(self.container_name, dest_blob_name, source_blob_url)

        # Assert
        self.assertEqual(copy.status, 'pending')
        self._wait_for_async_copy(self.container_name, dest_blob_name)
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy.id)

        copy_blob = self.bs.get_blob_properties(self.container_name, dest_blob_name)
        self.assertEqual(copy_blob.properties.copy.status, 'success')
        self.assertIsNotNone(copy_blob.properties.copy.destination_snapshot_time)

        # strip off protocol
        self.assertTrue(copy_blob.properties.copy.source.endswith(source_blob_url[5:]))

    @record
    def test_blob_tier_on_create(self):
        ps = self._create_premium_storage_service(PageBlobService, self.settings)
        try:
            container_name = self.get_resource_name('utpremiumcontainer')

            if not self.is_playback():
                ps.create_container(container_name)

            # test create_blob API
            blob_name = self._get_blob_reference()
            ps.create_blob(container_name, blob_name, 1024, premium_page_blob_tier=PremiumPageBlobTier.P4)

            blob = ps.get_blob_properties(container_name, blob_name)
            self.assertEqual(blob.properties.blob_tier, PremiumPageBlobTier.P4)
            self.assertFalse(blob.properties.blob_tier_inferred)

            # test create_blob_from_bytes API
            blob_name2 = self._get_blob_reference()
            byte_data = self.get_random_bytes(1024)
            ps.create_blob_from_bytes(container_name, blob_name2, byte_data, premium_page_blob_tier=PremiumPageBlobTier.P6)

            blob2 = ps.get_blob_properties(container_name, blob_name2)
            self.assertEqual(blob2.properties.blob_tier, PremiumPageBlobTier.P6)
            self.assertFalse(blob.properties.blob_tier_inferred)

            # test create_blob_from_path API
            blob_name3 = self._get_blob_reference()
            with open(FILE_PATH, 'wb') as stream:
                stream.write(byte_data)
            ps.create_blob_from_path(container_name, blob_name3, FILE_PATH, premium_page_blob_tier=PremiumPageBlobTier.P10)

            blob3 = ps.get_blob_properties(container_name, blob_name3)
            self.assertEqual(blob3.properties.blob_tier, PremiumPageBlobTier.P10)
            self.assertFalse(blob.properties.blob_tier_inferred)

            # test create_blob_from_stream API
            blob_name4 = self._get_blob_reference()
            with open(FILE_PATH, 'rb') as stream:
                ps.create_blob_from_stream(container_name, blob_name4, stream, 1024, premium_page_blob_tier=PremiumPageBlobTier.P20)

            blob4 = ps.get_blob_properties(container_name, blob_name4)
            self.assertEqual(blob4.properties.blob_tier, PremiumPageBlobTier.P20)
            self.assertFalse(blob.properties.blob_tier_inferred)
        finally:
            ps.delete_container(container_name)

    @record
    def test_blob_tier_set_tier_api(self):
        ps = self._create_premium_storage_service(PageBlobService, self.settings)
        try:
            container_name = self.get_resource_name('utpremiumcontainer')

            if not self.is_playback():
                ps.create_container(container_name)

            blob_name = self._get_blob_reference()
            ps.create_blob(container_name, blob_name, 1024)
            blob_ref = ps.get_blob_properties(container_name, blob_name)
            self.assertEqual(PremiumPageBlobTier.P10, blob_ref.properties.blob_tier)
            self.assertIsNotNone(blob_ref.properties.blob_tier)
            self.assertTrue(blob_ref.properties.blob_tier_inferred)

            blobs = list(ps.list_blobs(container_name))

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob_name)

            ps.set_premium_page_blob_tier(container_name, blob_name, PremiumPageBlobTier.P50)

            blob_ref2 = ps.get_blob_properties(container_name, blob_name)
            self.assertEqual(PremiumPageBlobTier.P50, blob_ref2.properties.blob_tier)
            self.assertFalse(blob_ref2.properties.blob_tier_inferred)

            blobs = list(ps.list_blobs(container_name))

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob_name)
            self.assertEqual(blobs[0].properties.blob_tier, PremiumPageBlobTier.P50)
            self.assertFalse(blobs[0].properties.blob_tier_inferred)
        finally:
            ps.delete_container(container_name)

    @record
    def test_blob_tier_copy_blob(self):
        ps = self._create_premium_storage_service(PageBlobService, self.settings)
        try:
            container_name = self.get_resource_name('utpremiumcontainer')

            if not self.is_playback():
                ps.create_container(container_name)

            # Arrange
            source_blob_name = self._get_blob_reference()
            ps.create_blob(container_name, source_blob_name, 1024, premium_page_blob_tier=PremiumPageBlobTier.P10)

            # Act
            source_blob = '/{0}/{1}/{2}'.format(self.settings.PREMIUM_STORAGE_ACCOUNT_NAME,
                                               container_name,
                                               source_blob_name)
            copy = ps.copy_blob(container_name, 'blob1copy', source_blob, premium_page_blob_tier=PremiumPageBlobTier.P30)

            # Assert
            self.assertIsNotNone(copy)
            self.assertEqual(copy.status, 'success')
            self.assertIsNotNone(copy.id)

            copy_ref = ps.get_blob_properties(container_name, 'blob1copy')
            self.assertEqual(copy_ref.properties.blob_tier, PremiumPageBlobTier.P30)

            source_blob_name2 = self._get_blob_reference()
            ps.create_blob(container_name, source_blob_name2, 1024)
            source_blob2 = '/{0}/{1}/{2}'.format(self.settings.STORAGE_ACCOUNT_NAME,
                                                container_name,
                                                source_blob_name2)

            copy2 = ps.copy_blob(container_name, 'blob2copy', source_blob2, premium_page_blob_tier=PremiumPageBlobTier.P60)
            self.assertIsNotNone(copy2)
            self.assertEqual(copy2.status, 'success')
            self.assertIsNotNone(copy2.id)

            copy_ref2 = ps.get_blob_properties(container_name, 'blob2copy')
            self.assertEqual(copy_ref2.properties.blob_tier, PremiumPageBlobTier.P60)
            self.assertFalse(copy_ref2.properties.blob_tier_inferred)

            copy3 = ps.copy_blob(container_name, 'blob3copy', source_blob2)
            self.assertIsNotNone(copy3)
            self.assertEqual(copy3.status, 'success')
            self.assertIsNotNone(copy3.id)

            copy_ref3 = ps.get_blob_properties(container_name, 'blob3copy')
            self.assertEqual(copy_ref3.properties.blob_tier, PremiumPageBlobTier.P10)
            self.assertTrue(copy_ref3.properties.blob_tier_inferred)
        finally:
            ps.delete_container(container_name)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
