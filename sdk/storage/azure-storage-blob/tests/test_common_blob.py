# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import tempfile
import uuid
from datetime import datetime, timedelta
from enum import Enum
from io import BytesIO

from azure.mgmt.storage import StorageManagementClient

import pytest
import requests
from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError)
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import (
    AccessPolicy,
    AccountSasPermissions,
    BlobClient,
    BlobImmutabilityPolicyMode,
    BlobProperties,
    BlobSasPermissions,
    BlobServiceClient,
    BlobType,
    ContainerClient,
    ContainerSasPermissions,
    ContentSettings,
    ImmutabilityPolicy,
    LinearRetry,
    ResourceTypes,
    RetentionPolicy,
    Services,
    StandardBlobTier,
    StorageErrorCode,
    download_blob_from_url,
    generate_account_sas,
    generate_blob_sas,
    generate_container_sas,
    upload_blob_to_url)
from azure.storage.blob._generated.models import RehydratePriority

from devtools_testutils import FakeTokenCredential, recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
# ------------------------------------------------------------------------------


class TestStorageCommonBlob(StorageRecordedTestCase):
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name, timeout=5)
            except ResourceExistsError:
                pass
            try:
                self.bsc.create_container(self.source_container_name, timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)

    def _create_blob(self, tags=None, data=b'', **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(data, tags=tags, overwrite=True, **kwargs)
        return blob

    def _create_source_blob(self, data):
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        blob_client.upload_blob(data, overwrite=True)
        return blob_client

    def _setup_remote(self, storage_account_name, key):
        self.bsc2 = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.remote_container_name = 'rmt'

    def _teardown(self, file_path):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
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
            blob_data = b'12345678' * 1024
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

    def _assert_blob_is_soft_deleted(self, blob):
        assert blob.deleted
        assert blob.deleted_time is not None
        assert blob.remaining_retention_days is not None

    def _assert_blob_not_soft_deleted(self, blob):
        assert not blob.deleted
        assert blob.deleted_time is None
        assert blob.remaining_retention_days is None

    # -- Common test cases for blobs ----------------------------------------------
    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob(overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = blob.get_blob_properties()

        # Assert
        assert exists

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_exists_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = self._create_block_blob(overwrite=True, tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        with pytest.raises(ResourceModifiedError):
            blob.get_blob_properties(if_tags_match_condition="\"tag1\"='first tag'")
        blob.get_blob_properties(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_snapshot_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        prop = blob.get_blob_properties()

        # Assert
        assert prop
        assert snapshot['snapshot'] == prop.snapshot

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_snapshot_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with pytest.raises(ResourceNotFoundError):
            blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_container_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # In this case both the blob and container do not exist
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with pytest.raises(ResourceNotFoundError):
            blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_question_mark(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = '?ques?tion?'
        blob_data = '???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Assert
        data = blob.download_blob(encoding='utf-8')
        assert data is not None
        assert data.readall() == blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = self._create_empty_block_blob(tags=tags, overwrite=True)
        blob_data = '???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceModifiedError):
            blob.upload_blob(blob_data, overwrite=True, if_tags_match_condition="\"tag1\"='first tag'")
        blob.upload_blob(blob_data, overwrite=True, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        data = blob.download_blob(encoding='utf-8')
        assert data is not None
        assert data.readall() == blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_special_chars(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob.upload_blob(blob_data, length=len(blob_data))

            data = blob.download_blob(encoding='utf-8')
            assert data.readall() == blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_and_download_blob_with_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)

        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            resp = blob.upload_blob(blob_data, length=len(blob_data), overwrite=True)
            assert resp.get('version_id') is not None

            data = blob.download_blob(encoding='utf-8', version_id=resp.get('version_id'))
            assert data.readall() == blob_data
            assert data.properties.get('version_id') is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        data = b'hello world again'
        resp = blob.upload_blob(data, length=len(data), lease=lease)

        # Assert
        assert resp.get('etag') is not None
        content = blob.download_blob(lease=lease).readall()
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        # Act
        def gen():
            yield "hello"
            yield "world!"
            yield " eom"
        blob = self.bsc.get_blob_client(self.container_name, "gen_blob")
        resp = blob.upload_blob(data=gen())

        # Assert
        assert resp.get('etag') is not None
        content = blob.download_blob().readall()
        assert content == b"helloworld! eom"

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_with_requests(self, **kwargs):
        # Live only due to size of blob
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        # Create a blob to download with requests using SAS
        data = b'a' * 1024 * 1024
        blob = self._create_blob(data=data)

        sas = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        uri = blob.url + '?' + sas
        data = requests.get(uri, stream=True)
        blob2 = self.bsc.get_blob_client(self.container_name, blob.blob_name + '_copy')
        resp = blob2.upload_blob(data=data.raw)

        assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        metadata={'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        assert resp.get('etag') is not None
        md = blob.get_blob_properties().metadata
        assert md == metadata

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_with_dictionary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = 'test_blob'
        blob_data = {'hello': 'world'}

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with pytest.raises(TypeError):
            blob.upload_blob(blob_data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        # Act
        raw_data = self.get_random_bytes(3 * 1024 * 1024) + b"hello random text"

        def data_generator():
            for i in range(0, 2):
                yield raw_data

        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(data=data_generator())
        data = blob.download_blob().readall()

        # Assert
        assert data == raw_data*2

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_upload_blob_from_pipe(self, **kwargs):
        # Different OSs have different behavior, so this can't be recorded.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b"Hello World"

        reader_fd, writer_fd = os.pipe()

        with os.fdopen(writer_fd, 'wb') as writer:
            writer.write(data)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with os.fdopen(reader_fd, mode='rb') as reader:
            blob.upload_blob(data=reader, overwrite=True)

        blob_data = blob.download_blob().readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        content = data.readall()
        assert content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        data = snapshot.download_blob()

        # Assert
        content = data.readall()
        assert content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_snapshot_previous(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert blob_previous.readall() == self.byte_data
        assert blob_latest.readall() == b'hello world again'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob(offset=0, length=5)

        # Assert
        assert data.readall() == self.byte_data[:5]

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        data = blob.download_blob(lease=lease)
        lease.release()

        # Assert
        assert data.readall() == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_non_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            blob.download_blob()

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceModifiedError):
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
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_blob_settings_param(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Act
        props.content_settings.content_language = 'spanish'
        props.content_settings.content_disposition = 'inline'
        blob.set_http_headers(content_settings=props.content_settings)

        # Assert
        props = blob.get_blob_properties()
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'


    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.lease.status == 'unlocked'
        assert props.creation_time is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_returns_rehydrate_priority(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob(standard_blob_tier=StandardBlobTier.Archive, overwrite=True)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_standard_blob_tier(StandardBlobTier.Hot, rehydrate_priority=RehydratePriority.high)

        # Act
        props = blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.rehydrate_priority == 'High'

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # HEAD request.
    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)

        with pytest.raises(HttpResponseError) as e:
            blob.get_blob_properties() # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        #assert StorageErrorCode.invalid_query_parameter_value == e.exception.error_code

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with pytest.raises(HttpResponseError) as e:
            blob.get_blob_properties().metadata # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        #assert StorageErrorCode.invalid_query_parameter_value == e.exception.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = blob.download_blob()

        # Assert
        assert data.properties.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = blob.get_blob_properties()

        # Assert
        assert props.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy
    def test_list_blobs_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs()

        #Act

        #Assert
        for blob in blob_list:
            assert blob.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy
    def test_no_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        #Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = blob.get_blob_properties(raw_response_hook=callback)

        #Assert
        assert not props.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        res = blob.create_snapshot()
        blobs = list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 2

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=res)
        props = snapshot.get_blob_properties()

        # Assert
        assert blob is not None
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_leased_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        props = blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.lease.status == 'locked'
        assert props.lease.state == 'leased'
        assert props.lease.duration == 'infinite'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = blob.get_blob_properties().metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_upper_case(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.set_blob_metadata(metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceModifiedError):
            blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1\"='first tag'")
        blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        md = blob.get_blob_properties().metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.set_blob_metadata(metadata)

        # Assert
        assert resp['version_id'] is not None
        md = blob.get_blob_properties().metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.delete_blob()

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = self._create_block_blob(tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        prop = blob.get_blob_properties()

        with pytest.raises(ResourceModifiedError):
            blob.delete_blob(if_tags_match_condition="\"tag1\"='first tag'")
        resp = blob.delete_blob(etag=prop.etag, match_condition=MatchConditions.IfNotModified, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_specific_blob_version(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)

        resp = blob_client.upload_blob(b'abc', overwrite=True)
        assert resp['version_id'] is not None

        blob_client.upload_blob(b'abc', overwrite=True)

        # Act
        resp = blob_client.delete_blob(version_id=resp['version_id'])

        blob_list = list(self.bsc.get_container_client(self.container_name).list_blobs(include="versions"))

        # Assert
        assert resp is None
        assert len(blob_list) > 0

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_delete_blob_version_with_blob_sas(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob_client.upload_blob(b'abcde', overwrite=True)

        version_id = resp['version_id']
        assert version_id is not None
        blob_client.upload_blob(b'abc', overwrite=True)

        token = self.generate_sas(
            generate_blob_sas,
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            version_id=version_id,
            account_key=versioned_storage_account_key,
            permission=BlobSasPermissions(delete=True, delete_previous_version=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob_client_using_sas = BlobClient.from_blob_url(blob_client.url, credential=token)
        resp = blob_client_using_sas.delete_blob(version_id=version_id)

        # Assert
        assert resp is None

        blob_list = list(self.bsc.get_container_client(self.container_name).list_blobs(include="versions"))
        # make sure the deleted version is not in the blob version list
        for blob in blob_list:
            assert blob.version_id != version_id

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_non_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            blob.delete_blob()

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob.create_snapshot())

        # Act
        snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 1
        assert blobs[0].name == blob_name
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        blob.delete_blob(delete_snapshots='only')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 1
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_snapshot_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container = self.bsc.get_container_client(self.container_name)

        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()
        blobs = list(container.list_blobs(include='versions'))

        assert resp['version_id'] is not None
        # Both create blob and create snapshot will create a new version
        assert len(blobs) >= 2

        # Act
        blob.delete_blob(delete_snapshots='include')

        # Assert
        blobs = list(container.list_blobs(include=['snapshots', 'versions']))
        # versions are not deleted so blob lists shouldn't be empty
        assert len(blobs) > 0
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.create_snapshot()

        # Act
        #with pytest.raises(HttpResponseError):
        #    blob.delete_blob()

        blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(include='snapshots'))
        assert len(blobs) == 0

    @BlobPreparer()
    @recorded_by_proxy
    def test_soft_delete_blob_without_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        container = self.bsc.get_container_client(self.container_name)
        blob = container.get_blob_client(blob_name)

        # Soft delete the blob
        blob.delete_blob()
        blob_list = list(container.list_blobs(include='deleted'))

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_is_soft_deleted(blob_list[0])

        # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
        blob_list = list(container.list_blobs())

        # Assert
        assert len(blob_list) == 0

        # Restore blob with undelete
        blob.undelete_blob()
        blob_list = list(container.list_blobs(include='deleted'))

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_not_soft_deleted(blob_list[0])

    @BlobPreparer()
    @recorded_by_proxy
    def test_soft_delete_single_blob_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = blob.create_snapshot()
        blob_snapshot_2 = blob.create_snapshot()

        # Soft delete blob_snapshot_1
        snapshot_1 = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob_snapshot_1)
        snapshot_1.delete_blob()

        with pytest.raises(ValueError):
            snapshot_1.delete_blob(delete_snapshots='only')

        container = self.bsc.get_container_client(self.container_name)
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
        for listedblob in blob_list:
            if listedblob.snapshot == blob_snapshot_1['snapshot']:
                self._assert_blob_is_soft_deleted(listedblob)
            else:
                self._assert_blob_not_soft_deleted(listedblob)

        # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
        blob_list = list(container.list_blobs(include='snapshots'))

        # Assert
        assert len(blob_list) == 2

        # Restore snapshot with undelete
        blob.undelete_blob()
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy
    def test_soft_delete_only_snapshots_of_blob(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = blob.create_snapshot()
        blob_snapshot_2 = blob.create_snapshot()

        # Soft delete all snapshots
        blob.delete_blob(delete_snapshots='only')
        container = self.bsc.get_container_client(self.container_name)
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
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
        assert len(blob_list) == 1

        # Restore snapshots with undelete
        blob.undelete_blob()
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy
    def test_soft_delete_blob_including_all_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = blob.create_snapshot()
        blob_snapshot_2 = blob.create_snapshot()

        # Soft delete blob and all snapshots
        blob.delete_blob(delete_snapshots='include')
        container = self.bsc.get_container_client(self.container_name)
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
        for listedblob in blob_list:
            self._assert_blob_is_soft_deleted(listedblob)

        # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
        blob_list = list(container.list_blobs(include=["snapshots"]))

        # Assert
        assert len(blob_list) == 0

        # Restore blob and snapshots with undelete
        blob.undelete_blob()
        blob_list = list(container.list_blobs(include=["snapshots", "deleted"]))

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy
    def test_soft_delete_with_leased_blob(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Soft delete the blob without lease_id should fail
        with pytest.raises(HttpResponseError):
            blob.delete_blob()

        # Soft delete the blob
        blob.delete_blob(lease=lease)
        container = self.bsc.get_container_client(self.container_name)
        blob_list = list(container.list_blobs(include="deleted"))

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_is_soft_deleted(blob_list[0])

        # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
        blob_list = list(container.list_blobs())

        # Assert
        assert len(blob_list) == 0

        # Restore blob with undelete, this also gets rid of the lease
        blob.undelete_blob()
        blob_list = list(container.list_blobs(include="deleted"))

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_not_soft_deleted(blob_list[0])

    @BlobPreparer()
    @recorded_by_proxy
    def test_start_copy_from_url_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        # Create source blob
        source_blob_data = self.get_random_bytes(16 * 1024 + 5)
        source_blob_client = self._create_source_blob(data=source_blob_data)
        # Create destination blob
        destination_blob_client = self._create_blob()
        token = "Bearer {}".format(self.get_credential(BlobServiceClient).get_token("https://storage.azure.com/.default").token)

        with pytest.raises(HttpResponseError):
            destination_blob_client.start_copy_from_url(source_blob_client.url, requires_sync=True)
        with pytest.raises(ValueError):
            destination_blob_client.start_copy_from_url(
                source_blob_client.url, source_authorization=token, requires_sync=False)

        destination_blob_client.start_copy_from_url(
            source_blob_client.url, source_authorization=token, requires_sync=True)
        destination_blob_data = destination_blob_client.download_blob().readall()
        assert source_blob_data == destination_blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_content = copyblob.download_blob().readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = self._create_block_blob()
        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(versioned_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(container_name, 'blob1copy')
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        copy = copyblob.start_copy_from_url(sourceblob, immutability_policy=immutability_policy,
                                            legal_hold=True)

        download_resp = copyblob.download_blob()
        assert download_resp.readall() == self.byte_data

        assert download_resp.properties['has_legal_hold']
        assert download_resp.properties['immutability_policy']['expiry_time'] is not None
        assert download_resp.properties['immutability_policy']['policy_mode'] is not None
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)

        if self.is_live:
            copyblob.delete_immutability_policy()
            copyblob.set_legal_hold(False)
            copyblob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_async_copy_blob_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_tags = {"source": "source tag"}
        blob_name = self._create_block_blob(overwrite=True, tags=source_tags)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        tags1 = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copyblob.upload_blob("abc", overwrite=True)
        copyblob.set_blob_tags(tags=tags1)

        tags = {"tag1": "first tag", "tag2": "secondtag", "tag3": "thirdtag"}
        with pytest.raises(ResourceModifiedError):
            copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1\"='first tag'")
        copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        with pytest.raises(ResourceModifiedError):
            copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first taga'")
        dest_tags = copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first tag'")

        assert len(dest_tags) == len(tags)

        with pytest.raises(ResourceModifiedError):
            copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='sourcetag'")
        copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='source tag'")

        with pytest.raises(ResourceModifiedError):
            copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='abc'")
        copy = copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='first tag'")

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        with pytest.raises(ResourceModifiedError):
            copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc1'").readall()
        copy_content = copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc'").readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(versioned_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob)

        # Assert
        assert copy is not None
        assert copy['version_id'] is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_content = copyblob.download_blob().readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_with_blob_tier_specified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        blob_tier = StandardBlobTier.Cool
        copyblob.start_copy_from_url(sourceblob, standard_blob_tier=blob_tier)

        copy_blob_properties = copyblob.get_blob_properties()

        # Assert
        assert copy_blob_properties.blob_tier == blob_tier

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_with_rehydrate_priority(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

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
        assert copy is not None
        assert copy.get('copy_id') is not None
        assert copy_blob_properties.blob_tier == blob_tier
        assert second_resp.archive_status == 'rehydrate-pending-to-hot'

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_async_private_blob_no_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with pytest.raises(ClientAuthenticationError):
            target_blob.start_copy_from_url(source_blob.url)

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_async_private_blob_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024
        self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        self._create_remote_container()
        source_blob = self._create_remote_block_blob(blob_data=data)
        sas_token = self.generate_sas(
            generate_blob_sas,
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
        assert props.copy.status == 'success'
        actual_data = target_blob.download_blob()
        assert actual_data.readall() == data

    @BlobPreparer()
    @recorded_by_proxy
    def test_abort_copy_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')

        # Act
        copy = copied_blob.start_copy_from_url(source_blob)
        assert copy['copy_status'] == 'pending'

        try:
            copied_blob.abort_copy(copy)
            props = self._wait_for_async_copy(copied_blob)
            assert props.copy.status == 'aborted'

            # Assert
            actual_data = copied_blob.download_blob()
            assert actual_data.readall() == b""
            assert actual_data.properties.copy.status == 'aborted'

        # In the Live test pipeline, the copy occasionally finishes before it can be aborted.
        # Catch and assert on error code to prevent this test from failing.
        except HttpResponseError as e:
            assert e.error_code == StorageErrorCode.NO_PENDING_COPY_OPERATION

    @BlobPreparer()
    @recorded_by_proxy
    def test_abort_copy_blob_with_synchronous_copy_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_blob_name = self._create_block_blob()
        source_blob = self.bsc.get_blob_client(self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = target_blob.start_copy_from_url(source_blob.url)

        with pytest.raises(HttpResponseError):
            target_blob.abort_copy(copy_resp)

        # Assert
        assert copy_resp['copy_status'] == 'success'

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob.create_snapshot()

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_acquire_and_release(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        lease.release()
        lease2 = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Assert
        assert lease is not None
        assert lease2 is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_duration(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)
        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(20)

        # Assert
        with pytest.raises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_proposed_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(lease_id=lease_id)

        # Assert
        assert lease.id == lease_id

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_change_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        first_lease_id = lease.id
        lease.change(lease_id)
        lease.renew()

        # Assert
        assert first_lease_id != lease.id
        assert lease.id == lease_id

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_break_period(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)
        lease_time = lease.break_lease(lease_break_period=5)

        resp = blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(5)

        with pytest.raises(HttpResponseError):
            blob.upload_blob(b'hello 3', length=7, lease=lease)

        # Assert
        assert lease.id is not None
        assert lease_time is not None
        assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_acquire_and_renew(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        first_id = lease.id
        lease.renew()

        # Assert
        assert first_id == lease.id

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_acquire_twice_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            blob.acquire_lease(lease_id='00000000-1111-2222-3333-555555555555')

        # Assert
        assert lease.id is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_unicode_get_blob_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'hello world')

        # Act
        data = blob.download_blob()

        # Assert
        assert data.readall() == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_blob_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = blob.upload_blob(data)

        # Assert
        assert resp.get('etag') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_sas_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert self.byte_data == content

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_sas_access_blob_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot = blob_client.create_snapshot()
        blob_snapshot_client = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=blob_snapshot)

        permission = BlobSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                          permanent_delete=True, list=True, add=True, create=True, update=True)
        assert 'y' in str(permission)
        token = self.generate_sas(
            generate_blob_sas,
            blob_snapshot_client.account_name,
            blob_snapshot_client.container_name,
            blob_snapshot_client.blob_name,
            snapshot=blob_snapshot_client.snapshot,
            account_key=blob_snapshot_client.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        service = BlobClient.from_blob_url(blob_snapshot_client.url, credential=token)

        # Act
        snapshot_content = service.download_blob().readall()

        # Assert
        assert self.byte_data == snapshot_content

        # Act
        service.delete_blob()

        # Assert
        with pytest.raises(ResourceNotFoundError):
            service.get_blob_properties()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_sas_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        start = self.get_datetime_variable(variables, 'start', datetime.utcnow() - timedelta(hours=1))
        expiry = self.get_datetime_variable(variables, 'expiry', datetime.utcnow() + timedelta(hours=1))

        access_policy = AccessPolicy()
        access_policy.start = start
        access_policy.expiry = expiry
        access_policy.permission = BlobSasPermissions(read=True)
        identifiers = {'testid': access_policy}

        container.set_container_access_policy(identifiers)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert self.byte_data == result

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        token = self.generate_sas(
            generate_account_sas,
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

        container_props = container.get_container_properties()
        blob_props = blob.get_blob_properties()

        # Assert
        assert container_props is not None
        assert blob_props is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_service_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blob_name = self._create_block_blob(overwrite=True)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Generate SAS with all available permissions
        container_sas = self.generate_sas(
            generate_container_sas,
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=ContainerSasPermissions(
                read=True, write=True, delete=True, list=True, delete_previous_version=True,
                tag=True, add=True, create=True, permanent_delete=True, filter_by_tags=True, move=True,
                execute=True, set_immutability_policy=True
            ),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        blob_sas = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(
                read=True, add=True, create=True, write=True, delete=True, delete_previous_version=True,
                permanent_delete=True, tag=True, move=True, execute=True, set_immutability_policy=True
            ),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        container_client = ContainerClient.from_container_url(container.url, credential=container_sas)
        blob_list = list(container_client.list_blobs())

        blob_client = BlobClient.from_blob_url(blob.url, credential=blob_sas)
        blob_props = blob_client.get_blob_properties()

        # Assert
        assert blob_list is not None
        assert blob_props is not None

    @BlobPreparer()
    def test_multiple_services_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            storage_account_key,
            ResourceTypes(container=True, object=True, service=True),
            AccountSasPermissions(read=True, list=True),
            datetime.utcnow() + timedelta(hours=1),
            services=Services(blob=True, fileshare=True)
        )

        # Assert
        assert 'ss=bf' in token

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_set_immutability_policy_using_sas(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = self.get_resource_name('vlwblob')
        blob_client = self.bsc.get_blob_client(container_name, blob_name)
        blob_client.upload_blob(b"abc", overwrite=True)

        # Act using account sas
        account_sas_token = self.generate_sas(
            generate_account_sas,
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            AccountSasPermissions(read=True, set_immutability_policy=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient(
            self.bsc.url, container_name= container_name, blob_name=blob_name, credential=account_sas_token)
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp_with_account_sas = blob.set_immutability_policy(immutability_policy=immutability_policy)
        blob_response = requests.get(blob.url)

        # Assert response using account sas
        assert blob_response.ok
        assert resp_with_account_sas['immutability_policy_until_date'] is not None
        assert resp_with_account_sas['immutability_policy_mode'] is not None

        # Acting using container sas
        container_sas_token = self.generate_sas(
            generate_container_sas,
            self.bsc.account_name,
            container_name,
            account_key=self.bsc.credential.account_key,
            permission=ContainerSasPermissions(read=True, set_immutability_policy=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob1 = BlobClient(
            self.bsc.url, container_name=container_name, blob_name=blob_name, credential=container_sas_token)

        expiry_time2 = self.get_datetime_variable(variables, 'expiry_time2', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time2,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp_with_container_sas = blob1.set_immutability_policy(immutability_policy=immutability_policy)
        # Assert response using container sas
        assert resp_with_container_sas['immutability_policy_until_date'] is not None
        assert resp_with_container_sas['immutability_policy_mode'] is not None

        # Acting using blob sas
        blob_sas_token = self.generate_sas(
            generate_blob_sas,
            self.bsc.account_name,
            container_name,
            blob_name,
            account_key=self.bsc.credential.account_key,
            permission=BlobSasPermissions(read=True, set_immutability_policy=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob2 = BlobClient(
            self.bsc.url, container_name=container_name, blob_name=blob_name, credential=blob_sas_token)

        expiry_time3 = self.get_datetime_variable(variables, 'expiry_time3', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time3,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp_with_blob_sas = blob2.set_immutability_policy(immutability_policy=immutability_policy)

        # Assert response using blob sas
        assert resp_with_blob_sas['immutability_policy_until_date'] is not None
        assert resp_with_blob_sas['immutability_policy_mode'] is not None

        if self.is_live:
            blob_client.delete_immutability_policy()
            blob_client.set_legal_hold(False)
            blob_client.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_account_sas_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()

        account_sas_permission = AccountSasPermissions(read=True, write=True, delete=True, add=True,
                                                       permanent_delete=True, list=True)
        assert 'y' in str(account_sas_permission)

        token = self.generate_sas(
            generate_account_sas,
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            account_sas_permission,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=AzureSasCredential(token))
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=AzureSasCredential(token))
        blob_properties = blob.get_blob_properties()
        container_properties = container.get_container_properties()

        # Assert
        assert blob_name == blob_properties.name
        assert self.container_name == container_properties.name

    @BlobPreparer()
    @recorded_by_proxy
    def test_azure_named_key_credential_access(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), named_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = container.create_container()

        # Assert
        assert created

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_user_delegation_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        # Act
        self._setup(storage_account_name, storage_account_key)
        token_credential = self.get_credential(BlobServiceClient)

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)

        start = self.get_datetime_variable(variables, 'start', datetime.utcnow())
        expiry = self.get_datetime_variable(variables, 'expiry', datetime.utcnow() + timedelta(hours=1))
        user_delegation_key_1 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)
        user_delegation_key_2 = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)

        # Assert key1 is valid
        assert user_delegation_key_1.signed_oid is not None
        assert user_delegation_key_1.signed_tid is not None
        assert user_delegation_key_1.signed_start is not None
        assert user_delegation_key_1.signed_expiry is not None
        assert user_delegation_key_1.signed_version is not None
        assert user_delegation_key_1.signed_service is not None
        assert user_delegation_key_1.value is not None

        # Assert key1 and key2 are equal, since they have the exact same start and end times
        assert user_delegation_key_1.signed_oid == user_delegation_key_2.signed_oid
        assert user_delegation_key_1.signed_tid == user_delegation_key_2.signed_tid
        assert user_delegation_key_1.signed_start == user_delegation_key_2.signed_start
        assert user_delegation_key_1.signed_expiry == user_delegation_key_2.signed_expiry
        assert user_delegation_key_1.signed_version == user_delegation_key_2.signed_version
        assert user_delegation_key_1.signed_service == user_delegation_key_2.signed_service
        assert user_delegation_key_1.value == user_delegation_key_2.value

        return variables

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_user_delegation_sas_for_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        variables = kwargs.pop("variables", {})
        byte_data = self.get_random_bytes(1024)
        # Arrange
        token_credential = self.get_credential(BlobServiceClient)
        service_client = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)

        start = self.get_datetime_variable(variables, 'start', datetime.utcnow())
        expiry = self.get_datetime_variable(variables, 'expiry', datetime.utcnow() + timedelta(hours=1))
        user_delegation_key = service_client.get_user_delegation_key(start, expiry)

        container_client = service_client.create_container(self.get_resource_name('oauthcontainer'))
        blob_client = container_client.get_blob_client(self.get_resource_name('oauthblob'))
        blob_client.upload_blob(byte_data, length=len(byte_data))

        token = self.generate_sas(
            generate_blob_sas,
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            snapshot=blob_client.snapshot,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            user_delegation_key=user_delegation_key,
        )

        # Act
        # Use the generated identity sas
        new_blob_client = BlobClient.from_blob_url(blob_client.url, credential=token)
        content = new_blob_client.download_blob()

        # Assert
        assert byte_data == content.readall()

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_token_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        token_credential = self.get_credential(BlobServiceClient)

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        result = service.get_service_properties()
        assert result is not None

        # Action 2: change token value to make request fail
        fake_credential = FakeTokenCredential()
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=fake_credential)
        with pytest.raises(ClientAuthenticationError):
            service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        result = service.get_service_properties()
        assert result is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_token_credential_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        blob_data = b'Helloworld'
        token_credential = self.get_credential(BlobServiceClient)

        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        container = service.get_container_client(container_name)

        # Act / Assert
        try:
            container.create_container()
            blob = container.upload_blob(blob_name, blob_data)

            data = blob.download_blob().readall()
            assert blob_data == data

            blob.delete_blob()
        finally:
            container.delete_container()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_token_credential_with_batch_operation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        token_credential = self.get_credential(BlobServiceClient)
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
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
    @BlobPreparer()
    def test_shared_read_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert response.ok
        assert self.byte_data == response.content

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_shared_read_access_blob_with_content_query_params(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert self.byte_data == response.content
        assert response.headers['cache-control'] == 'no-cache'
        assert response.headers['content-disposition'] == 'inline'
        assert response.headers['content-encoding'] == 'utf-8'
        assert response.headers['content-language'] == 'fr'
        assert response.headers['content-type'] == 'text'

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_shared_write_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        updated_data = b'updated blob data'
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert response.ok
        data = blob.download_blob()
        assert updated_data == data.readall()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_shared_delete_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert response.ok
        with pytest.raises(HttpResponseError):
            sas_blob.download_blob()

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_account_information(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        bsc_info = self.bsc.get_account_information()
        container_client = self.bsc.get_container_client(self.container_name)
        cc_info = container_client.get_account_information()
        blob_client = self._create_blob()
        bc_info = blob_client.get_account_information()

        # Assert
        assert bsc_info.get('sku_name') is not None
        assert bsc_info.get('account_kind') is not None
        assert not bsc_info.get('is_hns_enabled')
        assert cc_info.get('sku_name') is not None
        assert cc_info.get('account_kind') is not None
        assert not cc_info.get('is_hns_enabled')
        assert bc_info.get('sku_name') is not None
        assert bc_info.get('account_kind') is not None
        assert not bc_info.get('is_hns_enabled')

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_account_information_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        self._setup(storage_account_name, storage_account_key)

        account_token = self.generate_sas(
            generate_account_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        container_token = self.generate_sas(
            generate_container_sas,
            account_name=storage_account_name,
            container_name=self.container_name,
            account_key=storage_account_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        blob_token = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            container_name=self.container_name,
            blob_name=self._get_blob_reference(),
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=account_token)
        bsc_info = bsc.get_account_information()
        container_client = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.container_name,
            credential=container_token)
        cc_info = container_client.get_account_information()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            self.container_name,
            self._get_blob_reference(),
            credential=blob_token)
        bc_info = blob_client.get_account_information()

        # Assert
        assert bsc_info.get('sku_name') is not None
        assert bsc_info.get('account_kind') is not None
        assert not bsc_info.get('is_hns_enabled')
        assert cc_info.get('sku_name') is not None
        assert cc_info.get('account_kind') is not None
        assert not cc_info.get('is_hns_enabled')
        assert bc_info.get('sku_name') is not None
        assert bc_info.get('account_kind') is not None
        assert not bc_info.get('is_hns_enabled')

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_account_information_with_container_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        # Container name gets ignored
        container = self.bsc.get_container_client("missing")
        info = container.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_account_information_with_blob_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        # Both container and blob names get ignored
        blob = self.bsc.get_blob_client("missing", "missing")
        info = blob.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_account_information_with_container_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        permission = ContainerSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                             list=True, tag=True, set_immutability_policy=True,
                                             permanent_delete=True)
        assert 'y' in str(permission)
        token = self.generate_sas(
            generate_container_sas,
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_container = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        info = sas_container.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_get_account_information_with_blob_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_download_to_file_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = self._create_blob(data=data)

        sas_token = self.generate_sas(
            generate_blob_sas,
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
        with tempfile.TemporaryFile() as temp_file:
            download_blob_from_url(blob.url, temp_file)
            temp_file.seek(0)
            # Assert
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_to_file_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = self._create_blob(data=data)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            download_blob_from_url(source_blob.url, temp_file, credential=storage_account_key)
            temp_file.seek(0)
            # Assert
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_to_stream_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = self._create_blob(data=data)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            download_blob_from_url(source_blob.url, temp_file, credential=storage_account_key)
            temp_file.seek(0)
            # Assert
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_to_file_with_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = self._create_blob(data=data)

        # Act
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            download_blob_from_url(source_blob.url, temp_file.name, credential=storage_account_key, overwrite=True)

            with pytest.raises(ValueError):
                download_blob_from_url(source_blob.url, temp_file.name)

            # Assert
            temp_file.seek(0)
            actual = temp_file.read()
            assert data == actual

            temp_file.close()
            os.unlink(temp_file.name)

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_to_file_with_existing_file_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = self._create_blob(data=data)
        file_path = 'file_with_existing_file_overwrite.temp.{}.dat'.format(str(uuid.uuid4()))

        # Act
        download_blob_from_url(
            source_blob.url, file_path,
            credential=storage_account_key)

        data2 = b'ABC' * 1024
        source_blob = self._create_blob(data=data2)
        download_blob_from_url(
            source_blob.url, file_path, overwrite=True,
            credential=storage_account_key)

        # Assert
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            assert data2 == actual
        self._teardown(file_path)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_upload_to_url_bytes_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
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
        assert uploaded is not None
        content = blob.download_blob().readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_to_url_bytes_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        assert uploaded is not None
        content = blob.download_blob().readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_to_url_bytes_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        with pytest.raises(ResourceExistsError):
            upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        content = blob.download_blob().readall()
        assert b"existing_data" == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_to_url_bytes_with_existing_blob_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b"existing_data")

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=storage_account_key)

        # Assert
        assert uploaded is not None
        content = blob.download_blob().readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_to_url_text_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = '123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        assert uploaded is not None

        stream = blob.download_blob(encoding='UTF-8')
        content = stream.readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_to_url_file_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            uploaded = upload_blob_to_url(blob.url, data, credential=storage_account_key)

            # Assert
            assert uploaded is not None
            content = blob.download_blob().readall()
            assert data == content

    def test_set_blob_permission_from_string(self):
        # Arrange
        permission1 = BlobSasPermissions(read=True, write=True)
        permission2 = BlobSasPermissions.from_string('wr')
        assert permission1.read == permission2.read
        assert permission1.write == permission2.write

    def test_set_blob_permission(self):
        # Arrange
        permission = BlobSasPermissions.from_string('wrdx')
        assert permission.read == True
        assert permission.delete == True
        assert permission.write == True
        assert permission._str == 'rwdx'

    @BlobPreparer()
    @recorded_by_proxy
    def test_transport_closed_only_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container_name = self.get_resource_name('utcontainersync')
        transport = RequestsTransport()
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=transport)
        blob_name = self._get_blob_reference()
        with bsc:
            bsc.get_service_properties()
            assert transport.session is not None
            with bsc.get_blob_client(container_name, blob_name) as bc:
                assert transport.session is not None
            bsc.get_service_properties()
            assert transport.session is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_tier_for_a_version(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data_for_the_first_version = "abc"
        data_for_the_second_version = "efgefgefg"
        resp = blob.upload_blob(data_for_the_first_version, overwrite=True)
        assert resp['version_id'] is not None
        blob.upload_blob(data_for_the_second_version, overwrite=True)
        blob.set_standard_blob_tier(StandardBlobTier.Cool)
        blob.set_standard_blob_tier(StandardBlobTier.Cool, rehydrate_priority=RehydratePriority.high, version_id=resp['version_id'])
        blob.set_standard_blob_tier(StandardBlobTier.Hot, version_id=resp['version_id'])
        # Act
        props = blob.get_blob_properties(version_id=resp['version_id'])
        origin_props = blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(data_for_the_first_version)
        assert props.blob_tier == 'Hot'
        assert origin_props.blob_tier == 'Cool'

    @BlobPreparer()
    @recorded_by_proxy
    def test_access_token_refresh_after_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        def fail_response(response):
            response.http_response.status_code = 408
        token_credential = FakeTokenCredential()
        retry = LinearRetry(backoff=2, random_jitter_range=1, retry_total=4)

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential, retry_policy=retry)
        self.container_name = self.get_resource_name('retrytest')
        container = bsc.get_container_client(self.container_name)
        with pytest.raises(Exception):
            container.create_container(raw_response_hook=fail_response)
        # Assert that the token attempts to refresh 4 times (i.e, get_token called 4 times)
        assert token_credential.get_token_count == 4

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        blob.upload_blob(b"abc", overwrite=True)

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp = blob.set_immutability_policy(immutability_policy=immutability_policy)

        # Assert
        # check immutability policy after set_immutability_policy()
        props = blob.get_blob_properties()
        assert resp['immutability_policy_until_date'] is not None
        assert resp['immutability_policy_mode'] is not None
        assert props['immutability_policy']['expiry_time'] is not None
        assert props['immutability_policy']['policy_mode'] is not None
        assert props['immutability_policy']['policy_mode'] == "unlocked"

        # check immutability policy after delete_immutability_policy()
        blob.delete_immutability_policy()
        props = blob.get_blob_properties()
        assert props['immutability_policy']['policy_mode'] is None
        assert props['immutability_policy']['policy_mode'] is None

        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_legal_hold(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        blob.upload_blob(b"abc", overwrite=True)
        resp = blob.set_legal_hold(True)
        props = blob.get_blob_properties()

        with pytest.raises(HttpResponseError):
            blob.delete_blob()

        assert resp['legal_hold']
        assert props['has_legal_hold']

        resp2 = blob.set_legal_hold(False)
        props2 = blob.get_blob_properties()

        assert not resp2['legal_hold']
        assert not props2['has_legal_hold']

        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_blob_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        blob.upload_blob(content,
                         immutability_policy=immutability_policy,
                         legal_hold=True,
                         overwrite=True)

        download_resp = blob.download_blob()

        with pytest.raises(HttpResponseError):
            blob.delete_blob()

        assert download_resp.properties['has_legal_hold']
        assert download_resp.properties['immutability_policy']['expiry_time'] is not None
        assert download_resp.properties['immutability_policy']['policy_mode'] is not None

        # Cleanup
        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_list_blobs_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        container_client = self.bsc.get_container_client(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        blob.upload_blob(content,immutability_policy=immutability_policy,
                         legal_hold=True,
                         overwrite=True)

        blob_list = list(container_client.list_blobs(include=['immutabilitypolicy', 'legalhold']))

        assert blob_list[0]['has_legal_hold']
        assert blob_list[0]['immutability_policy']['expiry_time'] is not None
        assert blob_list[0]['immutability_policy']['policy_mode'] is not None

        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_validate_empty_blob(self, **kwargs):
        """Test that we can upload an empty blob with validate=True."""
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        blob_name = self.get_resource_name("utcontainer")
        container_client = self.bsc.get_container_client(self.container_name)
        container_client.upload_blob(blob_name, b"", validate_content=True)

        blob_client = container_client.get_blob_client(blob_name)

        assert blob_client.exists()
        assert blob_client.get_blob_properties().size == 0

    @BlobPreparer()
    @recorded_by_proxy
    def test_download_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        blob_name = self.get_resource_name("utcontainer")
        blob_data = 'abc'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Assert
        data = blob.download_blob(encoding='utf-8')
        props = data.properties

        assert data is not None
        assert data.readall() == blob_data
        assert props['name'] == blob_name
        assert props['creation_time'] is not None
        assert props['content_settings'] is not None
        assert props['size'] == len(blob_data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_version_id_operations(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blob_name = self.get_resource_name("utcontainer")
        blob_data = b'abc'
        blob_client = container.get_blob_client(blob_name)
        tags_a = {"color": "red"}
        tags_b = {"color": "yellow"}
        tags_c = {"color": "orange"}

        blob_client.upload_blob(blob_data, overwrite=True)
        v1_props = blob_client.get_blob_properties()
        v1_blob = BlobClient(self.bsc.url, container_name=self.container_name, blob_name=blob_name,
                             version_id=v1_props['version_id'], credential=versioned_storage_account_key)
        blob_client.upload_blob(blob_data * 2, overwrite=True)
        v2_props = blob_client.get_blob_properties()
        v2_blob = container.get_blob_client(v2_props, version_id=v2_props['version_id'])
        blob_client.upload_blob(blob_data * 3, overwrite=True)
        v3_props = blob_client.get_blob_properties()

        v1_blob.set_standard_blob_tier(StandardBlobTier.Cool)
        v1_blob.set_blob_tags(tags_a)
        v2_blob.set_standard_blob_tier(StandardBlobTier.Cool, version_id=v3_props['version_id'])
        v1_blob.set_blob_tags(tags_c, version_id=v3_props['version_id'])
        v2_blob.set_standard_blob_tier(StandardBlobTier.Hot)
        v2_blob.set_blob_tags(tags_b)

        # Assert
        assert (v1_blob.download_blob()).readall() == blob_data
        assert (v2_blob.download_blob()).readall() == blob_data * 2
        assert (v1_blob.download_blob(version_id=v3_props['version_id'])).readall() == blob_data * 3
        assert v1_blob.get_blob_tags() == tags_a
        assert v2_blob.get_blob_tags() == tags_b
        assert v2_blob.get_blob_tags(version_id=v3_props['version_id']) == tags_c
        v1_blob.delete_blob(version_id=v2_props['version_id'])
        assert v1_blob.exists() is True
        assert v1_blob.exists(version_id=v2_props['version_id']) is False
        assert blob_client.exists() is True

    @BlobPreparer()
    @recorded_by_proxy
    def test_storage_account_audience_blob_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        self.bsc.list_containers()

        # Act
        token_credential = self.get_credential(BlobServiceClient)
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), credential=token_credential,
            audience=f'https://{storage_account_name}.blob.core.windows.net'
        )

        # Assert
        response = bsc.list_containers()
        assert response is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_storage_account_audience_blob_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.exists()

        # Act
        token_credential = self.get_credential(BlobClient)
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name,
            credential=token_credential, audience=f'https://{storage_account_name}.blob.core.windows.net'
        )

        # Assert
        response = blob.exists()
        assert response is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_oauth_error_handling(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        from azure.identity import ClientSecretCredential

        # Generate an invalid credential
        creds = ClientSecretCredential(
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000" + 'a'
        )

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=creds, retry_total=0)
        container = bsc.get_container_client('testing')

        # Act
        with pytest.raises(ClientAuthenticationError):
            container.exists()

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_partial_stream(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_container_client(self.container_name).get_blob_client(self._get_blob_reference())
        data = b'abcde' * 100
        stream = BytesIO(data)
        read_length = 207

        # Act
        blob.upload_blob(stream, length=read_length, overwrite=True)

        # Assert
        result = blob.download_blob().readall()
        assert result == data[:read_length]

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_partial_stream_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob = self.bsc.get_container_client(self.container_name).get_blob_client(self._get_blob_reference())
        data = b'abcde' * 1024
        stream = BytesIO(data)
        length = 3000

        # Act
        blob.upload_blob(stream, length=length, overwrite=True)

        # Assert
        result = blob.download_blob().readall()
        assert result == data[:length]

    # ------------------------------------------------------------------------------