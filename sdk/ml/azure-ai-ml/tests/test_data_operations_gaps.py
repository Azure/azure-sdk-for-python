import os
import tempfile
import uuid
from types import SimpleNamespace

import pytest

from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.exceptions import MlException, ValidationErrorType, ValidationException
from azure.ai.ml.operations import _data_operations as data_ops_module
from azure.ai.ml.operations._data_operations import DataOperations, _assert_local_path_matches_asset_type


def _build_data_operations_for_validate():
    operations = object.__new__(DataOperations)
    operations._datastore_operation = object()
    operations._requests_pipeline = object()
    operations._operation_scope = SimpleNamespace(
        _resource_group_name="rg",
        _subscription_id="sub",
        _workspace_name="ws",
        registry_name=None,
    )
    operations._scope_kwargs = {}
    operations._init_kwargs = {}
    return operations


def _build_data_operations_stub():
    data_operations = DataOperations.__new__(DataOperations)
    data_operations._datastore_operation = SimpleNamespace()
    data_operations._requests_pipeline = SimpleNamespace()
    data_operations._operation_scope = SimpleNamespace(
        _subscription_id="sub",
        _resource_group_name="rg",
        _workspace_name="ws",
        registry_name=None,
    )
    data_operations._scope_kwargs = {}
    data_operations._init_kwargs = {}
    return data_operations


def test_get_with_version_and_label_raises():
    operations = object.__new__(DataOperations)
    with pytest.raises(MlException) as error:
        operations.get(name="data", version="1", label="latest")
    assert "Cannot specify both version and label." in str(error.value)


def test_get_without_version_or_label_raises():
    operations = object.__new__(DataOperations)
    with pytest.raises(MlException) as error:
        operations.get(name="data")
    assert "Must provide either version or label." in str(error.value)


def test_validate_remote_mltable_read_failure_skips_validation(monkeypatch):
    operations = _build_data_operations_for_validate()
    data = SimpleNamespace(
        path="https://example.com/mltable",
        type=AssetTypes.MLTABLE,
        base_path="",
        _mltable_schema_url=None,
        _skip_validation=False,
    )
    monkeypatch.setattr(data_ops_module, "is_url", lambda _value: True)

    def _raise(*_, **__):
        raise RuntimeError("unreachable")

    monkeypatch.setattr(
        data_ops_module,
        "read_remote_mltable_metadata_contents",
        _raise,
    )
    assert operations._validate(data) is None


def test_validate_remote_non_mltable_skips_validation(monkeypatch):
    operations = _build_data_operations_for_validate()
    data = SimpleNamespace(
        path="https://example.com/data",
        type=AssetTypes.URI_FOLDER,
        base_path="",
        _mltable_schema_url=None,
        _skip_validation=False,
    )
    monkeypatch.setattr(data_ops_module, "is_url", lambda _value: True)
    assert operations._validate(data) is None


def test_validate_absolute_path_mismatch_raises(monkeypatch):
    operations = _build_data_operations_for_validate()
    random_path = os.path.join(tempfile.gettempdir(), f"missing_{uuid.uuid4().hex}")
    assert not os.path.exists(random_path)
    data = SimpleNamespace(
        path=random_path,
        type=AssetTypes.URI_FOLDER,
        base_path="",
        _mltable_schema_url=None,
        _skip_validation=False,
    )
    monkeypatch.setattr(data_ops_module, "is_url", lambda _value: False)
    with pytest.raises(ValidationException) as error:
        operations._validate(data)
    assert "File path does not match asset type" in str(error.value)


def test_assert_local_path_matches_asset_type_folder_mismatch():
    random_path = os.path.join(tempfile.gettempdir(), f"missing_folder_{uuid.uuid4().hex}")
    assert not os.path.exists(random_path)
    with pytest.raises(ValidationException) as error:
        _assert_local_path_matches_asset_type(random_path, AssetTypes.URI_FOLDER)
    assert "File path does not match asset type" in str(error.value)


def test_assert_local_path_matches_asset_type_file_mismatch():
    random_path = os.path.join(tempfile.gettempdir(), f"missing_file_{uuid.uuid4().hex}")
    assert not os.path.exists(random_path)
    with pytest.raises(ValidationException) as error:
        _assert_local_path_matches_asset_type(random_path, AssetTypes.URI_FILE)
    assert "File path does not match asset type" in str(error.value)


def test_validate_returns_none_when_remote_mltable_metadata_cannot_be_read(monkeypatch):
    data_operations = _build_data_operations_stub()
    remote_data = SimpleNamespace(
        path="https://example.com/fake",
        type=AssetTypes.MLTABLE,
        base_path=".",
        _mltable_schema_url=None,
        _skip_validation=False,
    )

    def _raise_error(*_, **__):
        raise RuntimeError("test failure")

    monkeypatch.setattr(
        data_ops_module,
        "read_remote_mltable_metadata_contents",
        _raise_error,
    )
    result = data_operations._validate(remote_data)
    assert result is None


def test_try_get_mltable_metadata_jsonschema_returns_schema_when_available(monkeypatch):
    data_operations = _build_data_operations_stub()
    pipeline = SimpleNamespace()
    data_operations._requests_pipeline = pipeline
    expected_schema = {"example": "schema"}
    captured = {}

    def _download(url, requests_pipeline):
        captured["url"] = url
        captured["pipeline"] = requests_pipeline
        return expected_schema

    monkeypatch.setattr(
        data_ops_module,
        "download_mltable_metadata_schema",
        _download,
    )
    result = data_operations._try_get_mltable_metadata_jsonschema(None)
    assert result is expected_schema
    assert captured["pipeline"] is pipeline


def test_try_get_mltable_metadata_jsonschema_returns_none_when_download_fails(monkeypatch):
    data_operations = _build_data_operations_stub()
    pipeline = SimpleNamespace()
    data_operations._requests_pipeline = pipeline

    def _download(_, __):
        raise RuntimeError("unreachable")

    monkeypatch.setattr(
        data_ops_module,
        "download_mltable_metadata_schema",
        _download,
    )
    result = data_operations._try_get_mltable_metadata_jsonschema("https://custom/schema")
    assert result is None


def test_assert_local_path_matches_asset_type_raises_when_folder_missing(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("content")
    with pytest.raises(ValidationException) as excinfo:
        _assert_local_path_matches_asset_type(str(file_path), AssetTypes.URI_FOLDER)
    assert excinfo.value.error_type == ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND
