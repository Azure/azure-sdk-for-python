import json
import logging
import uuid
from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import load_online_endpoint
from azure.ai.ml._arm_deployments.arm_deployment_executor import ArmDeploymentExecutor
from azure.ai.ml._artifacts._constants import EMPTY_DIRECTORY_ERROR
from azure.ai.ml._ml_client import MLClient
from azure.ai.ml._utils.utils import dump_yaml_to_file, load_yaml
from azure.ai.ml.constants._common import AML_TOKEN_YAML, KEY, ONLINE_ENDPOINT_TYPE
from azure.ai.ml.constants._endpoint import EndpointKeyType
from azure.ai.ml.entities import EndpointAuthKeys, EndpointAuthToken, KubernetesOnlineEndpoint, OnlineEndpoint
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.identity import EnvironmentCredential


@pytest.fixture
def endpoint_mir_yaml() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_create_mir.yml"


@pytest.fixture
def request_file() -> str:
    return "./tests/test_configs/endpoints/online/data.json"


@pytest.mark.e2etest
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.production_experiences_test
class TestOnlineEndpoint(AzureRecordedTestCase):
    def test_online_endpoint_e2e(
        self,
        endpoint_mir_yaml: str,
        rand_online_name: Callable[[], str],
        request_file: str,
        client: MLClient,
    ) -> None:
        mir_endpoint_name = rand_online_name("mir-test-")
        print(f"Creating endpoint with name {mir_endpoint_name}")
        try:
            endpoint = load_online_endpoint(endpoint_mir_yaml)
            endpoint.name = mir_endpoint_name
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            get_obj = client.online_endpoints.get(name=mir_endpoint_name)
            assert get_obj.name == mir_endpoint_name
            if isinstance(get_obj, OnlineEndpoint):
                assert get_obj.auth_mode == AML_TOKEN_YAML

            credentials = client.online_endpoints.get_keys(name=mir_endpoint_name)
            assert credentials is not None
            if get_obj.auth_mode == KEY:
                assert isinstance(credentials, EndpointAuthKeys)
            elif get_obj.auth_mode == AML_TOKEN_YAML:
                assert isinstance(credentials, EndpointAuthToken)

            if get_obj.auth_mode == KEY:
                client.online_endpoints.begin_regenerate_keys(
                    name=mir_endpoint_name, key_type=EndpointKeyType.SECONDARY_KEY_TYPE
                ).result()
                updated_credentials = client.online_endpoints.get_keys(name=mir_endpoint_name)
                assert credentials.secondary_key != updated_credentials.secondary_key
                assert credentials.primary_key == updated_credentials.primary_key

            # there is a bug on the MFE. When RG has upper case charater in the name, then fetching logs will return 400
            # disable the test until the service side is fixed.
            # for deployment in deployment_names:
            #     logs = client.endpoints.get_deployment_logs(endpoint_name, deployment, 10, endpoint_type=ONLINE_ENDPOINT_TYPE)
            #     assert logs
            #     assert logs.count("\n") <= 10

            endpoint_resources = client.online_endpoints.list()
            assert endpoint_resources is not None
            assert isinstance(endpoint_resources, ItemPaged)

            """
            # Create an online deployment
            for deployment_name in deployment_names:
                endpoint.traffic[deployment_name] = 100
            client.endpoints.update(
                endpoint=endpoint,
                deployment=None,
                no_wait=False,
            )

            # Set traffic



            # test invoke
            for deployment_name in deployment_names:
                pred = client.online_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    request_file=request_file,
                    deployment_name=deployment_name,
                )
                assert pred
            """
        except Exception as e:
            raise e
        finally:
            client.online_endpoints.begin_delete(name=mir_endpoint_name).result()

    @pytest.mark.skip("skip for now to run e2e in eastus2. will undo this once we go back to centraluseuap")
    @pytest.mark.e2etest
    def test_online_endpoint_submit(self, client: MLClient, location: str, rand_online_name: Callable[[], str]):
        import logging, sys

        logger = logging.getLogger("azure")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        logger.addHandler(handler)
        # TODO: current e2e workspace has no k8s compute. So use the old sdk_vnext_cli workspace for testing temporarily.
        # endpoint name should be consistent with the name in the template
        endpoint_name = rand_online_name("k8s-e2e-endpoint-")
        deployment_name = rand_online_name("test_submission_")
        try:
            deployment_executor = ArmDeploymentExecutor(
                credentials=client._credential,
                resource_group_name=client._operation_scope.resource_group_name,
                subscription_id=client._operation_scope.subscription_id,
                deployment_name=deployment_name,
                workspace_name=client.workspace_name,
            )
            template_file = "tests/test_configs/deployments/online/online-endpoint_arm_template.json"
            with open(template_file, "r") as f:
                template = json.load(f)
            template["parameters"]["workspaceName"]["defaultValue"] = client.workspace_name
            template["parameters"]["identityType"]["defaultValue"] = "SystemAssigned"
            template["parameters"]["onlineEndpointName"]["defaultValue"] = endpoint_name
            template["parameters"]["location"]["defaultValue"] = location
            deployed_resources = {f"sdk_vnext_cli/{endpoint_name}": ("online-endpoint", None)}
            # the location here does not matter
            deployment_executor.deploy_resource(
                template=template,
                resources_being_deployed=deployed_resources,
                wait=True,
            )
            # assert client.online_endpoints.get(name=endpoint_name).name == endpoint_name
        except Exception as e:
            logging.error("Hit exception {}".format(e))
            assert False
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()
