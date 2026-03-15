# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient, ContainerProperties
from azure.storage.blob._lease import BlobLeaseClient
from azure.storage.blob._shared.models import LocationMode
from azure.storage.blob._shared.response_handlers import return_response_headers

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestBlobServiceClientGaps(StorageRecordedTestCase):

    def _create_service(self, storage_account_name, storage_account_key):
        return BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret)

    @BlobPreparer()
    def test_get_user_delegation_key_when_generated_call_raises_http_response_error_processes_storage_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        start = datetime.utcnow()
        expiry = start + timedelta(hours=1)
        error = HttpResponseError(message="delegation key failure")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc._client.service, "get_user_delegation_key", side_effect=error) as get_user_delegation_key, mock.patch(
            "azure.storage.blob._blob_service_client.process_storage_error",
            side_effect=RuntimeError("delegation key processed")
        ) as process_storage_error:
            with pytest.raises(RuntimeError) as exc:
                bsc.get_user_delegation_key(start, expiry, delegated_user_tid="tenant-id", timeout=9)

        assert str(exc.value) == "delegation key processed"
        assert get_user_delegation_key.call_count == 1
        assert get_user_delegation_key.call_args.kwargs["timeout"] == 9
        assert get_user_delegation_key.call_args.kwargs["key_info"].delegated_user_tid == "tenant-id"
        assert process_storage_error.call_count == 1

    @BlobPreparer()
    def test_get_user_delegation_key_when_http_response_error_is_processed_original_error_forwarded(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        start = datetime.utcnow()
        expiry = start + timedelta(hours=2)
        error = HttpResponseError(message="delegation key forwarded")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc._client.service, "get_user_delegation_key", side_effect=error) as get_user_delegation_key, mock.patch(
            "azure.storage.blob._blob_service_client.process_storage_error",
            side_effect=RuntimeError("delegation key forwarded")
        ) as process_storage_error:
            with pytest.raises(RuntimeError) as exc:
                bsc.get_user_delegation_key(start, expiry)

        assert str(exc.value) == "delegation key forwarded"
        assert get_user_delegation_key.call_args.kwargs["timeout"] is None
        assert process_storage_error.call_args[0][0] is error

    @BlobPreparer()
    def test_get_account_information_when_generated_call_raises_http_response_error_processes_storage_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        error = HttpResponseError(message="account info failure")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc._client.service, "get_account_info", side_effect=error) as get_account_info, mock.patch(
            "azure.storage.blob._blob_service_client.process_storage_error",
            side_effect=RuntimeError("account info processed")
        ) as process_storage_error:
            with pytest.raises(RuntimeError) as exc:
                bsc.get_account_information(timeout=5)

        assert str(exc.value) == "account info processed"
        assert get_account_info.call_count == 1
        assert get_account_info.call_args.kwargs["timeout"] == 5
        assert get_account_info.call_args.kwargs["cls"] is return_response_headers
        assert process_storage_error.call_count == 1

    @BlobPreparer()
    def test_get_account_information_when_http_response_error_is_processed_original_error_forwarded(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        error = HttpResponseError(message="account info forwarded")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc._client.service, "get_account_info", side_effect=error) as get_account_info, mock.patch(
            "azure.storage.blob._blob_service_client.process_storage_error",
            side_effect=RuntimeError("account info forwarded")
        ) as process_storage_error:
            with pytest.raises(RuntimeError) as exc:
                bsc.get_account_information(client_request_id="req-123")

        assert str(exc.value) == "account info forwarded"
        assert get_account_info.call_args.kwargs["client_request_id"] == "req-123"
        assert process_storage_error.call_args[0][0] is error

    @BlobPreparer()
    def test_get_service_stats_when_generated_call_raises_http_response_error_processes_storage_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        error = HttpResponseError(message="service stats failure")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc._client.service, "get_statistics", side_effect=error) as get_statistics, mock.patch(
            "azure.storage.blob._blob_service_client.process_storage_error",
            side_effect=RuntimeError("service stats processed")
        ) as process_storage_error:
            with pytest.raises(RuntimeError) as exc:
                bsc.get_service_stats(timeout=11)

        assert str(exc.value) == "service stats processed"
        assert get_statistics.call_count == 1
        assert get_statistics.call_args.kwargs["timeout"] == 11
        assert get_statistics.call_args.kwargs["use_location"] == LocationMode.SECONDARY
        assert process_storage_error.call_args[0][0] is error

    def _create_service_client(self, storage_account_name, storage_account_key):
        return BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key.secret
        )

    def _create_renamed_container(self, service, container_name):
        renamed_container = service.get_container_client(container_name)
        renamed_container._client.container.rename = mock.Mock(return_value=None)
        return renamed_container

    @BlobPreparer()
    def test_get_service_stats_when_generated_call_fails_passes_error_to_process_storage_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = self._create_service_client(storage_account_name, storage_account_key)
        error = HttpResponseError(message="service stats failure")

        # Tests defensive branch — requires mock.
        with mock.patch.object(service._client.service, "get_statistics", side_effect=error) as get_statistics:
            with mock.patch(
                "azure.storage.blob._blob_service_client.process_storage_error",
                side_effect=ValueError("processed stats failure")
            ) as process_storage_error:
                with pytest.raises(ValueError, match="processed stats failure"):
                    service.get_service_stats(timeout=12)

        process_storage_error.assert_called_once_with(error)
        assert get_statistics.call_args.kwargs["timeout"] == 12
        assert get_statistics.call_args.kwargs["use_location"] == LocationMode.SECONDARY

    @BlobPreparer()
    def test_rename_container_when_called_uses_new_name_to_create_returned_container_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = self._create_service_client(storage_account_name, storage_account_key)
        renamed_container = self._create_renamed_container(service, "renamed-container")

        # Tests defensive branch — requires mock.
        with mock.patch.object(service, "get_container_client", return_value=renamed_container) as get_container_client:
            returned = service._rename_container(name="original-container", new_name="renamed-container")

        assert returned is renamed_container
        get_container_client.assert_called_once_with("renamed-container")
        renamed_container._client.container.rename.assert_called_once_with(
            "original-container",
            source_lease_id=None
        )

    @BlobPreparer()
    def test_rename_container_when_string_lease_is_provided_pops_lease_kwarg_and_passes_source_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = self._create_service_client(storage_account_name, storage_account_key)
        renamed_container = self._create_renamed_container(service, "renamed-container")

        # Tests defensive branch — requires mock.
        with mock.patch.object(service, "get_container_client", return_value=renamed_container):
            returned = service._rename_container(
                name="original-container",
                new_name="renamed-container",
                lease="lease-string",
                timeout=7
            )

        assert returned is renamed_container
        renamed_container._client.container.rename.assert_called_once_with(
            "original-container",
            source_lease_id="lease-string",
            timeout=7
        )
        assert "lease" not in renamed_container._client.container.rename.call_args.kwargs

    @BlobPreparer()
    def test_rename_container_when_lease_has_no_id_attribute_falls_back_after_try_block_to_raw_lease_value(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = self._create_service_client(storage_account_name, storage_account_key)
        renamed_container = self._create_renamed_container(service, "renamed-container")
        lease = LeaseWithoutId()

        # Tests defensive branch — requires mock.
        with mock.patch.object(service, "get_container_client", return_value=renamed_container):
            returned = service._rename_container(
                name="original-container",
                new_name="renamed-container",
                lease=lease,
                timeout=3
            )

        assert returned is renamed_container
        assert renamed_container._client.container.rename.call_args.kwargs["source_lease_id"] is lease
        assert renamed_container._client.container.rename.call_args.kwargs["timeout"] == 3

    @BlobPreparer()
    def test_rename_container_when_blob_lease_client_is_provided_uses_lease_id_attribute_value(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        service = self._create_service_client(storage_account_name, storage_account_key)
        source_container = service.get_container_client("original-container")
        lease = BlobLeaseClient(source_container, lease_id="00000000-1111-2222-3333-444444444444")
        renamed_container = self._create_renamed_container(service, "renamed-container")

        # Tests defensive branch — requires mock.
        with mock.patch.object(service, "get_container_client", return_value=renamed_container):
            returned = service._rename_container(
                name="original-container",
                new_name="renamed-container",
                lease=lease
            )

        assert returned.container_name == "renamed-container"
        renamed_container._client.container.rename.assert_called_once_with(
            "original-container",
            source_lease_id="00000000-1111-2222-3333-444444444444"
        )


class LeaseWithoutId(object):
    @property
    def id(self):
        raise AttributeError("lease id unavailable")


class TestBlobServiceClientGapsAdditional(StorageRecordedTestCase):

    def _get_service_client(self, storage_account_name, storage_account_key):
        return BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret)

    def _get_container_client(self, service_client, container_name):
        return BlobServiceClient.get_container_client(service_client, container_name)

    @BlobPreparer()
    def test_rename_container_when_lease_is_none_sets_source_lease_id_to_none(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._get_service_client(storage_account_name, storage_account_key)
        source_name = self.get_resource_name("sourcecontainer")
        new_name = self.get_resource_name("newcontainer")
        renamed_container = self._get_container_client(bsc, new_name)

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", return_value=None, create=True) as rename:
                bsc._rename_container(name=source_name, new_name=new_name, lease=None)

        assert rename.call_args.args[0] == source_name
        assert rename.call_args.kwargs["source_lease_id"] is None

    @BlobPreparer()
    def test_rename_container_when_lease_id_accessor_raises_attribute_error_passes_raw_lease_object(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        class BrokenLease(object):
            @property
            def id(self):
                raise AttributeError("lease id is unavailable")

        bsc = self._get_service_client(storage_account_name, storage_account_key)
        source_name = self.get_resource_name("sourcecontainer")
        new_name = self.get_resource_name("newcontainer")
        renamed_container = self._get_container_client(bsc, new_name)
        lease = BrokenLease()

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", return_value=None, create=True) as rename:
                bsc._rename_container(name=source_name, new_name=new_name, lease=lease, timeout=7)

        assert rename.call_args.args[0] == source_name
        assert rename.call_args.kwargs["source_lease_id"] is lease
        assert rename.call_args.kwargs["timeout"] == 7

    @BlobPreparer()
    def test_rename_container_when_generated_rename_succeeds_calls_underlying_api_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._get_service_client(storage_account_name, storage_account_key)
        source_name = self.get_resource_name("sourcecontainer")
        new_name = self.get_resource_name("newcontainer")
        renamed_container = self._get_container_client(bsc, new_name)

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", return_value=None, create=True) as rename:
                bsc._rename_container(name=source_name, new_name=new_name)

        assert rename.call_count == 1

    @BlobPreparer()
    def test_rename_container_when_generated_rename_succeeds_passes_name_and_remaining_kwargs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._get_service_client(storage_account_name, storage_account_key)
        source_name = self.get_resource_name("sourcecontainer")
        new_name = self.get_resource_name("newcontainer")
        renamed_container = self._get_container_client(bsc, new_name)

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", return_value=None, create=True) as rename:
                bsc._rename_container(name=source_name, new_name=new_name, timeout=11, foo="bar")

        rename.assert_called_once_with(source_name, timeout=11, foo="bar", source_lease_id=None)

    @BlobPreparer()
    def test_rename_container_when_generated_rename_succeeds_returns_container_client_for_new_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._get_service_client(storage_account_name, storage_account_key)
        source_name = self.get_resource_name("sourcecontainer")
        new_name = self.get_resource_name("newcontainer")
        renamed_container = self._get_container_client(bsc, new_name)

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", return_value=None, create=True):
                result = bsc._rename_container(name=source_name, new_name=new_name)

        assert isinstance(result, ContainerClient)
        assert result is renamed_container
        assert result.container_name == new_name
        assert result.url == "{}/{}".format(self.account_url(storage_account_name, "blob"), new_name)


class TestBlobServiceClientGapsRenameUndelete(StorageRecordedTestCase):

    def _create_service(self, storage_account_name, storage_account_key):
        return BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret)

    @BlobPreparer()
    def test_rename_container_when_generated_rename_raises_http_response_error_returns_none_if_processed(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        renamed_container = bsc.get_container_client("renamed")
        error = HttpResponseError(message="rename failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", side_effect=error):
                with mock.patch("azure.storage.blob._blob_service_client.process_storage_error", return_value=None) as process_error:
                    result = bsc._rename_container(name="source", new_name="renamed")

        assert result is None
        process_error.assert_called_once_with(error)

    @BlobPreparer()
    def test_rename_container_when_generated_rename_raises_http_response_error_forwards_processed_exception(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        renamed_container = bsc.get_container_client("renamed")
        error = HttpResponseError(message="rename failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=renamed_container):
            with mock.patch.object(renamed_container._client.container, "rename", side_effect=error):
                with mock.patch(
                    "azure.storage.blob._blob_service_client.process_storage_error",
                    side_effect=ValueError("processed rename")
                ) as process_error:
                    with pytest.raises(ValueError, match="processed rename"):
                        bsc._rename_container(name="source", new_name="renamed")

        process_error.assert_called_once_with(error)

    @BlobPreparer()
    def test_undelete_container_when_new_name_is_provided_warns_and_returns_client_for_new_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        restored_container = bsc.get_container_client("replacement")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=restored_container) as get_container_client:
            with mock.patch.object(restored_container._client.container, "restore", return_value=None) as restore:
                with pytest.warns(DeprecationWarning, match="`new_name` is no longer supported."):
                    result = bsc.undelete_container(
                        deleted_container_name="deleted",
                        deleted_container_version="version123",
                        new_name="replacement",
                        timeout=7
                    )

        assert result.container_name == "replacement"
        get_container_client.assert_called_once_with("replacement")
        restore.assert_called_once_with(
            deleted_container_name="deleted",
            deleted_container_version="version123",
            timeout=7
        )

    @BlobPreparer()
    def test_undelete_container_when_restore_raises_http_response_error_returns_none_if_processed(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        restored_container = bsc.get_container_client("deleted")
        error = HttpResponseError(message="restore failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=restored_container):
            with mock.patch.object(restored_container._client.container, "restore", side_effect=error):
                with mock.patch("azure.storage.blob._blob_service_client.process_storage_error", return_value=None) as process_error:
                    result = bsc.undelete_container("deleted", "version123")

        assert result is None
        process_error.assert_called_once_with(error)

    @BlobPreparer()
    def test_undelete_container_when_restore_raises_http_response_error_forwards_processed_exception(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = self._create_service(storage_account_name, storage_account_key)
        restored_container = bsc.get_container_client("deleted")
        error = HttpResponseError(message="restore failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(bsc, "get_container_client", return_value=restored_container):
            with mock.patch.object(restored_container._client.container, "restore", side_effect=error):
                with mock.patch(
                    "azure.storage.blob._blob_service_client.process_storage_error",
                    side_effect=ValueError("processed undelete")
                ) as process_error:
                    with pytest.raises(ValueError, match="processed undelete"):
                        bsc.undelete_container("deleted", "version123")

        process_error.assert_called_once_with(error)


class TestBlobServiceClientGapsContainerProperties(StorageRecordedTestCase):

    def _get_container_properties(self, container_name):
        try:
            container_properties = ContainerProperties(name=container_name)
        except TypeError:
            container_properties = ContainerProperties()
        if getattr(container_properties, "name", None) != container_name:
            container_properties.name = container_name
        return container_properties

    @BlobPreparer()
    def test_get_container_client_when_container_properties_is_provided_uses_container_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret)
        container_name = self.get_resource_name("utcontainer")
        container_properties = self._get_container_properties(container_name)

        container_client = bsc.get_container_client(container_properties)

        assert isinstance(container_properties, ContainerProperties)
        assert isinstance(container_client, ContainerClient)
        assert container_client.container_name == container_name
        assert container_client.url == "{}/{}".format(self.account_url(storage_account_name, "blob"), container_name)
        assert container_client.account_name == storage_account_name

    @BlobPreparer()
    def test_get_blob_client_when_container_properties_is_provided_uses_container_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret)
        container_name = self.get_resource_name("utcontainer")
        blob_name = self.get_resource_name("blob")
        container_properties = self._get_container_properties(container_name)

        blob_client = bsc.get_blob_client(container_properties, blob_name)

        assert isinstance(container_properties, ContainerProperties)
        assert isinstance(blob_client, BlobClient)
        assert blob_client.container_name == container_name
        assert blob_client.blob_name == blob_name
        assert blob_client.url == "{}/{}/{}".format(self.account_url(storage_account_name, "blob"), container_name, blob_name)
        assert blob_client.account_name == storage_account_name
