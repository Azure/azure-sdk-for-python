import os
import platform
import sys
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml import load_datastore
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.operations import DatastoreOperations

IS_CPYTHON = platform.python_implementation() == "CPython"
IS_PYPY = platform.python_implementation() == "PyPy"
IS_MACOS_ARM64 = sys.platform == "darwin" and platform.machine() == "arm64"


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2024_10_01_preview: Mock,
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2024_10_01_preview=mock_aml_services_2024_10_01_preview,
    )


@patch.object(Datastore, "_from_rest_object")
@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestDatastoreOperations:
    def test_list(self, mock_from_rest, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation.list()
        mock_datastore_operation._operation.list.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_delete(self, mock_from_rest, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation.delete("random_name")
        mock_datastore_operation._operation.delete.assert_called_once()

    def test_get_no_secrets(self, mock_from_rest, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation.get("random_name")
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_get_no_secrets_with_secrets(self, mock_from_rest, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation.get("random_name", include_secrets=True)
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_called_once()

    @pytest.mark.parametrize(
        "path",
        [
            "blob_store.yml",
            "file_store.yml",
            "adls_gen1.yml",
            "adls_gen2.yml",
            "one_lake.yml",
            "one_lake_auth_url_back_compat.yml",
            "credential_less_one_lake.yml",
            # disable until preview release
            # "hdfs_kerberos_pw.yml",
            # "hdfs_kerberos_keytab.yml",
            # "hdfs_kerberos_minimal.yml",
        ],
    )
    def test_create(self, mock_from_rest, mock_datastore_operation: DatastoreOperations, path) -> None:
        ds = load_datastore(f"./tests/test_configs/datastore/{path}")
        mock_datastore_operation.create_or_update(ds)
        mock_datastore_operation._operation.create_or_update.assert_called_once()

    @pytest.mark.parametrize(
        "path",
        [
            "blob_store.yml",
            "file_store.yml",
            "adls_gen1.yml",
            "adls_gen2.yml",
            "one_lake.yml",
            "credential_less_one_lake.yml",
        ],
    )
    def test_create_body_is_json_serializable(
        self, mock_from_rest, mock_datastore_operation: DatastoreOperations, path
    ) -> None:
        # Regression test (regressed in 1.34.0): the datastore operation was switched to the
        # TypeSpec/arm_ml_service client, whose ``SdkJSONEncoder`` only serializes hybrid models. Passing a
        # non-hybrid body raised ``TypeError: Object of type Datastore is not JSON serializable`` on every
        # ``datastore create``. Durable fix: ``_to_rest_object()`` now returns an arm_ml_service hybrid model.
        # Guard: the body handed to the operation must serialize cleanly with the same encoder the client uses.
        import json

        from azure.ai.ml._restclient.arm_ml_service._utils.model_base import SdkJSONEncoder

        ds = load_datastore(f"./tests/test_configs/datastore/{path}")
        mock_datastore_operation.create_or_update(ds)
        body = mock_datastore_operation._operation.create_or_update.call_args.kwargs["body"]
        # Must not raise ``TypeError: Object of type Datastore is not JSON serializable``.
        json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)

    @pytest.mark.skipif(
        (IS_CPYTHON and sys.version_info >= (3, 13)) or (IS_PYPY and sys.version_info >= (3, 10)) or IS_MACOS_ARM64,
        reason="Skipping because azureml.dataprep.rslex is unavailable: CPython>=3.13, PyPy>=3.10, or macOS arm64 (no wheel).",
    )
    def test_mount_persistent(
        self,
        mock_from_rest,
        mock_datastore_operation: DatastoreOperations,
    ):
        update_response = Mock(status_code=200)
        get_response = Mock(status_code=200)
        get_response.json.return_value = {
            "properties": {
                "properties": {"dataMounts": [{"mountName": "unified_mount_random_uuid", "mountState": "Mounted"}]}
            }
        }
        mock_datastore_operation._service_client.send_request.side_effect = [update_response, get_response]
        with patch("uuid.uuid4", return_value="random_uuid"), patch(
            "azureml.dataprep.rslex_fuse_subprocess_wrapper.build_datastore_uri"
        ) as mock_build_uri, patch.dict(os.environ, {"CI_NAME": "random_ci"}):
            # build_datastore_uri returns a str in production; the mount request now JSON-encodes this value
            # into the HttpRequest body, so the mock must return a real string (a bare Mock would be fed to
            # SdkJSONEncoder and recurse unboundedly).
            mock_build_uri.return_value = "azureml://datastores/random_name/paths/random"
            mock_datastore_operation.mount(
                path="azureml://datastores/random_name",
                mount_point="/tmp/mount/random-local-path-for-datastore/",
                persistent=True,
            )
            mock_build_uri.assert_called_once()
            assert mock_datastore_operation._service_client.send_request.call_count == 2

    @pytest.mark.skipif(
        (IS_CPYTHON and sys.version_info >= (3, 13)) or (IS_PYPY and sys.version_info >= (3, 10)) or IS_MACOS_ARM64,
        reason="Skipping because azureml.dataprep.rslex is unavailable: CPython>=3.13, PyPy>=3.10, or macOS arm64 (no wheel).",
    )
    def test_mount_non_persistent(
        self,
        mock_from_rest,
        mock_datastore_operation: DatastoreOperations,
    ):
        with patch("azureml.dataprep.rslex_fuse_subprocess_wrapper.build_datastore_uri") as mock_build_uri, patch(
            "azureml.dataprep.rslex_fuse_subprocess_wrapper.start_fuse_mount_subprocess"
        ) as mock_start_subprocess:
            mock_datastore_operation.mount(
                path="azureml://datastores/random_name",
                mount_point="/tmp/mount/random-local-path-for-datastore/",
                persistent=False,
            )
            mock_build_uri.assert_called_once()
            mock_start_subprocess.assert_called_once()

    def test_get_default(self, mock_from_rest, mock_datastore_operation: DatastoreOperations):
        mock_datastore_operation.get_default()
        mock_datastore_operation._operation.list.assert_called_once()
        assert "is_default=True" in str(mock_datastore_operation._operation.list.call_args)

    def test_get_default_with_secrets(self, mock_from_rest, mock_datastore_operation: DatastoreOperations):
        mock_datastore_operation.get_default(include_secrets=True)
        mock_datastore_operation._operation.list.assert_called_once()
        assert "is_default=True" in str(mock_datastore_operation._operation.list.call_args)
        mock_datastore_operation._operation.list_secrets.assert_called_once()
