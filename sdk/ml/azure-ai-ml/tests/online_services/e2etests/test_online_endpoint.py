import json
import logging
import random
import uuid
from pathlib import Path

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
def debug_client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    credential = EnvironmentCredential()
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )


@pytest.fixture
def k8s_endpoint_name() -> str:
    return f"k8s-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_k8s_yaml() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_create_k8s.yml"


@pytest.fixture
def k8s_update_file() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_update_k8s.yml"


@pytest.fixture
def k8s_deployment_update_file() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_deployment_update_k8s.yml"


@pytest.fixture
def mir_deployment_update_file() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_deployment_update_mir.yml"


@pytest.fixture
def mir_endpoint_name() -> str:
    return f"mir-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_mir_yaml() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_create_mir.yml"


@pytest.fixture
def mir_update_file() -> str:
    return "./tests/test_configs/endpoints/online/online_endpoint_update_mir.yml"


@pytest.fixture
def request_file() -> str:
    return "./tests/test_configs/endpoints/online/data.json"


@pytest.fixture
def endpoint_k8s_yaml_empty_model(tmp_path: Path, resource_group_name: str) -> Path:
    import os

    empty_model_dir = "empty_model"
    os.mkdir(tmp_path.joinpath(empty_model_dir))
    content = f"""
name: k8sendpoint
target: azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/sdkv2endpointk8s
auth_mode: Key
traffic:
    blue: 0
    """
    p = tmp_path / "create_yaml_empty_model.yaml"
    p.write_text(content)
    return p


@pytest.mark.skip(
    reason="Tests failing in internal automation due to lack of quota. Cannot record or run in live mode."
)
@pytest.mark.e2etest
@pytest.mark.production_experiences_test
class TestOnlineEndpoint(AzureRecordedTestCase):
    def test_online_endpoint_e2e(
        self,
        endpoint_mir_yaml: str,
        mir_endpoint_name: str,
        request_file: str,
        client: MLClient,
    ) -> None:
        print(f"Creating endpoint with name {mir_endpoint_name}")
        try:
            endpoint = load_online_endpoint(endpoint_mir_yaml)
            endpoint.name = mir_endpoint_name
            client.online_endpoints.begin_create_or_update(endpoint=endpoint)

            get_obj = client.online_endpoints.get(name=mir_endpoint_name)
            assert get_obj.name == mir_endpoint_name
            if isinstance(get_obj, OnlineEndpoint):
                assert get_obj.auth_mode == AML_TOKEN_YAML

            credentials = client.online_endpoints.list_keys(name=mir_endpoint_name)
            assert credentials is not None
            if get_obj.auth_mode == KEY:
                assert isinstance(credentials, EndpointAuthKeys)
            elif get_obj.auth_mode == AML_TOKEN_YAML:
                assert isinstance(credentials, EndpointAuthToken)

            if get_obj.auth_mode == KEY:
                client.online_endpoints.regenerate_keys(
                    name=mir_endpoint_name, key_type=EndpointKeyType.SECONDARY_KEY_TYPE
                )
                updated_credentials = client.endpoints.list_keys(name=mir_endpoint_name)
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
            client.online_endpoints.begin_delete(name=mir_endpoint_name, no_wait=True)

    @pytest.mark.skip("skip for now to run e2e in eastus2. will undo this once we go back to centraluseuap")
    @pytest.mark.e2etest
    def test_online_endpoint_submit(self, client: MLClient, location: str):
        # TODO: current e2e workspace has no k8s compute. So use the old sdk_vnext_cli workspace for testing temporarily.
        # endpoint name should be consistent with the name in the template
        endpoint_name = f"k8s-e2e-endpoint-{random.randint(1, 100)}"
        deployment_name = f"test_submission_{random.randint(1, 1000)}"
        try:
            deployment_executor = ArmDeploymentExecutor(
                credentials=client._credential,
                resource_group_name=client._operation_scope.resource_group_name,
                subscription_id=client._operation_scope.subscription_id,
                deployment_name=deployment_name,
            )

            template_file = "./tests/test_configs/online_endpoint_template.json"
            with open(template_file, "r") as f:
                template = json.load(f)
            template["parameters"]["onlineEndpointName"]["defaultValue"] = endpoint_name
            template["parameters"]["location"]["defaultValue"] = location
            deployed_resources = {f"sdk_vnext_cli/{endpoint_name}": ("online-endpoint", None)}
            # the location here does not matter
            deployment_executor.deploy_resource(
                template=template,
                resources_being_deployed=deployed_resources,
                wait=True,
            )
            assert client.endpoints.get(name=endpoint_name).name == endpoint_name
        except Exception as e:
            logging.error("Hit exception {}".format(e))
            assert False
        finally:
            client.endpoints.begin_delete(endpoint_type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)

    @pytest.mark.skip(reason="TODO: 1166616 re-enable once we know why it keeps failing")
    @pytest.mark.e2etest
    def test_online_endpoint_k8s_empty_model_e2e(
        self,
        endpoint_k8s_yaml_empty_model: str,
        client: MLClient,
    ) -> None:
        with pytest.raises(Exception) as e:
            endpoint = Endpoint.load(endpoint_k8s_yaml_empty_model)
            client.endpoints.begin_create(endpoint=endpoint, no_wait=False)

        assert EMPTY_DIRECTORY_ERROR in str(e.value)

    @pytest.mark.skip(reason="TODO: disable the mir test until we figured out a way to run it")
    @pytest.mark.e2etest
    def test_online_endpoint_mir_e2e(
        self,
        endpoint_mir_yaml: str,
        mir_update_file: str,
        mir_deployment_update_file: str,
        mir_endpoint_name: str,
        request_file: str,
        client: MLClient,
    ) -> None:
        run_endpoint_tests_e2e_create(
            endpoint_yaml=endpoint_mir_yaml,
            update_file=mir_update_file,
            update_deployment_file=mir_deployment_update_file,
            endpoint_name=mir_endpoint_name,
            request_file=request_file,
            client=client,
            is_k8s=False,
        )


def run_endpoint_tests_e2e_create(
    endpoint_yaml: str,
    update_file: str,
    update_deployment_file: str,
    endpoint_name: str,
    request_file: str,
    client: MLClient,
    is_k8s: bool = False,
) -> None:
    print(f"Creating endpoint with name {endpoint_name}")
    try:
        endpoint_file, deployment_names = _prepare_endpoint(endpoint_yaml, is_k8s)
        endpoint = Endpoint.load(endpoint_file)
        endpoint.name = endpoint_name
        client.endpoints.begin_create(endpoint=endpoint, no_wait=False)

        get_obj = client.endpoints.get(name=endpoint_name)
        assert get_obj.name == endpoint_name
        if isinstance(get_obj, KubernetesOnlineEndpoint):
            assert get_obj.auth_mode == AML_TOKEN_YAML

        credentials = client.endpoints.list_keys(name=endpoint_name)
        assert credentials is not None
        if get_obj.auth_mode == KEY:
            assert isinstance(credentials, EndpointAuthKeys)
        elif get_obj.auth_mode == AML_TOKEN_YAML:
            assert isinstance(credentials, EndpointAuthToken)

        if get_obj.auth_mode == KEY:
            client.endpoints.begin_regenerate_keys(name=endpoint_name, key_type=EndpointKeyType.SECONDARY_KEY_TYPE)
            updated_credentials = client.endpoints.list_keys(endpoint_type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)
            assert credentials.secondary_key != updated_credentials.secondary_key
            assert credentials.primary_key == updated_credentials.primary_key

        # there is a bug on the MFE. When RG has upper case charater in the name, then fetching logs will return 400
        # disable the test until the service side is fixed.
        # for deployment in deployment_names:
        #     logs = client.endpoints.get_deployment_logs(endpoint_name, deployment, 10, endpoint_type=ONLINE_ENDPOINT_TYPE)
        #     assert logs
        #     assert logs.count("\n") <= 10

        endpoint_resources = client.endpoints.list()
        assert endpoint_resources is not None
        assert isinstance(endpoint_resources, ItemPaged)

        # Updating endpoint traffic
        for deployment_name in deployment_names:
            endpoint.traffic[deployment_name] = 100
        client.endpoints.begin_update(
            endpoint=endpoint,
            deployment=None,
            no_wait=False,
        )

        # test invoke
        for deployment_name in deployment_names:
            pred = client.endpoints.invoke(
                endpoint_name=endpoint_name,
                request_file=request_file,
                deployment_name=deployment_name,
            )
            assert pred
    except Exception as e:
        raise e
    finally:
        client.endpoints.begin_delete(endpoint_type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)


def run_double_create_e2e(endpoint_yaml: str, endpoint_name: str, client: MLClient):
    endpoint = Endpoint.load(endpoint_yaml)
    endpoint.name = endpoint_name
    resource1 = client.endpoints.begin_create(endpoint=endpoint, no_wait=False)
    resource2 = client.endpoints.begin_create(endpoint=endpoint, no_wait=False)
    assert resource1 == resource2


def _prepare_endpoint(file, is_k8s=False):
    # Updating deployment names to be unique to circumvent as issue in MMS
    # MMS expects deployments name to be unique. This is a bug and MMS will
    # fix it. But this is short term solution on our side
    endpoint = load_yaml(file)
    if is_k8s:
        deployments = endpoint["deployments"]
        deployment_names = []

        for deployment in deployments:
            name = deployment["name"]
            # endpoint name limit is 32 characters
            new_name = (name + "-" + str(uuid.uuid4()))[:32].strip("-")
            deployment["name"] = new_name
            deployment_names.append(new_name)

        file = Path(file)
        new_file = Path.joinpath(file.parent, str(uuid.uuid4()) + "-" + file.name)
        dump_yaml_to_file(new_file, endpoint)
        return new_file, deployment_names
    else:
        return file, {d["name"] for d in endpoint["deployments"]}


@pytest.mark.skip(reason="Disable the test because it is used for debugging")
@pytest.mark.e2etest
def test_debug_online_endpoin(client: MLClient) -> None:
    eps = client.endpoints.get(name="k8s-update-test-4")
    print(eps._deserialize())
