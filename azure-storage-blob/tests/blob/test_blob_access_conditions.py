# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

pytestmark = pytest.mark.xfail

import datetime
import os
import unittest

from azure.common import AzureHttpError
from azure.core.exceptions import HttpResponseError
# from azure.storage.blob import (  # TODO
#     Blob,
#     BlobBlock,
#     PageRange,
#     ContentSettings,
# )
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    SharedKeyCredentials,
    Lease
)
from azure.storage.blob.common import BlobType
from azure.storage.blob.models import(
    ContentSettings,
    BlobProperties
)
from tests.testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
LARGE_APPEND_BLOB_SIZE = 64 * 1024
# ------------------------------------------------------------------------------


class StorageBlobAccessConditionsTest(StorageTestCase):

    def setUp(self):
        super(StorageBlobAccessConditionsTest, self).setUp()

        url = self._get_account_url()
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.config = BlobServiceClient.create_configuration()
        self.config.connection.data_block_size = 4 * 1024

        self.bsc = BlobServiceClient(url, credentials=credentials, configuration=self.config)

        #self.bs = self._create_storage_service(BlockBlobService, self.settings)
        #self.pbs = self._create_storage_service(PageBlobService, self.settings)
        #self.abs = self._create_storage_service(AppendBlobService, self.settings)
        self.container_name = self.get_resource_name('utcontainer')

    def tearDown(self):
        if not self.is_playback():
            try:
                container = self.bsc.get_container_client(self.container_name)
                container.delete_container()
            except:
                pass

        return super(StorageBlobAccessConditionsTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _create_container(self, container_name):
        container = self.bsc.get_container_client(container_name)
        container.create_container()

    def _create_container_and_block_blob(self, container_name, blob_name,
                                         blob_data):
        self._create_container(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        resp = blob.upload_blob(blob_data, length=len(blob_data))
        self.assertIsNotNone(resp.get('ETag'))

    def _create_container_and_page_blob(self, container_name, blob_name,
                                        content_length):
        self._create_container(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name, blob_type=BlobType.PageBlob)
        resp = blob.create_blob(str(content_length))

    def _create_container_and_append_blob(self, container_name, blob_name):
        self._create_container(container_name)
        resp = self.abs.create_blob(container_name, blob_name)
        return resp

    # --Test cases for blob service --------------------------------------------
    @record
    def test_set_container_metadata_with_if_modified(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = container.get_container_metadata()
        self.assertDictEqual(metadata, md)

    @record
    def test_set_container_metadata_with_if_modified_fail(self):
        # Arrange
        contianer_name = self.container_name
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            metadata = {'hello': 'world', 'number': '43'}
            container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert

    @record
    def test_set_container_acl_with_if_modified(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        container.set_container_acl(if_modified_since=test_datetime)

        # Assert
        acl = container.get_container_acl()
        self.assertIsNotNone(acl)

    @record
    def test_set_container_acl_with_if_modified_fail(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            container.set_container_acl(if_modified_since=test_datetime)

            # Assert

    @record
    def test_set_container_acl_with_if_unmodified(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        container.set_container_acl(if_unmodified_since=test_datetime)

        # Assert
        acl = container.get_container_acl()
        self.assertIsNotNone(acl)

    @record
    def test_set_container_acl_with_if_unmodified_fail(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            container.set_container_acl(if_unmodified_since=test_datetime)

            # Assert

    @record
    def test_lease_container_acquire_with_if_modified(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        container.acquire_lease(if_modified_since=test_datetime)
        container.break_lease()

        # Assert

    @record
    def test_lease_container_acquire_with_if_modified_fail(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            container.acquire_lease(if_modified_since=test_datetime)

            # Assert

    @record
    def test_lease_container_acquire_with_if_unmodified(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        container.acquire_lease(if_unmodified_since=test_datetime)
        container.break_lease()

        # Assert

    @record
    def test_lease_container_acquire_with_if_unmodified_fail(self):
        # Arrange
        container = self.bsc.get_container_client(self.container_name)
        container.create_container()
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            container.acquire_lease(if_unmodified_since=test_datetime)

            # Assert

    @record
    def test_delete_container_with_if_modified(self):
        # Arrange
        self.bs.create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        deleted = self.bs.delete_container(self.container_name,
                                           if_modified_since=test_datetime)

        # Assert
        self.assertTrue(deleted)
        exists = self.bs.exists(self.container_name)
        self.assertFalse(exists)

    @record
    def test_delete_container_with_if_modified_fail(self):
        # Arrange
        self.bs.create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.delete_container(self.container_name,
                                     if_modified_since=test_datetime)

            # Assert

    @record
    def test_delete_container_with_if_unmodified(self):
        # Arrange
        self.bs.create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        deleted = self.bs.delete_container(self.container_name,
                                           if_unmodified_since=test_datetime)

        # Assert
        self.assertTrue(deleted)
        exists = self.bs.exists(self.container_name)
        self.assertFalse(exists)

    @record
    def test_delete_container_with_if_unmodified_fail(self):
        # Arrange
        self.bs.create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.delete_container(self.container_name,
                                     if_unmodified_since=test_datetime)

    @record
    def test_put_blob_with_if_modified(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.upload_blob(data, length=len(data), if_modified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp.get('ETag'))

    @record
    def test_put_blob_with_if_modified_fail(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(data, length=len(data), if_modified_since=test_datetime)

        # Assert

    @record
    def test_put_blob_with_if_unmodified(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp.get('ETag'))

    @record
    def test_put_blob_with_if_unmodified_fail(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_put_blob_with_if_match(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        resp = blob.upload_blob(data, length=len(data), if_match=etag)

        # Assert
        self.assertIsNotNone(resp.get('ETag'))

    @record
    def test_put_blob_with_if_match_fail(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(data, length=len(data), if_match='0x111111111111111')

        # Assert

    @record
    def test_put_blob_with_if_none_match(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.upload_blob(data, length=len(data), if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(resp.get('ETag'))

    @record
    def test_put_blob_with_if_none_match_fail(self):
        # Arrange
        data = b'hello world'
        self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(data, length=len(data), if_none_match=etag)

        # Assert

    @record
    def test_get_blob_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                         if_modified_since=test_datetime)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, b'hello world')

    @record
    def test_get_blob_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                      if_modified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                         if_unmodified_since=test_datetime)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, b'hello world')

    @record
    def test_get_blob_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                      if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        etag = self.bs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1', if_match=etag)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, b'hello world')

    @record
    def test_get_blob_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                      if_match='0x111111111111111')

        # Assert

    @record
    def test_get_blob_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                         if_none_match='0x111111111111111')

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, b'hello world')

    @record
    def test_get_blob_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        etag = self.bs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, 'blob1',
                                      if_none_match=etag)

        # Assert

    @record
    def test_set_blob_properties_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_properties(content_settings, if_modified_since=test_datetime)

        # Assert
        properties = blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(HttpResponseError):
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_properties(content_settings, if_modified_since=test_datetime)

        # Assert

    @record
    def test_set_blob_properties_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_properties(content_settings, if_unmodified_since=test_datetime)

        # Assert
        properties = blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(HttpResponseError):
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_properties(content_settings, if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_set_blob_properties_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob.set_blob_properties(content_settings, if_match=etag)

        # Assert
        properties = blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(HttpResponseError):
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_properties(content_settings, if_match='0x111111111111111')

        # Assert

    @record
    def test_set_blob_properties_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_properties(content_settings, if_none_match='0x111111111111111')

        # Assert
        properties = blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob.set_blob_properties(content_settings, if_none_match=etag)

        # Assert

    @record
    def test_get_blob_properties_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.content_length, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_properties_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.content_length, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_properties_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        properties = blob.get_blob_properties(if_match=etag)

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.content_length, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_match='0x111111111111111')

        # Assert

    @record
    def test_get_blob_properties_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.content_length, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.get_blob_properties(if_none_match=etag)

        # Assert

    @record
    def test_get_blob_metadata_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_metadata(if_modified_since=test_datetime)

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_metadata(if_modified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_metadata_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_metadata(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_metadata(if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_get_blob_metadata_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        md = blob.get_blob_metadata(if_match=etag)

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_metadata(if_match='0x111111111111111')

        # Assert

    @record
    def test_get_blob_metadata_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_metadata(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.get_blob_metadata(if_none_match=etag)

        # Assert

    @record
    def test_set_blob_metadata_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = blob.get_blob_metadata()
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert

    @record
    def test_set_blob_metadata_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        md = blob.get_blob_metadata()
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_set_blob_metadata_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob.set_blob_metadata(metadata, if_match=etag)

        # Assert
        md = blob.get_blob_metadata()
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(HttpResponseError):
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, if_match='0x111111111111111')

        # Assert

    @record
    def test_set_blob_metadata_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, if_none_match='0x111111111111111')

        # Assert
        md = blob.get_blob_metadata()
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            metadata = {'hello': 'world', 'number': '42'}
            blob.set_blob_metadata(metadata, if_none_match=etag)

        # Assert

    @record
    def test_delete_blob_with_if_modified(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_modified_fail(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.delete_blob(if_modified_since=test_datetime)

        # Assert

    @record
    def test_delete_blob_with_if_unmodified(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_unmodified_fail(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_delete_blob_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        
        resp = blob.delete_blob(if_match=etag)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.delete_blob(if_match='0x111111111111111')

        # Assert

    @record
    def test_delete_blob_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.delete_blob(if_none_match=etag)

        # Assert

    @record
    def test_snapshot_blob_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

    @record
    def test_snapshot_blob_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(if_modified_since=test_datetime)

        # Assert

    @record
    def test_snapshot_blob_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

    @record
    def test_snapshot_blob_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_snapshot_blob_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        resp = blob.create_snapshot(if_match=etag)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

    @record
    def test_snapshot_blob_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(if_match='0x111111111111111')

        # Assert

    @record
    def test_snapshot_blob_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.snapshot)

    @record
    def test_snapshot_blob_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.create_snapshot(if_none_match=etag)

        # Assert

    @record
    def test_lease_blob_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            if_modified_since=test_datetime,
            lease_id=test_lease_id)

        blob.break_lease()

        # Assert
        self.assertIsInstance(lease, Lease)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(HttpResponseError):
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            blob.acquire_lease(if_modified_since=test_datetime)

        # Assert

    @record
    def test_lease_blob_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            if_unmodified_since=test_datetime,
            lease_id=test_lease_id)

        blob.break_lease()

        # Assert
        self.assertIsInstance(lease, Lease)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease(if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_lease_blob_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = blob.acquire_lease(
            lease_id=test_lease_id,
            if_match=etag)

        blob.break_lease()

        # Assert
        self.assertIsInstance(lease, Lease)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease(if_match='0x111111111111111')

        # Assert

    @record
    def test_lease_blob_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            lease_id=test_lease_id,
            if_none_match='0x111111111111111')

        blob.break_lease()

        # Assert
        self.assertIsInstance(lease, Lease)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease(if_none_match=etag)

        # Assert

    @record
    def test_put_block_list_with_if_modified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')]
        self.bs.put_block_list(self.container_name, 'blob1', block_list, if_modified_since=test_datetime)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(blob.content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.put_block_list(
                self.container_name, 'blob1', [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')],
                if_modified_since=test_datetime)

        # Assert

    @record
    def test_put_block_list_with_if_unmodified(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')]
        self.bs.put_block_list(self.container_name, 'blob1', block_list, if_unmodified_since=test_datetime)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(blob.content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.put_block_list(
                self.container_name, 'blob1', [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')],
                if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_put_block_list_with_if_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        etag = self.bs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        block_list = [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')]
        self.bs.put_block_list(self.container_name, 'blob1', block_list, if_match=etag)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(blob.content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')

        # Act
        with self.assertRaises(AzureHttpError):
            self.bs.put_block_list(
                self.container_name, 'blob1', [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')],
                if_match='0x111111111111111')

        # Assert

    @record
    def test_put_block_list_with_if_none_match(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')

        # Act
        block_list = [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')]
        self.bs.put_block_list(self.container_name, 'blob1', block_list, if_none_match='0x111111111111111')

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(blob.content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        self.bs.put_block(self.container_name, 'blob1', b'AAA', '1')
        self.bs.put_block(self.container_name, 'blob1', b'BBB', '2')
        self.bs.put_block(self.container_name, 'blob1', b'CCC', '3')
        etag = self.bs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        with self.assertRaises(AzureHttpError):
            block_list = [BlobBlock(id='1'), BlobBlock(id='2'), BlobBlock(id='3')]
            self.bs.put_block_list(self.container_name, 'blob1', block_list, if_none_match=etag)

        # Assert

    @record
    def test_update_page_with_if_modified(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511, if_modified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_modified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_unmodified(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511, if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_match(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        etag = blob.get_blob_properties().etag

        # Act
        blob.upload_page(data, 0, 511, if_match=etag)

        # Assert

    @record
    def test_update_page_with_if_match_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_match='0x111111111111111')

        # Assert

    @record
    def test_update_page_with_if_none_match(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511, if_none_match='0x111111111111111')

        # Assert

    @record
    def test_update_page_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        etag = blob.get_blob_properties().etag

        # Act
        with self.assertRaises(HttpResponseError):
            blob.upload_page(data, 0, 511, if_none_match=etag)

        # Assert

    @record
    def test_get_page_ranges_iter_with_if_modified(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511)
        blob.upload_page(data, 1024, 1535)

        # Act
        ranges = self.pbs.get_page_ranges(self.container_name, 'blob1',
                                          if_modified_since=test_datetime)
        for byte_range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    @record
    def test_get_page_ranges_iter_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511)
        blob.upload_page(data, 1024, 1535)

        # Act
        with self.assertRaises(AzureHttpError):
            self.pbs.get_page_ranges(self.container_name, 'blob1',
                                     if_modified_since=test_datetime)

        # Assert

    @record
    def test_get_page_ranges_iter_with_if_unmodified(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        blob.upload_page(data, 0, 511)
        blob.upload_page(data, 1024, 1535)

        # Act
        ranges = self.pbs.get_page_ranges(self.container_name, 'blob1',
                                          if_unmodified_since=test_datetime)
        for byte_range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    @record
    def test_get_page_ranges_iter_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        blob = self.bsc.get_blob_client(self.container_name, 'blob1', blob_type=BlobType.PageBlob)
        self.pbs.update_page(self.container_name, 'blob1', data, 0, 511)
        self.pbs.update_page(self.container_name, 'blob1', data, 1024, 1535)

        # Act
        with self.assertRaises(AzureHttpError):
            self.pbs.get_page_ranges(self.container_name, 'blob1',
                                     if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_get_page_ranges_iter_with_if_match(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        self.pbs.update_page(self.container_name, 'blob1', data, 0, 511)
        self.pbs.update_page(self.container_name, 'blob1', data, 1024, 1535)
        etag = self.pbs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        ranges = self.pbs.get_page_ranges(self.container_name, 'blob1',
                                          if_match=etag)
        for byte_range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    @record
    def test_get_page_ranges_iter_with_if_match_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        self.pbs.update_page(self.container_name, 'blob1', data, 0, 511)
        self.pbs.update_page(self.container_name, 'blob1', data, 1024, 1535)

        # Act
        with self.assertRaises(AzureHttpError):
            self.pbs.get_page_ranges(self.container_name, 'blob1',
                                     if_match='0x111111111111111')

        # Assert

    @record
    def test_get_page_ranges_iter_with_if_none_match(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        self.pbs.update_page(self.container_name, 'blob1', data, 0, 511)
        self.pbs.update_page(self.container_name, 'blob1', data, 1024, 1535)

        # Act
        ranges = self.pbs.get_page_ranges(self.container_name, 'blob1',
                                          if_none_match='0x111111111111111')
        for byte_range in ranges:
            pass

        # Assert
        self.assertEqual(len(ranges), 2)
        self.assertIsInstance(ranges[0], PageRange)
        self.assertIsInstance(ranges[1], PageRange)

    @record
    def test_get_page_ranges_iter_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        self.pbs.update_page(self.container_name, 'blob1', data, 0, 511)
        self.pbs.update_page(self.container_name, 'blob1', data, 1024, 1535)
        etag = self.pbs.get_blob_properties(self.container_name, 'blob1').properties.etag

        # Act
        with self.assertRaises(AzureHttpError):
            self.pbs.get_page_ranges(self.container_name, 'blob1',
                                     if_none_match=etag)

        # Assert

    @record
    def test_append_block_with_if_modified(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = self.abs.append_block(
                self.container_name, 'blob1',
                u'block {0}'.format(i).encode('utf-8'),
                if_modified_since=test_datetime)
            self.assertIsNotNone(resp)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(b'block 0block 1block 2block 3block 4', blob.content)

    @record
    def test_append_block_with_if_modified_fail(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            for i in range(5):
                resp = self.abs.append_block(
                    self.container_name, 'blob1',
                    u'block {0}'.format(i).encode('utf-8'),
                    if_modified_since=test_datetime)

        # Assert

    @record
    def test_append_block_with_if_unmodified(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = self.abs.append_block(
                self.container_name, 'blob1',
                u'block {0}'.format(i).encode('utf-8'),
                if_unmodified_since=test_datetime)
            self.assertIsNotNone(resp)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(b'block 0block 1block 2block 3block 4', blob.content)

    @record
    def test_append_block_with_if_unmodified_fail(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(AzureHttpError):
            for i in range(5):
                resp = self.abs.append_block(
                    self.container_name, 'blob1',
                    u'block {0}'.format(i).encode('utf-8'),
                    if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_append_block_with_if_match(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        for i in range(5):
            etag = self.abs.get_blob_properties(self.container_name, 'blob1').properties.etag
            resp = self.abs.append_block(
                self.container_name, 'blob1',
                u'block {0}'.format(i).encode('utf-8'),
                if_match=etag)
            self.assertIsNotNone(resp)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(b'block 0block 1block 2block 3block 4', blob.content)

    @record
    def test_append_block_with_if_match_fail(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        with self.assertRaises(AzureHttpError):
            for i in range(5):
                resp = self.abs.append_block(
                    self.container_name, 'blob1',
                    u'block {0}'.format(i).encode('utf-8'),
                    if_match='0x111111111111111')

        # Assert

    @record
    def test_append_block_with_if_none_match(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        for i in range(5):
            resp = self.abs.append_block(
                self.container_name, 'blob1',
                u'block {0}'.format(i).encode('utf-8'),
                if_none_match='0x8D2C9167D53FC2C')
            self.assertIsNotNone(resp)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, 'blob1')
        self.assertEqual(b'block 0block 1block 2block 3block 4', blob.content)

    @record
    def test_append_block_with_if_none_match_fail(self):
        # Arrange
        self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        with self.assertRaises(AzureHttpError):
            for i in range(5):
                etag = self.abs.get_blob_properties(self.container_name, 'blob1').properties.etag
                resp = self.abs.append_block(
                    self.container_name, 'blob1',
                    u'block {0}'.format(i).encode('utf-8'),
                    if_none_match=etag)

        # Assert
        
    @record
    def test_append_blob_from_bytes_with_if_modified(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (resp.last_modified - datetime.timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_modified_since=test_datetime)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(data, blob.content)

    @record
    def test_append_blob_from_bytes_with_if_modified_fail(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (resp.last_modified + datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_modified_since=test_datetime)

    @record
    def test_append_blob_from_bytes_with_if_unmodified(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (resp.last_modified + datetime.timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_unmodified_since=test_datetime)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(data, blob.content)

    @record
    def test_append_blob_from_bytes_with_if_unmodified_fail(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (resp.last_modified - datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(AzureHttpError):
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_unmodified_since=test_datetime)

    @record
    def test_append_blob_from_bytes_with_if_match(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = resp.get('ETag')

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_match=test_etag)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(data, blob.content)

    @record
    def test_append_blob_from_bytes_with_if_match_fail(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        with self.assertRaises(AzureHttpError):
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_match=test_etag)

    @record
    def test_append_blob_from_bytes_with_if_none_match(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_none_match=test_etag)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(data, blob.content)

    @record
    def test_append_blob_from_bytes_with_if_none_match_fail(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        resp = self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = resp.get('ETag')

        # Act
        with self.assertRaises(AzureHttpError):
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            self.abs.append_blob_from_bytes(self.container_name, blob_name, data, if_none_match=test_etag)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
