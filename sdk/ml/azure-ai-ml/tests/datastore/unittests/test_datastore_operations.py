import os
from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml import load_datastore
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.operations import DatastoreOperations


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2024_01_01_preview: Mock,
    mock_aml_services_2024_07_01_preview: Mock,
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        serviceclient_2024_01_01_preview=mock_aml_services_2024_01_01_preview,
        serviceclient_2024_07_01_preview=mock_aml_services_2024_07_01_preview,
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

    def test_mount_persistent(
        self,
        mock_from_rest,
        mock_datastore_operation: DatastoreOperations,
    ):
        mock_datastore_operation._compute_operation.get.return_value = Mock(
            properties=Mock(
                properties=Mock(data_mounts=[Mock(mount_name="unified_mount_random_uuid", mount_state="Mounted")])
            )
        )
        with patch("uuid.uuid4", return_value="random_uuid"), patch(
            "azureml.dataprep.rslex_fuse_subprocess_wrapper.build_datastore_uri"
        ) as mock_build_uri, patch.dict(os.environ, {"CI_NAME": "random_ci"}):
            mock_datastore_operation.mount(
                path="azureml://datastores/random_name",
                mount_point="/tmp/mount/random-local-path-for-datastore/",
                persistent=True,
            )
            mock_build_uri.assert_called_once()
            mock_datastore_operation._compute_operation.update_data_mounts.assert_called_once()

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
