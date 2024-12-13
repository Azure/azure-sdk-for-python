import random

import pytest
import platform
import sys

from azure.ai.ml import MLClient, load_online_deployment, load_online_endpoint
from azure.ai.ml.entities import OnlineDeployment, OnlineEndpoint
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._assets.environment import Environment
from azure.core.exceptions import ResourceNotFoundError


@pytest.fixture
def mir_endpoint_name() -> str:
    return f"mir-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_mir_yaml() -> str:
    return "tests/test_configs/deployments/online/simple_online_endpoint_mir.yaml"


@pytest.fixture
def deployment_create_yaml() -> str:
    return "./tests/test_configs/deployments/online/online_deployment_2.yaml"


@pytest.fixture
def deployment_update_file() -> str:
    return "./tests/test_configs/deployments/online/online_deployment_2.yaml"


@pytest.fixture
def mir_update_file() -> str:
    return "./tests/test_configs/online/managed/canary-declarative-flow/6-delete-blue.yaml"


@pytest.fixture
def request_file() -> str:
    return "./tests/test_configs/deployments/model-1/sample-request.json"


@pytest.mark.e2etest
@pytest.mark.local_endpoint_local_assets
@pytest.mark.skipif(
    platform.python_implementation() == "PyPy" or sys.platform.startswith("darwin"),
    reason="Skipping for PyPy and macOS as docker installation is not supported and skipped in dev_requirement.txt",
)
def test_local_endpoint_mir_e2e(
    endpoint_mir_yaml: str,
    mir_endpoint_name: str,
    request_file: str,
    client: MLClient,
) -> None:
    endpoint = load_online_endpoint(endpoint_mir_yaml)
    endpoint.name = mir_endpoint_name
    client.online_endpoints.begin_create_or_update(endpoint=endpoint, local=True)

    get_obj = client.online_endpoints.get(name=mir_endpoint_name, local=True)
    assert get_obj is not None

    list_obj = client.online_endpoints.list(local=True)
    assert list_obj is not None
    assert len(list(list_obj)) > 0

    response = client.online_endpoints.invoke(endpoint_name=mir_endpoint_name, request_file=request_file, local=True)
    assert "az ml online-deployment" in response

    client.online_endpoints.begin_delete(name=mir_endpoint_name, local=True)


@pytest.mark.e2etest
@pytest.mark.local_endpoint_local_assets
@pytest.mark.skip()
def test_local_deployment_mir_e2e(
    deployment_create_yaml: str,
    deployment_update_file: str,
    mir_endpoint_name: str,
    request_file: str,
    client: MLClient,
) -> None:
    run_local_endpoint_tests_e2e_create(
        deployment_yaml=deployment_create_yaml,
        update_file=deployment_update_file,
        deployment_name="dep",
        endpoint_name=mir_endpoint_name,
        request_file=request_file,
        client=client,
    )


@pytest.mark.e2etest
@pytest.mark.local_endpoint_local_assets
@pytest.mark.skip()
def test_local_deployment_mir_model_code_overlap_e2e(
    mir_endpoint_name: str,
    request_file: str,
    client: MLClient,
) -> None:
    run_local_endpoint_tests_e2e_create(
        deployment_yaml="tests/test_configs/deployments/online/online_deployment_model_code_overlap.yaml",
        update_file=None,
        deployment_name="dep",
        endpoint_name=mir_endpoint_name,
        request_file=request_file,
        client=client,
    )


@pytest.mark.e2etest
@pytest.mark.local_endpoint_byoc
@pytest.mark.local_endpoint_local_assets
@pytest.mark.skip()
def test_local_deployment_mir_e2e_byoc(
    mir_endpoint_name: str,
    client: MLClient,
) -> None:
    run_local_endpoint_tests_e2e_create(
        deployment_yaml="tests/test_configs/deployments/byoc/tfserving/online_deployment_tfserving.yaml",
        update_file=None,
        deployment_name="dep",
        endpoint_name=mir_endpoint_name,
        request_file="tests/test_configs/deployments/byoc/tfserving/sample_request.json",
        client=client,
        is_sklearn=False,
    )


@pytest.mark.e2etest
@pytest.mark.local_endpoint_byoc
@pytest.mark.skip("Requires building docker image and specific ACR info we don't have from pipelines.")
def test_local_deployment_mir_e2e_byoc_sklearn(
    mir_endpoint_name: str,
    request_file: str,
    client: MLClient,
) -> None:
    ## Uncomment for helping with running BYOC for sklearn scenario
    # register_env(
    #     name="sklearn-env",
    #     version="1",
    #     image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04",
    #     conda_file="tests/test_configs/deployments/model-1/environment/conda.yml",
    #     client=client,
    # )
    # workspace = client.workspaces.get(name=client.workspace_name)
    # acr_name = workspace.container_registry.split("/")[-1]
    # # Get acr_image_name from AML Studio for environment after built
    # acr_image_name = "azureml/azureml_0d501feced865646087d1b823b8c3c35"
    # image_name = f"{acr_name}.azurecr.io/{acr_image_name}"
    ## Update deployment yaml with image name
    run_local_endpoint_tests_e2e_create(
        deployment_yaml="tests/test_configs/deployments/byoc/sklearn/online_deployment_byoc_sklearn.yaml",
        update_file=None,
        deployment_name="dep",
        endpoint_name=mir_endpoint_name,
        request_file=request_file,
        client=client,
        is_sklearn=True,
    )


@pytest.mark.e2etest
@pytest.mark.local_endpoint_registered_assets
@pytest.mark.parametrize(
    """deployment_create_yaml,model_to_register,code_to_register,conda_env_to_register""",
    [
        pytest.param(
            "tests/test_configs/deployments/online/online_deployment_registered_model.yaml",
            "tests/test_configs/deployments/model-1/model/sklearn_regression_model.pkl",
            None,
            None,
            marks=pytest.mark.skip(reason="Registered model covered in full registered assets test."),
        ),
        pytest.param(
            "tests/test_configs/deployments/online/online_deployment_registered_code.yaml",
            None,
            "tests/test_configs/deployments/model-1/onlinescoring/",
            None,
            marks=pytest.mark.skip(reason="Registered code covered in full registered assets test."),
        ),
        pytest.param(
            "tests/test_configs/deployments/online/online_deployment_registered_env.yaml",
            None,
            None,
            "tests/test_configs/deployments/model-1/environment/conda.yml",
            marks=pytest.mark.skip(reason="Registered env covered in full registered assets test."),
        ),
        pytest.param(
            "tests/test_configs/deployments/online/online_deployment_registered_artifacts.yaml",
            "tests/test_configs/deployments/model-1/model/sklearn_regression_model.pkl",
            "tests/test_configs/deployments/model-1/onlinescoring/",
            "tests/test_configs/deployments/model-1/environment/conda.yml",
        ),
    ],
)
@pytest.mark.skip()
def test_local_deployment_mir_e2e_registered_artifacts(
    mir_endpoint_name: str,
    request_file: str,
    client: MLClient,
    deployment_create_yaml: str,
    model_to_register: str,
    code_to_register: str,
    conda_env_to_register: str,
) -> None:
    if model_to_register:
        register_model(
            name="sklearn-model",
            version="1",
            path=model_to_register,
            client=client,
        )
    if code_to_register:
        register_code(
            name="code-1",
            version="1",
            path=code_to_register,
            client=client,
        )
    if conda_env_to_register:
        register_env(
            name="sklearn-env",
            version="1",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04",
            conda_file=conda_env_to_register,
            client=client,
        )
    run_local_endpoint_tests_e2e_create(
        deployment_yaml=deployment_create_yaml,
        update_file=None,
        deployment_name="dep",
        endpoint_name=mir_endpoint_name,
        request_file=request_file,
        client=client,
    )


def register_model(
    name: str,
    version: str,
    path: str,
    client: MLClient,
):
    model = Model(name=name, path=path, version=version)
    client.models.create_or_update(model)


def register_code(
    name: str,
    version: str,
    path: str,
    client: MLClient,
):
    code = Code(name=name, path=path, version=version)
    client._code.create_or_update(code)


def register_env(
    name: str,
    version: str,
    image: str,
    conda_file: str,
    client: MLClient,
) -> Environment:
    try:
        env = client.environments.get(name=name, version=version)
    except ResourceNotFoundError:
        env = Environment(name=name, image=image, conda_file=conda_file, version=version)
        env = client.environments.create_or_update(env)
    return env


def run_local_endpoint_tests_e2e_create(
    deployment_yaml: str,
    update_file: str,
    endpoint_name: str,
    deployment_name: str,
    request_file: str,
    client: MLClient,
    is_sklearn: bool = True,
) -> None:
    print(f"Creating endpoint with name {endpoint_name}")
    try:
        deployment = load_online_deployment(deployment_yaml)
        deployment.endpoint_name = endpoint_name
        deployment.name = deployment_name
        client.online_deployments.begin_create_or_update(deployment=deployment, no_wait=False, local=True)

        get_obj = client.online_deployments.get(endpoint_name=endpoint_name, name=deployment_name, local=True)
        assert get_obj.name == deployment_name
        assert get_obj.endpoint_name == endpoint_name

        get_obj = client.online_endpoints.get(name=endpoint_name, local=True)
        assert get_obj.name == endpoint_name
        assert get_obj.scoring_uri is not None
        assert get_obj.scoring_uri != ""

        data = client.online_endpoints.invoke(endpoint_name=endpoint_name, request_file=request_file, local=True)
        assert type(data) is str
        if is_sklearn:
            assert "5215" in data
            assert "3726" in data

        logs = client.online_deployments.get_logs(
            endpoint_name=endpoint_name, name=deployment_name, lines=10, local=True
        )
        assert logs
        if is_sklearn:
            assert logs.count("\n") == 10

        deployments = client.online_deployments.list(endpoint_name=endpoint_name, local=True)
        assert deployments is not None
        assert len(list(deployments)) > 0

        if update_file:
            deployment = load_online_deployment(update_file)
            deployment.endpoint_name = endpoint_name
            deployment.name = deployment_name
            client.online_deployments.begin_create_or_update(deployment=deployment, no_wait=False, local=True)

        client.online_deployments.delete(name=deployment_name, endpoint_name=endpoint_name, local=True)
        deployments = client.online_deployments.list(endpoint_name=endpoint_name, local=True)
        assert deployments is not None
        assert endpoint_name not in [dep.endpoint_name for dep in deployments]
    except Exception as e:
        raise e
    finally:
        try:
            client.online_endpoints.begin_delete(name=endpoint_name, local=True)
        except Exception:
            pass
