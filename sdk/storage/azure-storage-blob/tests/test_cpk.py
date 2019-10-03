# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.storage.blob import (
    BlobServiceClient,
    BlobType,
    BlobBlock,
)
from azure.storage.blob.models import CustomerProvidedEncryptionKey, BlobPermissions
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                    key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")


# ------------------------------------------------------------------------------

class StorageCPKTest(StorageTestCase):
    def setUp(self):
        super(StorageCPKTest, self).setUp()

        url = self._get_account_url()

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            url,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        # prep some test data so that they can be used in upload tests
        self.byte_data = self.get_random_bytes(64 * 1024)

        if not self.is_playback():
            self.bsc.create_container(self.container_name)

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bsc.delete_container(self.container_name)
            except:
                pass

        return super(StorageCPKTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("cpk")

    def _create_block_blob(self, blob_name=None, data=None, cpk=None, max_concurrency=1):
        blob_name = blob_name if blob_name else self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        data = data if data else b''
        resp = blob_client.upload_blob(data, cpk=cpk, max_concurrency=max_concurrency)
        return blob_client, resp

    def _create_append_blob(self, cpk=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name)
        blob.create_append_blob(cpk=cpk)
        return blob

    def _create_page_blob(self, cpk=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name)
        blob.create_page_blob(1024 * 1024, cpk=cpk)
        return blob

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @record
    def test_put_block_and_put_block_list(self):
        # Arrange
        blob_client, _ = self._create_block_blob()
        blob_client.stage_block('1', b'AAA', cpk=TEST_ENCRYPTION_KEY)
        blob_client.stage_block('2', b'BBB', cpk=TEST_ENCRYPTION_KEY)
        blob_client.stage_block('3', b'CCC', cpk=TEST_ENCRYPTION_KEY)

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = blob_client.commit_block_list(block_list,
                                                            cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), b'AAABBBCCC')
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    def test_create_block_blob_with_chunks(self):
        # parallel operation
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(data=self.byte_data, cpk=TEST_ENCRYPTION_KEY,
                                                               max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    def test_create_block_blob_with_sub_streams(self):
        # problem with the recording framework can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(data=self.byte_data, cpk=TEST_ENCRYPTION_KEY,
                                                               max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_create_block_blob_with_single_chunk(self):
        # Act
        data = b'AAABBBCCC'
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(data=data, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_put_block_from_url_and_commit(self):
        # Arrange
        # create source blob and get source blob url
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = self._create_block_blob(blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        # create destination blob
        self.config.use_byte_buffer = False
        destination_blob_client, _ = self._create_block_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act part 1: make put block from url calls
        destination_blob_client.stage_block_from_url(block_id=1, source_url=source_blob_url,
                                                     source_offset=0, source_length=4 * 1024,
                                                     cpk=TEST_ENCRYPTION_KEY)
        destination_blob_client.stage_block_from_url(block_id=2, source_url=source_blob_url,
                                                     source_offset=4 * 1024, source_length=4 * 1024,
                                                     cpk=TEST_ENCRYPTION_KEY)

        # Assert blocks
        committed, uncommitted = destination_blob_client.get_block_list('all')
        self.assertEqual(len(uncommitted), 2)
        self.assertEqual(len(committed), 0)

        # commit the blocks without cpk should fail
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2')]
        with self.assertRaises(HttpResponseError):
            destination_blob_client.commit_block_list(block_list)

        # Act commit the blocks with cpk should succeed
        put_block_list_resp = destination_blob_client.commit_block_list(block_list,
                                                                        cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content
        blob = destination_blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data[0: 8 * 1024])
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_append_block(self):
        # Arrange
        blob_client = self._create_append_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act
        for content in [b'AAA', b'BBB', b'CCC']:
            append_blob_prop = blob_client.append_block(content, cpk=TEST_ENCRYPTION_KEY)

            # Assert
            self.assertIsNotNone(append_blob_prop['etag'])
            self.assertIsNotNone(append_blob_prop['last_modified'])
            self.assertTrue(append_blob_prop['request_server_encrypted'])
            self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), b'AAABBBCCC')
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_append_block_from_url(self):
        # Arrange
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # chunk upload
        source_blob_client, _ = self._create_block_blob(blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        destination_blob_client = self._create_append_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act
        append_blob_prop = destination_blob_client.append_block_from_url(source_blob_url,
                                                                         source_offset=0,
                                                                         source_length=4 * 1024,
                                                                         cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        # TODO: verify that the swagger is correct, header wasn't added for the response
        # self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            destination_blob_client.download_blob()

            # Act get the blob content
        blob = destination_blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data[0: 4 * 1024])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_create_append_blob_with_chunks(self):
        # Arrange
        blob_client = self._create_append_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act
        append_blob_prop = blob_client.upload_blob(self.byte_data,
                                                   blob_type=BlobType.AppendBlob, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_update_page(self):
        # Arrange
        blob_client = self._create_page_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act
        page_blob_prop = blob_client.upload_page(self.byte_data,
                                                 offset=0,
                                                 length=len(self.byte_data),
                                                 cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(offset=0,
                                         length=len(self.byte_data),
                                         cpk=TEST_ENCRYPTION_KEY, )

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @record
    def test_update_page_from_url(self):
        # Arrange
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = self._create_block_blob(blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        blob_client = self._create_page_blob(cpk=TEST_ENCRYPTION_KEY)

        # Act
        page_blob_prop = blob_client.upload_pages_from_url(source_blob_url,
                                                           offset=0,
                                                           length=len(self.byte_data),
                                                           source_offset=0,
                                                           cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        # TODO: FIX SWAGGER
        # self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(offset=0,
                                         length=len(self.byte_data),
                                         cpk=TEST_ENCRYPTION_KEY, )

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    def test_create_page_blob_with_chunks(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Act
        blob_client = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        page_blob_prop = blob_client.upload_blob(self.byte_data,
                                                 blob_type=BlobType.PageBlob,
                                                 max_concurrency=2,
                                                 cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            blob_client.download_blob()

        # Act get the blob content
        blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.content_as_bytes(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    # TODO: verify why clear page works without providing cpk
    # @record
    # def test_clear_page(self):
    #     # Arrange
    #     blob_client = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
    #     data = self.get_random_bytes(1024)
    #     blob_client.upload_blob(data, blob_type=BlobType.PageBlob, cpk=TEST_ENCRYPTION_KEY)
    #
    #     # Act
    #     blob = blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)
    #     self.assertEquals(blob.content_as_bytes(), data)
    #
    #     # with self.assertRaises(HttpResponseError):
    #     #     blob_client.clear_page(0, 511)
    #
    #     resp = blob_client.clear_page(0, 511, cpk=TEST_ENCRYPTION_KEY)
    #     blob = blob_client.download_blob(0, 511, cpk=TEST_ENCRYPTION_KEY)
    #
    #     # Assert
    #     self.assertIsNotNone(resp.get('etag'))
    #     self.assertIsNotNone(resp.get('last_modified'))
    #     self.assertIsNotNone(resp.get('blob_sequence_number'))
    #     self.assertEquals(blob.content_as_bytes(), b'\x00' * 512)
    #
    #     blob = blob_client.download_blob(512, 1023, cpk=TEST_ENCRYPTION_KEY)
    #     self.assertEquals(blob.content_as_bytes(), data[512:])

    @record
    def test_get_set_blob_metadata(self):
        # Arrange
        blob_client, _ = self._create_block_blob(data=b'AAABBBCCC', cpk=TEST_ENCRYPTION_KEY)

        # Act without the encryption key should fail
        with self.assertRaises(HttpResponseError):
            blob_client.get_blob_properties()

        # Act
        blob_props = blob_client.get_blob_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertTrue(blob_props.server_encrypted)
        self.assertEqual(blob_props.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

        # Act set blob properties
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        with self.assertRaises(HttpResponseError):
            blob_client.set_blob_metadata(
                metadata=metadata,
            )

        blob_client.set_blob_metadata(metadata=metadata, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        blob_props = blob_client.get_blob_properties(cpk=TEST_ENCRYPTION_KEY)
        md = blob_props.metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @record
    def test_snapshot_blob(self):
        # Arrange
        blob_client, _ = self._create_block_blob(data=b'AAABBBCCC', cpk=TEST_ENCRYPTION_KEY)

        # Act without cpk should not work
        with self.assertRaises(HttpResponseError):
            blob_client.create_snapshot()

        # Act with cpk should work
        blob_snapshot = blob_client.create_snapshot(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(blob_snapshot)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
