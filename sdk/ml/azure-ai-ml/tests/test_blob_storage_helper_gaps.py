# pytest tests for azure/ai/ml/_artifacts/_blob_storage_helper.py
import logging
import os
import sys
from pathlib import Path
from typing import Any

import pytest
from azure.ai.ml._artifacts import _blob_storage_helper as helper
from azure.ai.ml._artifacts._blob_storage_helper import BlobStorageClient, _blob_is_hdi_folder
from azure.ai.ml._artifacts._constants import (
    ARTIFACT_ORIGIN,
    BLOB_DATASTORE_IS_HDI_FOLDER_KEY,
    FILE_SIZE_WARNING,
    KEY_AUTHENTICATION_ERROR_CODE,
    LEGACY_ARTIFACT_DIRECTORY,
    MAX_CONCURRENCY,
    SAS_KEY_AUTHENTICATION_ERROR_MSG,
    UPLOAD_CONFIRMATION,
)
from azure.ai.ml._azure_environments import _get_cloud_details
from azure.ai.ml._utils._asset_utils import (
    AssetNotChangedError,
    IgnoreFile,
    _build_metadata_dict,
    generate_asset_id,
    get_directory_size,
    upload_directory,
    upload_file,
)
from azure.ai.ml.constants._common import STORAGE_AUTH_MISMATCH_ERROR
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient


class DummyBlobClient:
    def __init__(self, metadata=None, exception=None):
        self.metadata = metadata or {}
        self.exception = exception

    def get_blob_properties(self):
        if self.exception:
            raise self.exception
        return {"metadata": self.metadata}

    def set_blob_metadata(self, metadata):
        self.metadata = metadata


class DummyContainerClient:
    def __init__(self):
        self.calls = []
        self.blobs = {}

    def get_blob_client(self, blob=None):
        return DummyBlobClient(metadata=self.blobs.get(blob, {}))

    def list_blobs(self, name_starts_with=None, include=None):
        return []

    def download_blob(self, item):
        class DummyDownload:
            size = 1

            def content_as_bytes(self, max_concurrency):
                return b""

        return DummyDownload()

    def walk_blobs(self, name_starts_with=None, delimiter=None):
        return iter([])


@pytest.fixture(autouse=True)
def patch_blob_storage(monkeypatch):
    container_client = DummyContainerClient()
    monkeypatch.setattr(BlobStorageClient, "container_client", container_client, raising=False)
    return container_client


def test_blob_is_hdi_folder_true():
    class DummyBlob:
        metadata = {BLOB_DATASTORE_IS_HDI_FOLDER_KEY: "true"}

    assert _blob_is_hdi_folder(DummyBlob())


def test_blob_is_hdi_folder_false():
    class DummyBlob:
        metadata = {}

    assert not _blob_is_hdi_folder(DummyBlob())


def test_upload_sets_indicator_and_handles_asset_not_changed(monkeypatch, tmp_path):
    client = BlobStorageClient(credential="cred", account_url="https://account.blob.core.windows.net", container_name="cont")
    monkeypatch.setattr(client, "check_blob_exists", lambda: None)
    monkeypatch.setattr("azure.ai.ml._artifacts._blob_storage_helper.get_directory_size", lambda source, ignore_file: (101 * 10**6, None))

    def dummy_upload_file(storage_client, **kwargs):
        storage_client.uploaded_file_count = storage_client.total_file_count

    monkeypatch.setattr("azure.ai.ml._artifacts._blob_storage_helper.upload_file", dummy_upload_file)
    monkeypatch.setattr("azure.ai.ml._artifacts._blob_storage_helper.AssetNotChangedError", AssetNotChangedError)
    monkeypatch.setattr("azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details", lambda: {"storage_endpoint": "core.windows.net"})
    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper.BlobStorageClient._set_confirmation_metadata",
        lambda self, name, version: None,
    )

    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("content")

    artifact_info = client.upload(str(tmp_file), name="name", version="v1")

    assert artifact_info["name"] == "name"
    assert artifact_info["version"] == "v1"
    assert artifact_info["indicator file"] is not None


def test_download_warns_on_large_download(monkeypatch, tmp_path):
    client = BlobStorageClient(credential="cred", account_url="https://account.blob.core.windows.net", container_name="cont")
    class DummyItem:
        name = "blob"
        metadata = {}

    class DummyContent:
        size = 101 * 10**6

        def content_as_bytes(self, max_concurrency):
            return b"data"

    client.container_client = DummyContainerClient()
    client.container_client.list_blobs = lambda name_starts_with, include: [DummyItem()]
    client.container_client.download_blob = lambda item: DummyContent()
    monkeypatch.setattr("azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details", lambda: {"storage_endpoint": "core.windows.net"})

    target_path = tmp_path / "output"
    client.download("prefix", target_path)

    assert target_path.exists()


def test_exists_returns_true_for_existing_blob(monkeypatch):
    client = BlobStorageClient(credential="cred", account_url="https://account.blob.core.windows.net", container_name="cont")
    class DummyBean:
        def exists(self):
            return True

    client.container_client = DummyContainerClient()
    client.container_client.get_blob_client = lambda blobpath: DummyBean()

    assert client.exists("path")


class DummyBlob:
    def __init__(self, name, metadata=None):
        self.name = name
        self.metadata = metadata


def test_set_confirmation_metadata_sets_metadata(monkeypatch):
    class DummyBlobClient:
        def __init__(self):
            self.metadata = None

        def set_blob_metadata(self, metadata):
            self.metadata = metadata

    class DummyContainer:
        def __init__(self):
            self.requested_blob = None
            self.blob_client = DummyBlobClient()

        def get_blob_client(self, blob):
            self.requested_blob = blob
            return self.blob_client

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.container_client = DummyContainer()
    client.indicator_file = "indicator/path"
    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper._build_metadata_dict",
        lambda name, version: {"foo": name, "bar": version},
    )

    client._set_confirmation_metadata("demo", "v1")

    assert client.container_client.requested_blob == "indicator/path"
    assert client.container_client.blob_client.metadata == {"foo": "demo", "bar": "v1"}


def test_download_handles_hdi_folder_and_warns(tmp_path, monkeypatch):
    class FolderBlob(DummyBlob):
        def __init__(self):
            super().__init__("prefix/folder", {BLOB_DATASTORE_IS_HDI_FOLDER_KEY: "1"})

    class FileBlob(DummyBlob):
        def __init__(self):
            super().__init__("prefix/file.txt", {})

    class FakeDownload:
        def __init__(self):
            self.size = 150 * 10**6

        def content_as_bytes(self, max_concurrency):
            return b"payload"

    class DummyContainer:
        def __init__(self):
            self.items = [FolderBlob(), FileBlob()]

        def list_blobs(self, name_starts_with, include):
            return self.items

        def download_blob(self, item):
            return FakeDownload()

    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details",
        lambda: {"storage_endpoint": "test"},
    )
    warnings = []
    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper.module_logger.warning",
        lambda message, *args, **kwargs: warnings.append(message),
    )
    client = BlobStorageClient.__new__(BlobStorageClient)
    client.account_name = "accttest"
    client.container = "container"
    client.container_client = DummyContainer()

    client.download("prefix", destination=tmp_path)

    assert (tmp_path / "file.txt").read_bytes() == b"payload"
    assert (tmp_path / "folder").is_dir()
    expected_warning = FILE_SIZE_WARNING.format(
        source=f"https://{client.account_name}.blob.test/{client.container}/prefix",
        destination=tmp_path,
    )
    assert warnings == [expected_warning]


def test_download_reraises_os_error():
    class DummyContainer:
        def list_blobs(self, name_starts_with, include):
            raise OSError("disk full")

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.account_name = "acc"
    client.container = "container"
    client.container_client = DummyContainer()

    with pytest.raises(OSError) as excinfo:
        client.download("prefix")

    assert str(excinfo.value) == "disk full"


def test_download_raises_ml_exception_for_unexpected_error():
    class DummyContainer:
        def list_blobs(self, name_starts_with, include):
            raise ValueError("boom")

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.account_name = "acc"
    client.container = "container"
    client.container_client = DummyContainer()

    with pytest.raises(MlException) as excinfo:
        client.download("prefix")

    assert "Saving blob with prefix" in str(excinfo.value)


def test_list_returns_blob_names():
    class DummyContainer:
        def __init__(self):
            self.name = None

        def list_blobs(self, name_starts_with):
            self.name = name_starts_with
            return [DummyBlob("prefix/one"), DummyBlob("prefix/two")]

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.container_client = DummyContainer()

    result = client.list("prefix")

    assert result == ["prefix/one", "prefix/two"]
    assert client.container_client.name == "prefix"


def test_exists_returns_true_when_blob_exists():
    class BlobClient:
        def exists(self):
            return True

    class DummyContainer:
        def __init__(self):
            self.requested = None

        def get_blob_client(self, blobpath):
            self.requested = blobpath
            return BlobClient()

        def walk_blobs(self, name_starts_with, delimiter):
            return iter([])

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.container_client = DummyContainer()

    assert client.exists("blob/path")
    assert client.container_client.requested == "blob/path"


def test_exists_returns_true_for_virtual_directory():
    class BlobClient:
        def exists(self):
            return False

    class DummyContainer:
        def get_blob_client(self, blobpath):
            return BlobClient()

        def walk_blobs(self, name_starts_with, delimiter):
            yield DummyBlob(name_starts_with + "child")

    client = BlobStorageClient.__new__(BlobStorageClient)
    client.container_client = DummyContainer()

    assert client.exists("dir")


def test_blob_is_hdi_folder_returns_true_for_metadata():
    blob = DummyBlob("folder", {BLOB_DATASTORE_IS_HDI_FOLDER_KEY: "1"})

    assert _blob_is_hdi_folder(blob)


def test_blob_is_hdi_folder_returns_false_without_metadata():
    blob = DummyBlob("file")

    assert not _blob_is_hdi_folder(blob)


class FakeBlobItem:
    def __init__(self, name, metadata=None):
        self.name = name
        self.metadata = metadata or {}


class FakeBlobContent:
    def __init__(self, size, payload):
        self.size = size
        self._payload = payload

    def content_as_bytes(self, max_concurrency):
        return self._payload


class FakeDownloadContainerClient:
    def __init__(self, blobs, blob_content):
        self._blobs = blobs
        self._blob_content = blob_content

    def list_blobs(self, **kwargs):
        return self._blobs

    def download_blob(self, item):
        return self._blob_content


class FakeErrorContainerClient:
    def __init__(self, error):
        self._error = error

    def list_blobs(self, **kwargs):
        raise self._error


class FakeListContainerClient:
    def __init__(self, names):
        self._names = names

    def list_blobs(self, **kwargs):
        return [FakeBlobItem(name) for name in self._names]


class FakeExistsContainerClient:
    def __init__(self, exists_value, walk_entries=None):
        self._exists_value = exists_value
        self._walk_entries = walk_entries or []

    def get_blob_client(self, blobpath):
        class BlobClient:
            def __init__(self, exists_value):
                self._exists_value = exists_value

            def exists(self):
                return self._exists_value

        return BlobClient(self._exists_value)

    def walk_blobs(self, name_starts_with=None, delimiter=None):
        return iter(self._walk_entries)


def test_download_warns_when_size_threshold_exceeded(tmp_path, monkeypatch):
    client = BlobStorageClient.__new__(BlobStorageClient)
    client.account_name = "account"
    client.container = "container"
    blobs = [
        FakeBlobItem("prefix/blob1"),
        FakeBlobItem("prefix/folder", metadata={BLOB_DATASTORE_IS_HDI_FOLDER_KEY: "true"}),
    ]
    content = FakeBlobContent(size=150 * 10**6, payload=b"payload")
    client.container_client = FakeDownloadContainerClient(blobs, content)

    monkeypatch.setattr(helper, "_get_cloud_details", lambda: {"storage_endpoint": "test.endpoint"})
    warnings = []
    monkeypatch.setattr(helper.module_logger, "warning", lambda message: warnings.append(message))

    client.download("prefix", destination=tmp_path)

    assert warnings
    assert (tmp_path / "blob1").read_bytes() == b"payload"


def test_download_wraps_generic_exception_in_ml_exception(tmp_path):
    client = BlobStorageClient.__new__(BlobStorageClient)
    client.account_name = "account"
    client.container = "container"
    client.container_client = FakeErrorContainerClient(ValueError("bad"))

    with pytest.raises(MlException) as excinfo:
        client.download("prefix", destination=tmp_path)

    assert "Saving blob with prefix prefix" in excinfo.value.message
    assert isinstance(excinfo.value.__cause__, ValueError)


def test_exists_returns_false_when_no_blob_or_directory():
    client = BlobStorageClient.__new__(BlobStorageClient)
    client.container_client = FakeExistsContainerClient(False, walk_entries=[])

    assert not client.exists("missing")


def test_blob_is_hdi_folder_identifies_folder_metadata():
    folder_blob = FakeBlobItem("folder", metadata={BLOB_DATASTORE_IS_HDI_FOLDER_KEY: "true"})
    assert _blob_is_hdi_folder(folder_blob)
    file_blob = FakeBlobItem("file")
    assert not _blob_is_hdi_folder(file_blob)


def build_blob_storage_client(container_client):
    client = object.__new__(BlobStorageClient)
    client.account_name = "testaccount"
    client.container = "testcontainer"
    client.container_client = container_client
    client.total_file_count = 1
    client.uploaded_file_count = 0
    client.indicator_file = None
    return client


def test_download_propagates_os_error(monkeypatch, tmp_path):
    class DummyContainer:
        def list_blobs(self, *args, **kwargs):
            raise OSError("simulated failure")

    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details",
        lambda: {"storage_endpoint": "core.windows.net"},
    )
    client = build_blob_storage_client(DummyContainer())
    with pytest.raises(OSError) as excinfo:
        client.download(starts_with="prefix", destination=tmp_path)
    assert str(excinfo.value) == "simulated failure"


def test_download_wraps_unexpected_exception_in_ml_exception(monkeypatch, tmp_path):
    class DummyBlobItem:
        def __init__(self):
            self.name = "prefix/blob.txt"
            self.metadata = {}

    class DummyContainer:
        def list_blobs(self, *args, **kwargs):
            return [DummyBlobItem()]

        def download_blob(self, blob):
            raise ValueError("download failure")

    monkeypatch.setattr(
        "azure.ai.ml._artifacts._blob_storage_helper._get_cloud_details",
        lambda: {"storage_endpoint": "core.windows.net"},
    )
    client = build_blob_storage_client(DummyContainer())
    with pytest.raises(MlException) as excinfo:
        client.download(starts_with="prefix", destination=tmp_path)
    expected_message = "Saving blob with prefix prefix was unsuccessful. exception=download failure"
    assert excinfo.value.args[0] == expected_message
    assert isinstance(excinfo.value.__cause__, ValueError)
