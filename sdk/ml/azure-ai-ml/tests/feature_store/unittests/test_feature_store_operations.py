from unittest.mock import DEFAULT, Mock

import pytest
from pytest_mock import MockFixture

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import (
    FeatureStore,
    Workspace,
)
from azure.ai.ml.operations._feature_store_operations import FeatureStoreOperations
from azure.core.polling import LROPoller


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_feature_store_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_12_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> FeatureStoreOperations:
    yield FeatureStoreOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_12_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreOperation:
    @pytest.mark.parametrize("arg", ["resource_group", "subscription", "other_rand_str"])
    def test_list(self, arg: str, mock_feature_store_operation: FeatureStoreOperations) -> None:
        mock_feature_store_operation.list(scope=arg)
        if arg == "subscription":
            mock_feature_store_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_feature_store_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_feature_store_operation: FeatureStoreOperations) -> None:
        mock_feature_store_operation.get("random_name")
        mock_feature_store_operation._operation.get.assert_called_once()

    def test_begin_create(
        self,
        mock_feature_store_operation: FeatureStoreOperations,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations._feature_store_operations.FeatureStoreOperations.get", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._feature_store_operations.FeatureStoreOperations._populate_arm_paramaters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_feature_store_operation.begin_create(feature_store=FeatureStore(name="name"))

    def test_update(self, mock_feature_store_operation: FeatureStoreOperations) -> None:
        fs = FeatureStore(
            name="name",
            description="description",
        )

        def outgoing_get_call(rg, name, **kwargs):
            return Workspace(name=name, kind="featurestore")._to_rest_object()

        def outgoing_call(rg, name, params, polling, cls, **kwargs):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == "description"
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call
        mock_feature_store_operation._operation.begin_update.side_effect = outgoing_call
        mock_feature_store_operation.begin_update(fs, update_dependent_resources=True)
        mock_feature_store_operation._operation.begin_update.assert_called()

    def test_delete(self, mock_feature_store_operation: FeatureStoreOperations, mocker: MockFixture) -> None:
        def outgoing_call(rg, name, **kwargs):
            return Workspace(name=name, kind="featurestore")._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mock_feature_store_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_feature_store_operation._operation.begin_delete.assert_called_once()

    def test_delete_non_feature_store_kind(
        self, mock_feature_store_operation: FeatureStoreOperations, mocker: MockFixture
    ) -> None:
        def outgoing_call(rg, name, **kwargs):
            return Workspace(name=name)._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        with pytest.raises(Exception):
            mock_feature_store_operation.begin_delete("randstr", delete_dependent_resources=True)
