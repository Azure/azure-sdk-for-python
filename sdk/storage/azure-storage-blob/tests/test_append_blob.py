# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from os import (
    path,
    remove,
)
import unittest
import uuid
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError, ResourceModifiedError, HttpResponseError
from azure.storage.blob import (
    generate_blob_sas,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    BlobSasPermissions)
from azure.storage.blob._shared.policies import StorageContentValidation

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer, StorageAccountPreparer, \
    GlobalResourceGroupPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 64 * 1024


# ------------------------------------------------------------------------------

class StorageAppendBlobTest(StorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                bsc.create_container(self.container_name)
            except:
                pass
            try:
                bsc.create_container(self.source_container_name)
            except:
                pass

    def _teardown(self, file_name):
        if path.isfile(file_name):
            try:
                remove(file_name)
            except:
                pass

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    def _create_blob(self, bsc, tags=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        blob.create_append_blob(tags=tags)
        return blob

    def _create_source_blob(self, data, bsc):
        blob_client = bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        blob_client.create_append_blob()
        blob_client.append_block(data)
        return blob_client

    def assertBlobEqual(self, blob, expected_data):
        stream = blob.download_blob()
        actual_data = stream.readall()
        self.assertEqual(actual_data, expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # --Test cases for block blobs --------------------------------------------

    @GlobalStorageAccountPreparer()
    def test_create_blob(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob = bsc.get_blob_client(self.container_name, blob_name)
        create_resp = blob.create_append_blob()

        # Assert
        blob_properties = blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_using_vid(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob_name = self._get_blob_reference()

        # Act
        blob = bsc.get_blob_client(self.container_name, blob_name)
        create_resp = blob.create_append_blob()
        # create operation will return a version id
        self.assertIsNotNone(create_resp['version_id'])

        # Assert
        blob_properties = blob.get_blob_properties(version_id=create_resp['version_id'])
        self.assertIsNotNone(blob_properties)
        self.assertTrue(blob_properties.is_current_version)
        self.assertIsNotNone(blob_properties.version_id)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        lease = blob.acquire_lease()
        create_resp = blob.create_append_blob(lease=lease)

        # Assert
        blob_properties = blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        metadata = {'hello': 'world', 'number': '42'}
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(self.container_name, blob_name)

        # Act
        blob.create_append_blob(metadata=metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    def test_append_block(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        for i in range(5):
            resp = blob.append_block(u'block {0}'.format(i).encode('utf-8'))
            self.assertEqual(int(resp['blob_append_offset']), 7 * i)
            self.assertEqual(resp['blob_committed_block_count'], i + 1)
            self.assertIsNotNone(resp['etag'])
            self.assertIsNotNone(resp['last_modified'])

        # Assert
        self.assertBlobEqual(blob, b'block 0block 1block 2block 3block 4')

    @GlobalStorageAccountPreparer()
    def test_append_block_unicode(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        resp = blob.append_block(u'啊齄丂狛狜', encoding='utf-16')

        # Assert
        self.assertEqual(int(resp['blob_append_offset']), 0)
        self.assertEqual(resp['blob_committed_block_count'], 1)
        self.assertIsNotNone(resp['etag'])
        self.assertIsNotNone(resp['last_modified'])

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_append_block_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key,
                                max_block_size=4 * 1024)
        self._setup(bsc)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = self._create_blob(bsc, tags=tags)
        with self.assertRaises(ResourceModifiedError):
            blob.append_block(u'啊齄丂狛狜', encoding='utf-16', if_tags_match_condition="\"tag1\"='first tag'")
        resp = blob.append_block(u'啊齄丂狛狜', encoding='utf-16', if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        self.assertEqual(int(resp['blob_append_offset']), 0)
        self.assertEqual(resp['blob_committed_block_count'], 1)
        self.assertIsNotNone(resp['etag'])
        self.assertIsNotNone(resp['last_modified'])

    @GlobalStorageAccountPreparer()
    def test_append_block_with_md5(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        resp = blob.append_block(b'block', validate_content=True)
        self.assertEqual(int(resp['blob_append_offset']), 0)
        self.assertEqual(resp['blob_committed_block_count'], 1)
        self.assertIsNotNone(resp['etag'])
        self.assertIsNotNone(resp['last_modified'])

        # Assert

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_append_block_from_url(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act: make append block from url calls
        split = 4 * 1024
        resp = destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                             source_offset=0, source_length=split)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        destination_blob_client.set_blob_tags(tags=tags)
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=split,
                                                          source_length=LARGE_BLOB_SIZE - split,
                                                          if_tags_match_condition="\"tag1\"='first tag'")
        resp = destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                             source_offset=split,
                                                             source_length=LARGE_BLOB_SIZE - split,
                                                             if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")
        self.assertEqual(resp.get('blob_append_offset'), str(4 * 1024))
        self.assertEqual(resp.get('blob_committed_block_count'), 2)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Missing start range shouldn't pass the validation
        with self.assertRaises(ValueError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_length=LARGE_BLOB_SIZE)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_and_validate_content_md5(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        src_md5 = StorageContentValidation.get_content_md5(source_blob_data)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls with correct md5
        resp = destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                             source_content_md5=src_md5)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with wrong md5
        with self.assertRaises(HttpResponseError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_content_md5=StorageContentValidation.get_content_md5(
                                                              b"POTATO"))

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_source_if_modified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_blob_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                             source_offset=0,
                                                             source_length=LARGE_BLOB_SIZE,
                                                             source_if_modified_since=source_blob_properties.get(
                                                                 'last_modified') - timedelta(hours=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          source_if_modified_since=source_blob_properties.get(
                                                              'last_modified'))

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_source_if_unmodified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_blob_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                             source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                             source_if_unmodified_since=source_blob_properties.get(
                                                                 'last_modified'))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client \
                .append_block_from_url(source_blob_client.url + '?' + sas,
                                       source_offset=0, source_length=LARGE_BLOB_SIZE,
                                       if_unmodified_since=source_blob_properties.get('last_modified') - timedelta(
                                           hours=15))

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_source_if_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_blob_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  source_etag=source_blob_properties.get('etag'),
                                  source_match_condition=MatchConditions.IfNotModified)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          source_etag='0x111111111111111',
                                                          source_match_condition=MatchConditions.IfNotModified)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_source_if_none_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_blob_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  source_etag='0x111111111111111',
                                  source_match_condition=MatchConditions.IfModified)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          source_etag=source_blob_properties.get('etag'),
                                                          source_match_condition=MatchConditions.IfModified)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_if_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_name = self._get_blob_reference()
        destination_blob_client = bsc.get_blob_client(
            self.container_name,
            destination_blob_name)
        destination_blob_properties_on_creation = destination_blob_client.create_append_blob()

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  etag=destination_blob_properties_on_creation.get('etag'),
                                  match_condition=MatchConditions.IfNotModified)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          etag='0x111111111111111',
                                                          match_condition=MatchConditions.IfNotModified)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_if_none_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  etag='0x111111111111111', match_condition=MatchConditions.IfModified)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          etag=destination_blob_properties.get('etag'),
                                                          match_condition=MatchConditions.IfModified)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_maxsize_condition(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  maxsize_condition=LARGE_BLOB_SIZE + 1)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          maxsize_condition=LARGE_BLOB_SIZE + 1)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_appendpos_condition(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  appendpos_condition=0)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          appendpos_condition=0)

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_if_modified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_properties = source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_modified_since=source_properties.get('last_modified') - timedelta(minutes=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          if_modified_since=destination_blob_properties.get(
                                                              'last_modified'))

    @GlobalStorageAccountPreparer()
    def test_append_block_from_url_with_if_unmodified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(source_blob_data, bsc)
        source_properties = source_blob_client.append_block(source_blob_data)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = self._create_blob(bsc)

        # Act part 1: make append block from url calls
        resp = destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_unmodified_since=source_properties.get('last_modified') + timedelta(minutes=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                          source_offset=0, source_length=LARGE_BLOB_SIZE,
                                                          if_unmodified_since=source_properties.get(
                                                              'last_modified') - timedelta(minutes=15))

    @GlobalStorageAccountPreparer()
    def test_create_append_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'blobdata': 'Data1'})

        update_resp = blob.upload_blob(
            data2,
            overwrite=False,
            blob_type=BlobType.AppendBlob,
            metadata={'blobdata': 'Data2'})

        props = blob.get_blob_properties()

        # Assert
        appended_data = data1 + data2
        self.assertBlobEqual(blob, appended_data)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.blob_type, BlobType.AppendBlob)
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'blobdata': 'Data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + LARGE_BLOB_SIZE + 512)

    @GlobalStorageAccountPreparer()
    def test_create_append_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'blobdata': 'Data1'})
        update_resp = blob.upload_blob(
            data2,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'blobdata': 'Data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'blobdata': 'Data2'})
        self.assertEqual(props.blob_type, BlobType.AppendBlob)
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        append_resp = blob.upload_blob(data, blob_type=BlobType.AppendBlob)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['etag'])
        self.assertEqual(blob_properties.last_modified, append_resp['last_modified'])

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_0_bytes(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = b''
        append_resp = blob.upload_blob(data, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)
        # appending nothing should not make any network call
        self.assertIsNone(append_resp.get('etag'))
        self.assertIsNone(append_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_with_progress(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = b'abcdefghijklmnopqrstuvwxyz'

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(upload)))
            yield upload

        upload_data = progress_gen(data)
        blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_with_index(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        blob.upload_blob(data[3:], blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data[3:])

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_with_index_and_count(self, resource_group, location, storage_account,
                                                         storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        blob.upload_blob(data[3:], length=5, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data[3:8])

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_chunked_upload(self, resource_group, location, storage_account,
                                                   storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        append_resp = blob.upload_blob(data, blob_type=BlobType.AppendBlob)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['etag'])
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_with_progress_chunked_upload(self, resource_group, location, storage_account,
                                                                 storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.max_block_size
            total = len(upload)
            current = 0
            while upload:
                progress.append((current, total))
                yield upload[:n]
                current += len(upload[:n])
                upload = upload[n:]

        upload_data = progress_gen(data)
        blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_bytes_chunked_upload_with_index_and_count(self, resource_group, location, storage_account,
                                                                        storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 33
        blob_size = len(data) - 66

        # Act
        blob.upload_blob(data[index:], length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data[index:index + blob_size])

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_path_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'from_path_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream, blob_type=BlobType.AppendBlob)

        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_path_with_progress_chunked_upload(self, resource_group, location, storage_account,
                                                                storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'progress_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.max_block_size
            total = LARGE_BLOB_SIZE
            current = 0
            while upload:
                chunk = upload.read(n)
                if not chunk:
                    break
                progress.append((current, total))
                yield chunk
                current += len(chunk)

        with open(FILE_PATH, 'rb') as stream:
            upload_data = progress_gen(stream)
            blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_stream_chunked_upload(self, resource_group, location, storage_account,
                                                    storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream, blob_type=BlobType.AppendBlob)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_app_blob_from_stream_nonseekable_chnked_upload_known_size(self, resource_group, location,
                                                                            storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'upload_known_size.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_size = len(data) - 66

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file, length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_app_blob_from_stream_nonseekable_chnked_upload_unk_size(self, resource_group, location,
                                                                              storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'upload_unk_size.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_stream_with_multiple_appends(self, resource_group, location, storage_account,
                                                           storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'multiple_appends.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream1:
            stream1.write(data)
        with open(FILE_PATH, 'wb') as stream2:
            stream2.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream1:
            blob.upload_blob(stream1, blob_type=BlobType.AppendBlob)
        with open(FILE_PATH, 'rb') as stream2:
            blob.upload_blob(stream2, blob_type=BlobType.AppendBlob)

        # Assert
        data = data * 2
        self.assertBlobEqual(blob, data)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_stream_chunked_upload_with_count(self, resource_group, location, storage_account,
                                                               storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'upload_with_count.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_append_blob_from_stream_chunked_upload_with_count_parallel(self, resource_group, location, storage_account,
                                                                        storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'upload_with_count_parallel.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream, length=blob_size, blob_type=BlobType.AppendBlob)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_text(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        append_resp = blob.upload_blob(text, blob_type=BlobType.AppendBlob)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_text_with_encoding(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        blob.upload_blob(text, encoding='utf-16', blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, data)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_text_with_encoding_and_progress(self, resource_group, location, storage_account,
                                                              storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(data)))
            yield upload

        upload_data = progress_gen(text)
        blob.upload_blob(upload_data, encoding='utf-16', blob_type=BlobType.AppendBlob)

        # Assert
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @GlobalStorageAccountPreparer()
    def test_append_blob_from_text_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        blob.upload_blob(data, blob_type=BlobType.AppendBlob)

        # Assert
        self.assertBlobEqual(blob, encoded_data)

    @GlobalStorageAccountPreparer()
    def test_append_blob_with_md5(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        data = b'hello world'

        # Act
        blob.append_block(data, validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_seal_append_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        resp = blob.seal_append_blob()
        self.assertTrue(resp['blob_sealed'])

        with self.assertRaises(HttpResponseError):
            blob.append_block("abc")

        blob.set_blob_metadata({'isseal': 'yes'})
        prop = blob.get_blob_properties()

        self.assertEqual(prop.metadata['isseal'], 'yes')

    @GlobalStorageAccountPreparer()
    def test_seal_append_blob_with_append_condition(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)
        with self.assertRaises(HttpResponseError):
            blob.seal_append_blob(appendpos_condition=1)

        resp = blob.seal_append_blob(appendpos_condition=0)
        self.assertTrue(resp['blob_sealed'])

    @GlobalStorageAccountPreparer()
    def test_copy_sealed_blob_will_get_a_sealed_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # copy sealed blob will get a sealed blob
        blob.seal_append_blob()
        copied_blob = bsc.get_blob_client(self.container_name, "copiedblob")
        copied_blob.start_copy_from_url(blob.url)
        prop = copied_blob.get_blob_properties()

        self.assertTrue(prop.is_append_blob_sealed)
        with self.assertRaises(HttpResponseError):
            copied_blob.append_block("abc")

    @GlobalStorageAccountPreparer()
    def test_copy_unsealed_blob_will_get_a_sealed_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # copy unsealed blob with seal_destination_blob=True will get a sealed blob
        copied_blob2 = bsc.get_blob_client(self.container_name, "copiedblob2")
        copied_blob2.start_copy_from_url(blob.url, seal_destination_blob=True)
        prop = copied_blob2.get_blob_properties()

        self.assertTrue(prop.is_append_blob_sealed)
        with self.assertRaises(HttpResponseError):
            copied_blob2.append_block("abc")

        blobs_gen = bsc.get_container_client(self.container_name).list_blobs()
        for blob in blobs_gen:
            if blob.name == "copiedblob2":
                self.assertTrue(blob.is_append_blob_sealed)

    @GlobalStorageAccountPreparer()
    def test_copy_sealed_blob_with_seal_blob_will_get_a_sealed_blob(self, resource_group, location, storage_account, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), storage_account_key, max_block_size=4 * 1024)
        self._setup(bsc)
        blob = self._create_blob(bsc)

        # copy sealed blob with seal_destination_blob=False will get a unsealed blob
        blob.seal_append_blob()
        copied_blob3 = bsc.get_blob_client(self.container_name, "copiedblob3")
        copied_blob3.start_copy_from_url(blob.url, seal_destination_blob=False)
        prop = copied_blob3.get_blob_properties()

        self.assertIsNone(prop.is_append_blob_sealed)
        copied_blob3.append_block("abc")
# ------------------------------------------------------------------------------
