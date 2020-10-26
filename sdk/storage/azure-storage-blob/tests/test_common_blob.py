# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
import pytest
import requests
import time
import uuid
import os
import sys
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError, ResourceModifiedError)
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import (
    upload_blob_to_url,
    download_blob_from_url,
    generate_account_sas,
    generate_blob_sas,
    generate_container_sas,
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    BlobSasPermissions,
    ContainerSasPermissions,
    ContentSettings,
    BlobProperties,
    RetentionPolicy,
    AccessPolicy,
    ResourceTypes,
    AccountSasPermissions,
    StandardBlobTier,
)
from azure.storage.blob._generated.models import RehydratePriority
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer, GlobalResourceGroupPreparer

# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'

# ------------------------------------------------------------------------------
class StorageCommonBlobTest(StorageTestCase):
    def _setup(self, storage_account, key, **kwargs):
        self.bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=key)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container(timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)

    def _setup_remote(self, storage_account, key):
        self.bsc2 = BlobServiceClient(self.account_url(storage_account, "blob"), credential=key)
        self.remote_container_name = 'rmt'

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_block_blob(self, standard_blob_tier=None, overwrite=False, tags=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(self.byte_data, length=len(self.byte_data), standard_blob_tier=standard_blob_tier,
                         overwrite=overwrite, tags=tags)
        return blob_name

    def _create_empty_block_blob(self, overwrite=False, tags=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob("", length=0, overwrite=overwrite, tags=tags)
        return blob_name

    def _create_remote_container(self):
        self.remote_container_name = self.get_resource_name('remotectnr')
        remote_container = self.bsc2.get_container_client(self.remote_container_name)
        try:
            remote_container.create_container()
        except ResourceExistsError:
            pass

    def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        source_blob = self.bsc2.get_blob_client(self.remote_container_name, source_blob_name)
        source_blob.upload_blob(blob_data, overwrite=True)
        return source_blob

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

    def _enable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)

        # wait until the policy has gone into effect
        if self.is_live:
            self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)
            time.sleep(30)

    def _disable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=False)
        self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

    def _assert_blob_is_soft_deleted(self, blob):
        self.assertTrue(blob.deleted)
        self.assertIsNotNone(blob.deleted_time)
        self.assertIsNotNone(blob.remaining_retention_days)

    def _assert_blob_not_soft_deleted(self, blob):
        self.assertFalse(blob.deleted)
        self.assertIsNone(blob.deleted_time)
        self.assertIsNone(blob.remaining_retention_days)

    # -- Common test cases for blobs ----------------------------------------------
    @GlobalStorageAccountPreparer()
    def test_blob_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_blob_exists_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = self._create_block_blob(overwrite=True, tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        with self.assertRaises(ResourceModifiedError):
            blob.get_blob_properties(if_tags_match_condition="\"tag1\"='first tag'")
        resp = blob.get_blob_properties(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

    @GlobalStorageAccountPreparer()
    def test_blob_not_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()


    @GlobalStorageAccountPreparer()
    def test_blob_snapshot_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        prop = blob.get_blob_properties()

        # Assert
        self.assertTrue(prop)
        self.assertEqual(snapshot['snapshot'], prop.snapshot)


    @GlobalStorageAccountPreparer()
    def test_blob_snapshot_not_exists(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()


    @GlobalStorageAccountPreparer()
    def test_blob_container_not_exists(self, resource_group, location, storage_account, storage_account_key):
        # In this case both the blob and container do not exist
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.get_blob_properties()


    @GlobalStorageAccountPreparer()
    def test_create_blob_with_question_mark(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = '?ques?tion?'
        blob_data = u'???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Assert
        data = blob.download_blob(encoding='utf-8')
        self.assertIsNotNone(data)
        self.assertEqual(data.readall(), blob_data)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_create_blob_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = self._create_empty_block_blob(tags=tags, overwrite=True)
        blob_data = u'???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceModifiedError):
            blob.upload_blob(blob_data, overwrite=True, if_tags_match_condition="\"tag1\"='first tag'")
        blob.upload_blob(blob_data, overwrite=True, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        data = blob.download_blob(encoding='utf-8')
        self.assertIsNotNone(data)
        self.assertEqual(data.readall(), blob_data)

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_special_chars(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob.upload_blob(blob_data, length=len(blob_data))

            data = blob.download_blob(encoding='utf-8')
            self.assertEqual(data.readall(), blob_data)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_and_download_blob_with_vid(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            resp = blob.upload_blob(blob_data, length=len(blob_data), overwrite=True)
            self.assertIsNotNone(resp.get('version_id'))

            data = blob.download_blob(encoding='utf-8', version_id=resp.get('version_id'))
            self.assertEqual(data.readall(), blob_data)
            self.assertIsNotNone(data.properties.get('version_id'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        data = b'hello world again'
        resp = blob.upload_blob(data, length=len(data), lease=lease)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        content = blob.download_blob(lease=lease).readall()
        self.assertEqual(content, data)

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_generator(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        # Act
        def gen():
            yield "hello"
            yield "world!"
            yield " eom"
        blob = self.bsc.get_blob_client(self.container_name, "gen_blob")
        resp = blob.upload_blob(data=gen())

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        content = blob.download_blob().readall()
        self.assertEqual(content, b"helloworld! eom")

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_with_requests(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        # Act
        uri = "http://www.gutenberg.org/files/59466/59466-0.txt"
        data = requests.get(uri, stream=True)
        blob = self.bsc.get_blob_client(self.container_name, "gutenberg")
        resp = blob.upload_blob(data=data.raw)

        self.assertIsNotNone(resp.get('etag'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        metadata={'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        md = blob.get_blob_properties().metadata
        self.assertDictEqual(md, metadata)


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        content = data.readall()
        self.assertEqual(content, self.byte_data)


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        data = snapshot.download_blob()

        # Assert
        content = data.readall()
        self.assertEqual(content, self.byte_data)


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_snapshot_previous(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        upload_data = b'hello world again'
        blob.upload_blob(upload_data, length=len(upload_data), overwrite=True)

        # Act
        blob_previous = snapshot.download_blob()
        blob_latest = blob.download_blob()

        # Assert
        self.assertEqual(blob_previous.readall(), self.byte_data)
        self.assertEqual(blob_latest.readall(), b'hello world again')


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_range(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob(offset=0, length=5)

        # Assert
        self.assertEqual(data.readall(), self.byte_data[:5])


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_lease(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        data = blob.download_blob(lease=lease)
        lease.release()

        # Assert
        self.assertEqual(data.readall(), self.byte_data)


    @GlobalStorageAccountPreparer()
    def test_get_blob_with_non_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.download_blob()

        # Assert

    @GlobalStorageAccountPreparer()
    def test_set_blob_properties_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
        )

        # Assert
        props = blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_set_blob_properties_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceModifiedError):
            blob.set_http_headers(content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
                if_tags_match_condition="\"tag1\"='first tag'")
        blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
            if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'"
        )

        # Assert
        props = blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')

    @GlobalStorageAccountPreparer()
    def test_set_blob_properties_with_blob_settings_param(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Act
        props.content_settings.content_language = 'spanish'
        props.content_settings.content_disposition = 'inline'
        blob.set_http_headers(content_settings=props.content_settings)

        # Assert
        props = blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')


    @GlobalStorageAccountPreparer()
    def test_get_blob_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'unlocked')
        self.assertIsNotNone(props.creation_time)

    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_returns_rehydrate_priority(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob(standard_blob_tier=StandardBlobTier.Archive, overwrite=True)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_standard_blob_tier(StandardBlobTier.Hot, rehydrate_priority=RehydratePriority.high)

        # Act
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.rehydrate_priority, 'High')

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # HEAD request.
    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_fail(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)

        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties() # Invalid snapshot value of 1


        # Assert
        # TODO: No error code returned
        #self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @GlobalStorageAccountPreparer()
    def test_get_blob_metadata_fail(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            blob.get_blob_properties().metadata # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        #self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    @GlobalStorageAccountPreparer()
    def test_get_blob_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        self.assertTrue(data.properties.server_encrypted)


    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        self.assertTrue(props.server_encrypted)


    @GlobalStorageAccountPreparer()
    def test_list_blobs_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs()

        #Act

        #Assert
        for blob in blob_list:
            self.assertTrue(blob.server_encrypted)


    @GlobalStorageAccountPreparer()
    def test_no_server_encryption(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        #Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = blob.get_blob_properties(raw_response_hook=callback)

        #Assert
        self.assertFalse(props.server_encrypted)


    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_with_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        res = blob.create_snapshot()
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 2)

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=res)
        props = snapshot.get_blob_properties()

        # Assert
        self.assertIsNotNone(blob)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))


    @GlobalStorageAccountPreparer()
    def test_get_blob_properties_with_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'locked')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.duration, 'infinite')


    @GlobalStorageAccountPreparer()
    def test_get_blob_metadata(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = blob.get_blob_properties().metadata

        # Assert
        self.assertIsNotNone(md)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_set_blob_metadata_with_upper_case(self, resource_group, location, storage_account, storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_blob_metadata(metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @pytest.mark.live_test_only
    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_set_blob_metadata_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        self._setup(storage_account, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceModifiedError):
            blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1\"='first tag'")
        blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        md = blob.get_blob_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @pytest.mark.playback_test_only
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_set_blob_metadata_returns_vid(self, resource_group, location, storage_account, storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.set_blob_metadata(metadata)

        # Assert
        self.assertIsNotNone(resp['version_id'])
        md = blob.get_blob_properties().metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @GlobalStorageAccountPreparer()
    def test_delete_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.delete_blob()

        # Assert
        self.assertIsNone(resp)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_delete_blob_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = self._create_block_blob(tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        prop = blob.get_blob_properties()

        with self.assertRaises(ResourceModifiedError):
            blob.delete_blob(if_tags_match_condition="\"tag1\"='first tag'")
        resp = blob.delete_blob(etag=prop.etag, match_condition=MatchConditions.IfNotModified, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        self.assertIsNone(resp)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_delete_specific_blob_version(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)

        resp = blob_client.upload_blob(b'abc', overwrite=True)
        self.assertIsNotNone(resp['version_id'])

        blob_client.upload_blob(b'abc', overwrite=True)

        # Act
        resp = blob_client.delete_blob(version_id=resp['version_id'])

        blob_list = list(self.bsc.get_container_client(self.container_name).list_blobs(include="versions"))

        # Assert
        self.assertIsNone(resp)
        self.assertTrue(len(blob_list) > 0)

    @pytest.mark.playback_test_only
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_delete_blob_version_with_blob_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob_client.upload_blob(b'abcde', overwrite=True)

        version_id = resp['version_id']
        self.assertIsNotNone(version_id)
        blob_client.upload_blob(b'abc', overwrite=True)

        token = generate_blob_sas(
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            version_id=version_id,
            account_key=storage_account_key,
            permission=BlobSasPermissions(delete=True, delete_previous_version=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob_client_using_sas = BlobClient.from_blob_url(blob_client.url, credential=token)
        resp = blob_client_using_sas.delete_blob(version_id=version_id)

        # Assert
        self.assertIsNone(resp)

        blob_list = list(self.bsc.get_container_client(self.container_name).list_blobs(include="versions"))
        # make sure the deleted version is not in the blob version list
        for blob in blob_list:
            self.assertNotEqual(blob.version_id, version_id)

    @GlobalStorageAccountPreparer()
    def test_delete_blob_with_non_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            blob.delete_blob()

        # Assert

    @GlobalStorageAccountPreparer()
    def test_delete_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].name, blob_name)
        self.assertIsNone(blobs[0].snapshot)


    @GlobalStorageAccountPreparer()
    def test_delete_blob_snapshots(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        blob.delete_blob(delete_snapshots='only')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 1)
        self.assertIsNone(blobs[0].snapshot)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_snapshot_returns_vid(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)

        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()
        blobs = list(container.list_blobs(include='versions'))

        self.assertIsNotNone(resp['version_id'])
        # Both create blob and create snapshot will create a new version
        self.assertTrue(len(blobs) >= 2)

        # Act
        blob.delete_blob(delete_snapshots='include')

        # Assert
        blobs = list(container.list_blobs(include=['snapshots', 'versions']))
        # versions are not deleted so blob lists shouldn't be empty
        self.assertTrue(len(blobs) > 0)
        self.assertIsNone(blobs[0].snapshot)

    @GlobalStorageAccountPreparer()
    def test_delete_blob_with_snapshots(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        #with self.assertRaises(HttpResponseError):
        #    blob.delete_blob()

        blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        self.assertEqual(len(blobs), 0)


    @GlobalStorageAccountPreparer()
    def test_soft_delete_blob_without_snapshots(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()

            container = self.bsc.get_container_client(self.container_name)
            blob = container.get_blob_client(blob_name)

            # Soft delete the blob
            blob.delete_blob()
            blob_list = list(container.list_blobs(include='deleted'))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include='deleted'))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()


    @GlobalStorageAccountPreparer()
    def test_soft_delete_single_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete blob_snapshot_1
            snapshot_1 = self.bsc.get_blob_client(
                self.container_name, blob_name, snapshot=blob_snapshot_1)
            snapshot_1.delete_blob()

            with self.assertRaises(ValueError):
                snapshot_1.delete_blob(delete_snapshots='only')

            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include='snapshots'))

            # Assert
            self.assertEqual(len(blob_list), 2)

            # Restore snapshot with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)
        finally:
            self._disable_soft_delete()


    @GlobalStorageAccountPreparer()
    def test_soft_delete_only_snapshots_of_blob(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete all snapshots
            blob.delete_blob(delete_snapshots='only')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                elif listedblob.snapshot == blob_snapshot_2['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include="snapshots"))

            # Assert
            self.assertEqual(len(blob_list), 1)

            # Restore snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            self._disable_soft_delete()


    @GlobalStorageAccountPreparer()
    def test_soft_delete_blob_including_all_snapshots(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = blob.create_snapshot()
            blob_snapshot_2 = blob.create_snapshot()

            # Soft delete blob and all snapshots
            blob.delete_blob(delete_snapshots='include')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                self._assert_blob_is_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs(include=["snapshots"]))

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob and snapshots with undelete
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            self._disable_soft_delete()


    @GlobalStorageAccountPreparer()
    def test_soft_delete_with_leased_blob(self, resource_group, location, storage_account, storage_account_key):
        try:
            self._setup(storage_account, storage_account_key)
            self._enable_soft_delete()
            blob_name = self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            lease = blob.acquire_lease()

            # Soft delete the blob without lease_id should fail
            with self.assertRaises(HttpResponseError):
                blob.delete_blob()

            # Soft delete the blob
            blob.delete_blob(lease=lease)
            container = self.bsc.get_container_client(self.container_name)
            blob_list = list(container.list_blobs(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = list(container.list_blobs())

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete, this also gets rid of the lease
            blob.undelete_blob()
            blob_list = list(container.list_blobs(include="deleted"))

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            self._disable_soft_delete()


    @GlobalStorageAccountPreparer()
    def test_copy_blob_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = copyblob.download_blob().readall()
        self.assertEqual(copy_content, self.byte_data)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_async_copy_blob_with_if_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_tags = {"source": "source tag"}
        blob_name = self._create_block_blob(overwrite=True, tags=source_tags)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        tags1 = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copyblob.upload_blob("abc", overwrite=True)
        copyblob.set_blob_tags(tags=tags1)

        tags = {"tag1": "first tag", "tag2": "secondtag", "tag3": "thirdtag"}
        with self.assertRaises(ResourceModifiedError):
            copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1\"='first tag'")
        copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        with self.assertRaises(ResourceModifiedError):
            copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first taga'")
        dest_tags = copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first tag'")

        self.assertEqual(len(dest_tags), len(tags))

        with self.assertRaises(ResourceModifiedError):
            copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='sourcetag'")
        copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='source tag'")

        with self.assertRaises(ResourceModifiedError):
            copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='abc'")
        copy = copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='first tag'")

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        with self.assertRaises(ResourceModifiedError):
            copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc1'").readall()
        copy_content = copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc'").readall()
        self.assertEqual(copy_content, self.byte_data)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_copy_blob_returns_vid(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy['version_id'])
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = copyblob.download_blob().readall()
        self.assertEqual(copy_content, self.byte_data)

    @GlobalStorageAccountPreparer()
    def test_copy_blob_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip("Unable to set premium account")
        # Arrange
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        blob_tier = StandardBlobTier.Cool
        copyblob.start_copy_from_url(sourceblob, standard_blob_tier=blob_tier)

        copy_blob_properties = copyblob.get_blob_properties()

        # Assert
        self.assertEqual(copy_blob_properties.blob_tier, blob_tier)


    @GlobalStorageAccountPreparer()
    def test_copy_blob_with_rehydrate_priority(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        pytest.skip("Unabe to set up premium storage account type")
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_name)

        blob_tier = StandardBlobTier.Archive
        rehydrate_priority = RehydratePriority.high
        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob,
                                            standard_blob_tier=blob_tier,
                                            rehydrate_priority=rehydrate_priority)
        copy_blob_properties = copyblob.get_blob_properties()
        copyblob.set_standard_blob_tier(StandardBlobTier.Hot)
        second_resp = copyblob.get_blob_properties()

        # Assert
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy.get('copy_id'))
        self.assertEqual(copy_blob_properties.blob_tier, blob_tier)
        self.assertEqual(second_resp.archive_status, 'rehydrate-pending-to-hot')


    # TODO: external copy was supported since 2019-02-02
    # @record
    # def test_copy_blob_with_external_blob_fails(self):
    #     # Arrange
    #     source_blob = "http://www.google.com"
    #     copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')
    #
    #     # Act
    #     copy = copied_blob.start_copy_from_url(source_blob)
    #     self.assertEqual(copy['copy_status'], 'pending')
    #     props = self._wait_for_async_copy(copied_blob)
    #
    #     # Assert
    #     self.assertEqual(props.copy.status_description, '500 InternalServerError "Copy failed."')
    #     self.assertEqual(props.copy.status, 'success')
    #     self.assertIsNotNone(props.copy.id)

    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_copy_blob_async_private_blob_no_sas(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            target_blob.start_copy_from_url(source_blob.url)

    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_copy_blob_async_private_blob_with_sas(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = generate_blob_sas(
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.start_copy_from_url(blob.url)

        # Assert
        props = self._wait_for_async_copy(target_blob)
        self.assertEqual(props.copy.status, 'success')
        actual_data = target_blob.download_blob()
        self.assertEqual(actual_data.readall(), data)


    @GlobalStorageAccountPreparer()
    def test_abort_copy_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')

        # Act
        copy = copied_blob.start_copy_from_url(source_blob)
        self.assertEqual(copy['copy_status'], 'pending')

        copied_blob.abort_copy(copy)
        props = self._wait_for_async_copy(copied_blob)
        self.assertEqual(props.copy.status, 'aborted')

        # Assert
        actual_data = copied_blob.download_blob()
        self.assertEqual(actual_data.readall(), b"")
        self.assertEqual(actual_data.properties.copy.status, 'aborted')


    @GlobalStorageAccountPreparer()
    def test_abort_copy_blob_with_synchronous_copy_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        source_blob_name = self._create_block_blob()
        source_blob = self.bsc.get_blob_client(self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.start_copy_from_url(source_blob.url)

        with self.assertRaises(HttpResponseError):
            target_blob.abort_copy(copy_resp)

        # Assert
        self.assertEqual(copy_resp['copy_status'], 'success')


    @GlobalStorageAccountPreparer()
    def test_snapshot_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])


    @GlobalStorageAccountPreparer()
    def test_lease_blob_acquire_and_release(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        lease.release()
        lease2 = blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease)
        self.assertIsNotNone(lease2)


    @GlobalStorageAccountPreparer()
    def test_lease_blob_with_duration(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_duration=15)
        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(15)

        # Assert
        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)


    @GlobalStorageAccountPreparer()
    def test_lease_blob_with_proposed_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(lease_id=lease_id)

        # Assert
        self.assertEqual(lease.id, lease_id)


    @GlobalStorageAccountPreparer()
    def test_lease_blob_change_lease_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease()
        first_lease_id = lease.id
        lease.change(lease_id)
        lease.renew()

        # Assert
        self.assertNotEqual(first_lease_id, lease.id)
        self.assertEqual(lease.id, lease_id)


    @GlobalStorageAccountPreparer()
    def test_lease_blob_break_period(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_duration=15)
        lease_time = lease.break_lease(lease_break_period=5)

        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(5)

        with self.assertRaises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)

        # Assert
        self.assertIsNotNone(lease.id)
        self.assertIsNotNone(lease_time)
        self.assertIsNotNone(resp.get('etag'))


    @GlobalStorageAccountPreparer()
    def test_lease_blob_acquire_and_renew(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()
        first_id = lease.id
        lease.renew()

        # Assert
        self.assertEqual(first_id, lease.id)


    @GlobalStorageAccountPreparer()
    def test_lease_blob_acquire_twice_fails(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease.id)


    @GlobalStorageAccountPreparer()
    def test_unicode_get_blob_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'hello world')

        # Act
        data = blob.download_blob()

        # Assert
        self.assertEqual(data.readall(), b'hello world')


    @GlobalStorageAccountPreparer()
    def test_create_blob_blob_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = blob.upload_blob(data)

        # Assert
        self.assertIsNotNone(resp.get('etag'))


    @GlobalStorageAccountPreparer()
    def test_no_sas_private_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))


    @GlobalStorageAccountPreparer()
    def test_no_sas_public_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        data = b'a public blob can be read without a shared access signature'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = container.upload_blob(blob_name, data, overwrite=True)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)


    @GlobalStorageAccountPreparer()
    def test_public_access_blob(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        data = b'public access blob'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = container.upload_blob(blob_name, data, overwrite=True)

        # Act
        service = BlobClient.from_blob_url(blob.url)
        #self._set_test_proxy(service, self.settings)
        content = service.download_blob().readall()

        # Assert
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_sas_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        #self._set_test_proxy(service, self.settings)
        content = service.download_blob().readall()

        # Assert
        self.assertEqual(self.byte_data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_sas_access_blob_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot = blob_client.create_snapshot()
        blob_snapshot_client = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=blob_snapshot)

        token = generate_blob_sas(
            blob_snapshot_client.account_name,
            blob_snapshot_client.container_name,
            blob_snapshot_client.blob_name,
            snapshot=blob_snapshot_client.snapshot,
            account_key=blob_snapshot_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        service = BlobClient.from_blob_url(blob_snapshot_client.url, credential=token)

        # Act
        snapshot_content = service.download_blob().readall()

        # Assert
        self.assertEqual(self.byte_data, snapshot_content)

        # Act
        service.delete_blob()

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            service.get_blob_properties()

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = BlobSasPermissions(read=True)
        identifiers = {'testid': access_policy}

        resp = container.set_container_access_policy(identifiers)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            policy_id='testid')

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        #self._set_test_proxy(service, self.settings)
        result = service.download_blob().readall()

        # Assert
        self.assertEqual(self.byte_data, result)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()

        token = generate_account_sas(
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=token)
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=token)
        container.get_container_properties()
        blob_response = requests.get(blob.url)
        container_response = requests.get(container.url, params={'restype':'container'})

        # Assert
        self.assertTrue(blob_response.ok)
        self.assertEqual(self.byte_data, blob_response.content)
        self.assertTrue(container_response.ok)

    @GlobalStorageAccountPreparer()
    def test_get_user_delegation_key(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account, storage_account_key)
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)

        start = datetime.utcnow()
        expiry = datetime.utcnow() + timedelta(hours=1)
        user_delegation_key_1 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)
        user_delegation_key_2 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)

        # Assert key1 is valid
        self.assertIsNotNone(user_delegation_key_1.signed_oid)
        self.assertIsNotNone(user_delegation_key_1.signed_tid)
        self.assertIsNotNone(user_delegation_key_1.signed_start)
        self.assertIsNotNone(user_delegation_key_1.signed_expiry)
        self.assertIsNotNone(user_delegation_key_1.signed_version)
        self.assertIsNotNone(user_delegation_key_1.signed_service)
        self.assertIsNotNone(user_delegation_key_1.value)

        # Assert key1 and key2 are equal, since they have the exact same start and end times
        self.assertEqual(user_delegation_key_1.signed_oid, user_delegation_key_2.signed_oid)
        self.assertEqual(user_delegation_key_1.signed_tid, user_delegation_key_2.signed_tid)
        self.assertEqual(user_delegation_key_1.signed_start, user_delegation_key_2.signed_start)
        self.assertEqual(user_delegation_key_1.signed_expiry, user_delegation_key_2.signed_expiry)
        self.assertEqual(user_delegation_key_1.signed_version, user_delegation_key_2.signed_version)
        self.assertEqual(user_delegation_key_1.signed_service, user_delegation_key_2.signed_service)
        self.assertEqual(user_delegation_key_1.value, user_delegation_key_2.value)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_user_delegation_sas_for_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        byte_data = self.get_random_bytes(1024)
        # Arrange
        token_credential = self.generate_oauth_token()
        service_client = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)
        user_delegation_key = service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        container_client = service_client.create_container(self.get_resource_name('oauthcontainer'))
        blob_client = container_client.get_blob_client(self.get_resource_name('oauthblob'))
        blob_client.upload_blob(byte_data, length=len(byte_data))

        token = generate_blob_sas(
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            snapshot=blob_client.snapshot,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            user_delegation_key=user_delegation_key,
        )

        # Act
        # Use the generated identity sas
        new_blob_client = BlobClient.from_blob_url(blob_client.url, credential=token)
        content = new_blob_client.download_blob()

        # Assert
        self.assertEqual(byte_data, content.readall())

    @GlobalStorageAccountPreparer()
    def test_token_credential(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)
        result = service.get_service_properties()
        self.assertIsNotNone(result)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="Batch not supported on Python 2.7")
    @GlobalStorageAccountPreparer()
    def test_token_credential_with_batch_operation(self, resource_group, location, storage_account, storage_account_key):
        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        token_credential = self.generate_oauth_token()
        service = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential)
        container = service.get_container_client(container_name)
        try:
            container.create_container()
            container.upload_blob(blob_name + '1', b'HelloWorld')
            container.upload_blob(blob_name + '2', b'HelloWorld')
            container.upload_blob(blob_name + '3', b'HelloWorld')

            delete_batch = []
            blob_list = container.list_blobs(name_starts_with=blob_name)
            for blob in blob_list:
                delete_batch.append(blob.name)

            container.delete_blobs(*delete_batch)
        finally:
            container.delete_container()

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_shared_read_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        self.assertEqual(self.byte_data, response.content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_shared_read_access_blob_with_content_query_params(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertEqual(self.byte_data, response.content)
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        self.assertEqual(response.headers['content-disposition'], 'inline')
        self.assertEqual(response.headers['content-encoding'], 'utf-8')
        self.assertEqual(response.headers['content-language'], 'fr')
        self.assertEqual(response.headers['content-type'], 'text')

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_shared_write_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        updated_data = b'updated blob data'
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        headers = {'x-ms-blob-type': 'BlockBlob'}
        response = requests.put(sas_blob.url, headers=headers, data=updated_data)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        data = blob.download_blob()
        self.assertEqual(updated_data, data.readall())

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_shared_delete_access_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.delete(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        with self.assertRaises(HttpResponseError):
            sas_blob.download_blob()


    @GlobalStorageAccountPreparer()
    def test_get_account_information(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account, storage_account_key)
        info = self.bsc.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))


    @GlobalStorageAccountPreparer()
    def test_get_account_information_with_container_name(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account, storage_account_key)
        # Container name gets ignored
        container = self.bsc.get_container_client("missing")
        info = container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))


    @GlobalStorageAccountPreparer()
    def test_get_account_information_with_blob_name(self, resource_group, location, storage_account, storage_account_key):
        # Act
        self._setup(storage_account, storage_account_key)
        # Both container and blob names get ignored
        blob = self.bsc.get_blob_client("missing", "missing")
        info = blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_get_account_information_with_container_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        token = generate_container_sas(
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_container = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        info = sas_container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_get_account_information_with_blob_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        info = sas_blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_download_to_file_with_sas(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = generate_blob_sas(
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)
        FILE_PATH = 'download_to_file_with_sas.temp.{}.dat'.format(str(uuid.uuid4()))

        # Act
        download_blob_from_url(blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_download_to_file_with_credential(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'to_file_with_credential.temp.{}.dat'.format(str(uuid.uuid4()))
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            max_concurrency=2,
            credential=rmt_key)
        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_download_to_stream_with_credential(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'download_to_stream_with_credential.temp.{}.dat'.format(str(uuid.uuid4()))
        # Act
        with open(FILE_PATH, 'wb') as stream:
            download_blob_from_url(
                source_blob.url, stream,
                max_concurrency=2,
                credential=rmt_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_download_to_file_with_existing_file(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'file_with_existing_file.temp.{}.dat'.format(str(uuid.uuid4()))
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=rmt_key)

        with self.assertRaises(ValueError):
            download_blob_from_url(source_blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @StorageAccountPreparer(random_name_enabled=True, name_prefix='pyrmtstorage', parameter_name='rmt')
    def test_download_to_file_with_existing_file_overwrite(self, resource_group, location, storage_account, storage_account_key, rmt, rmt_key):
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        self._setup_remote(rmt, rmt_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'file_with_existing_file_overwrite.temp.{}.dat'.format(str(uuid.uuid4()))
        # Act
        download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=rmt_key)

        data2 = b'ABCDEFGH' * 1024 * 1024
        source_blob = self._create_remote_block_blob(blob_data=data2)
        download_blob_from_url(
            source_blob.url, FILE_PATH, overwrite=True,
            credential=rmt_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data2, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_bytes_with_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        uploaded = upload_blob_to_url(sas_blob.url, data)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_bytes_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_bytes_with_existing_blob(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        with self.assertRaises(ResourceExistsError):
            upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        content = blob.download_blob().readall()
        self.assertEqual(b"existing_data", content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_bytes_with_existing_blob_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_text_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        self._setup(storage_account, storage_account_key)
        data = '12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)

        stream = blob.download_blob(encoding='UTF-8')
        content = stream.readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_upload_to_url_file_with_credential(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        FILE_PATH = 'upload_to_url_file_with_credential.temp.{}.dat'.format(str(uuid.uuid4()))
        self._setup(storage_account, storage_account_key)
        data = b'12345678' * 1024 * 1024
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with open(FILE_PATH, 'rb'):
            uploaded = upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = blob.download_blob().readall()
        self.assertEqual(data, content)
        self._teardown(FILE_PATH)

    def test_set_blob_permission_from_string(self):
        # Arrange
        permission1 = BlobSasPermissions(read=True, write=True)
        permission2 = BlobSasPermissions.from_string('wr')
        self.assertEqual(permission1.read, permission2.read)
        self.assertEqual(permission1.write, permission2.write)

    def test_set_blob_permission(self):
        # Arrange
        permission = BlobSasPermissions.from_string('wrdx')
        self.assertEqual(permission.read, True)
        self.assertEqual(permission.delete, True)
        self.assertEqual(permission.write, True)
        self.assertEqual(permission._str, 'rwdx')

    @GlobalStorageAccountPreparer()
    def test_transport_closed_only_once(self, resource_group, location, storage_account, storage_account_key):
        container_name = self.get_resource_name('utcontainersync')
        transport = RequestsTransport()
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key, transport=transport)
        blob_name = self._get_blob_reference()
        with bsc:
            bsc.get_service_properties()
            assert transport.session is not None
            with bsc.get_blob_client(container_name, blob_name) as bc:
                assert transport.session is not None
            bsc.get_service_properties()
            assert transport.session is not None

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_set_blob_tier_for_a_version(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data_for_the_first_version = "abc"
        data_for_the_second_version = "efgefgefg"
        resp = blob.upload_blob(data_for_the_first_version, overwrite=True)
        self.assertIsNotNone(resp['version_id'])
        blob.upload_blob(data_for_the_second_version, overwrite=True)
        blob.set_standard_blob_tier(StandardBlobTier.Cool)
        blob.set_standard_blob_tier(StandardBlobTier.Cool, rehydrate_priority=RehydratePriority.high, version_id=resp['version_id'])
        blob.set_standard_blob_tier(StandardBlobTier.Hot, version_id=resp['version_id'])
        # Act
        props = blob.get_blob_properties(version_id=resp['version_id'])
        origin_props = blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(data_for_the_first_version))
        self.assertEqual(props.blob_tier, 'Hot')
        self.assertEqual(origin_props.blob_tier, 'Cool')

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_access_token_refresh_after_retry(self, resource_group, location, storage_account, storage_account_key):
        def fail_response(response):
            response.http_response.status_code = 408
        token_credential = self.generate_fake_token()
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=token_credential, retry_total=4)
        self.container_name = self.get_resource_name('retrytest')
        container = bsc.get_container_client(self.container_name)
        with self.assertRaises(Exception):
            container.create_container(raw_response_hook=fail_response)
        # Assert that the token attempts to refresh 4 times (i.e, get_token called 4 times)
        self.assertEqual(token_credential.get_token_count, 4)

# ------------------------------------------------------------------------------
