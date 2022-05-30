# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import uuid
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError
from azure.mgmt.storage import StorageManagementClient

from azure.storage.blob import (
    BlobClient,
    BlobImmutabilityPolicyMode,
    BlobProperties,
    BlobSasPermissions,
    BlobServiceClient,
    BlobType,
    ImmutabilityPolicy,
    PremiumPageBlobTier,
    SequenceNumberAction,
    generate_blob_sas)
from azure.storage.blob._shared.policies import StorageContentValidation
from devtools_testutils.storage import StorageTestCase
from test_helpers import ProgressTracker
from settings.testcase import BlobPreparer


#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 64 * 1024 + 512
EIGHT_TB = 8 * 1024 * 1024 * 1024 * 1024
SOURCE_BLOB_SIZE = 8 * 1024
#------------------------------------------------------------------------------s

class StoragePageBlobTest(StorageTestCase):
    #--Helpers-----------------------------------------------------------------

    def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                bsc.create_container(self.container_name)
                bsc.create_container(self.source_container_name)
            except:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    def _get_blob_reference(self, bsc):
        return bsc.get_blob_client(
            self.container_name,
            self.get_resource_name(TEST_BLOB_PREFIX))

    def _create_blob(self, bsc, length=512, sequence_number=None, tags=None):
        blob = self._get_blob_reference(bsc)
        blob.create_page_blob(size=length, sequence_number=sequence_number, tags=tags)
        return blob

    def _create_source_blob_with_special_chars(self, bs, data, offset, length):
        blob_client = bs.get_blob_client(self.source_container_name,
                                         'भारत¥test/testsubÐirÍ/'+self.get_resource_name('srcÆblob'))
        blob_client.create_page_blob(size=length)
        blob_client.upload_page(data, offset=offset, length=length)
        return blob_client

    def _create_source_blob(self, bs, data, offset, length):
        blob_client = bs.get_blob_client(self.source_container_name,
                                         self.get_resource_name(TEST_BLOB_PREFIX))
        blob_client.create_page_blob(size=length)
        blob_client.upload_page(data, offset=offset, length=length)
        return blob_client

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

    def _create_sparse_page_blob(self, bsc, size=1024*1024, data=''):
        blob_client = self._get_blob_reference(bsc)
        blob_client.create_page_blob(size=size)

        range_start = 8*1024 + 512

        # the page blob will be super sparse like this:'                         some data                      '
        blob_client.upload_page(data, offset=range_start, length=len(data))

        return blob_client

    def assertBlobEqual(self, container_name, blob_name, expected_data, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(actual_data.readall(), expected_data)

    def assertRangeEqual(self, container_name, blob_name, expected_data, offset, length, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob(offset=offset, length=length)
        self.assertEqual(actual_data.readall(), expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for page blobs --------------------------------------------
    @BlobPreparer()
    def test_create_blob(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        resp = blob.create_page_blob(1024)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertTrue(blob.get_blob_properties())

    @BlobPreparer()
    def test_create_blob_with_immutability_policy(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), credential=versioned_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = self.get_resource_name("vlwblob")
        blob = bsc.get_blob_client(container_name, blob_name)

        # Act
        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp = blob.create_page_blob(1024, immutability_policy=immutability_policy,
                                     legal_hold=True)
        props = blob.get_blob_properties()

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertTrue(props['has_legal_hold'])
        self.assertIsNotNone(props['immutability_policy']['expiry_time'])
        self.assertIsNotNone(props['immutability_policy']['policy_mode'])

        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_create_page_blob_returns_vid(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        resp = blob.create_page_blob(1024)

        # Assert
        self.assertIsNotNone(resp['version_id'])
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertTrue(blob.get_blob_properties())

    @BlobPreparer()
    def test_create_blob_with_metadata(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        resp = blob.create_page_blob(512, metadata=metadata)

        # Assert
        md = blob.get_blob_properties()
        self.assertDictEqual(md.metadata, metadata)

    @BlobPreparer()
    def test_put_page_with_lease_id(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        lease = blob.acquire_lease()

        # Act
        data = self.get_random_bytes(512)
        blob.upload_page(data, offset=0, length=512, lease=lease)

        # Assert
        content = blob.download_blob(lease=lease)
        self.assertEqual(content.readall(), data)

    @BlobPreparer()
    def test_put_page_with_lease_id_and_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        bsc = BlobServiceClient(self.account_url(blob_storage_account_name, "blob"), credential=blob_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = self._create_blob(bsc, tags=tags)
        with self.assertRaises(ResourceModifiedError):
            blob.acquire_lease(if_tags_match_condition="\"tag1\"='first tag'")
        lease = blob.acquire_lease(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Act
        data = self.get_random_bytes(512)
        with self.assertRaises(ResourceModifiedError):
            blob.upload_page(data, offset=0, length=512, lease=lease, if_tags_match_condition="\"tag1\"='first tag'")
        blob.upload_page(data, offset=0, length=512, lease=lease, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        page_ranges, cleared = blob.get_page_ranges()

        # Assert
        content = blob.download_blob(lease=lease)
        self.assertEqual(content.readall(), data)
        self.assertEqual(1, len(page_ranges))

    @BlobPreparer()
    def test_update_page(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = blob.upload_page(data, offset=0, length=512)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    def test_create_8tb_blob(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
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

    @BlobPreparer()
    def test_create_larger_than_8tb_blob_fail(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.create_page_blob(EIGHT_TB + 1)

    @BlobPreparer()
    def test_update_8tb_blob_page(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        blob.create_page_blob(EIGHT_TB)

        # Act
        data = self.get_random_bytes(512)
        start_offset = EIGHT_TB - 512
        length = 512
        resp = blob.upload_page(data, offset=start_offset, length=length)
        props = blob.get_blob_properties()
        page_ranges, cleared = blob.get_page_ranges()

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertRangeEqual(self.container_name, blob.blob_name, data, start_offset, length, bsc)
        self.assertEqual(props.size, EIGHT_TB)
        self.assertEqual(1, len(page_ranges))
        self.assertEqual(page_ranges[0]['start'], start_offset)
        self.assertEqual(page_ranges[0]['end'], start_offset + length - 1)

    @BlobPreparer()
    def test_update_page_with_md5(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = blob.upload_page(data, offset=0, length=512, validate_content=True)

        # Assert

    @BlobPreparer()
    def test_clear_page(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        resp = blob.clear_page(offset=0, length=512)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        self.assertBlobEqual(self.container_name, blob.blob_name, b'\x00' * 512, bsc)

    @BlobPreparer()
    def test_put_page_if_sequence_number_lt_success(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)

        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, offset=0, length=512, if_sequence_number_lt=start_sequence + 1)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    def test_update_page_if_sequence_number_lt_failure(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, offset=0, length=512, if_sequence_number_lt=start_sequence)

        # Assert

    @BlobPreparer()
    def test_update_page_if_sequence_number_lte_success(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, offset=0, length=512, if_sequence_number_lte=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    def test_update_page_if_sequence_number_lte_failure(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, offset=0, length=512, if_sequence_number_lte=start_sequence - 1)

        # Assert

    @BlobPreparer()
    def test_update_page_if_sequence_number_eq_success(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        blob.upload_page(data, offset=0, length=512, if_sequence_number_eq=start_sequence)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    def test_update_page_if_sequence_number_eq_failure(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, offset=0, length=512, if_sequence_number_eq=start_sequence - 1)

    @BlobPreparer()
    def test_update_page_unicode(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = u'abcdefghijklmnop' * 32
        resp = blob.upload_page(data, offset=0, length=512)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

    @BlobPreparer()
    def test_upload_pages_from_url(self, storage_account_name, storage_account_key):
        # Arrange
        account_url = self.account_url(storage_account_name, "blob")
        if not isinstance(account_url, str):
            account_url = account_url.encode('utf-8')
            storage_account_key = storage_account_key.encode('utf-8')
        bsc = BlobServiceClient(account_url, credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_blob_client_with_special_chars = self._create_source_blob_with_special_chars(
            bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)

        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        sas_token_for_blob_with_special_chars = generate_blob_sas(
            source_blob_client_with_special_chars.account_name,
            source_blob_client_with_special_chars.container_name,
            source_blob_client_with_special_chars.blob_name,
            snapshot=source_blob_client_with_special_chars.snapshot,
            account_key=source_blob_client_with_special_chars.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, offset=0, length=4 * 1024, source_offset=0)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        resp = destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, offset=4 * 1024,
            length=4 * 1024, source_offset=4 * 1024)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertEqual(blob_properties.size, SOURCE_BLOB_SIZE)
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

    # Act: make update page from url calls
        source_with_special_chars_resp = destination_blob_client.upload_pages_from_url(
            source_blob_client_with_special_chars.url + "?" + sas_token_for_blob_with_special_chars, offset=0, length=4 * 1024, source_offset=0)
        self.assertIsNotNone(source_with_special_chars_resp.get('etag'))
        self.assertIsNotNone(source_with_special_chars_resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertEqual(blob_properties.size, SOURCE_BLOB_SIZE)
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), source_with_special_chars_resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), source_with_special_chars_resp.get('last_modified'))

    @BlobPreparer()
    def test_upload_pages_from_url_with_oauth(self, storage_account_name, storage_account_key):
        # Arrange
        account_url = self.account_url(storage_account_name, "blob")
        if not isinstance(account_url, str):
            account_url = account_url.encode('utf-8')
            storage_account_key = storage_account_key.encode('utf-8')
        bsc = BlobServiceClient(account_url, credential=storage_account_key,
                                connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        token = "Bearer {}".format(self.generate_oauth_token().get_token("https://storage.azure.com/.default").token)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Assert failure without providing token
        with self.assertRaises(HttpResponseError):
            destination_blob_client.upload_pages_from_url(
                source_blob_client.url, offset=0, length=8 * 1024, source_offset=0)
        # Assert it works with oauth token
        destination_blob_client.upload_pages_from_url(
            source_blob_client.url, offset=0, length=8 * 1024, source_offset=0, source_authorization=token)
        destination_blob_data = destination_blob_client.download_blob().readall()
        self.assertEqual(source_blob_data, destination_blob_data)

    @BlobPreparer()
    def test_upload_pages_from_url_and_validate_content_md5(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        src_md5 = StorageContentValidation.get_content_md5(source_blob_data)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                             offset=0,
                                                             length=SOURCE_BLOB_SIZE,
                                                             source_offset=0,
                                                             source_content_md5=src_md5)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with wrong md5
        with self.assertRaises(HttpResponseError):
            destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                          offset=0,
                                                          length=SOURCE_BLOB_SIZE,
                                                          source_offset=0,
                                                          source_content_md5=StorageContentValidation.get_content_md5(
                                                              b"POTATO"))

    @BlobPreparer()
    def test_upload_pages_from_url_with_source_if_modified(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   source_if_modified_since=source_properties.get('last_modified') - timedelta(
                                       hours=15))
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                          offset=0,
                                                          length=SOURCE_BLOB_SIZE,
                                                          source_offset=0,
                                                          source_if_modified_since=source_properties.get(
                                                              'last_modified'))

    @BlobPreparer()
    def test_upload_pages_from_url_with_source_if_unmodified(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   source_if_unmodified_since=source_properties.get('last_modified'))
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, offset=0,
                                       length=SOURCE_BLOB_SIZE,
                                       source_offset=0,
                                       source_if_unmodified_since=source_properties.get('last_modified') - timedelta(
                                           hours=15))

    @BlobPreparer()
    def test_upload_pages_from_url_with_source_if_match(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   source_etag=source_properties.get('etag'),
                                   source_match_condition=MatchConditions.IfNotModified)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, offset=0,
                                       length=SOURCE_BLOB_SIZE,
                                       source_offset=0,
                                       source_etag='0x111111111111111',
                                       source_match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    def test_upload_pages_from_url_with_source_if_none_match(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   source_etag='0x111111111111111',
                                   source_match_condition=MatchConditions.IfModified)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, offset=0,
                                       length=SOURCE_BLOB_SIZE,
                                       source_offset=0,
                                       source_etag=source_properties.get('etag'),
                                       source_match_condition=MatchConditions.IfModified)

    @BlobPreparer()
    def test_upload_pages_from_url_with_if_modified(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   if_modified_since=source_properties.get('last_modified') - timedelta(
                                       minutes=15))
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, offset=0,
                                       length=SOURCE_BLOB_SIZE,
                                       source_offset=0,
                                       if_modified_since=blob_properties.get('last_modified'))

    @BlobPreparer()
    def test_upload_pages_from_url_with_if_unmodified(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)
        destination_blob_properties = destination_blob_client.get_blob_properties()

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   offset=0,
                                   length=SOURCE_BLOB_SIZE,
                                   source_offset=0,
                                   if_unmodified_since=destination_blob_properties.get('last_modified'))
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                       SOURCE_BLOB_SIZE,
                                       0,
                                       if_unmodified_since=source_properties.get('last_modified') - timedelta(
                                           minutes=15))

    @BlobPreparer()
    def test_upload_pages_from_url_with_if_match(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)
        destination_blob_properties = destination_blob_client.get_blob_properties()

        # Act: make update page from url calls
        resp = destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
            etag=destination_blob_properties.get('etag'),
            match_condition=MatchConditions.IfNotModified)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client.upload_pages_from_url(
                source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
                etag='0x111111111111111',
                match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    def test_upload_pages_from_url_with_if_none_match(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   0,
                                   SOURCE_BLOB_SIZE,
                                   0,
                                   etag='0x111111111111111',
                                   match_condition=MatchConditions.IfModified)

        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                       SOURCE_BLOB_SIZE,
                                       0,
                                       etag=blob_properties.get('etag'),
                                       match_condition=MatchConditions.IfModified)

    @BlobPreparer()
    def test_upload_pages_from_url_with_sequence_number_lt(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   0,
                                   SOURCE_BLOB_SIZE,
                                   0,
                                   if_sequence_number_lt=start_sequence + 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                       SOURCE_BLOB_SIZE,
                                       0,
                                       if_sequence_number_lt=start_sequence)

    @BlobPreparer()
    def test_upload_pages_from_url_with_sequence_number_lte(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   0,
                                   SOURCE_BLOB_SIZE,
                                   0,
                                   if_sequence_number_lte=start_sequence)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                       SOURCE_BLOB_SIZE,
                                       0,
                                       if_sequence_number_lte=start_sequence - 1)

    @BlobPreparer()
    def test_upload_pages_from_url_with_sequence_number_eq(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = self._create_blob(bsc, length=SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = destination_blob_client \
            .upload_pages_from_url(source_blob_client.url + "?" + sas,
                                   0,
                                   SOURCE_BLOB_SIZE,
                                   0,
                                   if_sequence_number_eq=start_sequence)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        self.assertEqual(blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client \
                .upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                       SOURCE_BLOB_SIZE,
                                       0,
                                       if_sequence_number_eq=start_sequence + 1)

    @BlobPreparer()
    def test_list_page_ranges(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClient = self._create_blob(bsc, length=2560)
        data = self.get_random_bytes(512)
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data*2, offset=1024, length=1024)

        # Act
        ranges = list(blob.list_page_ranges())

        # Assert
        self.assertIsNotNone(ranges)
        self.assertEqual(2, len(ranges))
        self.assertEqual(0, ranges[0].start)
        self.assertEqual(511, ranges[0].end)
        self.assertFalse(ranges[0].cleared)
        self.assertEqual(1024, ranges[1].start)
        self.assertEqual(2047, ranges[1].end)
        self.assertFalse(ranges[1].cleared)

    @BlobPreparer()
    def test_list_page_ranges_pagination(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClient = self._create_blob(bsc, length=3072)
        data = self.get_random_bytes(512)
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)
        blob.upload_page(data * 2, offset=2048, length=1024)

        # Act
        page_list = blob.list_page_ranges(results_per_page=2).by_page()
        first_page = next(page_list)
        items_on_page1 = list(first_page)
        second_page = next(page_list)
        items_on_page2 = list(second_page)

        # Assert
        self.assertEqual(2, len(items_on_page1))
        self.assertEqual(1, len(items_on_page2))

    @BlobPreparer()
    def test_list_page_ranges_empty(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClient = self._create_blob(bsc, length=2560)

        # Act
        ranges = list(blob.list_page_ranges())

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(0, len(ranges))

    @BlobPreparer()
    def test_list_page_ranges_offset(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClient = self._create_blob(bsc, length=2560)
        data = self.get_random_bytes(512)
        blob.upload_page(data * 3, offset=0, length=1536)
        blob.upload_page(data, offset=2048, length=512)

        # Act
        # Length with no offset, should raise ValueError
        with self.assertRaises(ValueError):
            ranges = list(blob.list_page_ranges(length=1024))

        ranges = list(blob.list_page_ranges(offset=1024, length=1024))

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(1, len(ranges))
        self.assertEqual(1024, ranges[0].start)
        self.assertEqual(1535, ranges[0].end)
        self.assertFalse(ranges[0].cleared)

    @BlobPreparer()
    def test_list_page_ranges_diff(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClient = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)
        snapshot1 = blob.create_snapshot()
        blob.upload_page(data, offset=0, length=1536)
        snapshot2 = blob.create_snapshot()
        blob.clear_page(offset=512, length=512)

        # Act
        ranges1 = list(blob.list_page_ranges(previous_snapshot=snapshot1))
        ranges2 = list(blob.list_page_ranges(previous_snapshot=snapshot2['snapshot']))

        # Assert
        self.assertIsNotNone(ranges1)
        self.assertIsInstance(ranges1, list)
        self.assertEqual(3, len(ranges1))
        self.assertEqual(0, ranges1[0].start)
        self.assertEqual(511, ranges1[0].end)
        self.assertFalse(ranges1[0].cleared)
        self.assertEqual(512, ranges1[1].start)
        self.assertEqual(1023, ranges1[1].end)
        self.assertTrue(ranges1[1].cleared)
        self.assertEqual(1024, ranges1[2].start)
        self.assertEqual(1535, ranges1[2].end)
        self.assertFalse(ranges1[2].cleared)

        self.assertIsNotNone(ranges2)
        self.assertIsInstance(ranges2, list)
        self.assertEqual(1, len(ranges2))
        self.assertEqual(512, ranges2[0].start)
        self.assertEqual(1023, ranges2[0].end)
        self.assertTrue(ranges2[0].cleared)

    @BlobPreparer()
    def test_list_page_ranges_diff_pagination(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self._setup(bsc)
        blob: BlobClinet = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)
        snapshot = blob.create_snapshot()
        blob.upload_page(data, offset=0, length=1536)
        blob.clear_page(offset=512, length=512)

        # Act
        page_list = blob.list_page_ranges(previous_snapshot=snapshot, results_per_page=2).by_page()
        first_page = next(page_list)
        items_on_page1 = list(first_page)
        second_page = next(page_list)
        items_on_page2 = list(second_page)

        # Assert
        self.assertEqual(2, len(items_on_page1))
        self.assertEqual(1, len(items_on_page2))

    @BlobPreparer()
    def test_get_page_ranges_no_pages(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        ranges, cleared = blob.get_page_ranges()

        # Assert
        self.assertIsNotNone(ranges)
        self.assertIsInstance(ranges, list)
        self.assertEqual(len(ranges), 0)

    @BlobPreparer()
    def test_get_page_ranges_2_pages(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(512)
        resp1 = blob.upload_page(data, offset=0, length=512)
        resp2 = blob.upload_page(data, offset=1024, length=512)

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

    @BlobPreparer()
    def test_get_page_ranges_diff(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)
        snapshot1 = blob.create_snapshot()
        blob.upload_page(data, offset=0, length=1536)
        snapshot2 = blob.create_snapshot()
        blob.clear_page(offset=512, length=512)

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

    @pytest.mark.playback_test_only
    @BlobPreparer()
    def test_get_page_managed_disk_diff(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)

        snapshot1 = blob.create_snapshot()
        snapshot_blob1 = BlobClient.from_blob_url(blob.url, credential=storage_account_key, snapshot=snapshot1['snapshot'])
        sas_token1 = generate_blob_sas(
            snapshot_blob1.account_name,
            snapshot_blob1.container_name,
            snapshot_blob1.blob_name,
            snapshot=snapshot_blob1.snapshot,
            account_key=snapshot_blob1.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob.upload_page(data, offset=0, length=1536)

        snapshot2 = blob.create_snapshot()
        snapshot_blob2 = BlobClient.from_blob_url(blob.url, credential=storage_account_key, snapshot=snapshot2['snapshot'])
        sas_token2 = generate_blob_sas(
            snapshot_blob2.account_name,
            snapshot_blob2.container_name,
            snapshot_blob2.blob_name,
            snapshot=snapshot_blob2.snapshot,
            account_key=snapshot_blob2.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        blob.clear_page(offset=512, length=512)

        # Act
        ranges1, cleared1 = blob.get_page_range_diff_for_managed_disk(snapshot_blob1.url + '&' + sas_token1)
        ranges2, cleared2 = blob.get_page_range_diff_for_managed_disk(snapshot_blob2.url + '&' + sas_token2)

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

    @BlobPreparer()
    def test_update_page_fail(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(512)
        resp1 = blob.upload_page(data, offset=0, length=512)

        # Act
        with self.assertRaises(ValueError):
            blob.upload_page(data, offset=1024, length=513)

        # TODO
        # self.assertEqual(str(e), 'end_range must be an integer that aligns with 512 page size')

    @BlobPreparer()
    def test_resize_blob(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc, length=1024)

        # Act
        resp = blob.resize_blob(512)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))
        self.assertIsNotNone(resp.get('blob_sequence_number'))
        props = blob.get_blob_properties()
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.size, 512)

    @BlobPreparer()
    def test_set_sequence_number_blob(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
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

    @BlobPreparer()
    def test_create_page_blob_with_no_overwrite(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data1'})

        with self.assertRaises(ResourceExistsError):
            blob.upload_blob(
                data2,
                overwrite=False,
                blob_type=BlobType.PageBlob,
                metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data1, bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'blobdata': 'data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE)
        self.assertEqual(props.blob_type, BlobType.PageBlob)

    @BlobPreparer()
    def test_create_page_blob_with_overwrite(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data1'})
        update_resp = blob.upload_blob(
            data2,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data2, bsc)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'blobdata': 'data2'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)
        self.assertEqual(props.blob_type, BlobType.PageBlob)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_bytes(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
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

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_0_bytes(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
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

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_bytes_with_progress_first(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
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

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_bytes_with_index(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 1024

        # Act
        blob.upload_blob(data[index:], blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[1024:], bsc)

    @BlobPreparer()
    def test_create_blob_from_bytes_with_index_and_count(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 512
        count = 1024

        # Act
        create_resp = blob.upload_blob(data[index:], length=count, blob_type=BlobType.PageBlob)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[index:index + count], bsc)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_path(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_path_with_progress(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path_with_progress.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'st_create_blob_from_stream.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_with_empty_pages(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        # data is almost all empty (0s) except two ranges
        blob = self._get_blob_reference(bsc)
        data = bytearray(LARGE_BLOB_SIZE)
        data[512: 1024] = self.get_random_bytes(512)
        data[8192: 8196] = self.get_random_bytes(4)
        FILE_PATH = 'create_blob_from_stream_with_empty_pages.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_non_seekable(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_stream_non_seekable.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StoragePageBlobTest.NonSeekableFile(stream)
            blob.upload_blob(
                non_seekable_file,
                length=blob_size,
                max_concurrency=1,
                blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_with_progress(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_stream_with_proge.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_truncated(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_stream_trun.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_with_progress_truncated(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = '_blob_from_stream_with_progress_trunca.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @BlobPreparer()
    def test_create_blob_with_md5_small(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)

        # Act
        blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_with_md5_large(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @pytest.mark.skip(reason="Requires further investigation. Failing for unexpected kwarg seal_blob")
    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_incremental_copy_blob(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        source_blob = self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(512)
        resp1 = source_blob.upload_page(data, offset=0, length=512)
        resp2 = source_blob.upload_page(data, offset=1024, length=512)
        source_snapshot_blob = source_blob.create_snapshot()

        snapshot_blob = BlobClient.from_blob_url(
            source_blob.url, credential=source_blob.credential, snapshot=source_snapshot_blob)
        sas_token = generate_blob_sas(
            snapshot_blob.account_name,
            snapshot_blob.container_name,
            snapshot_blob.blob_name,
            snapshot=snapshot_blob.snapshot,
            account_key=snapshot_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(snapshot_blob.url, credential=sas_token)


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

    @BlobPreparer()
    def test_blob_tier_on_create(self, premium_storage_account_name, premium_storage_account_key):
        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
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
                blob_type=BlobType.PageBlob,
                overwrite=True)

            props2 = pblob2.get_blob_properties()
            self.assertEqual(props2.blob_tier, PremiumPageBlobTier.P6)
            self.assertFalse(props2.blob_tier_inferred)

            # test create_blob_from_path API
            blob3 = self._get_blob_reference(bsc)
            pblob3 = pbs.get_blob_client(container_name, blob3.blob_name)
            FILE_PATH = '_blob_tier_on_create.temp.{}.dat'.format(str(uuid.uuid4()))
            with open(FILE_PATH, 'wb') as stream:
                stream.write(byte_data)
            with open(FILE_PATH, 'rb') as stream:
                pblob3.upload_blob(
                    stream,
                    blob_type=BlobType.PageBlob,
                    premium_page_blob_tier=PremiumPageBlobTier.P10,
                    overwrite=True)

            props3 = pblob3.get_blob_properties()
            self.assertEqual(props3.blob_tier, PremiumPageBlobTier.P10)
            self.assertFalse(props3.blob_tier_inferred)

        finally:
            container.delete_container()
        self._teardown(FILE_PATH)

    @BlobPreparer()
    def test_blob_tier_set_tier_api(self, premium_storage_account_name, premium_storage_account_key):
        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
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

    # TODO: check with service to see if premium blob supports tags
    # @GlobalResourceGroupPreparer()
    # @BlobPreparer(
    # def test_blob_tier_set_tier_api_with_if_tags(self, premium_storage_account_name, premium_storage_account_key):
    #     bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
    #     self._setup(bsc)
    #     url = self.account_url(storage_account_name, "blob")
    #     credential = storage_account_key
    #     pbs = BlobServiceClient(url, credential=credential)
    #     tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
    #
    #     try:
    #         container_name = self.get_resource_name('utpremiumcontainer')
    #         container = pbs.get_container_client(container_name)
    #
    #         if self.is_live:
    #             try:
    #                 container.create_container()
    #             except:
    #                 pass
    #
    #         blob = self._get_blob_reference(bsc)
    #         pblob = pbs.get_blob_client(container_name, blob.blob_name)
    #         # pblob.create_page_blob(1024, tags=tags)
    #         blob_ref = pblob.get_blob_properties()
    #         self.assertEqual(PremiumPageBlobTier.P10, blob_ref.blob_tier)
    #         self.assertIsNotNone(blob_ref.blob_tier)
    #         self.assertTrue(blob_ref.blob_tier_inferred)
    #
    #         pcontainer = pbs.get_container_client(container_name)
    #         blobs = list(pcontainer.list_blobs())
    #
    #         # Assert
    #         self.assertIsNotNone(blobs)
    #         self.assertGreaterEqual(len(blobs), 1)
    #         self.assertIsNotNone(blobs[0])
    #         self.assertNamedItemInContainer(blobs, blob.blob_name)
    #         with self.assertRaises(ResourceModifiedError):
    #             pblob.set_premium_page_blob_tier(PremiumPageBlobTier.P50, if_tags_match_condition="\"tag1\"='firsttag WRONG'")
    #         pblob.set_premium_page_blob_tier(PremiumPageBlobTier.P50, if_tags_match_condition="\"tag1\"='firsttag'")
    #
    #         blob_ref2 = pblob.get_blob_properties()
    #         self.assertEqual(PremiumPageBlobTier.P50, blob_ref2.blob_tier)
    #         self.assertFalse(blob_ref2.blob_tier_inferred)
    #
    #         blobs = list(pcontainer.list_blobs())
    #
    #         # Assert
    #         self.assertIsNotNone(blobs)
    #         self.assertGreaterEqual(len(blobs), 1)
    #         self.assertIsNotNone(blobs[0])
    #         self.assertNamedItemInContainer(blobs, blob.blob_name)
    #         self.assertEqual(blobs[0].blob_tier, PremiumPageBlobTier.P50)
    #         self.assertFalse(blobs[0].blob_tier_inferred)
    #     finally:
    #         container.delete_container()

    @BlobPreparer()
    @pytest.mark.playback_test_only
    def test_blob_tier_copy_blob(self, premium_storage_account_name, premium_storage_account_key):
        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
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
                self.account_url(premium_storage_account_name, "blob"), container_name, source_blob.blob_name)

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
                self.account_url(premium_storage_account_name, "blob"), source_blob2.container_name, source_blob2.blob_name)

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

    @BlobPreparer()
    def test_download_sparse_page_blob_non_parallel(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        self.config.max_single_get_size = 4*1024
        self.config.max_chunk_get_size = 1024

        sparse_page_blob_size = 1024 * 1024
        data = self.get_random_bytes(2048)
        blob_client = self._create_sparse_page_blob(bsc, size=sparse_page_blob_size, data=data)

        # Act
        page_ranges, cleared = blob_client.get_page_ranges()
        start = page_ranges[0]['start']
        end = page_ranges[0]['end']

        content = blob_client.download_blob().readall()

        # Assert
        self.assertEqual(sparse_page_blob_size, len(content))
        # make sure downloaded data is the same as the uploaded data
        self.assertEqual(data, content[start: end + 1])
        # assert all unlisted ranges are empty
        for byte in content[:start-1]:
            try:
                self.assertEqual(byte, '\x00')
            except:
                self.assertEqual(byte, 0)
        for byte in content[end+1:]:
            try:
                self.assertEqual(byte, '\x00')
            except:
                self.assertEqual(byte, 0)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_download_sparse_page_blob_parallel(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        self._setup(bsc)
        self.config.max_single_get_size = 4 * 1024
        self.config.max_chunk_get_size = 1024

        sparse_page_blob_size = 1024 * 1024
        data = self.get_random_bytes(2048)
        blob_client = self._create_sparse_page_blob(bsc, size=sparse_page_blob_size, data=data)

        # Act
        page_ranges, cleared = blob_client.get_page_ranges()
        start = page_ranges[0]['start']
        end = page_ranges[0]['end']

        content = blob_client.download_blob(max_concurrency=3).readall()

    @BlobPreparer()
    def test_upload_progress_chunked_non_parallel(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        self._setup(bsc)

        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_page_size=1024)

        blob_client.upload_blob(
            data,
            blob_type=BlobType.PageBlob,
            overwrite=True,
            max_concurrency=1,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_upload_progress_chunked_parallel(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        self._setup(bsc)

        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_page_size=1024)

        blob_client.upload_blob(
            data,
            blob_type=BlobType.PageBlob,
            overwrite=True,
            max_concurrency=3,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()
