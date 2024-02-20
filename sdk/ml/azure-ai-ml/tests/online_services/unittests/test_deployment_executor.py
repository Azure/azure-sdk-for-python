from unittest.mock import Mock, PropertyMock, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import MLClient
from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._vendor.azure_resources import ResourceManagementClient
from azure.ai.ml._vendor.azure_resources.operations import DeploymentsOperations
from azure.core.polling import LROPoller


def _raise_exception():
    raise Exception("test exception")


@pytest.fixture()
def mock_poller() -> LROPoller:
    poller = Mock(spec_set=LROPoller)
    poller.wait = _raise_exception
    poller.done = _raise_exception
    yield poller


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestDeploymentExecutor:
    def test_empty_resources_throws(self, mock_machinelearning_client: MLClient) -> None:
        with pytest.raises(Exception):
            executor = ArmDeploymentExecutor(
                credentials=mock_machinelearning_client.credentials,
                resouce_group_name=mock_machinelearning_client._operation_scope.resource_group_name,
                subscription_id=mock_machinelearning_client._operation_scope.subscription_id,
                deployment_name="testdeployment",
            )
            executor.deploy_resource(template="template", resources_being_deployed={})

    def test_deployment_source_show_output(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture, mock_poller: LROPoller
    ) -> None:
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor._get_poller", return_value=mock_poller)
        executor = ArmDeploymentExecutor(
            credentials=mock_machinelearning_client._credential,
            resource_group_name="test_group",
            subscription_id="test_subscription",
            deployment_name="testdeployment",
        )
        with pytest.raises(Exception):
            executor.deploy_resource(template="template", resources_being_deployed={"test": ("test", None)}, wait=True)

    def test_deployment_source_no_output(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture, mock_poller: LROPoller
    ) -> None:
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor._get_poller", return_value=mock_poller)
        executor = ArmDeploymentExecutor(
            credentials=mock_machinelearning_client._credential,
            resource_group_name="test_group",
            subscription_id="test_subscription",
            deployment_name="testdeployment",
        )
        executor.deploy_resource(template="template", resources_being_deployed={"test": ("test", None)}, wait=False)
        executor._get_poller.assert_called_once()
