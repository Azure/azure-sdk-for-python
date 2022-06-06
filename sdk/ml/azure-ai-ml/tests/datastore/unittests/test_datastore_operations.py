from typing import Callable
from azure.ai.ml.entities._datastore.datastore import Datastore
import pytest
from unittest.mock import Mock, patch
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._operations import DatastoreOperations


@pytest.fixture
def mock_datastore_operation(
    mock_workspace_scope: OperationScope, mock_aml_services_2022_05_01: Mock
) -> DatastoreOperations:
    yield DatastoreOperations(
        operation_scope=mock_workspace_scope,
        serviceclient_2022_05_01=mock_aml_services_2022_05_01,
    )


@patch.object(Datastore, "_from_rest_object")
@pytest.mark.unittest
class TestDatastoreOperations:
    def test_list(self, mock_from_rest, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation.list()
        mock_datastore_operation._operation.list.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_delete(
        self, mock_from_rest, mock_datastore_operation: DatastoreOperations, randstr: Callable[[], str]
    ) -> None:
        mock_datastore_operation.delete(randstr())
        mock_datastore_operation._operation.delete.assert_called_once()

    def test_get_no_secrets(
        self, mock_from_rest, mock_datastore_operation: DatastoreOperations, randstr: Callable[[], str]
    ) -> None:
        mock_datastore_operation.get(randstr())
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_get_no_secrets_with_secrets(
        self, mock_from_rest, mock_datastore_operation: DatastoreOperations, randstr: Callable[[], str]
    ) -> None:
        mock_datastore_operation.get(randstr(), include_secrets=True)
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_called_once()

    @pytest.mark.parametrize(
        "path",
        [
            "blob_store.yml",
            "file_store.yml",
            "adls_gen1.yml",
            "adls_gen2.yml",
            # disable until preview release
            # "hdfs_kerberos_pw.yml",
            # "hdfs_kerberos_keytab.yml",
            # "hdfs_kerberos_minimal.yml",
        ],
    )
    def test_create(self, mock_from_rest, mock_datastore_operation: DatastoreOperations, path) -> None:
        ds = Datastore.load(f"./tests/test_configs/datastore/{path}")
        mock_datastore_operation.create_or_update(ds)
        mock_datastore_operation._operation.create_or_update.assert_called_once()

    def test_get_default(self, mock_from_rest, mock_datastore_operation: DatastoreOperations):
        mock_datastore_operation.get_default()
        mock_datastore_operation._operation.list.assert_called_once()
        assert "is_default=True" in str(mock_datastore_operation._operation.list.call_args)

    def test_get_default_with_secrets(self, mock_from_rest, mock_datastore_operation: DatastoreOperations):
        mock_datastore_operation.get_default(include_secrets=True)
        mock_datastore_operation._operation.list.assert_called_once()
        assert "is_default=True" in str(mock_datastore_operation._operation.list.call_args)
        mock_datastore_operation._operation.list_secrets.assert_called_once()
