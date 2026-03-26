import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from colorama import Fore

import azure.ai.ml._artifacts._gen2_storage_helper as helper_module
from azure.ai.ml._artifacts._gen2_storage_helper import FILE_SIZE_WARNING, Gen2StorageClient
from azure.ai.ml.exceptions import MlException


class DummyDirectoryClient:
    def __init__(self):
        self._metadata = {}

    def exists(self):
        return False

    def get_directory_properties(self):
        return SimpleNamespace(metadata=self._metadata)

    def set_metadata(self, metadata):
        self._metadata = metadata


class DummyFileSystemClient:
    def __init__(self, directory_client):
        self._directory_client = directory_client

    def create_file_system(self):
        return None

    def get_directory_client(self, asset_id):
        return self._directory_client


class DummyDataLakeServiceClient:
    def __init__(self, account_url, credential, api_version=None):
        self._file_system_client = DummyFileSystemClient(DummyDirectoryClient())

    def get_file_system_client(self, file_system):
        return self._file_system_client


def test_upload_truncates_long_source_name_and_warns_large_file(monkeypatch, tmp_path):
    monkeypatch.setattr(helper_module, "DataLakeServiceClient", DummyDataLakeServiceClient)
    monkeypatch.setattr(helper_module, "generate_asset_id", lambda asset_hash, include_directory=True: "asset123")
    monkeypatch.setattr(helper_module, "get_directory_size", lambda source: (150 * 10**6, 0))
    monkeypatch.setattr(helper_module, "_get_cloud_details", lambda: {"storage_endpoint": "test.endpoint"})
    warning_calls = []
    monkeypatch.setattr(helper_module.module_logger, "warning", lambda msg: warning_calls.append(msg))
    long_name = "a" * 60
    source = tmp_path / long_name
    captured = {}

    def fake_upload_directory(**kwargs):
        captured["msg"] = kwargs["msg"]
        kwargs["storage_client"].uploaded_file_count = kwargs["storage_client"].total_file_count

    monkeypatch.setattr(helper_module, "upload_directory", fake_upload_directory)
    monkeypatch.setattr(helper_module, "upload_file", lambda **kwargs: pytest.fail("upload_file should not be called"))
    monkeypatch.setattr(helper_module.os.path, "isdir", lambda path: path == str(source))

    client = Gen2StorageClient("cred", "fs", "https://example.dfs.core.windows.net")
    client.total_file_count = 0

    artifact_info = client.upload(str(source), name="asset", version="1.0")

    expected_msg = Fore.GREEN + "Uploading " + ("a" * 47 + "...")
    assert captured["msg"] == expected_msg

    expected_remote_path = f"asset123/{long_name}"
    assert artifact_info["remote path"] == expected_remote_path

    expected_destination = (
        f"https://{client.account_name}.dfs.test.endpoint/{client.file_system}/{artifact_info['remote path']}"
    )
    expected_warning = FILE_SIZE_WARNING.format(source=str(source), destination=expected_destination)
    assert warning_calls == [expected_warning]


def test_upload_uses_short_source_name_for_file_upload(monkeypatch, tmp_path):
    monkeypatch.setattr(helper_module, "DataLakeServiceClient", DummyDataLakeServiceClient)
    monkeypatch.setattr(helper_module, "generate_asset_id", lambda asset_hash, include_directory=True: "asset123")
    monkeypatch.setattr(helper_module, "get_directory_size", lambda source: (50 * 10**6, 0))
    monkeypatch.setattr(helper_module, "_get_cloud_details", lambda: {"storage_endpoint": "test.endpoint"})
    warning_calls = []
    monkeypatch.setattr(helper_module.module_logger, "warning", lambda msg: warning_calls.append(msg))
    captured = {}

    def fake_upload_file(**kwargs):
        captured["msg"] = kwargs["msg"]
        kwargs["storage_client"].uploaded_file_count = kwargs["storage_client"].total_file_count

    monkeypatch.setattr(helper_module, "upload_directory", lambda **kwargs: pytest.fail("upload_directory should not be called"))
    monkeypatch.setattr(helper_module, "upload_file", fake_upload_file)
    monkeypatch.setattr(helper_module.os.path, "isdir", lambda path: False)

    client = Gen2StorageClient("cred", "fs", "https://example.dfs.core.windows.net")
    client.total_file_count = 0

    artifact_info = client.upload(str(tmp_path / "file.txt"), name="asset", version="2.0")

    expected_msg = Fore.GREEN + "Uploading file.txt"
    assert captured["msg"] == expected_msg
    assert warning_calls == []
    expected_remote_path = "asset123/file.txt"
    assert artifact_info["remote path"] == expected_remote_path


class FakeFileClient:
    def __init__(self, size, content):
        self._size = size
        self._content = content

    def get_file_properties(self):
        return SimpleNamespace(size=self._size)

    def download_file(self):
        return SimpleNamespace(readall=lambda: self._content)


class FakeFileSystemClient:
    def __init__(self, paths=None, file_clients=None, raise_os=False, raise_exception=None):
        self._paths = paths or []
        self._file_clients = file_clients or {}
        self._raise_os = raise_os
        self._raise_exception = raise_exception

    def get_paths(self, path):
        if self._raise_os:
            raise OSError("boom")
        if self._raise_exception:
            raise self._raise_exception
        return self._paths

    def get_file_client(self, name):
        return self._file_clients[name]


def _build_client(paths=None, file_clients=None, **kwargs):
    client = object.__new__(Gen2StorageClient)
    client.account_name = "account"
    client.file_system = "filesystem"
    client.file_system_client = FakeFileSystemClient(paths=paths, file_clients=file_clients, **kwargs)
    return client


def _patch_cloud(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml._artifacts._gen2_storage_helper._get_cloud_details",
        lambda: {"storage_endpoint": "test.endpoint"},
    )


def test_download_warns_and_writes_file_when_size_exceeds_limit(tmp_path, monkeypatch):
    _patch_cloud(monkeypatch)
    paths = [
        SimpleNamespace(name="prefix/dir", is_directory=True),
        SimpleNamespace(name="prefix/file.txt", is_directory=False),
    ]
    file_client = FakeFileClient(size=200 * 10**6, content=b"payload")
    client = _build_client(paths=paths, file_clients={"prefix/file.txt": file_client})

    warning_calls = []
    monkeypatch.setattr(helper_module.module_logger, "warning", lambda msg: warning_calls.append(msg))

    def _raise_file_exists(path, exist_ok=False):
        Path(path).mkdir(parents=True, exist_ok=True)
        raise FileExistsError("exists")

    monkeypatch.setattr("os.makedirs", _raise_file_exists)
    client.download("prefix", destination=tmp_path)

    assert (tmp_path / "dir").is_dir()
    assert (tmp_path / "file.txt").read_bytes() == b"payload"
    assert warning_calls
    warning_text = warning_calls[0]
    assert "https://account.dfs.test.endpoint/filesystem/prefix" in warning_text
    assert str(tmp_path) in warning_text


def test_download_propagates_os_error():
    client = _build_client(raise_os=True)
    with pytest.raises(OSError):
        client.download("prefix", destination="dest")


def test_download_wraps_non_os_errors_in_ml_exception(monkeypatch):
    _patch_cloud(monkeypatch)
    error = ValueError("boom")
    client = _build_client(raise_exception=error)
    with pytest.raises(MlException) as excinfo:
        client.download("prefix", destination="dest")
    assert "Saving output with prefix prefix was unsuccessful" in str(excinfo.value)


class FileSystemClientStub:
    def __init__(self, paths=None, file_client=None):
        self.paths = paths or []
        self.file_client = file_client
        self.file_system = None
        self.requested_path = None
        self.requested_client_path = None
        self.created = False

    def create_file_system(self):
        self.created = True

    def get_paths(self, path):
        self.requested_path = path
        return self.paths

    def get_file_client(self, path):
        self.requested_client_path = path
        if self.file_client is not None:
            self.file_client.requested_path = path
        return self.file_client


class FileClientStub:
    def __init__(self, exists_value):
        self.exists_value = exists_value
        self.requested_path = None

    def exists(self):
        self.exists_called = True
        return self.exists_value


def _build_client_with_fs_client(monkeypatch, *, paths=None, file_client=None):
    file_client = file_client or FileClientStub(False)
    fs_client = FileSystemClientStub(paths=paths, file_client=file_client)

    class DataLakeServiceClientStub:
        def __init__(self, account_url, credential, api_version=None):
            self.account_url = account_url
            self.credential = credential
            self.api_version = api_version

        def get_file_system_client(self, file_system):
            fs_client.file_system = file_system
            return fs_client

    monkeypatch.setattr(
        "azure.ai.ml._artifacts._gen2_storage_helper.DataLakeServiceClient",
        DataLakeServiceClientStub,
    )
    client = Gen2StorageClient(
        credential="credential",
        file_system="filesystem",
        account_url="https://account.dfs.azure.com",
    )
    return client, fs_client


def test_list_returns_names(monkeypatch):
    client, fs_client = _build_client_with_fs_client(
        monkeypatch,
        paths=[{"name": "prefix/file1"}, {"name": "prefix/file2"}],
    )
    result = client.list("prefix")
    assert result == ["prefix/file1", "prefix/file2"]
    assert fs_client.requested_path == "prefix"


def test_exists_returns_true(monkeypatch):
    file_client = FileClientStub(True)
    client, fs_client = _build_client_with_fs_client(monkeypatch, file_client=file_client)

    result = client.exists("some/path")
    assert result is True
    assert file_client.requested_path == "some/path"
    assert fs_client.requested_client_path == "some/path"


def test_exists_returns_false(monkeypatch):
    file_client = FileClientStub(False)
    client, _ = _build_client_with_fs_client(monkeypatch, file_client=file_client)

    result = client.exists("other/path")
    assert result is False
    assert file_client.requested_path == "other/path"
