# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceModifiedError
from azure.storage.blob import (
    AccessPolicy,
    BlobBlock,
    BlobLeaseClient,
    BlobProperties,
    BlobServiceClient,
    BlobType,
    ContainerClient,
    ContainerSasPermissions,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    StorageErrorCode,
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
LARGE_APPEND_BLOB_SIZE = 64 * 1024
# ------------------------------------------------------------------------------


class TestStorageBlobAccessConditions(StorageRecordedTestCase):

    # --Helpers-----------------------------------------------------------------
    def _setup(self):
        self.container_name = self.get_resource_name('utcontainer')

    def _create_container(self, container_name, bsc):
        container = bsc.get_container_client(container_name)
        container.create_container()
        return container

    def _create_container_and_block_blob(self, container_name, blob_name,
                                         blob_data, bsc):
        container = self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = blob.upload_blob(blob_data, length=len(blob_data))
        assert resp.get('etag') is not None
        return container, blob

    def _create_container_and_page_blob(self, container_name, blob_name,
                                        content_length, bsc):
        container = self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = blob.create_page_blob(str(content_length))
        return container, blob

    def _create_container_and_append_blob(self, container_name, blob_name, bsc):
        container = self._create_container(container_name, bsc)
        blob = bsc.get_blob_client(container_name, blob_name)
        resp = blob.create_append_blob()
        return container, blob

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_service_client_from_container(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc1 = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container_client1 = self._create_container(self.container_name, bsc1)

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        # Set metadata to check against later
        container_client1.set_container_metadata(metadata)

        # Assert metadata is set
        cc1_md1 = container_client1.get_container_properties().metadata
        assert metadata == cc1_md1

        # Get blob service client from container client
        bsc_props1 = bsc1.get_service_properties()
        bsc2 = container_client1._get_blob_service_client()
        bsc_props2 = bsc2.get_service_properties()
        assert bsc_props1 == bsc_props2

        # Return to container and assert its properties
        container_client2 = bsc2.get_container_client(self.container_name)
        cc2_md1 = container_client2.get_container_properties().metadata
        assert cc2_md1 == cc1_md1

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_container_client_from_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container_client1 = self._create_container(self.container_name, bsc)

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        # Set metadata to check against later
        container_client1.set_container_metadata(metadata)

        # Assert metadata is set
        md1 = container_client1.get_container_properties().metadata
        assert metadata == md1

        # Create a blob from container_client1
        blob_name = self.get_resource_name("testblob1")
        blob_client1 = container_client1.get_blob_client(blob_name)

        # Upload data to blob and get container_client again
        blob_client1.upload_blob(b"this is test data")
        blob_client1_data = blob_client1.download_blob().readall()
        container_client2 = blob_client1._get_container_client()

        md2 = container_client2.get_container_properties().metadata
        assert md1 == md2

        # Ensure we can get blob client again
        blob_client2 = container_client2.get_blob_client(blob_name)
        blob_client2_data = blob_client2.download_blob().readall()

        assert blob_client1_data == blob_client2_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = container.get_container_properties().metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_metadata_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '43'}
            container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_acl_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        container.set_container_access_policy(signed_identifiers, if_modified_since=test_datetime)

        # Assert
        acl = container.get_container_access_policy()
        assert acl is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_acl_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        with pytest.raises(ResourceModifiedError) as e:
            container.set_container_access_policy(signed_identifiers, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_acl_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        container.set_container_access_policy(signed_identifiers, if_unmodified_since=test_datetime)

        # Assert
        acl = container.get_container_access_policy()
        assert acl is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_container_acl_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))

        # Act
        access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}
        with pytest.raises(ResourceModifiedError) as e:
            container.set_container_access_policy(signed_identifiers, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_container_acquire_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = container.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)
        lease.break_lease()

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_container_acquire_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            container.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_container_acquire_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = container.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)
        lease.break_lease()

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_container_acquire_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            container.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_container_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        deleted = container.delete_container(if_modified_since=test_datetime)

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            container.get_container_properties()

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_container_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            container.delete_container(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_container_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        container.delete_container(if_unmodified_since=test_datetime)

        # Assert
        with pytest.raises(ResourceNotFoundError):
            container.get_container_properties()

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_container_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container = self._create_container(self.container_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            container.delete_container(if_unmodified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_multi_put_block_contains_headers(self, **kwargs):
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
        self._create_container(self.container_name, bsc)
        blob = bsc.get_blob_client(self.container_name, "blob1")
        blob.upload_blob(
            data,
            headers={'x-custom-header': 'test_value'},
            raw_request_hook=_validate_headers
        )
        assert len(counter) == 5

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        resp = blob.upload_blob(data, length=len(data), if_modified_since=test_datetime)

        # Assert
        assert resp.get('etag') is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_blob(data, length=len(data), if_modified_since=test_datetime, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        resp = blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime)

        # Assert
        assert resp.get('etag') is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        etag = blob.get_blob_properties().etag

        # Act
        resp = blob.upload_blob(data, length=len(data), etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp.get('etag') is not None

        with pytest.raises(ValueError):
            blob.upload_blob(data, length=len(data), etag=etag)
        with pytest.raises(ValueError):
            blob.upload_blob(data, length=len(data), match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_blob(
                data,
                length=len(data),
                etag='0x111111111111111',
                match_condition=MatchConditions.IfNotModified,
                overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)

        # Act
        resp = blob.upload_blob(data, length=len(data), etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp.get('etag') is not None
        with pytest.raises(ValueError):
            blob.upload_blob(data, length=len(data), etag='0x111111111111111')
        with pytest.raises(ValueError):
            blob.upload_blob(data, length=len(data), match_condition=MatchConditions.IfModified)

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        data = b'hello world'
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', data, bsc)
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_blob(data, length=len(data), etag=etag, match_condition=MatchConditions.IfModified, overwrite=True)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        content = blob.download_blob(if_modified_since=test_datetime).readall()

        # Assert
        assert content == b'hello world'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.download_blob(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        content = blob.download_blob(if_unmodified_since=test_datetime).readall()

        # Assert
        assert content == b'hello world'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.download_blob(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        etag = blob.get_blob_properties().etag

        # Act
        content = blob.download_blob(etag=etag, match_condition=MatchConditions.IfNotModified).readall()

        # Assert
        assert content == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.download_blob(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        content = blob.download_blob(etag='0x111111111111111', match_condition=MatchConditions.IfModified).readall()

        # Assert
        assert content == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.download_blob(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        properties = blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        properties = blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @pytest.mark.playback_test_only  # Last Access Time needs to be manually enabled on account
    @BlobPreparer()
    @recorded_by_proxy
    def test_get_properties_last_access_time(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key,
                                connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lat = blob.get_blob_properties().last_accessed_on
        self.sleep(5)

        # Act
        blob.stage_block(block_id='1', data="this is test content")
        blob.commit_block_list(['1'])
        new_lat = blob.get_blob_properties().last_accessed_on

        # Assert
        assert isinstance(lat, datetime)
        assert isinstance(new_lat, datetime)
        assert new_lat > lat
        assert isinstance(blob.download_blob().properties.last_accessed_on, datetime)

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob.set_http_headers(content_settings, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        properties = blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_http_headers(content_settings, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_http_headers(content_settings, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        properties = blob.get_blob_properties()
        assert content_settings.content_language == properties.content_settings.content_language
        assert content_settings.content_disposition == properties.content_settings.content_disposition

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_properties_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob.set_http_headers(content_settings, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        assert isinstance(properties, BlobProperties)
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_if_blob_exists_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), versioned_storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        old_blob_version_id = blob.get_blob_properties().get("version_id")
        assert old_blob_version_id is not None
        blob.stage_block(block_id='1', data="this is test content")
        blob.commit_block_list(['1'])
        new_blob_version_id = blob.get_blob_properties().get("version_id")

        # Assert
        assert blob.exists(version_id=old_blob_version_id)
        assert blob.exists(version_id=new_blob_version_id)
        assert not blob.exists(version_id="2020-08-21T21:24:15.3585832Z")

        # Act
        test_snapshot = blob.create_snapshot()
        blob_snapshot = bsc.get_blob_client(self.container_name, 'blob1', snapshot=test_snapshot)
        assert blob_snapshot.exists()
        blob.stage_block(block_id='1', data="this is additional test content")
        blob.commit_block_list(['1'])

        # Assert
        assert blob_snapshot.exists()
        assert blob.exists()

    @BlobPreparer()
    @recorded_by_proxy
    def test_if_blob_with_cpk_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container_name = self.get_resource_name("testcontainer1")
        cc = ContainerClient(
            self.account_url(storage_account_name, "blob"), credential=storage_account_key, container_name=container_name,
            connection_data_block_size=4 * 1024)
        cc.create_container()
        self._setup()
        test_cpk = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)
        blob_client = cc.get_blob_client("test_blob")
        blob_client.upload_blob(b"hello world", cpk=test_cpk)
        # Act
        assert blob_client.exists()

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        properties = blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        properties = blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert properties is not None
        assert properties.blob_type.value == 'BlockBlob'
        assert properties.size == 11
        assert properties.lease.status == 'unlocked'

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_properties(if_modified_since=test_datetime).metadata

        # Assert
        assert md is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_modified_since=test_datetime).metadata

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_properties(if_unmodified_since=test_datetime).metadata

        # Assert
        assert md is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(if_unmodified_since=test_datetime).metadata

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        md = blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfNotModified).metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified).metadata

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        md = blob.get_blob_properties(etag='0x111111111111111', match_condition=MatchConditions.IfModified).metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_metadata_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_blob_properties(etag=etag, match_condition=MatchConditions.IfModified).metadata

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = blob.get_blob_properties().metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        md = blob.get_blob_properties().metadata
        assert metadata == md

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob.set_blob_metadata(metadata, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        md = blob.get_blob_properties().metadata
        assert metadata == md

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.set_blob_metadata(metadata, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.set_blob_metadata(metadata, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        md = blob.get_blob_properties().metadata
        assert metadata == md

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_metadata_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob.set_blob_metadata(metadata, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        assert resp is None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        assert resp is None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act

        resp = blob.delete_blob(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.delete_blob(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.delete_blob(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_delete_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.delete_blob(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        resp = blob.create_snapshot(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.create_snapshot(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        resp = blob.create_snapshot(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_snapshot_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.create_snapshot(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            if_modified_since=test_datetime,
            lease_id=test_lease_id)

        lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob = bsc.get_blob_client(self.container_name, 'blob1')
            blob.acquire_lease(lease_id=test_lease_id, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            if_unmodified_since=test_datetime,
            lease_id=test_lease_id)

        lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.acquire_lease(lease_id=test_lease_id, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = blob.acquire_lease(
            lease_id=test_lease_id,
            etag=etag, match_condition=MatchConditions.IfNotModified)

        lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None
        assert lease.etag is not None
        assert lease.etag == etag

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.acquire_lease(lease_id=test_lease_id, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        lease = blob.acquire_lease(
            lease_id=test_lease_id,
            etag='0x111111111111111',
            match_condition=MatchConditions.IfModified)

        lease.break_lease()

        # Assert
        assert isinstance(lease, BlobLeaseClient)
        assert lease.id is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_lease_blob_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world', bsc)
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.acquire_lease(lease_id=test_lease_id, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, if_modified_since=test_datetime)

        # Assert
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), versioned_storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        resp = blob.commit_block_list(block_list)

        # Assert
        assert resp['version_id'] is not None
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, metadata=metadata)

        # Assert
        content = blob.download_blob()
        properties = blob.get_blob_properties()
        assert content.readall() == b'AAABBBCCC'
        assert properties.metadata == metadata

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, if_unmodified_since=test_datetime)

        # Assert
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        etag = blob.get_blob_properties().etag

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_block_blob(
            self.container_name, 'blob1', b'', bsc)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
            blob.commit_block_list(block_list, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        blob.upload_page(data, offset=0, length=512, etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_page(data, offset=0, length=512, etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        blob.upload_page(data, offset=0, length=512, etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_update_page_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024, bsc)
        data = b'abcdefghijklmnop' * 32
        blob = bsc.get_blob_client(self.container_name, 'blob1')
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.upload_page(data, offset=0, length=512, etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        ranges = blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        ranges = blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)
        etag = blob.get_blob_properties().etag

        # Act
        ranges = blob.get_page_ranges(etag=etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_page_ranges(etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32
        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)

        # Act
        ranges = blob.get_page_ranges(etag='0x111111111111111', match_condition=MatchConditions.IfModified)

        # Assert
        assert len(ranges[0]) == 2
        assert ranges[0][0] == {'start': 0, 'end': 511}
        assert ranges[0][1] == {'start': 1024, 'end': 1535}

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_page_ranges_iter_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048, bsc)
        data = b'abcdefghijklmnop' * 32

        blob.upload_page(data, offset=0, length=512)
        blob.upload_page(data, offset=1024, length=512)
        etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            blob.get_page_ranges(etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)
            assert resp is not None

        # Assert
        content = blob.download_blob().readall()
        assert b'block 0block 1block 2block 3block 4' == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                resp = blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)
            assert resp is not None

        # Assert
        content = blob.download_blob().readall()
        assert b'block 0block 1block 2block 3block 4' == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))
        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                resp = blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        for i in range(5):
            etag = blob.get_blob_properties().etag
            resp = blob.append_block(u'block {0}'.format(i), etag=etag, match_condition=MatchConditions.IfNotModified)
            assert resp is not None

        # Assert
        content = blob.download_blob().readall()
        assert b'block 0block 1block 2block 3block 4' == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        with pytest.raises(HttpResponseError) as e:
            for i in range(5):
                resp = blob.append_block(u'block {0}'.format(i), etag='0x111111111111111', match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        for i in range(5):
            resp = blob.append_block(u'block {0}'.format(i), etag='0x8D2C9167D53FC2C', match_condition=MatchConditions.IfModified)
            assert resp is not None

        # Assert
        content = blob.download_blob().readall()
        assert b'block 0block 1block 2block 3block 4' == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_block_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        container, blob = self._create_container_and_append_blob(self.container_name, 'blob1', bsc)

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            for i in range(5):
                etag = blob.get_blob_properties().etag
                resp = blob.append_block(u'block {0}'.format(i), etag=etag, match_condition=MatchConditions.IfModified)

        # Assert
        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        # Assert
        content = blob.download_blob().readall()
        assert data == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_modified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_unmodified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() + timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        # Assert
        content = blob.download_blob().readall()
        assert data == content

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_unmodified_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_datetime = self.get_datetime_variable(variables, 'if_modified', datetime.utcnow() - timedelta(minutes=15))

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        assert StorageErrorCode.condition_not_met == e.value.error_code

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = blob.get_blob_properties().etag

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfNotModified)

        # Assert
        content = blob.download_blob().readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfNotModified)

        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_none_match(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfModified)

        # Assert
        content = blob.download_blob().readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_append_blob_from_bytes_with_if_none_match_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key, connection_data_block_size=4 * 1024)
        self._setup()
        blob_name = self.get_resource_name("blob")
        container, blob = self._create_container_and_append_blob(self.container_name, blob_name, bsc)
        test_etag = blob.get_blob_properties().etag

        # Act
        with pytest.raises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            blob.upload_blob(data, blob_type=BlobType.AppendBlob, etag=test_etag, match_condition=MatchConditions.IfModified)

        assert StorageErrorCode.condition_not_met == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_header_metadata_sort_in_upload_blob_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup()
        data = b'hello world'
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        try:
            container_client = bsc.create_container(self.container_name)
        except:
            container_client = bsc.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client('blob1')

        # Relevant ASCII characters (excluding 'Bad Request' values)
        ascii_subset = "!#$%&*+.-^_~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz|~"

        # Build out metadata
        metadata = dict()
        for c in ascii_subset:
            metadata[c] = 'a'

        # Act
        # If we hit invalid metadata error, that means we have successfully sorted headers properly to pass auth error
        with pytest.raises(HttpResponseError) as e:
            blob_client.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        assert StorageErrorCode.invalid_metadata == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy
    def test_header_metadata_sort_in_upload_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup()
        data = b'hello world'
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        try:
            container_client = bsc.create_container(self.container_name)
        except:
            container_client = bsc.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client('blob1')

        # Hand-picked metadata examples as Python & service don't sort '_' with the same weight
        metadata = {'a0': 'a', 'a1': 'a', 'a2': 'a', 'a3': 'a', 'a4': 'a', 'a5': 'a', 'a6': 'a', 'a7': 'a', 'a8': 'a',
                    'a9': 'a', '_': 'a', '_a': 'a', 'a_': 'a', '__': 'a', '_a_': 'a', 'b': 'a', 'c': 'a', 'y': 'a',
                    'z': 'z_', '_z': 'a', '_F': 'a', 'F': 'a', 'F_': 'a', '_F_': 'a', '__F': 'a', '__a': 'a', 'a__': 'a'
                    }

        # Act
        blob_client.upload_blob(data, length=len(data), metadata=metadata)

    @BlobPreparer()
    @recorded_by_proxy
    def test_header_metadata_sort_in_upload_blob_translation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup()
        data = b'hello world'
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        try:
            container_client = bsc.create_container(self.container_name)
        except:
            container_client = bsc.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client('blob1')

        # Hand-picked metadata examples that sorted incorrectly with our previous implementation.
        metadata = {
            'test': 'val',
            'test-': 'val',
            'test--': 'val',
            'test-_': 'val',
            'test_-': 'val',
            'test__': 'val',
            'test-a': 'val',
            'test-A': 'val',
            'test-_A': 'val',
            'test_a': 'val',
            'test_Z': 'val',
            'test_a_': 'val',
            'test_a-': 'val',
            'test_a-_': 'val',
        }

        # Act
        # If we hit invalid metadata error, that means we have successfully sorted headers properly to pass auth error
        with pytest.raises(HttpResponseError) as e:
            blob_client.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        assert StorageErrorCode.invalid_metadata == e.value.error_code

# ------------------------------------------------------------------------------
