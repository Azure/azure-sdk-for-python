import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from azure.ai.ml._artifacts._constants import (
    UPLOAD_CONFIRMATION,
    ARTIFACT_ORIGIN,
    WORKSPACE_MANAGED_DATASTORE,
    WORKSPACE_MANAGED_DATASTORE_WITH_SLASH,
    AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA,
    INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA,
    BLOB_STORAGE_CLIENT_NAME,
    GEN2_STORAGE_CLIENT_NAME,
)
from azure.ai.ml.exceptions import (
    ValidationException,
    AssetPathException,
    ValidationErrorType,
    ErrorTarget,
    ErrorCategory,
    EmptyDirectoryError,
)
from azure.ai.ml._utils.utils import snake_to_camel
from azure.core.exceptions import ResourceNotFoundError
import azure.ai.ml._utils._asset_utils as asset_utils
from azure.ai.ml._restclient.v2023_04_01.models import PendingUploadRequestDto

from azure.ai.ml._utils._asset_utils import (
    EMPTY_DIRECTORY_ERROR,
    IgnoreFile,
    _build_metadata_dict,
    get_content_hash,
    traverse_directory,
    generate_asset_id,
    _validate_workspace_managed_datastore,
    _validate_auto_delete_setting_in_data_output,
    _check_or_modify_auto_delete_setting,
    _get_latest,
    _get_latest_version_from_container,
    _get_next_latest_versions_from_container,
    _resolve_label_to_asset,
    DirectoryUploadProgressBar,
    upload_directory,
    upload_file,
    FileUploadProgressBar,
    _create_or_update_autoincrement,
    _get_next_version_from_container,
    _archive_or_restore,
    get_storage_info_for_non_registry_asset,
    _get_existing_asset_name_and_version,
)


def test_build_metadata_dict_success_and_name_none():
    name = "my_asset"
    version = "1"
    metadata = _build_metadata_dict(name, version)
    assert metadata["name"] == name
    assert metadata["version"] == version
    for k, v in UPLOAD_CONFIRMATION.items():
        assert metadata[k] == v

    with pytest.raises(ValidationException) as ex:
        _build_metadata_dict("", version)
    assert ex.value.error_type == ValidationErrorType.INVALID_VALUE
    assert ex.value.target == ErrorTarget.ASSET


def test_get_content_hash_returns_none_for_nonexistent_path(tmp_path):
    non_existent = tmp_path / "does_not_exist.txt"
    result = get_content_hash(str(non_existent))
    assert result is None


class DummyIgnoreFile(IgnoreFile):
    def __init__(self, paths_to_ignore):  # type: ignore[no-untyped-def]
        self._paths_to_ignore = {str(p) for p in paths_to_ignore}

    def is_file_excluded(self, file_path):  # type: ignore[no-untyped-def]
        return str(file_path) in self._paths_to_ignore


def test_traverse_directory_respects_ignore_file(tmp_path):
    root = tmp_path
    included_file = root / "included.txt"
    excluded_file = root / "excluded.txt"
    included_file.write_text("included", encoding="utf-8")
    excluded_file.write_text("excluded", encoding="utf-8")

    files = [included_file.name, excluded_file.name]
    ignore_file = DummyIgnoreFile([excluded_file])

    results = list(
        traverse_directory(
            root=str(root),
            files=files,
            prefix="prefix",
            ignore_file=ignore_file,
        )
    )

    paths = [src for src, _ in results]
    assert str(included_file.resolve()) in paths
    assert str(excluded_file.resolve()) not in paths


def test_generate_asset_id_include_directory_flag():
    asset_hash = "abc123"

    with_dir = generate_asset_id(asset_hash, include_directory=True)
    assert with_dir == "/".join((ARTIFACT_ORIGIN, asset_hash))

    without_dir = generate_asset_id(asset_hash, include_directory=False)
    assert without_dir == asset_hash


def test_validate_workspace_managed_datastore_valid_invalid_and_other():
    # Valid managed datastore path (exact match)
    result = _validate_workspace_managed_datastore(WORKSPACE_MANAGED_DATASTORE)
    assert result == WORKSPACE_MANAGED_DATASTORE + "/paths"

    # Invalid managed datastore path (starts with managed datastore but extra segment)
    invalid_path = WORKSPACE_MANAGED_DATASTORE_WITH_SLASH + "foo"
    with pytest.raises(AssetPathException) as ex:
        _validate_workspace_managed_datastore(invalid_path)
    assert ex.value.message == INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA

    # Non-managed datastore path should pass through unchanged
    other_path = "some/other/path"
    assert _validate_workspace_managed_datastore(other_path) == other_path


def test_validate_auto_delete_setting_in_data_output():
    with pytest.raises(ValidationException) as ex:
        _validate_auto_delete_setting_in_data_output({"some": "value"})
    assert ex.value.message == AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA
    assert ex.value.error_category == ErrorCategory.USER_ERROR  # type: ignore[attr-defined]

    # None should be allowed (no exception)
    _validate_auto_delete_setting_in_data_output(None)


class AutoDeleteObject:
    def __init__(self, condition):  # type: ignore[no-untyped-def]
        self.condition = condition


def test_check_or_modify_auto_delete_setting_object_and_dict():
    obj = AutoDeleteObject("match_any")
    _check_or_modify_auto_delete_setting(obj)
    assert obj.condition == snake_to_camel("match_any")

    setting_dict = {"condition": "match_all"}
    _check_or_modify_auto_delete_setting(setting_dict)
    assert setting_dict["condition"] == snake_to_camel("match_all")

    # None should be a no-op
    _check_or_modify_auto_delete_setting(None)


class FakeVersionOperationNoResults:
    def list(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self

    def next(self):  # type: ignore[no-untyped-def]
        raise StopIteration


def test_get_latest_raises_when_no_versions():
    version_operation = FakeVersionOperationNoResults()

    with pytest.raises(ValidationException) as ex:
        _get_latest(
            asset_name="asset1",
            version_operation=version_operation,
            resource_group_name="rg",
            workspace_name="ws",
        )

    err = ex.value
    assert err.error_type == ValidationErrorType.RESOURCE_NOT_FOUND
    assert err.target == ErrorTarget.ASSET
    assert "does not exist in workspace ws" in err.message


class FakeContainerOperationNotFound:
    def get(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise ResourceNotFoundError("not found")


def test_get_latest_version_from_container_raises_when_not_found():
    container_operation = FakeContainerOperationNotFound()

    with pytest.raises(ValidationException) as ex:
        _get_latest_version_from_container(
            asset_name="asset2",
            container_operation=container_operation,
            resource_group_name="rg",
            registry_name="reg",
        )

    err = ex.value
    assert err.error_type == ValidationErrorType.RESOURCE_NOT_FOUND
    assert err.target == ErrorTarget.ASSET
    assert "does not exist in registry reg" in err.message


class FakeAssetOperations:
    def __init__(self, resolver_map, registry_name=None):  # type: ignore[no-untyped-def]
        self._managed_label_resolver = resolver_map
        self._registry_name = registry_name


def test_resolve_label_to_asset_not_found_and_success():
    name = "my_asset"
    label = "latest"

    # Case 1: no resolver found -> ValidationException
    ops_no_resolver = FakeAssetOperations({}, registry_name=None)
    with pytest.raises(ValidationException) as ex:
        _resolve_label_to_asset(ops_no_resolver, name, label)
    msg = "Asset {} with version label {} does not exist in {}.".format(name, label, "workspace")
    assert ex.value.message == msg

    # Case 2: resolver present -> returns asset
    expected_result = ("resolved", name)

    def resolver(asset_name):  # type: ignore[no-untyped-def]
        return ("resolved", asset_name)

    ops_with_resolver = FakeAssetOperations({label: resolver}, registry_name="reg")
    result = _resolve_label_to_asset(ops_with_resolver, name, label)
    assert result == expected_result


class DummyDirectoryClient:
    def __init__(self):
        self.created_subdirs = []
        self.last_file_client = None

    def create_sub_directory(self, name):
        self.created_subdirs.append(name)
        return DummySubDirectoryClient(self)


class DummySubDirectoryClient:
    def __init__(self, directory_client: DummyDirectoryClient):
        self._directory_client = directory_client

    def create_sub_directory(self, name):
        self._directory_client.created_subdirs.append(name)
        return self

    def create_file(self, name):
        self._directory_client.last_file_client = DummyFileClient()
        return self._directory_client.last_file_client


class DummyFileClient:
    def __init__(self):
        self.upload_calls = []

    def upload_data(self, **kwargs):
        self.upload_calls.append(kwargs)


def _make_gen2_storage_client():
    Gen2ClientClass = type(GEN2_STORAGE_CLIENT_NAME, (), {})
    client = Gen2ClientClass()
    client.directory_client = DummyDirectoryClient()
    client.temp_sub_directory_client = None
    client.file_client = None
    client.uploaded_file_count = 0
    return client


class DummyContainerClient:
    def __init__(self):
        self.upload_calls = []

    def upload_blob(
        self,
        name,
        data,
        validate_content,
        overwrite,
        raw_response_hook,
        max_concurrency,
        connection_timeout,
    ):
        if raw_response_hook is not None:
            class Response:
                pass

            response = Response()
            response.context = {
                "upload_stream_current": 10,
                "data_stream_total": 10,
            }
            raw_response_hook(response)
        self.upload_calls.append(
            {
                "name": name,
                "validate_content": validate_content,
                "overwrite": overwrite,
                "max_concurrency": max_concurrency,
                "connection_timeout": connection_timeout,
            }
        )


def _make_blob_storage_client():
    BlobClientClass = type(BLOB_STORAGE_CLIENT_NAME, (), {})
    client = BlobClientClass()
    client.container_client = DummyContainerClient()
    client.overwrite = True
    client.uploaded_file_count = 0
    client.total_file_count = 0
    client.indicator_file = None
    client._check_blob_exists_called = False

    def check_blob_exists():
        client._check_blob_exists_called = True

    client.check_blob_exists = check_blob_exists
    return client


def test_upload_file_gen2_in_directory_creates_subdirs_and_uploads():
    storage_client = _make_gen2_storage_client()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "file.txt"
        file_path.write_text("content", encoding="utf-8")
        dest = os.path.join("LocalUpload", "assetid", "dir1", "dir2", "file.txt")

        upload_file(
            storage_client=storage_client,
            source=str(file_path),
            dest=dest,
            msg=None,
            size=os.path.getsize(file_path),
            show_progress=False,
            in_directory=True,
        )

        assert storage_client.uploaded_file_count == 1
        assert storage_client.directory_client.created_subdirs == ["dir1", "dir2"]
        file_client = storage_client.directory_client.last_file_client
        assert isinstance(file_client, DummyFileClient)
        assert len(file_client.upload_calls) == 1
        call_kwargs = file_client.upload_calls[0]
        assert call_kwargs["overwrite"] is True
        assert call_kwargs["validate_content"] is True


def test_upload_file_blob_with_and_without_progress():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path_small = Path(tmpdir) / "small.txt"
        file_path_small.write_text("small", encoding="utf-8")

        # First call: no progress bar
        storage_client_no_progress = _make_blob_storage_client()
        upload_file(
            storage_client=storage_client_no_progress,
            source=str(file_path_small),
            dest="container/path/small.txt",
            msg="Upload small",
            size=os.path.getsize(file_path_small),
            show_progress=False,
            in_directory=False,
        )
        assert storage_client_no_progress.uploaded_file_count == 1
        assert len(storage_client_no_progress.container_client.upload_calls) == 1
        call_kwargs = storage_client_no_progress.container_client.upload_calls[0]
        assert call_kwargs["name"] == "container/path/small.txt"
        assert call_kwargs["validate_content"] is True
        assert call_kwargs["overwrite"] is True

        # Second call: with progress bar (non-directory)
        storage_client_progress = _make_blob_storage_client()
        upload_file(
            storage_client=storage_client_progress,
            source=str(file_path_small),
            dest="container/path/small2.txt",
            msg="Uploading small2",
            size=os.path.getsize(file_path_small),
            show_progress=True,
            in_directory=False,
        )
        assert storage_client_progress.uploaded_file_count == 1
        assert len(storage_client_progress.container_client.upload_calls) == 1
        progress_call_kwargs = storage_client_progress.container_client.upload_calls[0]
        assert progress_call_kwargs["name"] == "container/path/small2.txt"
        assert progress_call_kwargs["validate_content"] is True


def test_upload_directory_empty_raises_empty_directory_error():
    storage_client = _make_blob_storage_client()
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(EmptyDirectoryError) as exc:
            upload_directory(
                storage_client=storage_client,
                source=tmpdir,
                dest="",
                msg="Uploading dir",
                show_progress=False,
                ignore_file=IgnoreFile(None),
            )
        assert tmpdir in exc.value.message


def test_upload_directory_non_empty_blob_sets_indicator_and_uploads():
    storage_client = _make_blob_storage_client()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "file.txt"
        file_path.write_text("data", encoding="utf-8")

        upload_directory(
            storage_client=storage_client,
            source=tmpdir,
            dest="destprefix",
            msg="Uploading dir",
            show_progress=False,
            ignore_file=IgnoreFile(None),
        )

        assert storage_client.total_file_count == 1
        assert storage_client.uploaded_file_count == 1
        assert storage_client.indicator_file is not None
        assert storage_client._check_blob_exists_called is True


def test_directory_upload_progress_bar_update_to_branches():
    bar = DirectoryUploadProgressBar(dir_size=100, msg="dir upload")

    class Response:
        def __init__(self, current):
            self.context = {
                "upload_stream_current": current,
            }

    # When current is positive, completed and n should be updated
    response_positive = Response(40)
    bar.update_to(response_positive)
    assert bar.completed == 40
    assert bar.n == 40

    # When current is zero, nothing should change
    bar_zero = DirectoryUploadProgressBar(dir_size=100, msg="dir upload 2")
    response_zero = Response(0)
    bar_zero.update_to(response_zero)
    assert bar_zero.completed == 0
    assert bar_zero.n == 0


class DummyProperties:
    def __init__(self, next_version=None, latest_version=None, is_archived=False):
        self.next_version = next_version
        self.latest_version = latest_version
        self.is_archived = is_archived


class DummyContainer:
    def __init__(self, next_version=None, latest_version=None, is_archived=False):
        self.properties = DummyProperties(next_version=next_version, latest_version=latest_version, is_archived=is_archived)


class DummyContainerOperation:
    def __init__(self, container=None, raise_not_found=False):
        self.container = container
        self.raise_not_found = raise_not_found
        self.called_with = {}

    def get(self, **kwargs):
        self.called_with = kwargs.copy()
        if self.raise_not_found:
            raise ResourceNotFoundError("not found")
        return self.container or DummyContainer(next_version="1", latest_version="1")


class DummyVersionOperation:
    def __init__(self, result=None):
        self.result = result
        self.called_with = {}

    def create_or_update(self, **kwargs):
        self.called_with = kwargs.copy()
        return self.result


...