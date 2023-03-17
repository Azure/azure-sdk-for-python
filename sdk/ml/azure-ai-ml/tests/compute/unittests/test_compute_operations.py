import sys
from typing import Callable
from unittest.mock import Mock

import pytest
import vcr
from pytest_mock import MockFixture

from azure.ai.ml import load_compute
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml.entities import (
    AmlCompute,
    Compute,
    ComputeInstance,
    IdentityConfiguration,
    ManagedIdentityConfiguration,
)
from azure.ai.ml.operations import ComputeOperations
from azure.identity import DefaultAzureCredential


@pytest.fixture
def mock_compute_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_10_01_preview: Mock,
) -> ComputeOperations:
    yield ComputeOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_10_01_preview,
    )


class funny:
    def __init__(self):
        self.location = "somelocation"


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestComputeOperation:
    def test_list(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.list()
        mock_compute_operation._operation.list.assert_called_once()

    @pytest.mark.skipif(
        sys.version_info[1] == 11,
        reason=f"This test is not compatible with Python 3.11, skip in CI.",
    )
    def test_create_compute_instance(self, mock_compute_operation: ComputeOperations, mocker: MockFixture) -> None:
        mocker.patch(
            "azure.ai.ml._restclient.v2022_10_01_preview.workspaces.get",
            return_value=funny(),
        )
        mocker.patch(
            "azure.ai.ml.entities.Compute._from_rest_object",
            return_value=ComputeInstance(name="name", resource_id="test_resource_id"),
        )
        compute = load_compute("./tests/test_configs/compute/compute-ci-unit.yaml")

        mock_compute_operation.begin_create_or_update(compute=compute)
        mock_compute_operation._operation.begin_create_or_update.assert_called_once()

    @pytest.mark.skipif(
        sys.version_info[1] == 11,
        reason=f"This test is not compatible with Python 3.11, skip in CI.",
    )
    def test_create_aml_compute(self, mock_compute_operation: ComputeOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml._restclient.v2022_10_01_preview.workspaces.get", return_value=funny())
        compute = load_compute("./tests/test_configs/compute/compute-aml.yaml")
        mock_compute_operation.begin_create_or_update(compute=compute)
        mock_compute_operation._operation.begin_create_or_update.assert_called_once()

    def test_delete(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.begin_delete("randstr")
        mock_compute_operation._operation.begin_delete.assert_called_once()

    def test_show(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.get("randstr")
        mock_compute_operation._operation.get.assert_called_once()

    def test_start(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.begin_start("randstr")
        mock_compute_operation._operation.begin_start.assert_called_once()

    def test_stop(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.begin_stop("randstr")
        mock_compute_operation._operation.begin_stop.assert_called_once()

    def test_restart(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.begin_restart("randstr")
        mock_compute_operation._operation.begin_restart.assert_called_once()

    def test_update_aml_compute(self, mock_compute_operation: ComputeOperations, mocker: MockFixture) -> None:
        compute = AmlCompute(
            name="name",
            tags={"key1": "value1", "key2": "value2"},
            min_instances=0,
            max_instances=10,
            idle_time_before_scale_down=100,
            identity=IdentityConfiguration(
                type="UserAssigned",
                user_assigned_identities=[
                    ManagedIdentityConfiguration(
                        resource_id="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/MC_banibatch_bani-aks_eastus/providers/Microsoft.ManagedIdentity/userAssignedIdentities/omsagent-bani-aks"
                    )
                ],
            ),
        )
        mock_compute_operation.begin_update(compute)
        mock_compute_operation._operation.begin_create_or_update.assert_called_once()

    def test_detach(self, mock_compute_operation: ComputeOperations) -> None:
        mock_compute_operation.begin_delete(
            name="randstr",
            action="Detach",
        )
        mock_compute_operation._operation.begin_delete.assert_called_once()
