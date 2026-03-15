# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobClient
from azure.storage.blob import CustomerProvidedEncryptionKey
from azure.storage.blob import BlobProperties
from azure.storage.blob._deserialize import deserialize_pipeline_response_into_cls

from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer


class TestStorageClientGaps(StorageRecordedTestCase):

    @BlobPreparer()
    def test_blob_client_when_snapshot_has_snapshot_attribute_sets_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        class SnapshotObject(object):
            def __init__(self, snapshot):
                self.snapshot = snapshot

        snapshot = SnapshotObject("2024-01-02T03:04:05.0000000Z")

        # Act
        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='foo',
            blob_name='bar',
            snapshot=snapshot,
            credential=storage_account_key.secret)

        # Assert
        assert blob.snapshot == "2024-01-02T03:04:05.0000000Z"

    @BlobPreparer()
    def test_get_account_information_when_generated_client_raises_http_error_calls_error_processor(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret)
        http_error = HttpResponseError(message="boom")
        processed_error = ResourceNotFoundError(message="missing account information")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob._client.blob, 'get_account_info', side_effect=http_error), mock.patch(
            'azure.storage.blob._blob_client.process_storage_error', side_effect=processed_error
        ) as process_error:
            with pytest.raises(ResourceNotFoundError) as exc:
                blob.get_account_information()

        assert str(exc.value) == "missing account information"
        assert process_error.call_count == 1
        assert process_error.call_args[0][0] is http_error

    @BlobPreparer()
    def test_get_account_information_when_error_processor_swallows_error_returns_none(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret)
        http_error = HttpResponseError(message="boom")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob._client.blob, 'get_account_info', side_effect=http_error), mock.patch(
            'azure.storage.blob._blob_client.process_storage_error', return_value=None
        ) as process_error:
            result = blob.get_account_information()

        assert result is None
        assert process_error.call_count == 1
        assert process_error.call_args[0][0] is http_error

    @BlobPreparer()
    def test_upload_blob_from_url_when_http_and_source_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob").replace('https', 'http'),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret)

        with pytest.raises(ValueError) as exc:
            blob.upload_blob_from_url("https://source.example/blob", source_cpk=object())

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_upload_blob_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob").replace('https', 'http'),
            container_name='foo',
            blob_name='bar',
            credential=storage_account_key.secret)

        with pytest.raises(ValueError) as exc:
            blob.upload_blob(b"hello world", cpk=object())

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."


TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)


class TestStorageBlobClientGaps(StorageRecordedTestCase):

    def _get_blob_client(self, storage_account_name, credential, protocol='https'):
        account_url = self.account_url(storage_account_name, "blob").replace('https', protocol)
        return BlobClient(account_url, container_name='container', blob_name='blob', credential=credential)

    @BlobPreparer()
    def test_download_blob_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key.secret, protocol='http')

        with pytest.raises(ValueError) as exc:
            blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_query_blob_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key.secret, protocol='http')

        with pytest.raises(ValueError) as exc:
            blob_client.query_blob("SELECT * from BlobStorage", cpk=TEST_ENCRYPTION_KEY)

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_query_blob_when_generated_client_raises_http_error_raises_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key.secret)
        service_error = HttpResponseError(message="query failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "query", side_effect=service_error) as query_mock:
            with mock.patch(
                "azure.storage.blob._blob_client.process_storage_error",
                side_effect=ResourceNotFoundError("processed query error")
            ):
                with pytest.raises(ResourceNotFoundError) as exc:
                    blob_client.query_blob("SELECT * from BlobStorage")

        assert str(exc.value) == "processed query error"
        query_mock.assert_called_once()

    @BlobPreparer()
    def test_query_blob_when_generated_client_raises_http_error_calls_error_processor(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key.secret)
        service_error = HttpResponseError(message="query failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "query", side_effect=service_error) as query_mock:
            with mock.patch(
                "azure.storage.blob._blob_client.process_storage_error",
                side_effect=ResourceNotFoundError("processed query error")
            ) as process_error:
                with pytest.raises(ResourceNotFoundError) as exc:
                    blob_client.query_blob("SELECT * from BlobStorage")

        assert str(exc.value) == "processed query error"
        query_mock.assert_called_once()
        process_error.assert_called_once_with(service_error)

    @BlobPreparer()
    def test_undelete_blob_when_generated_client_raises_http_error_raises_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key.secret)
        service_error = HttpResponseError(message="undelete failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "undelete", side_effect=service_error) as undelete_mock:
            with mock.patch(
                "azure.storage.blob._blob_client.process_storage_error",
                side_effect=ResourceNotFoundError("processed undelete error")
            ):
                with pytest.raises(ResourceNotFoundError) as exc:
                    blob_client.undelete_blob()

        assert str(exc.value) == "processed undelete error"
        undelete_mock.assert_called_once_with(timeout=None)

    def test_undelete_blob_when_generated_client_raises_http_error_calls_error_processor(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        error = HttpResponseError(message="boom")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "undelete", side_effect=error) as undelete, mock.patch(
            "azure.storage.blob._blob_client.process_storage_error"
        ) as process_storage_error:
            result = blob_client.undelete_blob(timeout=5)

        assert result is None
        undelete.assert_called_once_with(timeout=5)
        process_storage_error.assert_called_once_with(error)

    def test_get_blob_properties_when_http_and_cpk_raises_value_error(self):
        blob_client = BlobClient(
            "http://foo.blob.core.windows.net/account",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )

        with pytest.raises(ValueError) as error:
            blob_client.get_blob_properties(cpk=TEST_ENCRYPTION_KEY)

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    def test_get_blob_properties_when_cls_is_provided_uses_pipeline_response_wrapper(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        pipeline_response = mock.Mock()
        pipeline_response.http_response = "wrapped-response"
        expected_headers = {"etag": "etag-value"}

        class CustomResult(object):
            def __init__(self):
                self.name = None
                self.marker = "custom-result"

        def custom_cls(response, obj, headers):
            assert response == "wrapped-response"
            assert obj == "generated-object"
            assert headers == expected_headers
            return CustomResult()

        def fake_get_properties(**kwargs):
            wrapped_cls = kwargs["cls"]
            assert wrapped_cls.func == deserialize_pipeline_response_into_cls
            assert wrapped_cls.args[0] == custom_cls
            return wrapped_cls(pipeline_response, "generated-object", expected_headers)

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "get_properties", side_effect=fake_get_properties):
            result = blob_client.get_blob_properties(cls=custom_cls)

        assert result.marker == "custom-result"
        assert result.name == "blob"

    def test_get_blob_properties_when_deserializer_returns_blob_properties_sets_container_and_snapshot(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name="container",
            blob_name="blob",
            snapshot="2024-01-01T00:00:00.0000000Z",
            credential="fake_key"
        )
        blob_properties = BlobProperties()

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "get_properties", return_value=blob_properties):
            result = blob_client.get_blob_properties()

        assert isinstance(result, BlobProperties)
        assert result.name == "blob"
        assert result.container == "container"
        assert result.snapshot == "2024-01-01T00:00:00.0000000Z"

    def test_set_blob_metadata_when_http_and_cpk_raises_value_error(self):
        blob_client = BlobClient(
            "http://foo.blob.core.windows.net/account",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )

        with pytest.raises(ValueError) as error:
            blob_client.set_blob_metadata(metadata={"hello": "world"}, cpk=TEST_ENCRYPTION_KEY)

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."
