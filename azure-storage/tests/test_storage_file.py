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
import unittest

from azure.common import (
    AzureHttpError,
    AzureConflictHttpError,
    AzureMissingResourceHttpError,
)
from azure.storage import (
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY
)
from azure.storage.file import (
    FILE_SERVICE_HOST_BASE,
    FileService,
    FileResult,
    FileService,
    RangeList,
    Range,
)
from azure.storage.storageclient import (
    AZURE_STORAGE_ACCESS_KEY,
    AZURE_STORAGE_ACCOUNT,
    EMULATED,
)
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.storage_testcase import StorageTestCase


#------------------------------------------------------------------------------


class StorageFileTest(StorageTestCase):

    def setUp(self):
        super(StorageFileTest, self).setUp()

        self.fs = self._create_storage_service(FileService, self.settings)

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.fs._FILE_MAX_DATA_SIZE = 64 * 1024
        self.fs._FILE_MAX_CHUNK_DATA_SIZE = 4 * 1024

        self.share_name = self.get_resource_name('utshare')
        self.additional_share_names = []

    def tearDown(self):
        if not self.is_playback():
            try:
                self.fs.delete_share(self.share_name)
            except:
                pass

            for name in self.additional_share_names:
                try:
                    self.fs.delete_share(name)
                except:
                    pass

        for tmp_file in ['file_input.temp.dat', 'file_output.temp.dat']:
            if os.path.isfile(tmp_file):
                try:
                    os.remove(tmp_file)
                except:
                    pass

        return super(StorageFileTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_share_and_file(self, share_name, file_name,
                                        content_length):
        self.fs.create_share(self.share_name)
        resp = self.fs.create_file(self.share_name, None, file_name, content_length)
        self.assertIsNone(resp)

    def _create_share_and_file_with_text(self, share_name, file_name,
                                        text):
        self.fs.create_share(self.share_name)
        resp = self.fs.put_file_from_text(self.share_name, None, file_name, text)
        self.assertIsNone(resp)

    def _file_exists(self, share_name, file_name):
        resp = self.fs.list_directories_and_files(share_name)
        for file in resp:
            if file.name == file_name:
                return True
        return False

    def assertFileEqual(self, share_name, file_name, expected_data):
        actual_data = self.fs.get_file(share_name, None, file_name)
        self.assertEqual(actual_data, expected_data)

    def assertFileLengthEqual(self, share_name, file_name, expected_length):
        props = self.fs.get_file_properties(share_name, None, file_name)
        self.assertEqual(int(props['content-length']), expected_length)

    def _get_oversized_binary_data(self):
        '''Returns random binary data exceeding the size threshold for
        chunking file upload.'''
        size = self.fs._FILE_MAX_DATA_SIZE + 12345
        return self._get_random_bytes(size)

    def _get_expected_progress(self, file_size, unknown_size=False):
        result = []
        index = 0
        total = None if unknown_size else file_size
        while (index < file_size):
            result.append((index, total))
            index += self.fs._FILE_MAX_CHUNK_DATA_SIZE
        result.append((file_size, total))
        return result

    def _get_random_bytes(self, size):
        # Must not be really random, otherwise playback of recordings
        # won't work. Data must be randomized, but the same for each run.
        # Use the checksum of the qualified test name as the random seed.
        rand = random.Random(self.checksum)
        result = bytearray(size)
        for i in range(size):
            result[i] = rand.randint(0, 255)
        return bytes(result)

    def _get_oversized_file_binary_data(self):
        '''Returns random binary data exceeding the size threshold for
        chunking file upload.'''
        size = self.fs._FILE_MAX_DATA_SIZE + 16384
        return self._get_random_bytes(size)

    def _get_oversized_text_data(self):
        '''Returns random unicode text data exceeding the size threshold for
        chunking file upload.'''
        # Must not be really random, otherwise playback of recordings
        # won't work. Data must be randomized, but the same for each run.
        # Use the checksum of the qualified test name as the random seed.
        rand = random.Random(self.checksum)
        size = self.fs._FILE_MAX_DATA_SIZE + 12345
        text = u''
        words = [u'hello', u'world', u'python', u'啊齄丂狛狜']
        while (len(text) < size):
            index = rand.randint(0, len(words) - 1)
            text = text + u' ' + words[index]

        return text

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for file service --------------------------------------------
    @record
    def test_create_file_service_missing_arguments(self):
        # Arrange
        if AZURE_STORAGE_ACCOUNT in os.environ:
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if AZURE_STORAGE_ACCESS_KEY in os.environ:
            del os.environ[AZURE_STORAGE_ACCESS_KEY]
        if EMULATED in os.environ:
            del os.environ[EMULATED]

        # Act
        with self.assertRaises(ValueError):
            fs = FileService()

        # Assert

    @record
    def test_create_file_service_env_variables(self):
        # Arrange
        os.environ[
            AZURE_STORAGE_ACCOUNT] = self.settings.STORAGE_ACCOUNT_NAME
        os.environ[
            AZURE_STORAGE_ACCESS_KEY] = self.settings.STORAGE_ACCOUNT_KEY

        # Act
        fs = FileService()

        if AZURE_STORAGE_ACCOUNT in os.environ:
            del os.environ[AZURE_STORAGE_ACCOUNT]
        if AZURE_STORAGE_ACCESS_KEY in os.environ:
            del os.environ[AZURE_STORAGE_ACCESS_KEY]

        # Assert
        self.assertIsNotNone(fs)
        self.assertEqual(fs.account_name, self.settings.STORAGE_ACCOUNT_NAME)
        self.assertEqual(fs.account_key, self.settings.STORAGE_ACCOUNT_KEY)
        self.assertEqual(fs.is_emulated, False)

    @record
    def test_create_file_service_connection_string(self):
        # Arrange
        connection_string = 'DefaultEndpointsProtocol={};AccountName={};AccountKey={}'.format(
                            'http', self.settings.STORAGE_ACCOUNT_NAME,
                            self.settings.STORAGE_ACCOUNT_KEY)
        
        # Act
        fs = FileService(connection_string = connection_string)
        
        # Assert
        self.assertIsNotNone(fs)
        self.assertEqual(fs.account_name, self.settings.STORAGE_ACCOUNT_NAME)
        self.assertEqual(fs.account_key, self.settings.STORAGE_ACCOUNT_KEY)
        self.assertEqual(fs.protocol, 'http')
        self.assertEqual(fs.host_base, FILE_SERVICE_HOST_BASE)
        self.assertFalse(fs.is_emulated)
        
    #--Test cases for shares -----------------------------------------
    @record
    def test_create_share(self):
        # Arrange

        # Act
        created = self.fs.create_share(self.share_name)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_share_fail_on_exist(self):
        # Arrange

        # Act
        created = self.fs.create_share(self.share_name)
        with self.assertRaises(AzureConflictHttpError):
            self.fs.create_share(self.share_name, None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_share_with_already_existing_share(self):
        # Arrange

        # Act
        created1 = self.fs.create_share(self.share_name)
        created2 = self.fs.create_share(self.share_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_share_with_metadata(self):
        # Arrange

        # Act
        created = self.fs.create_share(
            self.share_name, {'hello': 'world', 'number': '42'})

        # Assert
        self.assertTrue(created)
        md = self.fs.get_share_metadata(self.share_name)
        self.assertIsNotNone(md)
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    @record
    def test_list_shares_no_options(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        shares = self.fs.list_shares()
        for share in shares:
            name = share.name

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, self.share_name)

    @record
    def test_list_shares_with_prefix(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        shares = self.fs.list_shares(self.share_name)

        # Assert
        self.assertIsNotNone(shares)
        self.assertEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertEqual(shares[0].name, self.share_name)
        self.assertIsNone(shares[0].metadata)

    @record
    def test_list_shares_with_include_metadata(self):
        # Arrange
        self.fs.create_share(self.share_name)
        resp = self.fs.set_share_metadata(
            self.share_name, {'hello': 'world', 'number': '43'})

        # Act
        shares = self.fs.list_shares(
            self.share_name, None, None, 'metadata')

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, self.share_name)
        self.assertEqual(shares[0].metadata['hello'], 'world')
        self.assertEqual(shares[0].metadata['number'], '43')

    @record
    def test_list_shares_with_maxresults_and_marker(self):
        # Arrange
        self.additional_share_names = [self.share_name + 'a',
                                           self.share_name + 'b',
                                           self.share_name + 'c',
                                           self.share_name + 'd']
        for name in self.additional_share_names:
            self.fs.create_share(name)

        # Act
        shares1 = self.fs.list_shares(self.share_name, None, 2)
        shares2 = self.fs.list_shares(
            self.share_name, shares1.next_marker, 2)

        # Assert
        self.assertIsNotNone(shares1)
        self.assertEqual(len(shares1), 2)
        self.assertNamedItemInContainer(shares1, self.share_name + 'a')
        self.assertNamedItemInContainer(shares1, self.share_name + 'b')
        self.assertIsNotNone(shares2)
        self.assertEqual(len(shares2), 2)
        self.assertNamedItemInContainer(shares2, self.share_name + 'c')
        self.assertNamedItemInContainer(shares2, self.share_name + 'd')

    @record
    def test_set_share_metadata(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        resp = self.fs.set_share_metadata(
            self.share_name, {'hello': 'world', 'number': '43'})

        # Assert
        self.assertIsNone(resp)
        md = self.fs.get_share_metadata(self.share_name)
        self.assertIsNotNone(md)
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '43')

    @record
    def test_set_share_metadata_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.set_share_metadata(
                self.share_name, {'hello': 'world', 'number': '43'})

        # Assert

    @record
    def test_get_share_metadata(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.set_share_metadata(
            self.share_name, {'hello': 'world', 'number': '42'})

        # Act
        md = self.fs.get_share_metadata(self.share_name)

        # Assert
        self.assertIsNotNone(md)
        self.assertEqual(2, len(md))
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    @record
    def test_get_share_metadata_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_share_metadata(self.share_name)

        # Assert

    @record
    def test_get_share_properties(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.set_share_metadata(
            self.share_name, {'hello': 'world', 'number': '42'})

        # Act
        props = self.fs.get_share_properties(self.share_name)

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['x-ms-meta-hello'], 'world')
        self.assertEqual(props['x-ms-meta-number'], '42')

    @record
    def test_get_share_properties_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_share_properties(self.share_name)

        # Assert

    @record
    def test_delete_share_with_existing_share(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        deleted = self.fs.delete_share(self.share_name)

        # Assert
        self.assertTrue(deleted)
        shares = self.fs.list_shares()
        self.assertNamedItemNotInContainer(shares, self.share_name)

    @record
    def test_delete_share_with_existing_share_fail_not_exist(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        deleted = self.fs.delete_share(self.share_name)

        # Assert
        self.assertTrue(deleted)
        shares = self.fs.list_shares()
        self.assertNamedItemNotInContainer(shares, self.share_name)

    @record
    def test_delete_share_with_non_existing_share(self):
        # Arrange

        # Act
        deleted = self.fs.delete_share(self.share_name, False)

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_share_with_non_existing_share_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.delete_share(self.share_name, True)

        # Assert

    #--Test cases for directories ----------------------------------------------
    @record
    def test_create_directories(self):
        # Arrange

        # Act
        self.fs.create_share(self.share_name)
        created = self.fs.create_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directories_fail_on_exist(self):
        # Arrange

        # Act
        created = self.fs.create_share(self.share_name)
        created = self.fs.create_directory(self.share_name, 'dir1')
        with self.assertRaises(AzureConflictHttpError):
            self.fs.create_directory(self.share_name, 'dir1', True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_already_existing_directory(self):
        # Arrange

        # Act
        created = self.fs.create_share(self.share_name)
        created1 = self.fs.create_directory(self.share_name, 'dir1')
        created2 = self.fs.create_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_get_directory_properties(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        props = self.fs.get_directory_properties(self.share_name, 'dir1')

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props['ETag'])
        self.assertIsNotNone(props['Last-Modified'])

    @record
    def test_get_directory_properties_with_non_existing_directory(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

        # Assert

    @record
    def test_delete_directory_with_existing_share(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        deleted = self.fs.delete_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(deleted)
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

    @record
    def test_delete_directory_with_existing_directory_fail_not_exist(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        deleted = self.fs.delete_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(deleted)
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

    @record
    def test_delete_directory_with_non_existing_directory(self):
        # Arrange

        # Act
        deleted = self.fs.delete_directory(self.share_name, 'dir1', False)

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_directory_with_non_existing_directory_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.delete_directory(self.share_name, 'dir1', True)

        # Assert

    @record
    def test_list_directories_and_files(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')
        self.fs.create_directory(self.share_name, 'dir2')
        self.fs.create_file(self.share_name, None, 'file1', 1024)
        self.fs.create_file(self.share_name, 'dir1', 'file2', 1025)

        # Act
        resp = self.fs.list_directories_and_files(self.share_name)
        for file in resp.files:
            name = file.name

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp.files), 1)
        self.assertEqual(len(resp.directories), 2)
        self.assertIsNotNone(resp.files[0])
        self.assertNamedItemInContainer(resp.directories, 'dir1')
        self.assertNamedItemInContainer(resp.directories, 'dir2')
        self.assertNamedItemInContainer(resp.files, 'file1')
        self.assertEqual(resp.files[0].properties.content_length, 1024)

    @record
    def test_list_directories_and_files_with_maxresults(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')
        self.fs.create_file(self.share_name, None, 'filea1', 1024)
        self.fs.create_file(self.share_name, None, 'filea2', 1024)
        self.fs.create_file(self.share_name, None, 'filea3', 1024)
        self.fs.create_file(self.share_name, None, 'fileb1', 1024)

        # Act
        result = self.fs.list_directories_and_files(self.share_name, None, None, 2)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result.files), 1)
        self.assertEqual(len(result.directories), 1)
        self.assertEqual(result.max_results, 2)
        self.assertNamedItemInContainer(result.directories, 'dir1')
        self.assertNamedItemInContainer(result.files, 'filea1')
        self.assertIsNotNone(result.next_marker)

    @record
    def test_list_directories_and_files_with_maxresults_and_marker(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')
        self.fs.create_file(self.share_name, 'dir1', 'filea1', 1024)
        self.fs.create_file(self.share_name, 'dir1', 'filea2', 1024)
        self.fs.create_file(self.share_name, 'dir1', 'filea3', 1024)
        self.fs.create_file(self.share_name, 'dir1', 'fileb1', 1024)

        # Act
        result1 = self.fs.list_directories_and_files(self.share_name, 'dir1', None, 2)
        result2 = self.fs.list_directories_and_files(
            self.share_name, 'dir1', result1.next_marker, 2)

        # Assert
        self.assertEqual(len(result1.files), 2)
        self.assertEqual(len(result2.files), 2)
        self.assertNamedItemInContainer(result1.files, 'filea1')
        self.assertNamedItemInContainer(result1.files, 'filea2')
        self.assertNamedItemInContainer(result2.files, 'filea3')
        self.assertNamedItemInContainer(result2.files, 'fileb1')
        self.assertEqual(result2.next_marker, '')

    #--Test cases for files ----------------------------------------------
    @record
    def test_make_file_url(self):
        # Arrange

        # Act
        res = self.fs.make_file_url('vhds', 'vhd_dir', 'my.vhd')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @record
    def test_make_file_url_no_directory(self):
        # Arrange

        # Act
        res = self.fs.make_file_url('vhds', None, 'my.vhd')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.file.core.windows.net/vhds/my.vhd')

    @record
    def test_make_file_url_with_account_name(self):
        # Arrange

        # Act
        res = self.fs.make_file_url('vhds', 'vhd_dir', 'my.vhd', account_name='myaccount')

        # Assert
        self.assertEqual(
            res, 'https://myaccount.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @record
    def test_make_file_url_with_protocol(self):
        # Arrange

        # Act
        res = self.fs.make_file_url('vhds', 'vhd_dir', 'my.vhd', protocol='http')

        # Assert
        self.assertEqual(res, 'http://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @record
    def test_make_file_url_with_host_base(self):
        # Arrange

        # Act
        res = self.fs.make_file_url(
            'vhds', None, 'my.vhd', host_base='.file.internal.net')

        # Assert
        self.assertEqual(res, 'https://' + self.settings.STORAGE_ACCOUNT_NAME
                         + '.file.internal.net/vhds/my.vhd')

    @record
    def test_make_file_url_with_all(self):
        # Arrange

        # Act
        res = self.fs.make_file_url(
            'vhds', 'vhd_dir', 'my.vhd', account_name='myaccount', protocol='http',
            host_base='.file.internal.net')

        # Assert
        self.assertEqual(res, 'http://myaccount.file.internal.net/vhds/vhd_dir/my.vhd')

    @record
    def test_create_file(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        resp = self.fs.create_file(self.share_name, None, 'file1', 1024)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_create_file_with_metadata(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        resp = self.fs.create_file(
            self.share_name, None, 'file1', 1024,
            x_ms_meta_name_values={'hello': 'world', 'number': '42'})

        # Assert
        self.assertIsNone(resp)
        md = self.fs.get_file_metadata(self.share_name, None, 'file1')
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')

    @record
    def test_get_file_with_existing_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        file = self.fs.get_file(self.share_name, None, 'file1')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, b'hello world')

    @record
    def test_get_file_with_range(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        file = self.fs.get_file(
            self.share_name, None, 'file1', x_ms_range='bytes=0-5')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, b'hello ')

    @record
    def test_get_file_with_range_and_get_content_md5(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        file = self.fs.get_file(self.share_name, None, 'file1',
                                x_ms_range='bytes=0-5',
                                x_ms_range_get_content_md5='true')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, b'hello ')
        self.assertEqual(
            file.properties['content-md5'], '+BSJN3e8wilf/wXwDlCNpg==')

    @record
    def test_get_file_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_file(self.share_name, None, 'file1')

        # Assert

    @record
    def test_get_file_with_non_existing_file(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_file(self.share_name, None, 'file1')

        # Assert
        
    @record
    def test_resize_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        resp = self.fs.resize_file(self.share_name, None, 
            'file1', 5)

        # Assert
        self.assertIsNone(resp)
        props = self.fs.get_file_properties(self.share_name, None, 'file1')
        self.assertEqual(props['content-length'], '5')

    @record
    def test_set_file_properties(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        resp = self.fs.set_file_properties(
            self.share_name,
            None, 
            'file1',
            x_ms_content_language='spanish',
            x_ms_content_disposition='inline',
        )

        # Assert
        self.assertIsNone(resp)
        props = self.fs.get_file_properties(self.share_name, None, 'file1')
        self.assertEqual(props['content-language'], 'spanish')
        self.assertEqual(props['content-disposition'], 'inline')

    @record
    def test_set_file_properties_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.set_file_properties(
                self.share_name, None, 'file1',
                x_ms_content_language='spanish')

        # Assert

    @record
    def test_set_file_properties_with_non_existing_file(self):
        # Arrange
        self.fs.create_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.set_file_properties(
                self.share_name, 'dir1', 'file1',
                x_ms_content_language='spanish')

        # Assert

    @record
    def test_get_file_properties_with_existing_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        props = self.fs.get_file_properties(self.share_name, None, 
                                            'file1')

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props['content-length'], '11')

    @record
    def test_get_file_properties_with_non_existing_share(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_file_properties(self.share_name, None, 'file1')

        # Assert

    @record
    def test_get_file_properties_with_non_existing_file(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_file_properties(self.share_name, None, 'file1')

        # Assert

    @record
    def test_get_file_metadata_with_existing_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        md = self.fs.get_file_metadata(self.share_name, None, 'file1')

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_set_file_metadata_with_existing_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        resp = self.fs.set_file_metadata(
            self.share_name,
            None, 
            'file1',
            {'hello': 'world', 'number': '42', 'UP': 'UPval'})

        # Assert
        self.assertIsNone(resp)
        md = self.fs.get_file_metadata(self.share_name, None, 'file1')
        self.assertEqual(3, len(md))
        self.assertEqual(md['x-ms-meta-hello'], 'world')
        self.assertEqual(md['x-ms-meta-number'], '42')
        self.assertEqual(md['x-ms-meta-up'], 'UPval')

    @record
    def test_delete_file_with_existing_file(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, 'file1', b'hello world')

        # Act
        resp = self.fs.delete_file(self.share_name, None, 'file1')

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_file_with_non_existing_file(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.delete_file (self.share_name, None, 'file1')

        # Assert

    @record
    def test_update_file(self):
        # Arrange
        self._create_share_and_file(
            self.share_name, 'file1', 1024)

        # Act
        data = b'abcdefghijklmnop' * 32
        resp = self.fs.update_range(
            self.share_name, None, 'file1', 
            data, 'bytes=0-511')

        # Assert
        self.assertIsNone(resp)

    @record
    def test_clear_file(self):
        # Arrange
        self._create_share_and_file(
            self.share_name, 'file1', 1024)

        # Act
        resp = self.fs.clear_range(
            self.share_name, None, 'file1', 'bytes=0-511')

        # Assert
        self.assertIsNone(resp)

    @record
    def test_update_file_unicode(self):
        # Arrange
        self._create_share_and_file(self.share_name, 'file1', 512)

        # Act
        data = u'abcdefghijklmnop' * 32
        with self.assertRaises(TypeError):
            self.fs.update_range(self.share_name, None, 'file1',
                             data, 'bytes=0-511')

        # Assert

    @record
    def test_list_ranges_none(self):
        # Arrange
        self._create_share_and_file(
            self.share_name, 'file1', 1024)

        # Act
        ranges = self.fs.list_ranges(self.share_name, None, 'file1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, RangeList)
        self.assertEqual(len(ranges.file_ranges), 0)

    @record
    def test_list_ranges_2(self):
        # Arrange
        self._create_share_and_file(
            self.share_name, 'file1', 2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = self.fs.update_range(
            self.share_name, None, 'file1', data, 'bytes=0-511')
        resp2 = self.fs.update_range(
            self.share_name, None, 'file1', data, 'bytes=1024-1535')

        # Act
        ranges = self.fs.list_ranges(self.share_name, None, 'file1')

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, RangeList)
        self.assertEqual(len(ranges.file_ranges), 2)
        self.assertEqual(ranges.file_ranges[0].start, 0)
        self.assertEqual(ranges.file_ranges[0].end, 511)
        self.assertEqual(ranges.file_ranges[1].start, 1024)
        self.assertEqual(ranges.file_ranges[1].end, 1535)

    @record
    def test_list_ranges_iter(self):
        # Arrange
        self._create_share_and_file(
            self.share_name, 'file1', 2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = self.fs.update_range(
            self.share_name, None, 'file1', data,
            'bytes=0-511')
        resp2 = self.fs.update_range(
            self.share_name, None, 'file1', data,
            'bytes=1024-1535')

        # Act
        ranges = self.fs.list_ranges(self.share_name, None, 'file1')
        for range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], Range)
        self.assertIsInstance(ranges[1], Range)

    @record
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

            self.assertIsInstance(response.body, (bytes, type(None)))
            self.assertIsInstance(response.headers, list)
            for header in response.headers:
                self.assertIsInstance(header, tuple)
                for item in header:
                    self.assertIsInstance(item, strtype)
            self.assertIsInstance(response.status, int)
            return response

        bc = self.fs.with_filter(my_filter)
        bc.create_share(self.share_name + '0', None, False)

        self.assertTrue(called)

        del called[:]

        bc.delete_share(self.share_name + '0')

        self.assertTrue(called)
        del called[:]

        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)

        def filter_b(request, next):
            called.append('b')
            return next(request)

        bc = self.fs.with_filter(filter_a).with_filter(filter_b)
        bc.create_share(self.share_name + '1', None, False)

        self.assertEqual(called, ['b', 'a'])

        bc.delete_share(self.share_name + '1')

        self.assertEqual(called, ['b', 'a', 'b', 'a'])

    @record
    def test_unicode_create_share_unicode_name(self):
        # Arrange
        self.share_name = self.share_name + u'啊齄丂狛狜'

        # Act
        with self.assertRaises(AzureHttpError):
            # not supported - share name must be alphanumeric, lowercase
            self.fs.create_share(self.share_name)

        # Assert

    @record
    def test_unicode_get_file_unicode_name(self):
        # Arrange
        self._create_share_and_file_with_text(
            self.share_name, '啊齄丂狛狜', b'hello world')

        # Act
        file = self.fs.get_file(self.share_name, None, '啊齄丂狛狜')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, b'hello world')

    @record
    def test_put_file_block_file_unicode_data(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        resp = self.fs.create_file(
            self.share_name, None, 'file1', 1024)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_unicode_get_file_unicode_data(self):
        # Arrange
        file_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        self._create_share_and_file_with_text(
            self.share_name, 'file1', file_data)

        # Act
        file = self.fs.get_file(self.share_name, None, 'file1')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, file_data)

    @record
    def test_unicode_get_file_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        self._create_share_and_file_with_text(
            self.share_name, 'file1', binary_data)

        # Act
        file = self.fs.get_file(self.share_name, None, 'file1')

        # Assert
        self.assertIsInstance(file, FileResult)
        self.assertEqual(file, binary_data)

    @record
    def test_get_file_to_bytes(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_bytes(self.share_name, None, file_name)

        # Assert
        self.assertEqual(data, resp)

    @record
    def test_get_file_to_bytes_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_bytes(self.share_name, None, file_name)

        # Assert
        self.assertEqual(data, resp)

    def test_get_file_to_bytes_chunked_download_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_bytes(self.share_name, None, file_name,
                                         max_connections=10)

        # Assert
        self.assertEqual(data, resp)

    @record
    def test_get_file_to_bytes_with_progress(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_bytes(
            self.share_name, None, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(data, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_bytes_with_progress_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_bytes(
            self.share_name, None, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(data, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_stream(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_get_file_to_stream_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_file_to_stream_chunked_download_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_get_file_to_stream_non_seekable_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            non_seekable_stream = StorageFileTest.NonSeekableFile(stream)
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, non_seekable_stream,
                max_connections=1)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_file_to_stream_non_seekable_chunked_download_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        with open(file_path, 'wb') as stream:
            non_seekable_stream = StorageFileTest.NonSeekableFile(stream)

            # Parallel downloads require that the file be seekable
            with self.assertRaises(AttributeError):
                resp = self.fs.get_file_to_stream(
                    self.share_name, None, file_name, non_seekable_stream,
                    max_connections=10)

        # Assert

    @record
    def test_get_file_to_stream_with_progress(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_stream_with_progress_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_get_file_to_stream_with_progress_chunked_download_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(file_path, 'wb') as stream:
            resp = self.fs.get_file_to_stream(
                self.share_name, None, file_name, stream,
                progress_callback=callback,
                max_connections=5)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, sorted(progress))
        self.assertGreater(len(progress), 0)

    @record
    def test_get_file_to_path(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_get_file_to_path_chunked_downlad(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    def test_get_file_to_path_chunked_downlad_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_get_file_to_path_with_progress(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_path_with_progress_chunked_downlad(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_path_with_mode(self):
        # Arrange
        file_name = 'file1'
        data = b'abcdefghijklmnopqrstuvwxyz'
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)
        with open(file_path, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path, 'a+b')

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + data, actual)

    @record
    def test_get_file_to_path_with_mode_chunked_download(self):
        # Arrange
        file_name = 'file1'
        data = self._get_oversized_binary_data()
        file_path = 'file_output.temp.dat'
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)
        with open(file_path, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        resp = self.fs.get_file_to_path(
            self.share_name, None, file_name, file_path, 'a+b')

        # Assert
        self.assertIsNone(resp)
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + data, actual)

    @record
    def test_get_file_to_text(self):
        # Arrange
        file_name = 'file1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_text(self.share_name, None, file_name)

        # Assert
        self.assertEqual(text, resp)

    @record
    def test_get_file_to_text_with_encoding(self):
        # Arrange
        file_name = 'file1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_text(
            self.share_name, None, file_name, 'utf-16')

        # Assert
        self.assertEqual(text, resp)

    @record
    def test_get_file_to_text_chunked_download(self):
        # Arrange
        file_name = 'file1'
        text = self._get_oversized_text_data()
        data = text.encode('utf-8')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_text(self.share_name, None, file_name)

        # Assert
        self.assertEqual(text, resp)

    def test_get_file_to_text_chunked_download_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        file_name = 'file1'
        text = self._get_oversized_text_data()
        data = text.encode('utf-8')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        resp = self.fs.get_file_to_text(self.share_name, None, file_name,
                                        max_connections=10)

        # Assert
        self.assertEqual(text, resp)

    @record
    def test_get_file_to_text_with_progress(self):
        # Arrange
        file_name = 'file1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_text(
            self.share_name, None, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(text, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_get_file_to_text_with_encoding_and_progress(self):
        # Arrange
        file_name = 'file1'
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        self._create_share_and_file_with_text(
            self.share_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.get_file_to_text(
            self.share_name, None, file_name, 'utf-16',
            progress_callback=callback)

        # Assert
        self.assertEqual(text, resp)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_put_file_from_bytes(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        data = self._get_random_bytes(2048)
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, 'file1', data)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.fs.get_file(self.share_name, None, 'file1'))

    @record
    def test_put_file_from_bytes_with_progress(self):
        # Arrange
        self.fs.create_share(self.share_name)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        data = self._get_random_bytes(2048)
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, 'file1', data, progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data, self.fs.get_file(self.share_name, None, 'file1'))
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_put_file_from_bytes_with_index(self):
        # Arrange
        self.fs.create_share(self.share_name)
        index = 1024

        # Act
        data = self._get_random_bytes(2048)
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, 'file1', data, index)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data[index:],
                         self.fs.get_file(self.share_name, None, 'file1'))

    @record
    def test_put_file_from_bytes_with_index_and_count(self):
        # Arrange
        self.fs.create_share(self.share_name)
        index = 512
        count = 1024

        # Act
        data = self._get_random_bytes(2048)
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, 'file1', data, index, count)

        # Assert
        self.assertIsNone(resp)
        self.assertEqual(data[index:index + count],
                         self.fs.get_file(self.share_name, None, 'file1'))

    @record
    def test_put_file_from_bytes_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()

        # Act
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, file_name, data)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, len(data))
        self.assertFileEqual(self.share_name, file_name, data)

    def test_put_file_from_bytes_chunked_upload_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()

        # Act
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, file_name, data,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, len(data))
        self.assertFileEqual(self.share_name, file_name, data)

    @record
    def test_put_file_from_bytes_chunked_upload_with_index_and_count(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        index = 512
        count = len(data) - 1024

        # Act
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, file_name, data, index, count)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, count)
        self.assertFileEqual(self.share_name,
                             file_name, data[index:index + count])

    def test_put_file_from_bytes_chunked_upload_with_index_and_count_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        index = 512
        count = len(data) - 1024

        # Act
        resp = self.fs.put_file_from_bytes(
            self.share_name, None, file_name, data, index, count,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, count)
        self.assertFileEqual(self.share_name,
                             file_name, data[index:index + count])

    @record
    def test_put_file_from_path_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.fs.put_file_from_path(
            self.share_name, None, file_name, file_path)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, len(data))
        self.assertFileEqual(self.share_name, file_name, data)

    def test_put_file_from_path_chunked_upload_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        resp = self.fs.put_file_from_path(
            self.share_name, None, file_name, file_path,
            max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, len(data))
        self.assertFileEqual(self.share_name, file_name, data)

    @record
    def test_put_file_from_path_with_progress_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        resp = self.fs.put_file_from_path(
            self.share_name, None, file_name, file_path,
            progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, len(data))
        self.assertFileEqual(self.share_name, file_name, data)
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    @record
    def test_put_file_from_stream_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])

    def test_put_file_from_stream_chunked_upload_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])

    @record
    def test_put_file_from_stream_non_seekable_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data)
        with open(file_path, 'rb') as stream:
            non_seekable_file = StorageFileTest.NonSeekableFile(stream)
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, non_seekable_file, file_size,
                max_connections=1)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])

    def test_put_file_from_stream_non_seekable_chunked_upload_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data)
        with open(file_path, 'rb') as stream:
            non_seekable_file = StorageFileTest.NonSeekableFile(stream)

            # Parallel uploads require that the file be seekable
            with self.assertRaises(AttributeError):
                resp = self.fs.put_file_from_stream(
                    self.share_name, None, file_name, non_seekable_file, 
                    file_size, max_connections=10)

        # Assert

    @record
    def test_put_file_from_stream_with_progress_chunked_upload(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        file_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])
        self.assertEqual(progress, self._get_expected_progress(len(data)))

    def test_put_file_from_stream_with_progress_chunked_upload_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        file_size = len(data)
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size,
                progress_callback=callback,
                max_connections=5)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])
        self.assertEqual(progress, sorted(progress))
        self.assertGreater(len(progress), 0)

    @record
    def test_put_file_from_stream_chunked_upload_truncated(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])

    def test_put_file_from_stream_chunked_upload_truncated_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recordingfile(self.test_mode):
            return

        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        file_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size,
                max_connections=10)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])

    @record
    def test_put_file_from_stream_with_progress_chunked_upload_truncated(self):
        # Arrange
        self.fs.create_share(self.share_name)
        file_name = 'file1'
        data = self._get_oversized_file_binary_data()
        file_path = 'file_input.temp.dat'
        with open(file_path, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        file_size = len(data) - 512
        with open(file_path, 'rb') as stream:
            resp = self.fs.put_file_from_stream(
                self.share_name, None, file_name, stream, file_size,
                progress_callback=callback)

        # Assert
        self.assertIsNone(resp)
        self.assertFileLengthEqual(self.share_name, file_name, file_size)
        self.assertFileEqual(self.share_name, file_name, data[:file_size])
        self.assertEqual(progress, self._get_expected_progress(file_size))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
