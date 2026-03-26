import os
import uuid
from pathlib import Path

import pytest
from types import SimpleNamespace

from azure.ai.ml.constants._common import SHORT_URI_FORMAT
from azure.core.exceptions import HttpResponseError

from azure.ai.ml._artifacts import _artifact_utilities as artifact_utilities
from azure.ai.ml._artifacts._artifact_utilities import DatastoreType, MlException, get_datastore_info, list_logs_in_datastore

def test_get_datastore_info_blob_credentials_and_override(monkeypatch):
    monkeypatch.setattr(artifact_utilities, "_get_storage_endpoint_from_metadata", lambda: "region")
    datastore = SimpleNamespace(
        type=DatastoreType.AZURE_BLOB,
        account_name="acct",
        credentials=SimpleNamespace(),
        container_name="blob-container",
    )

    class DummyOperations:
        def __init__(self, datastore):
            self._datastore = datastore
            self._credential = "fallback-identity"

        def get(self, name):
            return self._datastore

        def _list_secrets(self, name, expirable_secret):
            return SimpleNamespace(sas_token="sas-token")

    operations = DummyOperations(datastore)
    info = get_datastore_info(operations, "store", container_name="override-container")

    assert info["storage_type"] == DatastoreType.AZURE_BLOB
    assert info["credential"] == "sas-token"
    assert info["container_name"] == "override-container"

def test_get_datastore_info_data_lake_handles_http_error(monkeypatch):
    monkeypatch.setattr(artifact_utilities, "_get_storage_endpoint_from_metadata", lambda: "region")
    datastore = SimpleNamespace(
        type=DatastoreType.AZURE_DATA_LAKE_GEN2,
        account_name="acct",
        credentials=SimpleNamespace(),
        filesystem="lakefs",
    )

    class DummyOperations:
        def __init__(self, datastore):
            self._datastore = datastore
            self._credential = "backup-token"

        def get(self, name):
            return self._datastore

        def get_default(self):
            return self._datastore

        def _list_secrets(self, name, expirable_secret):
            raise HttpResponseError(response=None, message="boom")

    operations = DummyOperations(datastore)
    info = get_datastore_info(operations, None)

    assert info["storage_type"] == DatastoreType.AZURE_DATA_LAKE_GEN2
    assert info["credential"] == "backup-token"
    assert info["container_name"] == "lakefs"

def test_get_datastore_info_unsupported_type_raises(monkeypatch):
    monkeypatch.setattr(artifact_utilities, "_get_storage_endpoint_from_metadata", lambda: "region")
    datastore = SimpleNamespace(
        type="unsupported",
        account_name="acct",
        credentials=SimpleNamespace(),
        container_name="ignore",
    )
    monkeypatch.setitem(artifact_utilities.STORAGE_ACCOUNT_URLS, datastore.type, "https://{0}.storage.{1}")

    class DummyOperations:
        def __init__(self, datastore):
            self._datastore = datastore
            self._credential = "backup-token"

        def get(self, name):
            return self._datastore

        def _list_secrets(self, name, expirable_secret):
            return SimpleNamespace(sas_token="unused")

    operations = DummyOperations(datastore)

    with pytest.raises(MlException) as excinfo:
        get_datastore_info(operations, "store")

    assert "not supported for uploads" in str(excinfo.value)

def test_list_logs_in_datastore_blob_generates_sas_urls(monkeypatch):
    prefix = "run-id"
    legacy = "/legacy/"
    ds_info = {
        "storage_type": DatastoreType.AZURE_BLOB,
        "storage_account": "account",
        "account_url": "https://storage.region",
        "container_name": "blob-container",
        "credential": "key",
    }

    class FakeBlobStorageClient:
        def __init__(self):
            self.container = ds_info["container_name"]
            self.container_client = SimpleNamespace(
                get_blob_client=lambda blob: SimpleNamespace(set_blob_metadata=lambda metadata: None)
            )
            self._calls = 0

        def list(self, starts_with):
            self._calls += 1
            return [f"{starts_with}log{self._calls}"]

    monkeypatch.setattr(artifact_utilities, "BlobStorageClient", FakeBlobStorageClient)
    monkeypatch.setattr(artifact_utilities, "get_storage_client", lambda **kwargs: FakeBlobStorageClient())
    monkeypatch.setattr(artifact_utilities, "generate_blob_sas", lambda **kwargs: "blob-token")

    result = list_logs_in_datastore(ds_info, prefix, legacy)

    assert set(result.keys()) == {"user_logs/log1", "legacy/log2"}
    for url in result.values():
        assert url.startswith("https://storage.region/blob-container/")
        assert url.endswith("?blob-token")

def test_list_logs_in_datastore_gen2_generates_sas_urls(monkeypatch):
    prefix = "run-id"
    legacy = "/legacy/"
    ds_info = {
        "storage_type": DatastoreType.AZURE_DATA_LAKE_GEN2,
        "storage_account": "account",
        "account_url": "https://storage.region",
        "container_name": "lakefs",
        "credential": "key",
    }

    class FakeGen2StorageClient:
        def __init__(self):
            self.file_system = ds_info["container_name"]
            self._calls = 0

        def list(self, starts_with):
            self._calls += 1
            return [f"{starts_with}log{self._calls}"]

    monkeypatch.setattr(artifact_utilities, "Gen2StorageClient", FakeGen2StorageClient)
    monkeypatch.setattr(artifact_utilities, "get_storage_client", lambda **kwargs: FakeGen2StorageClient())
    monkeypatch.setattr(artifact_utilities, "generate_file_sas", lambda **kwargs: "file-token")

    result = list_logs_in_datastore(ds_info, prefix, legacy)

    assert set(result.keys()) == {"user_logs/log1", "legacy/log2"}
    for url in result.values():
        assert url.startswith("https://storage.region/lakefs/")
        assert url.endswith("?file-token")

def test_upload_to_datastore_respects_provided_ignore_and_hash(monkeypatch, tmp_path):
    test_path = tmp_path / "asset"
    validate_calls = []

    def fake_validate_path(path, _type):
        validate_calls.append((path, _type))

    def fail_get_ignore(path):
        raise AssertionError("get_ignore_file should not be called when ignore_file is provided")

    def fail_get_hash(path, ignore_file):
        raise AssertionError("get_object_hash should not be called when asset_hash is provided")

    class DummyArtifact:
        def __init__(self):
            self.storage_account_url = "initial"
            self.relative_path = "remote"
            self.datastore_arm_id = "arm"
            self.indicator_file = "indicator"

    dummy_artifact = DummyArtifact()

    def fake_upload_artifact(local_path, datastore_operation, operation_scope, datastore_name, asset_hash=None, show_progress=True, asset_name=None, asset_version=None, ignore_file=None, sas_uri=None):
        assert local_path == str(test_path)
        assert asset_hash == "provided-hash"
        assert ignore_file == "provided-ignore"
        return dummy_artifact

    monkeypatch.setattr(artifact_utilities, "_validate_path", fake_validate_path)
    monkeypatch.setattr(artifact_utilities, "get_ignore_file", fail_get_ignore)
    monkeypatch.setattr(artifact_utilities, "get_object_hash", fail_get_hash)
    monkeypatch.setattr(artifact_utilities, "upload_artifact", fake_upload_artifact)

    artifact = artifact_utilities._upload_to_datastore(
        operation_scope="opscope",
        datastore_operation="dsop",
        path=test_path,
        artifact_type="artifact-type",
        datastore_name="datastore",
        asset_hash="provided-hash",
        show_progress=False,
        asset_name="asset",
        asset_version="1",
        ignore_file="provided-ignore",
        blob_uri="https://override",
    )

    assert validate_calls == [(test_path, "artifact-type")]
    assert artifact.storage_account_url == "https://override"

def test_upload_to_datastore_generates_ignore_and_hash(monkeypatch, tmp_path):
    test_path = tmp_path / "artifact"
    called = {}

    def fake_validate_path(path, _type):
        called["validate"] = (path, _type)

    def fake_get_ignore(path):
        called["ignore"] = str(path)
        return "generated-ignore"

    def fake_get_hash(path, ignore_file):
        called["hash"] = (str(path), ignore_file)
        return "generated-hash"

    class DummyArtifact:
        def __init__(self):
            self.storage_account_url = "initial"
            self.relative_path = "remote"
            self.datastore_arm_id = "arm"
            self.indicator_file = "indicator"

    dummy_artifact = DummyArtifact()

    def fake_upload_artifact(local_path, datastore_operation, operation_scope, datastore_name, asset_hash=None, show_progress=True, asset_name=None, asset_version=None, ignore_file=None, sas_uri=None):
        assert asset_hash == "generated-hash"
        assert ignore_file == "generated-ignore"
        assert local_path == str(test_path)
        return dummy_artifact

    monkeypatch.setattr(artifact_utilities, "_validate_path", fake_validate_path)
    monkeypatch.setattr(artifact_utilities, "get_ignore_file", fake_get_ignore)
    monkeypatch.setattr(artifact_utilities, "get_object_hash", fake_get_hash)
    monkeypatch.setattr(artifact_utilities, "upload_artifact", fake_upload_artifact)

    artifact_utilities._upload_to_datastore(
        operation_scope="opscope",
        datastore_operation="dsop",
        path=test_path,
        artifact_type="artifact-type",
        datastore_name="datastore",
        asset_name="asset",
        asset_version="2",
        show_progress=True,
    )

    assert called["validate"] == (test_path, "artifact-type")
    assert called["ignore"] == str(test_path)
    assert called["hash"] == (str(test_path), "generated-ignore")

def test_upload_and_generate_remote_uri_formats_short_uri(monkeypatch):
    class DummyArtifact:
        relative_path = "files/blob"
        datastore_arm_id = "arm/id"

    def fake_upload_to_datastore(operation_scope, datastore_operation, path, datastore_name, asset_name=None, asset_version=None, artifact_type=None, show_progress=None):
        assert operation_scope == "opscope"
        assert datastore_operation == "dsop"
        assert str(path) == "local-path"
        assert datastore_name == "store"
        assert asset_name == "fixed-asset"
        assert artifact_type == artifact_utilities.ErrorTarget.ARTIFACT
        assert show_progress is False
        return DummyArtifact()

    class DummyUUID:
        def __str__(self):
            return "fixed-asset"

    class DummyArmId:
        def __init__(self, arm_id):
            assert arm_id == "arm/id"
            self.asset_name = "datastore-name"

    monkeypatch.setattr(artifact_utilities, "_upload_to_datastore", fake_upload_to_datastore)
    monkeypatch.setattr(artifact_utilities.uuid, "uuid4", lambda: DummyUUID())
    monkeypatch.setattr(artifact_utilities, "AMLNamedArmId", DummyArmId)

    result = artifact_utilities._upload_and_generate_remote_uri(
        operation_scope="opscope",
        datastore_operation="dsop",
        path="local-path",
        datastore_name="store",
        show_progress=False,
    )

    assert result == artifact_utilities.SHORT_URI_FORMAT.format("datastore-name", "files/blob")

def test_update_metadata_invokes_blob_metadata(monkeypatch):
    class DummyBlobClient:
        pass

    dummy_client = DummyBlobClient()
    monkeypatch.setattr(artifact_utilities, "BlobStorageClient", DummyBlobClient)
    monkeypatch.setattr(artifact_utilities, "Gen2StorageClient", type("StubGen2", (), {}))
    monkeypatch.setattr(artifact_utilities, "get_storage_client", lambda **kwargs: dummy_client)

    called = {}

    def fake_blob_metadata(name, version, indicator_file, storage_client):
        called["blob"] = (name, version, indicator_file, storage_client)

    def fail_gen2(*args, **kwargs):
        raise AssertionError("gen2 branch should not run in blob scenario")

    monkeypatch.setattr(artifact_utilities, "_update_blob_metadata", fake_blob_metadata)
    monkeypatch.setattr(artifact_utilities, "_update_gen2_metadata", fail_gen2)

    artifact_utilities._update_metadata("env", "1", "indicator", {})

    assert called["blob"] == ("env", "1", "indicator", dummy_client)

def test_update_metadata_invokes_gen2_metadata(monkeypatch):
    class DummyGen2Client:
        pass

    dummy_client = DummyGen2Client()
    monkeypatch.setattr(artifact_utilities, "Gen2StorageClient", DummyGen2Client)
    monkeypatch.setattr(artifact_utilities, "BlobStorageClient", type("StubBlob", (), {}))
    monkeypatch.setattr(artifact_utilities, "get_storage_client", lambda **kwargs: dummy_client)

    called = {}

    def fail_blob(*args, **kwargs):
        raise AssertionError("blob branch should not run in gen2 scenario")

    def fake_gen2_metadata(name, version, indicator_file, storage_client):
        called["gen2"] = (name, version, indicator_file, storage_client)

    monkeypatch.setattr(artifact_utilities, "_update_blob_metadata", fail_blob)
    monkeypatch.setattr(artifact_utilities, "_update_gen2_metadata", fake_gen2_metadata)

    artifact_utilities._update_metadata("environment", "2", "indicator", {})

    assert called["gen2"] == ("environment", "2", "indicator", dummy_client)


class _StubArtifactStorageInfo:
    def __init__(self, name, version, relative_path, datastore_arm_id, indicator_file, full_storage_path="https://fake/storage"):
        self.name = name
        self.version = version
        self.relative_path = relative_path
        self.datastore_arm_id = datastore_arm_id
        self.indicator_file = indicator_file
        self.full_storage_path = full_storage_path
        self.storage_account_url = full_storage_path


class _StubStorageClient:
    def __init__(self):
        self.container = "container"
        self.file_system = "filesystem"
        self.container_client = self
        self.file_system_client = self
        self._metadata = None

    def upload(self, local_path, **kwargs):
        return {
            "name": "uploaded-name",
            "version": "1",
            "remote path": f"rel/{Path(local_path).name}",
            "indicator file": f"indicator/{Path(local_path).name}",
        }

    def get_blob_client(self, blob):
        return self

    def set_blob_metadata(self, metadata):
        self._metadata = metadata

    def get_directory_client(self, indicator_file):
        return self

    def set_metadata(self, metadata):
        self._metadata = metadata


class _StubOperations:
    def __init__(self):
        self._operation_scope = object()
        self._datastore_operation = object()
        self._credential = "cred"
        self.calls = []


class _StubArtifact:
    def __init__(self):
        self.datastore = "default"
        self.local_path = None
        self.path = "code"
        self.base_path = os.getcwd()
        self.name = "asset"
        self.version = 1
        self._upload_hash = "hash"
        self._ignore_file = None
        self._is_anonymous = True
        self._path_updated_with = None

    def _update_path(self, uploaded_artifact):
        self._path_updated_with = uploaded_artifact


class _StubEnvironment:
    def __init__(self):
        self.path = "context"
        self.name = "env"
        self.version = 2
        self.datastore = "default"
        self._upload_hash = "hash"
        self.build = type("Build", (), {"path": None})()

def test_upload_and_generate_remote_uri_formats_short_uri_with_short_uri_constant(monkeypatch):
    uploaded = _StubArtifactStorageInfo(
        name="uploaded-name",
        version="42",
        relative_path="rel/path",
        datastore_arm_id="/subscriptions/1/resourceGroups/g/providers/Microsoft.MachineLearningServices/workspaces/w/datastores/default",
        indicator_file="indicator",
    )

    monkeypatch.setattr(artifact_utilities, "_upload_to_datastore", lambda **kwargs: uploaded)
    monkeypatch.setattr(artifact_utilities, "AMLNamedArmId", lambda arm_id: type("Id", (), {"asset_name": "datastore-name"})())
    monkeypatch.setattr(uuid, "uuid4", lambda: "fixed-uuid")

    result = artifact_utilities._upload_and_generate_remote_uri(
        operation_scope=object(),
        datastore_operation=object(),
        path="some-path",
    )

    assert result == SHORT_URI_FORMAT.format("datastore-name", "rel/path")

def test_update_metadata_for_blob_and_gen2(monkeypatch):
    blob_client = _StubStorageClient()
    gen2_client = _StubStorageClient()

    monkeypatch.setattr(artifact_utilities, "BlobStorageClient", _StubStorageClient)
    monkeypatch.setattr(artifact_utilities, "Gen2StorageClient", _StubStorageClient)

    def fake_get_storage_client(*args, **kwargs):
        if kwargs.get("storage_type") == artifact_utilities.DatastoreType.AZURE_BLOB:
            return blob_client
        return gen2_client

    monkeypatch.setattr(artifact_utilities, "get_storage_client", fake_get_storage_client)

    datastore_info_blob = {"storage_type": artifact_utilities.DatastoreType.AZURE_BLOB, "credential": "cred", "storage_account": "acc", "container_name": "container"}
    datastore_info_gen2 = {"storage_type": artifact_utilities.DatastoreType.AZURE_DATA_LAKE_GEN2, "credential": "cred", "storage_account": "acc", "container_name": "filesystem"}

    artifact_utilities._update_metadata("name", "1", "container/indicator", datastore_info_blob)
    assert blob_client._metadata["name"] == "name"
    assert blob_client._metadata["version"] == "1"

    artifact_utilities._update_metadata("name", "2", "indicator", datastore_info_gen2)
    assert gen2_client._metadata["name"] == "name"
    assert gen2_client._metadata["version"] == "2"

def test_check_and_upload_path_uploads(monkeypatch, tmp_path):
    artifact = _StubArtifact()
    artifact.local_path = str(tmp_path / "file.txt")
    Path(artifact.local_path).write_text("data")

    operations = _StubOperations()
    uploaded = _StubArtifactStorageInfo(
        name="new-name",
        version="2",
        relative_path="rel/path",
        datastore_arm_id="/subscriptions/1/resourceGroups/g/providers/Microsoft.MachineLearningServices/workspaces/w/datastores/default",
        indicator_file="indicator",
        full_storage_path="https://storage/rel"
    )

    def fake_upload(*args, **kwargs):
        uploaded.storage_account_url = kwargs.get("blob_uri", uploaded.storage_account_url)
        return uploaded

    monkeypatch.setattr(artifact_utilities, "_upload_to_datastore", fake_upload)

    result_artifact, indicator = artifact_utilities._check_and_upload_path(
        artifact=artifact,
        asset_operations=operations,
        artifact_type="Code",
        blob_uri="https://override",
        show_progress=False,
    )

    assert result_artifact.name == "new-name"
    assert result_artifact.version == "2"
    assert indicator == "indicator"
    assert result_artifact._path_updated_with is uploaded
    assert uploaded.storage_account_url == "https://override"

def test_check_and_upload_env_build_context_updates_build_path(monkeypatch):
    environment = _StubEnvironment()
    operations = _StubOperations()

    uploaded = _StubArtifactStorageInfo(
        name="env-name",
        version="3",
        relative_path="rel/path",
        datastore_arm_id="/subscriptions/1/resourceGroups/g/providers/Microsoft.MachineLearningServices/workspaces/w/datastores/default",
        indicator_file="indicator",
        full_storage_path="https://storage/rel"
    )

    monkeypatch.setattr(artifact_utilities, "_upload_to_datastore", lambda *args, **kwargs: uploaded)

    updated = artifact_utilities._check_and_upload_env_build_context(environment, operations, sas_uri="https://sas")

    assert updated.build.path == "https://storage/rel/"

def test_get_snapshot_path_info_resolves_path(monkeypatch, tmp_path):
    file_path = tmp_path / "asset"
    file_path.write_text("content")

    artifact = type("Artifact", (), {
        "local_path": str(file_path),
        "path": None,
        "base_path": str(tmp_path),
    })()

    monkeypatch.setattr(artifact_utilities, "_validate_path", lambda path, _type: None)
    monkeypatch.setattr(artifact_utilities, "get_ignore_file", lambda path: "ignore")
    monkeypatch.setattr(artifact_utilities, "get_content_hash", lambda path, ignore: "hash-value")

    resolved_path, ignore_file, asset_hash = artifact_utilities._get_snapshot_path_info(artifact)

    assert resolved_path == Path(str(file_path))
    assert ignore_file == "ignore"
    assert asset_hash == "hash-value"

def test_check_and_upload_path_resolves_relative(monkeypatch, tmp_path):
    monkeypatch.setattr(artifact_utilities, '_validate_path', lambda path, _type=None: None)
    monkeypatch.setattr(artifact_utilities, 'get_ignore_file', lambda path: 'ignore-file')
    monkeypatch.setattr(artifact_utilities, 'get_object_hash', lambda path, ignore_file=None: 'object-hash')
    captured = {}

    def fake_upload_to_datastore(
        operation_scope,
        datastore_operation,
        path,
        **kwargs,
    ):
        captured['path'] = path
        return SimpleNamespace(
            relative_path='remote/path',
            indicator_file='indicator.txt',
            name='name',
            version='1',
            datastore_arm_id='arm-id',
            full_storage_path='https://account/container/remote',
            storage_account_url='https://account',
            container_name='container',
        )

    monkeypatch.setattr(artifact_utilities, '_upload_to_datastore', fake_upload_to_datastore)

    class DummyArtifact:
        def __init__(self):
            self.name = 'artifact-name'
            self.version = '1'
            self.datastore = 'datastore'
            self.base_path = tmp_path
            self.path = 'subdir/file'
            self.local_path = None
            self._is_anonymous = False
            self._upload_hash = None
            self._ignore_file = None

        def _update_path(self, uploaded_artifact):
            self.updated_path = uploaded_artifact.relative_path

    artifact = DummyArtifact()
    operations = SimpleNamespace(
        _operation_scope='scope',
        _datastore_operation='datastore-operation',
    )

    result_artifact, indicator_file = artifact_utilities._check_and_upload_path(
        artifact,
        operations,
        artifact_type='artifact-type',
        datastore_name='datastore-name',
        show_progress=False,
    )

    assert result_artifact is artifact
    assert indicator_file == 'indicator.txt'
    assert artifact.updated_path == 'remote/path'
    assert captured['path'] == (tmp_path / 'subdir' / 'file').resolve()

def test_check_and_upload_path_updates_anonymous_artifact(monkeypatch, tmp_path):
    monkeypatch.setattr(artifact_utilities, '_validate_path', lambda path, _type=None: None)
    monkeypatch.setattr(artifact_utilities, 'get_ignore_file', lambda path: 'ignore-file')
    monkeypatch.setattr(artifact_utilities, 'get_object_hash', lambda path, ignore_file=None: 'object-hash')

    def fake_upload_to_datastore(
        operation_scope,
        datastore_operation,
        path,
        **kwargs,
    ):
        return SimpleNamespace(
            relative_path='remote/path',
            indicator_file='indicator.txt',
            name='anonymous-name',
            version='2',
            datastore_arm_id='arm-id',
            full_storage_path='https://account/remote',
            storage_account_url='https://account',
            container_name='container',
        )

    monkeypatch.setattr(artifact_utilities, '_upload_to_datastore', fake_upload_to_datastore)

    class DummyArtifact:
        def __init__(self):
            self.name = 'artifact-name'
            self.version = '1'
            self.datastore = 'datastore'
            self.base_path = tmp_path
            self.path = 'subdir/file'
            self.local_path = None
            self._is_anonymous = True
            self._upload_hash = None
            self._ignore_file = None

        def _update_path(self, uploaded_artifact):
            self.updated_path = uploaded_artifact.relative_path

    artifact = DummyArtifact()
    operations = SimpleNamespace(
        _operation_scope='scope',
        _datastore_operation='datastore-operation',
    )

    artifact_utilities._check_and_upload_path(
        artifact,
        operations,
        artifact_type='artifact-type',
        datastore_name='datastore-name',
        show_progress=False,
    )

    assert artifact.name == 'anonymous-name'
    assert artifact.version == '2'

def test_check_and_upload_env_build_context_updates_build_path(monkeypatch, tmp_path):
    def fake_upload_to_datastore(
        operation_scope,
        datastore_operation,
        path,
        **kwargs,
    ):
        return SimpleNamespace(
            full_storage_path='https://account/path'
        )

    monkeypatch.setattr(artifact_utilities, '_upload_to_datastore', fake_upload_to_datastore)

    environment = SimpleNamespace(
        path=str(tmp_path / 'env-src'),
        name='env-name',
        version='3',
        datastore='datastore',
        build=SimpleNamespace(path=None),
        _upload_hash='hash',
    )
    operations = SimpleNamespace(
        _operation_scope='scope',
        _datastore_operation='datastore-operation',
    )

    result = artifact_utilities._check_and_upload_env_build_context(environment, operations)

    assert result is environment
    assert environment.build.path == 'https://account/path/'

def test_check_and_upload_env_build_context_skips_when_path_missing(monkeypatch):
    called = {'upload': False}

    def fake_upload_to_datastore(*args, **kwargs):
        called['upload'] = True
        return SimpleNamespace(full_storage_path='unused')

    monkeypatch.setattr(artifact_utilities, '_upload_to_datastore', fake_upload_to_datastore)

    environment = SimpleNamespace(
        path=None,
        name='env-name',
        version='3',
        datastore='datastore',
        build=SimpleNamespace(path='existing'),
        _upload_hash='hash',
    )
    operations = SimpleNamespace(
        _operation_scope='scope',
        _datastore_operation='datastore-operation',
    )

    result = artifact_utilities._check_and_upload_env_build_context(environment, operations)

    assert result is environment
    assert called['upload'] is False
    assert environment.build.path == 'existing'

def test_get_snapshot_path_info_returns_components(monkeypatch, tmp_path):
    monkeypatch.setattr(artifact_utilities, '_validate_path', lambda path, _type=None: None)
    monkeypatch.setattr(artifact_utilities, 'get_ignore_file', lambda path: 'ignore-file')
    monkeypatch.setattr(artifact_utilities, 'get_content_hash', lambda path, ignore_file: 'content-hash')

    artifact = SimpleNamespace(
        path='relative/code',
        base_path=tmp_path,
        local_path=None,
    )

    path, ignore_file, asset_hash = artifact_utilities._get_snapshot_path_info(artifact)

    assert path == (tmp_path / 'relative' / 'code').resolve()
    assert ignore_file == 'ignore-file'
    assert asset_hash == 'content-hash'

def test_get_snapshot_path_info_returns_none_for_url(monkeypatch):
    monkeypatch.setattr(artifact_utilities, 'is_url', lambda value: True)
    monkeypatch.setattr(artifact_utilities, 'is_mlflow_uri', lambda value: False)

    artifact = SimpleNamespace(
        path='https://example.com/asset',
        base_path=Path('/unused'),
        local_path=None,
    )

    assert artifact_utilities._get_snapshot_path_info(artifact) is None