# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from datetime import datetime, timedelta

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceModifiedError
from azure.storage.blob import (
    AccessPolicy,
    BlobBlock,
    BlobProperties,
    BlobType,
    ContainerSasPermissions,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    StorageErrorCode,
)
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobLeaseClient,
)

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer


# ------------------------------------------------------------------------------
LARGE_APPEND_BLOB_SIZE = 64 * 1024
# ------------------------------------------------------------------------------


class TestStorageBlobAccessConditionsAsync(AsyncStorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self):
        self.container_name = self.get_resource_name('utcontainer')

    async def _create_container(self, container_name, bsc):
        container = bsc.get_container_client(container_name)
        await container.create_container()
        return container

    async def _create_container_and_block_blob(self, container_name, blob_name, blob_data, bsc):
        container = await self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = await blob.upload_blob(blob_data, length=len(blob_data))
        assert resp.get('etag') is not None
        return container, blob

    async def _create_container_and_page_blob(self, container_name, blob_name, content_length, bsc):
        container = await self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = await blob.create_page_blob(str(content_length))
        return container, blob

    async def _create_container_and_append_blob(self, container_name, blob_name, bsc):
        container = await self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = await blob.create_append_blob()
        return container, blob

    def _get_datetime_variable(self, variables, name, dt):
        dt_string = variables.setdefault(name, dt.isoformat())
        return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%f")

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_service_client_from_container(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc1 = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container_client1 = await self._create_container(self.container_name, bsc1)

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        # Set metadata to check against later
        await container_client1.set_container_metadata(metadata)

        # Assert metadata is set
        cc1_props = await container_client1.get_container_properties()
        cc1_md1 = cc1_props.metadata
        assert metadata == cc1_md1

        # Get blob service client from container client
        bsc_props1 = await bsc1.get_service_properties()
        bsc2 = container_client1._get_blob_service_client()
        bsc_props2 = await bsc2.get_service_properties()
        assert bsc_props1 == bsc_props2

        # Return to container and assert its properties
        container_client2 = bsc2.get_container_client(self.container_name)
        cc2_props = await container_client2.get_container_properties()
        cc2_md1 = cc2_props.metadata
        assert cc2_md1 == cc1_md1

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_container_client_from_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container_client1 = await self._create_container(self.container_name, bsc)

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        # Set metadata to check against later
        await container_client1.set_container_metadata(metadata)

        # Assert metadata is set
        props1 = await container_client1.get_container_properties()
        md1 = props1.metadata
        assert metadata == md1

        # Create a blob from container_client1
        blob_name = self.get_resource_name("testblob1")
        blob_client1 = container_client1.get_blob_client(blob_name)

        # Upload data to blob and get container_client again
        await blob_client1.upload_blob(b"this is test data")
        downloaded_blob1 = await blob_client1.download_blob()
        blob_client1_data = await downloaded_blob1.readall()
        container_client2 = blob_client1._get_container_client()

        props2 = await container_client2.get_container_properties()
        md2 = props2.metadata
        assert md1 == md2

        # Ensure we can get blob client again
        blob_client2 = container_client2.get_blob_client(blob_name)
        downloaded_blob2 = await blob_client2.download_blob()
        blob_client2_data = await downloaded_blob2.readall()

        assert blob_client1_data == blob_client2_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        await container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = (await container.get_container_properties()).metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_md_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '43'}
            await container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_acl_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        start_time = self._get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self._get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        await container.set_container_access_policy(signed_identifiers, if_modified_since=test_datetime)

        # Assert
        acl = await container.get_container_access_policy()
        assert acl is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_acl_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        start_time = self._get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self._get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        with pytest.raises(ResourceModifiedError) as e:
            await container.set_container_access_policy(signed_identifiers, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_acl_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        start_time = self._get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self._get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        await container.set_container_access_policy(signed_identifiers, if_unmodified_since=test_datetime)

        # Assert
        acl = await container.get_container_access_policy()
        assert acl is not None

        return variables


    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_container_acl_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        start_time = self._get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self._get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        with pytest.raises(ResourceModifiedError) as e:
            await container.set_container_access_policy(signed_identifiers, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_container_acquire_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        lease = await container.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)
        await lease.break_lease()

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_cont_acquire_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await container.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_container_acquire_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        lease = await container.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)
        await lease.break_lease()

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_container_acquire_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await container.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_container_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        deleted = await container.delete_container(if_modified_since=test_datetime)

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            await container.get_container_properties()

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_container_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await container.delete_container(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_container_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        await container.delete_container(if_unmodified_since=test_datetime)

        # Assert
        with pytest.raises(ResourceNotFoundError):
            await container.get_container_properties()

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_container_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = await self._create_container(self.container_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await container.delete_container(if_unmodified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_multi_put_block_contains_headers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        counter = list()

        def _validate_headers(request):
            counter.append(request)
            header = request.http_request.headers.get('x-custom-header')
            assert header == 'test_value'

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), storage_account_key, max_single_put_size=100, max_block_size=50)
        self._setup()
        data = self.get_random_bytes(2 * 100)
        await self._create_container(self.container_name, bsc)
        blob = bsc.get_blob_client(self.container_name, "blob1")
        await blob.upload_blob(
            data,
            headers={'x-custom-header': 'test_value'},
            raw_request_hook=_validate_headers
        )
        assert len(counter) == 5

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_modified_since=test_datetime)

        # Assert
        assert resp.get('etag') is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_modified_since=test_datetime, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime)

        # Assert
        assert resp.get('etag') is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        etag = (await blob.get_blob_properties()).etag

        # Act
        resp = await blob.upload_blob(data, length=len(data), etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_blob(
                data, length=len(data), etag='0x111111111111111',
                match_condition=MatchConditions.IfNotModified, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)

        # Act
        resp = await blob.upload_blob(data, length=len(data), etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), etag=etag, match_condition=MatchConditions.IfModified, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        content = await blob.download_blob(if_modified_since=test_datetime)
        content = await content.readall()

        # Assert
        assert content == b'hello world'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.download_blob(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        content = await blob.download_blob(if_unmodified_since=test_datetime)
        content = await content.readall()

        # Assert
        assert content == b'hello world'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.download_blob(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        etag = (await blob.get_blob_properties()).etag

        # Act
        content = await blob.download_blob(etag=etag, match_condition=MatchConditions.IfNotModified)
        content = await content.readall()

        # Assert
        assert content == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.download_blob(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        content = await blob.download_blob(etag='0x111111111111111', match_condition=MatchConditions.IfModified)
        content = await content.readall()

        # Assert
        assert content == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.download_blob(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        properties = await blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        properties = await blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        await blob.set_http_headers(content_settings, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        properties = await blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        properties = await blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_props_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            await blob.set_http_headers(content_settings, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_if_blob_exists_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), versioned_storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        old_blob_props = await blob.get_blob_properties()
        old_blob_version_id = old_blob_props.get("version_id")
        assert old_blob_version_id is not None
        await blob.stage_block(block_id='1', data="this is test content")
        await blob.commit_block_list(['1'])
        new_blob_props = await blob.get_blob_properties()
        new_blob_version_id = new_blob_props.get("version_id")

        # Assert
        assert await blob.exists(version_id=old_blob_version_id)
        assert await blob.exists(version_id=new_blob_version_id)
        assert not await blob.exists(version_id="2020-08-21T21:24:15.3585832Z")

        # Act
        test_snapshot = await blob.create_snapshot()
        blob_snapshot = bsc.get_blob_client(self.container_name, 'blob1', snapshot=test_snapshot)
        assert await blob_snapshot.exists()
        await blob.stage_block(block_id='1', data="this is additional test content")
        await blob.commit_block_list(['1'])

        # Assert
        assert await blob_snapshot.exists()
        assert await blob.exists()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_if_blob_with_cpk_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container_name = self.get_resource_name("testcontainer1")
        cc = ContainerClient(
            self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name=container_name,
            connection_data_block_size=4 * 1024)
        await cc.create_container()
        self._setup()
        test_cpk = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)
        blob_client = cc.get_blob_client("test_blob")
        await blob_client.upload_blob(b"hello world", cpk=test_cpk)
        # Act
        assert await blob_client.exists()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        assert isinstance(properties, BlobProperties)
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        properties = await blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(if_modified_since=test_datetime)).metadata

        # Assert
        assert md is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(if_unmodified_since=test_datetime)).metadata

        # Assert
        assert md is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        md = (await blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfNotModified)).metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfModified)).metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        await blob.set_blob_metadata(metadata, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert metadata == md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert metadata == md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            await blob.set_blob_metadata(metadata, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        assert resp is None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        assert resp is None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act

        resp = await blob.delete_blob(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.delete_blob(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.delete_blob(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        resp = await blob.create_snapshot(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.create_snapshot(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            if_modified_since=test_datetime,
            lease_id=test_lease_id)

        await lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            await blob.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            if_unmodified_since=test_datetime,
            lease_id=test_lease_id)

        await lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = await blob.acquire_lease(
            lease_id=test_lease_id,
            etag=etag, match_condition=MatchConditions.IfNotModified)

        await lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None
        assert lease.etag is not None
        assert lease.etag == etag

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.acquire_lease(
                lease_id=test_lease_id,
                etag='0x111111111111111',
                match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            lease_id=test_lease_id,
            etag='0x111111111111111',
            match_condition=MatchConditions.IfModified)

        await lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.acquire_lease(
                lease_id=test_lease_id,
                etag=etag,
                match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_modified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert content == b'AAABBBCCC'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), versioned_storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        resp = await blob.commit_block_list(block_list)

        # Assert
        assert resp['version_id'] is not None
        content = await blob.download_blob()
        content = await content.readall()
        assert content == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_unmodified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert content == b'AAABBBCCC'

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        etag = (await blob.get_blob_properties()).etag

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert content == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert content == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_list_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
            await blob.commit_block_list(block_list, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        await blob.upload_page(data, offset=0, length=512, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_unmod_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))
        etag = (await blob.get_blob_properties()).etag

        # Act
        ranges = await blob.get_page_ranges(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_page_ranges(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_page_ranges_iter_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32

        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))
        etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            await blob.get_page_ranges(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)
            assert resp is not None

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert b'block 0block 1block 2block 3block 4' == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)
            assert resp is not None

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert b'block 0block 1block 2block 3block 4' == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        for i in range(5):
            etag = (await blob.get_blob_properties()).etag
            resp = await blob.append_block(u'block {0}'.format(i), etag=etag, match_condition=MatchConditions.IfNotModified)
            assert resp is not None

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert b'block 0block 1block 2block 3block 4' == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        with pytest.raises(HttpResponseError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), etag='0x8D2C9167D53FC2C', match_condition=MatchConditions.IfModified)
            assert resp is not None

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert b'block 0block 1block 2block 3block 4' == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                etag = (await blob.get_blob_properties()).etag
                resp = await blob.append_block(u'block {0}'.format(i), etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert data == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_apnd_blob_from_bytes_with_if_mod_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert data == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_unmod_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self._get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = (await blob.get_blob_properties()).etag

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfNotModified)

        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_blob_from_bytes_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfModified)

        # Assert
        content = await blob.download_blob()
        content = await content.readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_apnd_blob_from_bytes_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = (await blob.get_blob_properties()).etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfModified)

        assert StorageErrorCode.condition_not_met == e.value.error_code

# ------------------------------------------------------------------------------
