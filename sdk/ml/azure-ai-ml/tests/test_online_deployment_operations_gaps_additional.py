from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from azure.ai.ml import MLClient
from azure.ai.ml.constants._deployment import EndpointDeploymentLogContainerType
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineDeploymentOperationsGaps(AzureRecordedTestCase):

    def test_get_logs_with_known_container_enum_does_not_raise_validation(self, client, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]) -> None:
        # Passing a supported container enum value should not raise ValidationException (service call may still fail).
        endpoint_name = rand_online_name("endpoint_name")
        deployment_name = rand_online_deployment_name("deployment_name")

        # Use the enum value INFERENCE_SERVER which maps to a REST container type string
        # This call may raise service-side errors, but it should not raise ValidationException from client validation.
        try:
            client.online_deployments.get_logs(
                name=deployment_name,
                endpoint_name=endpoint_name,
                lines=5,
                container_type=EndpointDeploymentLogContainerType.INFERENCE_SERVER,
            )
        except Exception as ex:
            # Ensure that ValidationException was not raised
            assert not isinstance(ex, ValidationException)
