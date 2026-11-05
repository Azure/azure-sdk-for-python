# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from unittest.mock import Mock, patch

import pytest
import yaml

from azure.ai.ml import MLClient
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml._utils._data_path_resolver import _DataPathResolver, _MAX_DEFINITION_BYTES
from azure.ai.ml.entities import (
    AccountKeyConfiguration,
    AzureBlobDatastore,
    AzureDataLakeGen2Datastore,
    AzureFileDatastore,
    OneLakeDatastore,
)
from azure.ai.ml.entities._datastore.one_lake import LakeHouseArtifact
from azure.ai.ml.constants._common import AZUREML_CLOUD_ENV_NAME
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml.operations import DataOperations
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

pytestmark = [pytest.mark.unittest, pytest.mark.data_experiences_test]

WORKSPACE = "11111111-1111-1111-1111-111111111111"
LAKEHOUSE = "22222222-2222-2222-2222-222222222222"
LONG_PREFIX = "azureml://subscriptions/sub/resourcegroups/rg/workspaces/ws/"


def _not_found(code="BlobNotFound"):
    error = ResourceNotFoundError(message="Not found")
    error.error_code = code
    return error


@pytest.fixture
def operations():
    stores = {
        "blob": AzureBlobDatastore(name="blob", account_name="account", container_name="container"),
        "gen2": AzureDataLakeGen2Datastore(name="gen2", account_name="account", filesystem="filesystem"),
        "fabric": OneLakeDatastore(
            name="fabric", one_lake_workspace_name=WORKSPACE, artifact=LakeHouseArtifact(name=LAKEHOUSE)
        ),
    }
    value = Mock()
    value._operation_scope = OperationScope("sub", "rg", "ws")
    value.get.side_effect = lambda name: stores[name.lower()]
    value.stores = stores
    return value


@pytest.fixture
def blob_storage():
    blobs = {}
    with patch("azure.ai.ml._utils._data_path_resolver.BlobClient") as factory:

        def client(account_url, container_name, blob_name, **kwargs):
            value = Mock()
            value.__enter__ = Mock(return_value=value)
            value.__exit__ = Mock(return_value=False)

            def properties():
                if blob_name not in blobs:
                    raise _not_found()
                return Mock()

            def download(*, offset, length):
                if blob_name not in blobs:
                    raise _not_found()
                return Mock(readall=Mock(return_value=blobs[blob_name][offset : offset + length]))

            value.get_blob_properties.side_effect = properties
            value.download_blob.side_effect = download
            return value

        factory.side_effect = client
        yield blobs, factory


@pytest.mark.parametrize(
    "store,expected",
    [
        ("blob", "https://account.blob.core.windows.net/container/data.csv"),
        ("gen2", "abfss://filesystem@account.dfs.core.windows.net/data.csv"),
        ("fabric", f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}/data.csv"),
    ],
)
@pytest.mark.parametrize("prefix", ["azureml://", LONG_PREFIX])
def test_storage_types_and_uri_forms(operations, blob_storage, store, expected, prefix):
    result = _DataPathResolver(operations, False).resolve(f"{prefix}datastores/{store}/paths/data.csv")
    assert result.uri == expected
    operations.get.assert_called_once_with(store)
    operations._list_secrets.assert_not_called()
    blob_storage[1].assert_not_called()


def test_sovereign_endpoint_and_encoded_filename(operations):
    operations.stores["blob"].endpoint = "core.usgovcloudapi.net"
    result = _DataPathResolver(operations, False).resolve("azureml://datastores/blob/paths/data/a%20b%23c%25.csv")
    assert result.uri == "https://account.blob.core.usgovcloudapi.net/container/data/a%20b%23c%25.csv"


def test_cloud_endpoint_fallback(operations):
    operations.stores["gen2"].endpoint = None
    with patch(
        "azure.ai.ml._utils._data_path_resolver._get_storage_endpoint_from_metadata",
        return_value="core.chinacloudapi.cn",
    ):
        result = _DataPathResolver(operations, False).resolve("azureml://datastores/gen2/paths/data")
    assert result.uri == "abfss://filesystem@account.dfs.core.chinacloudapi.cn/data"


def test_named_onelake_artifact_and_subpath(operations):
    store = operations.stores["fabric"]
    store.one_lake_workspace_name = "workspace"
    store.artifact.name = "lake/Files"
    store.endpoint = "onelake.dfs.fabric.microsoft.com"
    result = _DataPathResolver(operations, False).resolve("azureml://datastores/fabric/paths/data.csv")
    assert result.uri == "abfss://workspace@onelake.dfs.fabric.microsoft.com/lake.lakehouse/Files/data.csv"


@pytest.mark.parametrize(
    "endpoint",
    ["http://host", "https://user:password@host", "https://host/path", "https://host?secret=value"],
)
def test_invalid_onelake_endpoint(operations, endpoint):
    operations.stores["fabric"].endpoint = endpoint
    with pytest.raises(ValidationException, match="endpoint"):
        _DataPathResolver(operations, False).resolve("azureml://datastores/fabric/paths/data")


def test_mixed_onelake_names_and_guids_rejected(operations):
    operations.stores["fabric"].artifact.name = "lake"
    with pytest.raises(ValidationException, match="both"):
        _DataPathResolver(operations, False).resolve("azureml://datastores/fabric/paths/data")


def test_unsupported_datastore(operations):
    operations.stores["files"] = AzureFileDatastore(name="files", account_name="account", file_share_name="share")
    with pytest.raises(ValidationException, match="supports"):
        _DataPathResolver(operations, False).resolve("azureml://datastores/files/paths/data")


@pytest.mark.parametrize(
    "uri",
    [
        "",
        "https://host/file",
        "azureml://datastores/blob/paths/../secret",
        "azureml://datastores/blob/paths/%2e%2e/secret",
        "azureml://datastores/blob/paths/data?secret=value",
        "azureml://subscriptions/other/resourcegroups/rg/workspaces/ws/datastores/blob/paths/data",
        "azureml://subscriptions/sub/resourcegroups/other/workspaces/ws/datastores/blob/paths/data",
        "azureml://subscriptions/sub/resourcegroups/rg/workspaces/other/datastores/blob/paths/data",
    ],
)
def test_invalid_input_rejected_before_io(operations, uri):
    with pytest.raises(ValidationException):
        _DataPathResolver(operations, False).resolve(uri)
    operations.get.assert_not_called()


def test_registry_scope_rejected(operations):
    operations._operation_scope = OperationScope("sub", "rg", None, registry_name="registry")
    with pytest.raises(ValidationException, match="workspace-scoped"):
        _DataPathResolver(operations, False).resolve("azureml://datastores/blob/paths/data")
    operations.get.assert_not_called()


def test_fabric_mltable_preserves_delta_snapshot(operations, blob_storage):
    blob_storage[0]["definition/MLTable"] = yaml.safe_dump(
        {
            "paths": [{"folder": f"{LONG_PREFIX}datastores/fabric/paths/Tables/dbo/people"}],
            "transformations": [{"read_delta_lake": {"version_as_of": 0}}],
        }
    ).encode()
    result = _DataPathResolver(operations, True).resolve(f"{LONG_PREFIX}datastores/blob/paths/definition/")
    assert result.uri == "https://account.blob.core.windows.net/container/definition"
    assert result.sources[0].uri == (
        f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}/Tables/dbo/people"
    )
    assert result.sources[0].path_type == "folder"
    assert result.transformations == [{"read_delta_lake": {"version_as_of": 0}}]
    operations._credential.close.assert_not_called()
    operations._list_secrets.assert_not_called()


def test_existing_blob_file_not_probed_as_directory(operations, blob_storage):
    blob_storage[0]["Titanic.csv"] = b"id,name\n1,Ada\n"
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/Titanic.csv")
    assert result.uri.endswith("/Titanic.csv")
    assert not result.sources
    assert [call.args[2] for call in blob_storage[1].call_args_list] == ["Titanic.csv"]


def test_absent_optional_definition(operations, blob_storage):
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/plain-folder/")
    assert result.uri.endswith("/plain-folder")
    assert not result.sources


def test_missing_explicit_definition_is_error(operations, blob_storage):
    with pytest.raises(ResourceNotFoundError):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/MLTable")


@pytest.mark.parametrize("code", ["ContainerNotFound", "AuthorizationFailure"])
def test_other_not_found_errors_are_not_swallowed(operations, code):
    with patch("azure.ai.ml._utils._data_path_resolver.BlobClient") as factory:
        factory.return_value.__enter__.return_value.download_blob.side_effect = _not_found(code)
        with pytest.raises(ResourceNotFoundError):
            _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")


def test_authentication_error_propagates(operations):
    error = HttpResponseError(message="Forbidden")
    with patch("azure.ai.ml._utils._data_path_resolver.BlobClient") as factory:
        factory.return_value.__enter__.return_value.download_blob.side_effect = error
        with pytest.raises(HttpResponseError, match="Forbidden"):
            _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")


def test_key_backed_definition_uses_datastore_secret(operations, blob_storage):
    operations.stores["blob"].credentials = AccountKeyConfiguration(account_key="not-used-directly")
    operations._list_secrets.return_value = Mock(sas_token="temporary-sas", key=None)
    _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")
    operations._list_secrets.assert_called_once_with(name="blob", expirable_secret=True)
    assert blob_storage[1].call_args.kwargs["credential"] == "temporary-sas"


@pytest.mark.parametrize(
    "endpoint",
    ["core.windows.net.attacker.example", "core.windows.net@attacker.example", "core.usgovcloudapi.net"],
)
def test_untrusted_endpoint_rejected_before_credentials_or_storage(operations, blob_storage, endpoint):
    operations.stores["blob"].endpoint = endpoint
    operations.stores["blob"].credentials = AccountKeyConfiguration(account_key="not-used-directly")
    with pytest.raises(ValidationException, match="configured Azure cloud"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")
    operations._list_secrets.assert_not_called()
    blob_storage[1].assert_not_called()


@pytest.mark.parametrize("account", ["account.evil", "account@attacker.example", "account/evil", "account?evil"])
def test_invalid_account_rejected_before_credentials_or_storage(operations, blob_storage, account):
    operations.stores["blob"].account_name = account
    operations.stores["blob"].credentials = AccountKeyConfiguration(account_key="not-used-directly")
    with pytest.raises(ValidationException, match="configured Azure cloud"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")
    operations._list_secrets.assert_not_called()
    blob_storage[1].assert_not_called()


def test_nested_untrusted_endpoint_rejected_before_credential_use(operations, blob_storage):
    operations.stores["untrusted"] = AzureBlobDatastore(
        name="untrusted",
        account_name="account",
        container_name="container",
        endpoint="core.windows.net.attacker.example",
        credentials=AccountKeyConfiguration(account_key="not-used-directly"),
    )
    blob_storage[0]["root/MLTable"] = b"paths:\n- folder: azureml://datastores/untrusted/paths/data"
    with pytest.raises(ValidationException, match="configured Azure cloud"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    operations._list_secrets.assert_not_called()
    assert len(blob_storage[1].call_args_list) == 1


def test_custom_endpoint_metadata_only_does_not_use_credentials(operations, blob_storage):
    operations.stores["blob"].endpoint = "custom.example"
    result = _DataPathResolver(operations, False).resolve("azureml://datastores/blob/paths/data.csv")
    assert result.uri == "https://account.blob.custom.example/container/data.csv"
    operations._list_secrets.assert_not_called()
    blob_storage[1].assert_not_called()


@pytest.mark.parametrize("endpoint", ["core.usgovcloudapi.net", "core.chinacloudapi.cn"])
def test_authenticated_discovery_uses_configured_cloud(operations, blob_storage, endpoint):
    operations.stores["blob"].endpoint = endpoint
    with patch("azure.ai.ml._utils._data_path_resolver._get_storage_endpoint_from_metadata", return_value=endpoint):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/folder/")
    assert blob_storage[1].call_args.args[0] == f"https://account.blob.{endpoint}"


@pytest.mark.parametrize(
    "clouds",
    [
        [("AzureUSGovernment", "core.usgovcloudapi.net"), ("AzureCloud", "core.windows.net")],
        [("AzureCloud", "core.windows.net"), ("AzureUSGovernment", "core.usgovcloudapi.net")],
        [("AzureChinaCloud", "core.chinacloudapi.cn"), ("AzureCloud", "core.windows.net")],
    ],
)
@pytest.mark.parametrize("explicit_endpoint", [True, False])
def test_resolution_uses_owning_client_cloud(monkeypatch, blob_storage, clouds, explicit_endpoint):
    monkeypatch.setenv(AZUREML_CLOUD_ENV_NAME, "AzureCloud")
    clients = [
        MLClient(Mock(), "sub", "rg", "ws", cloud=cloud, enable_telemetry=False, show_progress=False)
        for cloud, _ in clouds
    ]
    blob_storage[0]["root/MLTable"] = b"paths:\n- folder: azureml://datastores/gen2/paths/data"
    for client, (_, endpoint) in zip(clients, clouds):
        stores = {
            "blob": AzureBlobDatastore(name="blob", account_name="account", container_name="container"),
            "gen2": AzureDataLakeGen2Datastore(name="gen2", account_name="account", filesystem="filesystem"),
        }
        stores["blob"].endpoint = endpoint if explicit_endpoint else None
        stores["gen2"].endpoint = None
        with patch.object(client.datastores, "get", side_effect=lambda name: stores[name]):
            result = client.data.resolve_path("azureml://datastores/blob/paths/root/")
            metadata_only = client.data.resolve_path("azureml://datastores/blob/paths/data.csv", follow_mltable=False)
        assert result.uri == f"https://account.blob.{endpoint}/container/root"
        assert result.sources[0].uri == f"abfss://filesystem@account.dfs.{endpoint}/data"
        assert metadata_only.uri == f"https://account.blob.{endpoint}/container/data.csv"
        assert blob_storage[1].call_args.args[0] == f"https://account.blob.{endpoint}"


@pytest.mark.parametrize("follow_mltable", [False, True])
def test_blob_paths_preserve_internal_separators(operations, blob_storage, follow_mltable):
    blob_storage[0]["data//a.csv"] = b"correct"
    blob_storage[0]["data/a.csv"] = b"wrong"
    result = _DataPathResolver(operations, follow_mltable).resolve("azureml://datastores/blob/paths/data//a.csv")
    assert result.uri == "https://account.blob.core.windows.net/container/data//a.csv"
    if follow_mltable:
        assert [call.args[2] for call in blob_storage[1].call_args_list] == ["data//a.csv"]


def test_blob_definition_path_preserves_internal_separators(operations, blob_storage):
    blob_storage[0]["data//definition/MLTable"] = b"paths:\n- file: https://example.blob.core.windows.net/c/a.csv"
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/data//definition/")
    assert result.uri.endswith("/data//definition")
    assert len(result.sources) == 1
    assert blob_storage[1].call_args.args[2] == "data//definition/MLTable"


def test_relative_multiple_sources_and_patterns(operations, blob_storage):
    blob_storage[0]["definition/MLTable"] = yaml.safe_dump(
        {
            "paths": [
                {"file": "../data/a b.csv"},
                {"pattern": "../data/*.csv"},
                {"file": "https://example.blob.core.windows.net/container/other.csv"},
            ],
            "transformations": [{"read_delimited": {"delimiter": ","}}],
        }
    ).encode()
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/definition/")
    assert [source.uri for source in result.sources] == [
        "https://account.blob.core.windows.net/container/data/a%20b.csv",
        "https://account.blob.core.windows.net/container/data/*.csv",
        "https://example.blob.core.windows.net/container/other.csv",
    ]
    assert [source.path_type for source in result.sources] == ["file", "pattern", "file"]
    operations.get.assert_called_once_with("blob")
    assert len(blob_storage[1].call_args_list) == 1


def test_nested_definitions_keep_transformations_separate(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = yaml.safe_dump(
        {"paths": [{"folder": "./child"}], "transformations": [{"take": 5}]}
    ).encode()
    blob_storage[0]["root/child/MLTable"] = yaml.safe_dump(
        {"paths": [{"file": "data.csv"}], "transformations": [{"skip": 1}]}
    ).encode()
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    child = result.sources[0]
    assert result.transformations == [{"take": 5}]
    assert child.transformations == [{"skip": 1}]
    assert child.sources[0].uri.endswith("/root/child/data.csv")


def test_relative_reference_preserves_literal_percent_encoding(operations, blob_storage):
    blob_storage[0]["root%20/MLTable"] = b"paths:\n- file: './a%2520.csv'"
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root%2520/")
    assert result.sources[0].uri.endswith("/root%2520/a%2520.csv")


@pytest.mark.parametrize(
    "content",
    [
        b"paths: [",
        b"\xff",
        b"- not-a-mapping",
        b"paths: []",
        b"paths: [{file: a.csv}]\ntransformations: invalid",
        b"paths: [{unknown: a.csv}]",
        b"paths: [{file: a.csv, folder: data}]",
        b"paths: [{file: 42}]",
        b"paths: [{file: '../../../escape.csv'}]",
        b"paths: [{file: 'https://host/file?sig=secret'}]",
        b"paths: [{file: 'ftp://host/file'}]",
        b"paths: [{file: 'https:///missing-host'}]",
        b"paths: [{file: 'https://secret@host/file'}]",
    ],
)
def test_invalid_definition(operations, blob_storage, content):
    blob_storage[0]["root/MLTable"] = content
    with pytest.raises(ValidationException):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")


def test_definition_size_is_bounded(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = b"x" * (_MAX_DEFINITION_BYTES + 2)
    with pytest.raises(ValidationException, match="1 MiB"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")


def test_reference_cycle_detected(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = b"paths:\n- folder: ./"
    with pytest.raises(ValidationException, match="cycle"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")


def test_nesting_depth_is_bounded(operations, blob_storage):
    for depth in range(9):
        blob_storage[0][("root/" + "child/" * depth) + "MLTable"] = b"paths:\n- folder: child"
    with pytest.raises(ValidationException, match="nesting"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")


@pytest.mark.parametrize(
    "leaf",
    [
        {"file": "data.csv"},
        {"folder": "data"},
        {"file": "https://example.blob.core.windows.net/container/data.csv"},
    ],
)
def test_eight_definition_levels_allow_leaf_sources(operations, blob_storage, leaf):
    for depth in range(8):
        entry = {"folder": "child"} if depth < 7 else leaf
        blob_storage[0][("root/" + "child/" * depth) + "MLTable"] = yaml.safe_dump({"paths": [entry]}).encode()
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    for _ in range(8):
        result = result.sources[0]
    assert result.path_type == next(iter(leaf))
    assert not result.sources


def test_relative_folder_can_reference_container_root(operations, blob_storage):
    blob_storage[0]["definition/MLTable"] = b"paths:\n- folder: '..'"
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/definition/MLTable")
    assert result.sources[0].uri == "https://account.blob.core.windows.net/container/"
    assert blob_storage[1].call_args.args[2] == "MLTable"


def test_repeated_definitions_are_downloaded_and_parsed_once(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = b"paths:\n- folder: child\n- folder: child"
    blob_storage[0]["root/child/MLTable"] = b"paths:\n- file: a.csv"
    with patch("azure.ai.ml._utils._data_path_resolver.yaml.safe_load", wraps=yaml.safe_load) as parse:
        result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    assert len(blob_storage[1].call_args_list) == 2
    assert parse.call_count == 2
    assert len(result.sources) == 2
    assert result.sources[0] is not result.sources[1]
    assert result.sources[0].sources[0] is not result.sources[1].sources[0]


def test_missing_definition_probes_are_cached(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = b"paths:\n- folder: child\n- folder: child"
    result = _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    assert len(result.sources) == 2
    assert len(blob_storage[1].call_args_list) == 2


@pytest.mark.parametrize("kind", ["file", "folder", "pattern", "external"])
def test_shared_traversal_budget_bounds_wide_source_lists(operations, blob_storage, kind):
    entry = (
        {"file": "https://example.blob.core.windows.net/container/data.csv"} if kind == "external" else {kind: "data"}
    )
    blob_storage[0]["root/MLTable"] = yaml.safe_dump({"paths": [entry] * 4}).encode()
    with patch("azure.ai.ml._utils._data_path_resolver._MAX_RESOLVED_PATHS", 4):
        with pytest.raises(ValidationException, match="resolved paths"):
            _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    assert len(blob_storage[1].call_args_list) <= 2


def test_shared_budget_bounds_repeated_subtree_expansion(operations, blob_storage):
    blob_storage[0]["root/MLTable"] = yaml.safe_dump({"paths": [{"folder": "child"}] * 100}).encode()
    blob_storage[0]["root/child/MLTable"] = yaml.safe_dump({"paths": [{"folder": "child"}] * 100}).encode()
    blob_storage[0]["root/child/child/MLTable"] = b"paths:\n- file: a.csv"
    with pytest.raises(ValidationException, match="resolved paths"):
        _DataPathResolver(operations, True).resolve("azureml://datastores/blob/paths/root/")
    assert len(blob_storage[1].call_args_list) == 3


def test_public_operation_uses_its_datastore_client(operations):
    client = DataOperations(
        operation_scope=operations._operation_scope,
        operation_config=OperationConfig(show_progress=False, enable_telemetry=False),
        service_client=Mock(),
        datastore_operations=operations,
        requests_pipeline=Mock(),
        all_operations=Mock(),
    )
    result = client.resolve_path("azureml://datastores/blob/paths/data.csv", follow_mltable=False)
    assert result.uri == "https://account.blob.core.windows.net/container/data.csv"
    operations.get.assert_called_once_with("blob")
