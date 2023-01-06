import pytest

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils._arm_id_utils import get_arm_id_with_version


@pytest.mark.unittest
@pytest.mark.core_sdk_test
def test_get_arm_id(mock_workspace_scope: OperationScope) -> None:
    arm_id = get_arm_id_with_version(mock_workspace_scope, "models", "modeltest", "2")
    expected_arm_id = (
        "/subscriptions/test_subscription/resourceGroups/test_resource_group"
        "/providers/Microsoft.MachineLearningServices/workspaces/test_workspace_name/models/modeltest/versions/2"
    )
    assert expected_arm_id == arm_id
