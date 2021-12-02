# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.storage.blob import (
    BlobServiceClient,
    BlobType,
    BlobBlock,
    BlobSasPermissions,
    ContainerEncryptionScope,
    generate_blob_sas,
    generate_account_sas, ResourceTypes, AccountSasPermissions, generate_container_sas, ContainerSasPermissions
)
from settings.testcase import BlobPreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------
# The encryption scope are pre-created using management plane tool ArmClient.
# So we can directly use the scope in the test.
TEST_ENCRYPTION_KEY_SCOPE = "antjoscope1"
TEST_CONTAINER_ENCRYPTION_KEY_SCOPE = ContainerEncryptionScope(
    default_encryption_scope="containerscope")
TEST_CONTAINER_ENCRYPTION_KEY_SCOPE_DENY_OVERRIDE = {
    "default_encryption_scope": "containerscope",
    "prevent_encryption_scope_override": True
}
TEST_SAS_ENCRYPTION_SCOPE = "testscope1"
TEST_SAS_ENCRYPTION_SCOPE_2 = "testscope2"

# ------------------------------------------------------------------------------

class StorageCPKNTest(StorageTestCase):
    def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        # prep some test data so that they can be used in upload tests
        self.byte_data = self.get_random_bytes(64 * 1024)

        if self.is_live:
            try:
                bsc.create_container(self.container_name)
            except:
                pass

    def _teardown(self, bsc):
        if self.is_live:
            try:
                bsc.delete_container(self.container_name)
            except:
                pass

        return super(StorageCPKNTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("cpk")

    def _create_block_blob(self, bsc, blob_name=None, data=None, encryption_scope=None, max_concurrency=1, overwrite=False):
        blob_name = blob_name if blob_name else self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        data = data if data else b''
        resp = blob_client.upload_blob(data, encryption_scope=encryption_scope, max_concurrency=max_concurrency, overwrite=overwrite)
        return blob_client, resp

    def _create_append_blob(self, bsc, encryption_scope=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        blob.create_append_blob(encryption_scope=encryption_scope)
        return blob

    def _create_page_blob(self, bsc, encryption_scope=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        blob.create_page_blob(1024 * 1024, encryption_scope=encryption_scope)
        return blob

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_put_block_and_put_block_list(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client, _ = self._create_block_blob(bsc)
        blob_client.stage_block('1', b'AAA', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)
        blob_client.stage_block('2', b'BBB', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)
        blob_client.stage_block('3', b'CCC', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = blob_client.commit_block_list(block_list,
                                                            encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), b'AAABBBCCC')
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_and_put_block_list_with_blob_sas(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)

        blob_name = self._get_blob_reference()
        token1 = generate_blob_sas(
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE,
        )
        blob_client = BlobServiceClient(self.account_url(storage_account_name, "blob"), token1)\
            .get_blob_client(self.container_name, blob_name)

        blob_client.stage_block('1', b'AAA')
        blob_client.stage_block('2', b'BBB')
        blob_client.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = blob_client.commit_block_list(block_list)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_scope'], TEST_SAS_ENCRYPTION_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), b'AAABBBCCC')
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_and_put_block_list_with_blob_sas_fails(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)

        blob_name = self._get_blob_reference()
        token1 = generate_blob_sas(
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE,
        )
        blob_client = BlobServiceClient(self.account_url(storage_account_name, "blob"), token1)\
            .get_blob_client(self.container_name, blob_name)

        # both ses in SAS and encryption_scopes are both set and have DIFFERENT values will throw exception
        with self.assertRaises(HttpResponseError):
            blob_client.stage_block('1', b'AAA', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # both ses in SAS and encryption_scopes are both set and have SAME values will succeed
        blob_client.stage_block('1', b'AAA', encryption_scope=TEST_SAS_ENCRYPTION_SCOPE)

        # Act
        block_list = [BlobBlock(block_id='1')]
        # both ses in SAS and encryption_scopes are both set and have DIFFERENT values will throw exception
        with self.assertRaises(HttpResponseError):
            blob_client.commit_block_list(block_list, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # both ses in SAS and encryption_scopes are both set and have SAME values will succeed
        put_block_list_resp = blob_client.commit_block_list(block_list, encryption_scope=TEST_SAS_ENCRYPTION_SCOPE)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_scope'], TEST_SAS_ENCRYPTION_SCOPE)

        # generate a sas with a different encryption scope
        token2 = generate_blob_sas(
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_KEY_SCOPE,
        )
        blob_client_diff_encryption_scope_sas = BlobServiceClient(self.account_url(storage_account_name, "blob"), token2)\
            .get_blob_client(self.container_name, blob_name)

        # blob can be downloaded successfully no matter which encryption scope is used on the blob actually
        # the encryption scope on blob is TEST_SAS_ENCRYPTION_SCOPE and ses is TEST_ENCRYPTION_KEY_SCOPE in SAS token,
        # while we can still download the blob successfully
        blob = blob_client_diff_encryption_scope_sas.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), b'AAA')
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_block_blob_with_chunks(self, storage_account_name, storage_account_key):
        # parallel operation
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        # Arrange
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(bsc, data=self.byte_data, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE,
                                                               max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_block_blob_with_sub_streams(self, storage_account_name, storage_account_key):
        # problem with the recording framework can only run live
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(bsc, data=self.byte_data, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE,
                                                               max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_block_blob_with_single_chunk(self, storage_account_name, storage_account_key):
        # Act
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        data = b'AAABBBCCC'
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = self._create_block_blob(bsc, data=data, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_put_block_from_url_and_commit_with_cpk(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        # create source blob and get source blob url
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        # create destination blob
        self.config.use_byte_buffer = False
        destination_blob_client, _ = self._create_block_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act part 1: make put block from url calls
        destination_blob_client.stage_block_from_url(block_id=1, source_url=source_blob_url,
                                                     source_offset=0, source_length=4 * 1024,
                                                     encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)
        destination_blob_client.stage_block_from_url(block_id=2, source_url=source_blob_url,
                                                     source_offset=4 * 1024, source_length=4 * 1024,
                                                     encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

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
                                                                        encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])

        # Act get the blob content
        blob = destination_blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data[0: 8 * 1024])
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_append_block(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client = self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        for content in [b'AAA', b'BBB', b'CCC']:
            append_blob_prop = blob_client.append_block(content, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

            # Assert
            self.assertIsNotNone(append_blob_prop['etag'])
            self.assertIsNotNone(append_blob_prop['last_modified'])
            self.assertTrue(append_blob_prop['request_server_encrypted'])

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), b'AAABBBCCC')
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_append_block_from_url(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # chunk upload
        source_blob_client, _ = self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        destination_blob_client = self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        append_blob_prop = destination_blob_client.append_block_from_url(source_blob_url,
                                                                         source_offset=0,
                                                                         source_length=4 * 1024,
                                                                         encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = destination_blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data[0: 4 * 1024])
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_append_blob_with_chunks(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client = self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        append_blob_prop = blob_client.upload_blob(self.byte_data,
                                                   blob_type=BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_update_page(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client = self._create_page_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        page_blob_prop = blob_client.upload_page(self.byte_data,
                                                 offset=0,
                                                 length=len(self.byte_data),
                                                 encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob(offset=0,
                                         length=len(self.byte_data))

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_update_page_from_url(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        blob_client = self._create_page_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        page_blob_prop = blob_client.upload_pages_from_url(source_blob_url,
                                                           offset=0,
                                                           length=len(self.byte_data),
                                                           source_offset=0,
                                                           encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob(offset=0,
                                         length=len(self.byte_data))

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_page_blob_with_chunks(self, storage_account_name, storage_account_key):
        # Act
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        page_blob_prop = blob_client.upload_blob(self.byte_data,
                                                 blob_type=BlobType.PageBlob,
                                                 max_concurrency=2,
                                                 encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act get the blob content
        blob = blob_client.download_blob()

        # Assert content was retrieved with the cpk
        self.assertEqual(blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_get_set_blob_metadata(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client, _ = self._create_block_blob(bsc, data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act
        blob_props = blob_client.get_blob_properties()

        # Assert
        self.assertTrue(blob_props.server_encrypted)
        self.assertEqual(blob_props['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        # Act set blob properties
        metadata = {'hello': 'world', 'number': '42', 'up': 'upval'}
        with self.assertRaises(HttpResponseError):
            blob_client.set_blob_metadata(
                metadata=metadata,
            )

        blob_client.set_blob_metadata(metadata=metadata, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        blob_props = blob_client.get_blob_properties()
        md = blob_props.metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['up'], 'upval')
        self.assertFalse('Up' in md)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_snapshot_blob(self, storage_account_name, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client, _ = self._create_block_blob(bsc, data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Act without cpk should not work
        with self.assertRaises(HttpResponseError):
            blob_client.create_snapshot()

        # Act with cpk should work
        blob_snapshot = blob_client.create_snapshot(encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        # Assert
        self.assertIsNotNone(blob_snapshot)
        self._teardown(bsc)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_list_blobs(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)
        blob_client, _ = self._create_block_blob(bsc, blob_name="blockblob", data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)
        self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        container_client = bsc.get_container_client(self.container_name)

        generator = container_client.list_blobs(include="metadata")
        for blob in generator:
            self.assertIsNotNone(blob)
            # Assert: every listed blob has encryption_scope
            self.assertEqual(blob.encryption_scope, TEST_ENCRYPTION_KEY_SCOPE)

        self._teardown(bsc)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_list_blobs_using_container_encryption_scope_sas(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        self._setup(bsc)

        token = generate_container_sas(
            storage_account_name,
            self.container_name,
            storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, list=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=token,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        # blob is encrypted using TEST_SAS_ENCRYPTION_SCOPE
        blob_client, _ = self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)
        self._create_append_blob(bsc_with_sas_credential)

        # generate a token with TEST_ENCRYPTION_KEY_SCOPE
        token2 = generate_container_sas(
            storage_account_name,
            self.container_name,
            storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, list=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_KEY_SCOPE
        )
        bsc_with_diff_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=token2,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = bsc_with_diff_sas_credential.get_container_client(self.container_name)

        # The ses field in SAS token when list blobs is different from the encryption scope used on creating blob, while
        # list blobs should also succeed
        generator = container_client.list_blobs(include="metadata")
        for blob in generator:
            self.assertIsNotNone(blob)
            # Assert: every listed blob has encryption_scope
            # and the encryption scope is the same as the one on blob creation
            self.assertEqual(blob.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)

        self._teardown(bsc)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_copy_with_account_encryption_scope_sas(self, storage_account_name, storage_account_key):
        # Arrange
        sas_token = generate_account_sas(
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE_2
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        self._setup(bsc_with_sas_credential)
        # blob is encrypted using TEST_SAS_ENCRYPTION_SCOPE_2
        blob_client, _ = self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)

        #
        sas_token2 = generate_account_sas(
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE
        )
        bsc_with_account_key_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token2,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        copied_blob = self.get_resource_name('copiedblob')
        copied_blob_client = bsc_with_account_key_credential.get_blob_client(self.container_name, copied_blob)

        # TODO: to confirm with Sean/Heidi ses in SAS cannot be set for async copy.
        #  The test failed for async copy (without requires_sync=True)
        copied_blob_client.start_copy_from_url(blob_client.url, requires_sync=True)

        props = copied_blob_client.get_blob_properties()

        self.assertEqual(props.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)

        self._teardown(bsc_with_sas_credential)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_copy_blob_from_url_with_ecryption_scope(self, storage_account_name, storage_account_key):
        # Arrange

        # create sas for source blob
        sas_token = generate_account_sas(
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        self._setup(bsc_with_sas_credential)
        blob_client, _ = self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        copied_blob = self.get_resource_name('copiedblob')
        copied_blob_client = bsc.get_blob_client(self.container_name, copied_blob)

        copied_blob_client.start_copy_from_url(blob_client.url, requires_sync=True,
                                               encryption_scope=TEST_SAS_ENCRYPTION_SCOPE)

        props = copied_blob_client.get_blob_properties()

        self.assertEqual(props.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)

        self._teardown(bsc_with_sas_credential)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_copy_with_user_delegation_encryption_scope_sas(self, storage_account_name, storage_account_key):
        # Arrange
        # to get user delegation key
        oauth_token_credential = self.generate_oauth_token()
        service_client = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=oauth_token_credential,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        self._setup(service_client)

        blob_name = self.get_resource_name('blob')

        sas_token = generate_blob_sas(
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=user_delegation_key,
            permission=BlobSasPermissions(read=True, write=True, create=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_SAS_ENCRYPTION_SCOPE
        )
        bsc_with_delegation_sas = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        # blob is encrypted using TEST_SAS_ENCRYPTION_SCOPE
        blob_client, _ = self._create_block_blob(bsc_with_delegation_sas, blob_name=blob_name, data=b'AAABBBCCC', overwrite=True)
        props = blob_client.get_blob_properties()

        self.assertEqual(props.encryption_scope, TEST_SAS_ENCRYPTION_SCOPE)

        self._teardown(service_client)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_container_with_default_cpk_n(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = bsc.create_container('cpkcontainer',
                                                container_encryption_scope=TEST_CONTAINER_ENCRYPTION_KEY_SCOPE)
        container_props = container_client.get_container_properties()
        self.assertEqual(
            container_props.encryption_scope.default_encryption_scope,
            TEST_CONTAINER_ENCRYPTION_KEY_SCOPE.default_encryption_scope)
        self.assertEqual(container_props.encryption_scope.prevent_encryption_scope_override, False)
        for container in bsc.list_containers(name_starts_with='cpkcontainer'):
            self.assertEqual(
                container_props.encryption_scope.default_encryption_scope,
                TEST_CONTAINER_ENCRYPTION_KEY_SCOPE.default_encryption_scope)
            self.assertEqual(container_props.encryption_scope.prevent_encryption_scope_override, False)

        blob_client = container_client.get_blob_client("appendblob")

        # providing encryption scope when upload the blob
        resp = blob_client.upload_blob(b'aaaa', BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)
        # Use the provided encryption scope on the blob
        self.assertEqual(resp['encryption_scope'], TEST_ENCRYPTION_KEY_SCOPE)

        container_client.delete_container()

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_container_with_default_cpk_n_deny_override(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            connection_data_block_size=1024,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = bsc.create_container(
            'denyoverridecpkcontainer',
            container_encryption_scope=TEST_CONTAINER_ENCRYPTION_KEY_SCOPE_DENY_OVERRIDE
        )
        container_props = container_client.get_container_properties()
        self.assertEqual(
            container_props.encryption_scope.default_encryption_scope,
            TEST_CONTAINER_ENCRYPTION_KEY_SCOPE.default_encryption_scope)
        self.assertEqual(container_props.encryption_scope.prevent_encryption_scope_override, True)
        for container in bsc.list_containers(name_starts_with='denyoverridecpkcontainer'):
            self.assertEqual(
                container_props.encryption_scope.default_encryption_scope,
                TEST_CONTAINER_ENCRYPTION_KEY_SCOPE.default_encryption_scope)
            self.assertEqual(container_props.encryption_scope.prevent_encryption_scope_override, True)

        blob_client = container_client.get_blob_client("appendblob")

        # It's not allowed to set encryption scope on the blob when the container denies encryption scope override.
        with self.assertRaises(HttpResponseError):
            blob_client.upload_blob(b'aaaa', BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_KEY_SCOPE)

        resp = blob_client.upload_blob(b'aaaa', BlobType.AppendBlob)

        self.assertEqual(resp['encryption_scope'], TEST_CONTAINER_ENCRYPTION_KEY_SCOPE.default_encryption_scope)

        container_client.delete_container()
# ------------------------------------------------------------------------------
