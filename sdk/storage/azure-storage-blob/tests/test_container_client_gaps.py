# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace

import pytest
from unittest import mock

from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob._lease import BlobLeaseClient
from azure.storage.blob._shared.base_client import TransportWrapper

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestStorageContainerClientGaps(StorageRecordedTestCase):

    @BlobPreparer()
    def test_from_container_url_when_scheme_missing_prepends_https(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        container = ContainerClient.from_container_url(
            f"{storage_account_name}.blob.core.windows.net/sample-container"
        )

        assert container.scheme == "https"
        assert container.account_name == storage_account_name
        assert container.container_name == "sample-container"
        assert container.url == f"https://{storage_account_name}.blob.core.windows.net/sample-container"

    def test_from_container_url_when_url_is_not_string_raises_value_error(self):
        with pytest.raises(ValueError) as exc:
            ContainerClient.from_container_url(1)

        assert str(exc.value) == "Container URL must be a string."

    def test_from_container_url_when_url_is_not_string_sets_attribute_error_as_cause(self):
        with pytest.raises(ValueError) as exc:
            ContainerClient.from_container_url(1)

        assert isinstance(exc.value.__cause__, AttributeError)
        assert str(exc.value.__cause__) == "'int' object has no attribute 'lower'"

    def test_from_container_url_when_netloc_missing_raises_value_error(self):
        with pytest.raises(ValueError) as exc:
            ContainerClient.from_container_url("https:///sample-container")

        assert str(exc.value) == "Invalid URL: https:///sample-container"

    def test_from_container_url_when_container_name_missing_raises_value_error(self):
        with pytest.raises(ValueError) as exc:
            ContainerClient.from_container_url("https://fakename.blob.core.windows.net/")

        assert str(exc.value) == "Invalid URL. Please provide a URL with a valid container name"

    def _get_mock_generated_client(self):
        generated_client = mock.Mock()
        generated_client.container = mock.Mock()
        generated_client.close = mock.Mock()
        return generated_client

    def _get_mock_renamed_container(self, generated_client, container_name):
        renamed_container = mock.Mock()
        renamed_container.container_name = container_name
        renamed_container._client = generated_client
        return renamed_container

    @BlobPreparer()
    def test_rename_container_when_lease_not_provided_sets_source_lease_id_to_none(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        source_generated_client = self._get_mock_generated_client()
        renamed_generated_client = self._get_mock_generated_client()
        renamed_container = self._get_mock_renamed_container(renamed_generated_client, 'renamed-container')

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient._build_generated_client',
            return_value=source_generated_client
        ):
            container = ContainerClient(
                self.account_url(storage_account_name, "blob"),
                container_name='source-container',
                credential=storage_account_key.secret
            )

        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient',
            return_value=renamed_container
        ):
            renamed = container._rename_container('renamed-container', timeout=7)

        rename_args, rename_kwargs = renamed_generated_client.container.rename.call_args
        assert renamed.container_name == 'renamed-container'
        assert rename_args == ('source-container',)
        assert rename_kwargs['source_lease_id'] is None
        assert rename_kwargs['timeout'] == 7
        assert 'lease' not in rename_kwargs

    @BlobPreparer()
    def test_rename_container_when_lease_has_id_accesses_lease_id_property(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        class CountingLease(object):
            def __init__(self, lease_id):
                self._lease_id = lease_id
                self.access_count = 0

            @property
            def id(self):
                self.access_count += 1
                return self._lease_id

        source_generated_client = self._get_mock_generated_client()
        renamed_generated_client = self._get_mock_generated_client()
        renamed_container = self._get_mock_renamed_container(renamed_generated_client, 'renamed-container')

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient._build_generated_client',
            return_value=source_generated_client
        ):
            container = ContainerClient(
                self.account_url(storage_account_name, "blob"),
                container_name='source-container',
                credential=storage_account_key.secret
            )
            lease = CountingLease('counted-lease-id')

        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient',
            return_value=renamed_container
        ):
            container._rename_container('renamed-container', lease=lease)

        assert lease.access_count == 1
        renamed_generated_client.container.rename.assert_called_once()

    @BlobPreparer()
    def test_rename_container_when_lease_client_provided_passes_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        source_generated_client = self._get_mock_generated_client()
        renamed_generated_client = self._get_mock_generated_client()
        renamed_container = self._get_mock_renamed_container(renamed_generated_client, 'renamed-container')

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient._build_generated_client',
            return_value=source_generated_client
        ):
            container = ContainerClient(
                self.account_url(storage_account_name, "blob"),
                container_name='source-container',
                credential=storage_account_key.secret
            )
            lease = BlobLeaseClient(container, lease_id='00000000-1111-2222-3333-444444444444')

        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient',
            return_value=renamed_container
        ):
            container._rename_container('renamed-container', lease=lease)

        rename_args, rename_kwargs = renamed_generated_client.container.rename.call_args
        assert rename_args == ('source-container',)
        assert rename_kwargs['source_lease_id'] == '00000000-1111-2222-3333-444444444444'

    @BlobPreparer()
    def test_rename_container_when_lease_is_string_catches_missing_id_attribute(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        source_generated_client = self._get_mock_generated_client()
        renamed_generated_client = self._get_mock_generated_client()
        renamed_container = self._get_mock_renamed_container(renamed_generated_client, 'renamed-container')

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient._build_generated_client',
            return_value=source_generated_client
        ):
            container = ContainerClient(
                self.account_url(storage_account_name, "blob"),
                container_name='source-container',
                credential=storage_account_key.secret
            )

        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient',
            return_value=renamed_container
        ):
            renamed = container._rename_container('renamed-container', lease='plain-lease-id')

        assert renamed.container_name == 'renamed-container'
        renamed_generated_client.container.rename.assert_called_once()

    @BlobPreparer()
    def test_rename_container_when_lease_is_string_uses_string_as_source_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        source_generated_client = self._get_mock_generated_client()
        renamed_generated_client = self._get_mock_generated_client()
        renamed_container = self._get_mock_renamed_container(renamed_generated_client, 'renamed-container')

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient._build_generated_client',
            return_value=source_generated_client
        ):
            container = ContainerClient(
                self.account_url(storage_account_name, "blob"),
                container_name='source-container',
                credential=storage_account_key.secret
            )

        with mock.patch(
            'azure.storage.blob._container_client.ContainerClient',
            return_value=renamed_container
        ):
            container._rename_container('renamed-container', lease='plain-lease-id')

        rename_args, rename_kwargs = renamed_generated_client.container.rename.call_args
        assert rename_args == ('source-container',)
        assert rename_kwargs['source_lease_id'] == 'plain-lease-id'


class TestContainerClientGaps(StorageRecordedTestCase):

    def _create_container_client(self, storage_account_name, storage_account_key):
        return ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("sourcecontainer"),
            credential=storage_account_key.secret,
        )

    @BlobPreparer()
    def test__rename_container_when_generated_rename_succeeds_does_not_process_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_container_client(storage_account_name, storage_account_key)
        new_name = self.get_resource_name("renamedcontainer")
        renamed_container = SimpleNamespace(
            container_name=new_name,
            _client=SimpleNamespace(container=SimpleNamespace(rename=mock.Mock())),
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient", return_value=renamed_container) as container_client_class, \
                mock.patch("azure.storage.blob._container_client.process_storage_error") as process_storage_error:
            client._rename_container(new_name)

        assert container_client_class.call_count == 1
        assert process_storage_error.call_count == 0

    @BlobPreparer()
    def test__rename_container_when_called_builds_new_container_client_with_new_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_container_client(storage_account_name, storage_account_key)
        new_name = self.get_resource_name("renamedcontainer")
        renamed_container = SimpleNamespace(
            container_name=new_name,
            _client=SimpleNamespace(container=SimpleNamespace(rename=mock.Mock())),
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient", return_value=renamed_container) as container_client_class:
            client._rename_container(new_name)

        called_args, called_kwargs = container_client_class.call_args
        assert called_args[0] == f"{client.scheme}://{client.primary_hostname}"
        assert called_kwargs["container_name"] == new_name
        assert called_kwargs["credential"] == client.credential
        assert called_kwargs["api_version"] == client.api_version
        assert called_kwargs["_configuration"] == client._config
        assert called_kwargs["_pipeline"] == client._pipeline
        assert called_kwargs["_location_mode"] == client._location_mode
        assert called_kwargs["_hosts"] == client._hosts
        assert called_kwargs["require_encryption"] == client.require_encryption
        assert called_kwargs["encryption_version"] == client.encryption_version
        assert called_kwargs["key_encryption_key"] == client.key_encryption_key
        assert called_kwargs["key_resolver_function"] == client.key_resolver_function

    @BlobPreparer()
    def test__rename_container_when_called_invokes_generated_rename_on_new_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_container_client(storage_account_name, storage_account_key)
        new_name = self.get_resource_name("renamedcontainer")
        rename = mock.Mock()
        renamed_container = SimpleNamespace(
            container_name=new_name,
            _client=SimpleNamespace(container=SimpleNamespace(rename=rename)),
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient", return_value=renamed_container):
            client._rename_container(new_name, timeout=9)

        assert rename.call_args.args == (client.container_name,)
        assert rename.call_args.kwargs == {"source_lease_id": None, "timeout": 9}

    @BlobPreparer()
    def test__rename_container_when_generated_rename_succeeds_returns_new_container_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_container_client(storage_account_name, storage_account_key)
        new_name = self.get_resource_name("renamedcontainer")
        renamed_container = SimpleNamespace(
            container_name=new_name,
            _client=SimpleNamespace(container=SimpleNamespace(rename=mock.Mock())),
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient", return_value=renamed_container):
            result = client._rename_container(new_name)

        assert result == renamed_container
        assert result.container_name == new_name

    @BlobPreparer()
    def test__rename_container_when_generated_rename_raises_processes_storage_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_container_client(storage_account_name, storage_account_key)
        new_name = self.get_resource_name("renamedcontainer")
        error = HttpResponseError(message="rename failed")
        renamed_container = SimpleNamespace(
            container_name=new_name,
            _client=SimpleNamespace(container=SimpleNamespace(rename=mock.Mock(side_effect=error))),
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient", return_value=renamed_container), \
                mock.patch("azure.storage.blob._container_client.process_storage_error") as process_storage_error:
            result = client._rename_container(new_name)

        assert result is None
        assert process_storage_error.call_count == 1
        assert process_storage_error.call_args.args[0] is error

    @BlobPreparer()
    def test__rename_container_when_generated_rename_raises_resource_not_found_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )
        rename_error = HttpResponseError(message="rename failure")
        processed_error = ResourceNotFoundError(message="processed rename failure")

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._container_client.ContainerClient") as patched_container_client:
            renamed_container = mock.Mock()
            renamed_container._client.container.rename.side_effect = rename_error
            patched_container_client.return_value = renamed_container

            with mock.patch(
                "azure.storage.blob._container_client.process_storage_error",
                side_effect=processed_error,
            ) as patched_process:
                with pytest.raises(ResourceNotFoundError) as exc:
                    container._rename_container("renamed-container")

        assert str(exc.value) == "processed rename failure"
        assert patched_container_client.call_args.kwargs["container_name"] == "renamed-container"
        patched_process.assert_called_once_with(rename_error)

    @BlobPreparer()
    def test_get_account_information_when_generated_client_raises_http_response_error_returns_none(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )
        get_info_error = HttpResponseError(message="get account info failure")

        with mock.patch.object(
            container._client.container,
            "get_account_info",
            side_effect=get_info_error,
        ) as patched_get_account_info:
            with mock.patch(
                "azure.storage.blob._container_client.process_storage_error",
                return_value=None,
            ) as patched_process:
                result = container.get_account_information()

        assert result is None
        patched_get_account_info.assert_called_once()
        patched_process.assert_called_once_with(get_info_error)

    @BlobPreparer()
    def test_get_account_information_when_storage_error_processing_raises_resource_not_found_error_propagates(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )
        get_info_error = HttpResponseError(message="get account info failure")
        processed_error = ResourceNotFoundError(message="processed account info failure")

        with mock.patch.object(
            container._client.container,
            "get_account_info",
            side_effect=get_info_error,
        ) as patched_get_account_info:
            with mock.patch(
                "azure.storage.blob._container_client.process_storage_error",
                side_effect=processed_error,
            ) as patched_process:
                with pytest.raises(ResourceNotFoundError) as exc:
                    container.get_account_information()

        assert str(exc.value) == "processed account info failure"
        patched_get_account_info.assert_called_once()
        patched_process.assert_called_once_with(get_info_error)

    @BlobPreparer()
    def test__get_blob_service_client_when_transport_is_not_wrapped_creates_wrapped_pipeline(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )

        assert isinstance(container._pipeline._transport, TransportWrapper) is False

        service_client = container._get_blob_service_client()

        assert isinstance(service_client, BlobServiceClient)
        assert service_client.url == f"{self.account_url(storage_account_name, 'blob')}/"
        assert isinstance(service_client._pipeline._transport, TransportWrapper)
        assert service_client._pipeline is not container._pipeline
        assert service_client.account_name == container.account_name

    @BlobPreparer()
    def test_get_container_access_policy_when_generated_client_raises_processed_error_propagates(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )
        access_policy_error = HttpResponseError(message="get access policy failure")
        processed_error = ResourceNotFoundError(message="processed access policy failure")

        with mock.patch.object(
            container._client.container,
            "get_access_policy",
            side_effect=access_policy_error,
        ) as patched_get_access_policy:
            with mock.patch(
                "azure.storage.blob._container_client.process_storage_error",
                side_effect=processed_error,
            ) as patched_process:
                with pytest.raises(ResourceNotFoundError) as exc:
                    container.get_container_access_policy()

        assert str(exc.value) == "processed access policy failure"
        patched_get_access_policy.assert_called_once()
        patched_process.assert_called_once_with(access_policy_error)
