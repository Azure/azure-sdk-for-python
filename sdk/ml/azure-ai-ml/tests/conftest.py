from os import getenv
import time
import random
from typing import Callable, Tuple
import uuid
import os
from pathlib import Path

from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.ai.ml._scope_dependent_operations import OperationScope
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.ai.ml import MLClient
from test_utilities.constants import Test_Subscription, Test_Resource_Group, Test_Workspace_Name
from datetime import datetime
from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.mgmt.storage import StorageManagementClient
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml.entities import Job, Component, AzureBlobDatastore, CommandComponent
from azure.ai.ml.entities._component.parallel_component import ParallelComponent

from azure.ai.ml.entities._assets import Model, Data
from azure.ai.ml.entities._datastore.credentials import NoneCredentials
from azure.ai.ml import load_job, load_component

E2E_TEST_LOGGING_ENABLED = "E2E_TEST_LOGGING_ENABLED"
test_folder = Path(os.path.abspath(__file__)).parent.absolute()


def pytest_addoption(parser):
    parser.addoption("--location", action="store", default="eastus2euap")


@pytest.fixture
def location(request):
    return request.config.getoption("--location")


@pytest.fixture
def mock_credential():
    yield Mock(spec_set=DefaultAzureCredential)


@pytest.fixture
def mock_workspace_scope() -> OperationScope:
    yield OperationScope(
        subscription_id=Test_Subscription, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
    )


@pytest.fixture
def mock_machinelearning_client(mocker: MockFixture) -> MLClient:
    # TODO(1628638): remove when 2022_02 api is available in ARM
    mocker.patch("azure.ai.ml.operations.JobOperations._get_workspace_url", return_value="xxx")
    yield MLClient(
        credential=Mock(spec_set=DefaultAzureCredential),
        subscription_id=Test_Subscription,
        resource_group_name=Test_Resource_Group,
        workspace_name=Test_Workspace_Name,
    )


@pytest.fixture
def mock_aml_services_2021_10_01(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2021_10_01")


@pytest.fixture
def mock_aml_services_2022_01_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_01_01_preview")


@pytest.fixture
def mock_aml_services_2020_09_01_dataplanepreview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2020_09_01_dataplanepreview")


@pytest.fixture
def mock_aml_services_2022_02_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_02_01_preview")


@pytest.fixture
def mock_aml_services_run_history(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.runhistory")


@pytest.fixture
def mock_registry_discovery_client(mock_credential: DefaultAzureCredential) -> ServiceClientRegistryDiscovery:
    yield ServiceClientRegistryDiscovery(mock_credential)


@pytest.fixture
def mock_aml_services_2022_05_01(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_05_01")


@pytest.fixture(scope="session")
def randstr() -> Callable[[], str]:
    """return a random string, e.g. test-xxx"""
    return lambda: f"test_{str(random.randint(1, 1000000000000))}"


@pytest.fixture(scope="session")
def rand_compute_name() -> Callable[[], str]:
    """return a random compute name string, e.g. testxxx"""
    return lambda: f"test{str(random.randint(1, 10000000000))}"


@pytest.fixture(scope="session")
def randint() -> Callable[[], int]:
    """returns a random int"""
    return lambda: random.randint(1, 10000000)


@pytest.fixture
def e2e_ws_scope(resource_group_name: str, location: str) -> OperationScope:
    return OperationScope(
        subscription_id="b17253fa-f327-42d6-9686-f3e553e24763",
        resource_group_name=resource_group_name,
        workspace_name="sdk_vnext_cli",
    )


@pytest.fixture
def client(e2e_ws_scope: OperationScope) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=get_auth(),
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        workspace_name=e2e_ws_scope.workspace_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
    )


@pytest.fixture
def registry_client(e2e_ws_scope: OperationScope) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=get_auth(),
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        workspace_name=e2e_ws_scope.workspace_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="testFeed",
    )


@pytest.fixture
def only_registry_client(e2e_ws_scope: OperationScope) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=get_auth(),
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="testFeed",
    )


@pytest.fixture
def client_fixture(request, client) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    request.cls.client = client


@pytest.fixture
def resource_group_name(location: str) -> str:
    return f"test-rg-{location}-v2-t-{_get_week_format()}"


@pytest.fixture
def data_with_2_versions(client: MLClient) -> str:
    name = "list_data_v2_test"

    try:
        client.data.get(name, "1")
    except ResourceNotFoundError:
        # Create the data version if not exits
        data = Data(name=name, version="1", path="https://bla")
        client.data.create_or_update(data)

    try:
        client.data.get(name, "2")
    except ResourceNotFoundError:
        # Create the data version if not exits
        data = Data(name=name, version="2", path="http://bla")
        client.data.create_or_update(data)

    return name


@pytest.fixture
def batch_endpoint_model(client: MLClient) -> Model:
    name = "sklearn_regression_model"
    model = Model(name=name, version="1", path="tests/test_configs/batch_setup/batch_endpoint_model")

    try:
        model = client.models.get(name, "1")
    except ResourceNotFoundError:
        # Create the data version if not exits
        model._base_path = "."
        model = client.models.create_or_update(model)

    return model


@pytest.fixture
def light_gbm_model(client: MLClient) -> Model:
    job_name = "light_gbm_job_" + uuid.uuid4().hex
    model_name = "lightgbm_predict"  # specified in the mlflow training script

    try:
        client.models.get(name=model_name, version="1")
    except ResourceNotFoundError:
        job = load_job(path="./tests/test_configs/batch_setup/lgb.yml")
        job.name = job_name
        print(f"Starting new job with name {job_name}")
        job = client.jobs.create_or_update(job)
        job_status = job.status
        while job_status not in RunHistoryConstants.TERMINAL_STATUSES:
            print(f"Job status is {job_status}, waiting for 30 seconds for the job to finish.")
            time.sleep(30)
            job_status = client.jobs.get(job_name).status


@pytest.fixture
def hello_world_component(client: MLClient) -> Component:
    return _load_or_create_component(client, path="./tests/test_configs/components/helloworld_component.yml")


@pytest.fixture
def hello_world_component_no_paths(client: MLClient) -> Component:
    return _load_or_create_component(client, path="./tests/test_configs/components/helloworld_component_no_paths.yml")


@pytest.fixture
def helloworld_component_with_paths(client: MLClient) -> Component:
    return _load_or_create_component(client, path="./tests/test_configs/components/helloworld_component_with_paths.yml")


@pytest.fixture
def batch_inference(client: MLClient) -> ParallelComponent:
    return _load_or_create_component(
        client, path="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"
    )


@pytest.fixture
def pipeline_samples_e2e_registered_train_components(client: MLClient) -> Component:
    return _load_or_create_component(
        client, path=test_folder / "./test_configs/dsl_pipeline/e2e_registered_components/train.yml"
    )


@pytest.fixture
def pipeline_samples_e2e_registered_score_components(client: MLClient) -> Component:
    return _load_or_create_component(
        client, path=test_folder / "./test_configs/dsl_pipeline/e2e_registered_components/score.yml"
    )


@pytest.fixture
def pipeline_samples_e2e_registered_eval_components(client: MLClient) -> Component:
    return _load_or_create_component(
        client, path=test_folder / "./test_configs/dsl_pipeline/e2e_registered_components/eval.yml"
    )


@pytest.fixture
def mock_code_hash(mocker: MockFixture) -> None:
    mocker.patch("azure.ai.ml._artifacts._artifact_utilities.get_object_hash", return_value=str(uuid.uuid4()))


def _load_or_create_component(client: MLClient, path: str) -> Component:
    try:
        component = load_component(path)
        return client.components.get(name=component.name, version=component.version)
    except ResourceNotFoundError:
        return client.components.create_or_update(component)


def _get_week_format() -> str:
    """Will produce something like 2019W03 or 2019W16"""
    c = datetime.utcnow().isocalendar()
    return "{}W{:02d}".format(c[0], c[1])


def get_auth():
    from azure.identity import AzureCliCredential

    auth = AzureCliCredential()

    tenant_id = getenv("tenantId", None)
    sp_id = getenv("servicePrincipalId", None)
    sp_secret = getenv("servicePrincipalKey", None)

    if tenant_id and sp_id and sp_secret:
        auth = ClientSecretCredential(tenant_id, sp_id, sp_secret)
        print(f"Using Service Principal auth with tenantId {tenant_id}")

    return auth


@pytest.fixture
def storage_account_name(client: MLClient) -> str:
    storage_client = StorageManagementClient(client._credential, client._operation_scope._subscription_id)
    storage_account_list = storage_client.storage_accounts.list()
    return [
        account
        for account in storage_account_list
        if (account.name.startswith("sdkvnextcli") and client._operation_scope._resource_group_name in account.id)
    ][0].name


@pytest.fixture
def account_keys(client: MLClient, storage_account_name: str) -> Tuple[str, str]:
    storage_client = StorageManagementClient(client._credential, client._operation_scope._subscription_id)
    keys = storage_client.storage_accounts.list_keys(
        client._operation_scope._resource_group_name, storage_account_name
    ).keys
    return keys[0].value, keys[1].value


@pytest.fixture
def credentialless_datastore(client: MLClient, storage_account_name: str) -> AzureBlobDatastore:
    ds_name = "testcredentialless"
    container_name = "testblob"

    try:
        credentialless_ds = client.datastores.get(name=ds_name)
    except ResourceNotFoundError:
        ds = AzureBlobDatastore(name=ds_name, account_name=storage_account_name, container_name=container_name)
        credentialless_ds = client.datastores.create_or_update(ds)
        assert isinstance(credentialless_ds.credentials, NoneCredentials)

    return credentialless_ds.name


# this works UNLESS you use vcr.use_cassette. Since we are using vcr.use_cassette to
# specify the cassette location, don't provide the vcr config here
# @pytest.fixture(scope='module')
# def vcr_config():
#     return {
#     }


@pytest.fixture()
def enable_pipeline_private_preview_features(mocker: MockFixture):
    mocker.patch("azure.ai.ml.entities._job.pipeline.pipeline_job.is_private_preview_enabled", return_value=True)


@pytest.fixture()
def enable_internal_components():
    from azure.ai.ml.dsl._utils import environment_variable_overwrite
    from azure.ai.ml._utils.utils import try_enable_internal_components
    from azure.ai.ml.constants import AZUREML_INTERNAL_COMPONENTS_ENV_VAR

    with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "True"):
        # need to call _try_init_internal_components manually as environment variable is set after _internal is imported
        try_enable_internal_components()
