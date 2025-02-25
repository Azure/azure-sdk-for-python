from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_online_deployment, load_online_endpoint
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import ManagedOnlineDeployment, ManagedOnlineEndpoint, Model, CodeConfiguration, Environment


@pytest.mark.e2etest
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.production_experiences_test
class TestOnlineDeployment(AzureRecordedTestCase):
    def test_online_deployment(
        self, client: MLClient, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]
    ) -> None:
        endpoint_yaml = "tests/test_configs/deployments/online/simple_online_endpoint_mir.yaml"
        deployment_yaml = "tests/test_configs/deployments/online/online_deployment_1.yaml"
        name = rand_online_name("name")
        endpoint = load_online_endpoint(endpoint_yaml)
        endpoint.name = name

        deployment_name = rand_online_deployment_name("deployment_name")
        deployment = load_online_deployment(deployment_yaml)
        deployment.endpoint_name = name
        deployment.name = deployment_name

        # create a endpoint
        client.online_endpoints.begin_create_or_update(endpoint).result()

        try:
            # create a deployment
            client.online_deployments.begin_create_or_update(deployment).result()
            dep = client.online_deployments.get(name=deployment.name, endpoint_name=endpoint.name)
            assert dep.name == deployment.name

            deps = client.online_deployments.list(endpoint_name=endpoint.name)
            assert len(list(deps)) > 0

            endpoint.traffic = {deployment.name: 100}
            client.online_endpoints.begin_create_or_update(endpoint).result()
            endpoint_updated = client.online_endpoints.get(endpoint.name)
            assert endpoint_updated.traffic[deployment.name] == 100
            client.online_endpoints.invoke(
                endpoint_name=endpoint.name,
                request_file="tests/test_configs/deployments/model-1/sample-request.json",
            )
        except Exception as ex:
            raise ex
        finally:
            client.online_endpoints.begin_delete(name=endpoint.name)

    def test_online_deployment_skip_script_validation(
        self, client: MLClient, rand_online_name: Callable[[], str], rand_online_deployment_name: Callable[[], str]
    ) -> None:
        online_endpoint_name = rand_online_name("online_endpoint_name")
        online_deployment_name = rand_online_deployment_name("online_deployment_name")

        # create an online endpoint
        endpoint = ManagedOnlineEndpoint(
            name=online_endpoint_name,
            description="this is a sample online endpoint",
            auth_mode="key",
            tags={"foo": "bar"},
        )

        client.begin_create_or_update(endpoint).result()

        try:
            # create a blue deployment
            model = Model(
                name="test-model",
                path="tests/test_configs/deployments/model-1/model",
                description="my sample mlflow model",
            )

            code_config = CodeConfiguration(
                code="tests/test_configs/deployments/model-1/onlinescoring/",
                scoring_script="score.py",
            )

            environment = Environment(
                conda_file="tests/test_configs/deployments/model-1/environment/conda.yaml",
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
            )

            blue_deployment = ManagedOnlineDeployment(
                name=online_deployment_name,
                endpoint_name=online_endpoint_name,
                code_configuration=code_config,
                environment=environment,
                model=model,
                instance_type="Standard_DS3_v2",
                instance_count=1,
            )

            client.online_deployments.begin_create_or_update(blue_deployment, skip_script_validation=True).result()
        except Exception as ex:
            raise ex
        finally:
            client.online_endpoints.begin_delete(name=online_endpoint_name)
