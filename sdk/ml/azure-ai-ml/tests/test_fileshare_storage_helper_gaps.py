import logging
import pytest

from azure.ai.ml._artifacts import _fileshare_storage_helper as helper
from azure.ai.ml._artifacts._fileshare_storage_helper import delete, recursive_download
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException
from azure.storage.fileshare import ShareFileClient


def test_upload_truncates_long_source_name_and_warns_on_large_file(tmp_path, caplog, monkeypatch, capsys):
    caplog.set_level(logging.WARNING, logger=helper.__name__)
    source_file = tmp_path / ("a" * 52)
    source_file.write_text("content")
    asset_id = "artifact123"

    monkeypatch.setattr(helper, "generate_asset_id", lambda asset_hash, include_directory=False: asset_id)
    monkeypatch.setattr(helper, "get_directory_size", lambda source: (150 * 10**6, None))
    monkeypatch.setattr(helper.time, "sleep", lambda _: None)
    monkeypatch.setattr(helper.FileStorageClient, "exists", lambda self, asset_id_arg: False)
    recorded = {}

    def fake_upload_file(
        self,
        source,
        dest,
        show_progress=False,
        msg=None,
        in_directory=False,
        subdirectory_client=None,
        callback=None,
    ):
        recorded["msg"] = msg
        self.uploaded_file_count = self.total_file_count

    monkeypatch.setattr(helper.FileStorageClient, "upload_file", fake_upload_file)

    confirmation = {}

    def fake_set_confirmation_metadata(self, source, dest, name, version):
        confirmation["called_with"] = (source, dest, name, version)

    monkeypatch.setattr(helper.FileStorageClient, "_set_confirmation_metadata", fake_set_confirmation_metadata)

    warning_called = {}
    original_warning = helper.module_logger.warning

    def fake_warning(message):
        warning_called["message"] = message
        return original_warning(message)

    monkeypatch.setattr(helper.module_logger, "warning", fake_warning)

    client = helper.FileStorageClient.__new__(helper.FileStorageClient)
    client.directory_client = type(
        "DummyDirectoryClient",
        (),
        {"list_directories_and_files": lambda self, *args, **kwargs: []},
    )()
    client.legacy_directory_client = client.directory_client
    client.file_share = "share"
    client.total_file_count = 1
    client.uploaded_file_count = 0
    client.name = None
    client.version = None
    client.legacy = False
    client.subdirectory_client = None

    artifact_info = client.upload(str(source_file), name="name", version="version", show_progress=True)

    stderr_output = capsys.readouterr().err

    expected_msg = "Uploading " + source_file.name[:47] + "..."
    assert recorded["msg"] == expected_msg
    assert artifact_info["remote path"] == f"{asset_id}/{source_file.name}"
    assert confirmation["called_with"] == (str(source_file), asset_id, "name", "version")
    warning_prefix = helper.FILE_SIZE_WARNING.split("\n\n")[0]
    warning_logged = any(helper.FILE_SIZE_WARNING in record.getMessage() for record in caplog.records)
    warning_message = warning_called.get("message", "")
    assert warning_logged or warning_prefix in stderr_output or warning_prefix in warning_message


def test_exists_deletes_incomplete_asset_when_legacy_directory_missing(monkeypatch):
    asset_id = "artifact123"
    default_client = type(
        "DefaultDirectoryClient",
        (),
        {"list_directories_and_files": lambda self, *args, **kwargs: [{"name": asset_id, "is_directory": False}]},
    )()

    class LegacyDirectoryClient:
        def __init__(self):
            self.called = False

        def list_directories_and_files(self, *args, **kwargs):
            self.called = True
            raise helper.ResourceNotFoundError("missing")

    legacy_client = LegacyDirectoryClient()
    metadata_target = object()
    metadata_properties = {"metadata": {}}

    def fake_get_asset_metadata(self, asset_id_arg, default_items, legacy_items):
        return metadata_target, metadata_properties

    monkeypatch.setattr(helper.FileStorageClient, "_get_asset_metadata", fake_get_asset_metadata)
    deleted = []

    def fake_delete(client_arg):
        deleted.append(client_arg)

    monkeypatch.setattr(helper, "delete", fake_delete)

    client = helper.FileStorageClient.__new__(helper.FileStorageClient)
    client.directory_client = default_client
    client.legacy_directory_client = legacy_client
    client.file_share = "share"
    client.total_file_count = 1
    client.uploaded_file_count = 0
    client.name = None
    client.version = None
    client.legacy = False
    client.subdirectory_client = None

    result = helper.FileStorageClient.exists(client, asset_id)

    assert legacy_client.called
    assert deleted == [metadata_target]
    assert result is False


def test_recursive_download_writes_files_and_traverses_nested_directories(tmp_path):
    class DummyStream:
        def __init__(self, data):
            self._data = data

        def readall(self):
            return self._data

    class DummyFileClient:
        def __init__(self, content):
            self._content = content

        def download_file(self, max_concurrency):
            return DummyStream(self._content)

    class DummyDirectoryClient:
        def __init__(self, items, file_contents=None, subclients=None):
            self._items = items
            self._file_contents = file_contents or {}
            self._subclients = subclients or {}

        def list_directories_and_files(self, name_starts_with=""):
            return self._items

        def get_file_client(self, name):
            return DummyFileClient(self._file_contents[name])

        def get_subdirectory_client(self, name):
            if name not in self._subclients:
                self._subclients[name] = DummyDirectoryClient([])
            return self._subclients[name]

    inner_client = DummyDirectoryClient(
        items=[{"name": "inner.txt", "is_directory": False}],
        file_contents={"inner.txt": b"inner bytes"},
    )
    root_client = DummyDirectoryClient(
        items=[
            {"name": "file.txt", "is_directory": False},
            {"name": "nested", "is_directory": True},
        ],
        file_contents={"file.txt": b"root bytes"},
        subclients={"nested": inner_client},
    )

    destination = str(tmp_path / "downloads")
    recursive_download(
        client=root_client,
        destination=destination,
        max_concurrency=1,
    )

    assert (tmp_path / "downloads" / "file.txt").read_bytes() == b"root bytes"
    assert (tmp_path / "downloads" / "nested" / "inner.txt").read_bytes() == b"inner bytes"


def test_recursive_download_raises_ml_exception_on_list_failure(tmp_path):
    class FailingDirectoryClient:
        def list_directories_and_files(self, name_starts_with=""):
            raise RuntimeError("boom")

    with pytest.raises(MlException) as excinfo:
        recursive_download(
            client=FailingDirectoryClient(),
            destination=str(tmp_path / "dest"),
            max_concurrency=1,
            starts_with="pref",
        )

    assert excinfo.value.message == "Saving fileshare directory with prefix pref was unsuccessful."
    assert excinfo.value.no_personal_data_message == "Saving fileshare directory with prefix pref was unsuccessful."
    assert excinfo.value.target == ErrorTarget.ARTIFACT
    assert excinfo.value.error_category == ErrorCategory.SYSTEM_ERROR


class _DummyShareFileClient(ShareFileClient):
    def __init__(self):
        self.delete_calls = 0

    def delete_file(self):
        self.delete_calls += 1


class _DummyTrackingDirectoryClient:
    def __init__(self, name, files=None, directories=None):
        self.name = name
        self.files = files or []
        self.directories = directories or {}
        self.deleted_files = []
        self.deleted_directories = []

    def list_directories_and_files(self, name_starts_with=None):
        items = [{'name': file_name, 'is_directory': False} for file_name in self.files]
        items.extend({'name': dir_name, 'is_directory': True} for dir_name in self.directories)
        return items

    def delete_file(self, name=None):
        self.deleted_files.append(name)

    def get_subdirectory_client(self, name):
        return self.directories[name]

    def delete_directory(self):
        self.deleted_directories.append(self.name)


class _DummyFileContent:
    def __init__(self, data):
        self._data = data

    def readall(self):
        return self._data


class _DummyFileClient:
    def __init__(self, data):
        self._data = data
        self.download_calls = []

    def download_file(self, max_concurrency):
        self.download_calls.append(max_concurrency)
        return _DummyFileContent(self._data)


class _DummyShareDirectoryClient:
    def __init__(self, files=None, directories=None):
        self._files = files or {}
        self._directories = directories or {}
        self.list_calls = []

    def list_directories_and_files(self, name_starts_with=None):
        self.list_calls.append(name_starts_with)
        items = [{'name': name, 'is_directory': False} for name in self._files]
        items.extend({'name': name, 'is_directory': True} for name in self._directories)
        return items

    def get_file_client(self, name):
        return _DummyFileClient(self._files[name])

    def get_subdirectory_client(self, name):
        return self._directories[name]


class _FailingShareDirectoryClient:
    def list_directories_and_files(self, name_starts_with=None):
        raise RuntimeError('cannot list contents')


def test_delete_share_file_client_deletes_single_file():
    file_client = _DummyShareFileClient()

    delete(file_client)

    assert file_client.delete_calls == 1


def test_delete_directory_without_contents_only_deletes_directory():
    client = _DummyTrackingDirectoryClient(name='empty')

    delete(client)

    assert client.deleted_files == []
    assert client.deleted_directories == ['empty']


def test_delete_directory_with_contents_recurses_over_files_and_directories():
    child = _DummyTrackingDirectoryClient(name='nested', files=['deep.txt'])
    parent = _DummyTrackingDirectoryClient(
        name='parent',
        files=['root.txt'],
        directories={'nested': child},
    )

    delete(parent)

    assert parent.deleted_files == ['root.txt']
    assert parent.deleted_directories == ['parent']
    assert child.deleted_files == ['deep.txt']
    assert child.deleted_directories == ['nested']


def test_recursive_download_writes_nested_files(tmp_path):
    nested = _DummyShareDirectoryClient(files={'nested.txt': b'nested'})
    root = _DummyShareDirectoryClient(
        files={'root.txt': b'root'},
        directories={'nested': nested},
    )
    destination = tmp_path / 'downloaded'

    recursive_download(root, destination=str(destination), max_concurrency=2)

    root_file = destination / 'root.txt'
    nested_file = destination / 'nested' / 'nested.txt'

    assert root_file.read_bytes() == b'root'
    assert nested_file.read_bytes() == b'nested'


def test_recursive_download_raises_ml_exception_on_list_failure():
    failing_client = _FailingShareDirectoryClient()

    with pytest.raises(MlException) as excinfo:
        recursive_download(
            failing_client,
            destination='unused',
            max_concurrency=1,
            starts_with='prefix',
        )

    exception = excinfo.value
    assert exception.message == 'Saving fileshare directory with prefix prefix was unsuccessful.'
    assert exception.no_personal_data_message == 'Saving fileshare directory with prefix prefix was unsuccessful.'
    assert exception.target == ErrorTarget.ARTIFACT
    assert exception.error_category == ErrorCategory.SYSTEM_ERROR
