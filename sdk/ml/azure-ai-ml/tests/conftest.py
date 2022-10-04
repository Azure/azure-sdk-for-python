import base64
import os
import random
import time
import uuid
from datetime import datetime
from os import getenv
from pathlib import Path
from typing import Callable, Tuple, Union
from unittest.mock import Mock

import pytest
from azure.ai.ml import MLClient, load_component, load_job
from azure.ai.ml._restclient.registry_discovery import \
    AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.ai.ml._scope_dependent_operations import (OperationConfig,
                                                     OperationScope)
from azure.ai.ml._utils._asset_utils import get_object_hash
from azure.ai.ml._utils.utils import hash_dict
from azure.ai.ml.constants._common import GitProperties
from azure.ai.ml.entities import AzureBlobDatastore, Component
from azure.ai.ml.entities._assets import Data, Model
from azure.ai.ml.entities._component.parallel_component import \
    ParallelComponent
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import (AzureCliCredential, ClientSecretCredential,
                            DefaultAzureCredential)
from devtools_testutils import (add_body_key_sanitizer,
                                add_general_regex_sanitizer,
                                add_general_string_sanitizer,
                                add_remove_header_sanitizer, is_live,
                                set_custom_default_matcher, test_proxy)
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils.helpers import is_live_and_not_recording
from devtools_testutils.proxy_fixtures import (VariableRecorder,
                                               variable_recorder)
from pytest_mock import MockFixture

from test_utilities.constants import (Test_Registry_Name, Test_Resource_Group,
                                      Test_Subscription, Test_Workspace_Name)

E2E_TEST_LOGGING_ENABLED = "E2E_TEST_LOGGING_ENABLED"
test_folder = Path(os.path.abspath(__file__)).parent.absolute()


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session")
def fake_datastore_key() -> str:
    fake_key = "this is fake key"
    b64_key = base64.b64encode(fake_key.encode("ascii"))
    return str(b64_key, "ascii")


@pytest.fixture(autouse=True)
def add_sanitizers(test_proxy, fake_datastore_key):
    add_remove_header_sanitizer(headers="x-azureml-token,Log-URL")
    set_custom_default_matcher(
        excluded_headers="x-ms-meta-name,x-ms-meta-version")
    add_body_key_sanitizer(json_path="$.key", value=fake_datastore_key)
    add_body_key_sanitizer(json_path="$....key", value=fake_datastore_key)
    add_body_key_sanitizer(
        json_path="$.properties.properties.['mlflow.source.git.repoURL']", value="fake_git_url")
    add_body_key_sanitizer(
        json_path="$.properties.properties.['mlflow.source.git.branch']", value="fake_git_branch")
    add_body_key_sanitizer(
        json_path="$.properties.properties.['mlflow.source.git.commit']", value="fake_git_commit")
    add_body_key_sanitizer(
        json_path="$.properties.properties.hash_sha256", value="0000000000000")
    add_body_key_sanitizer(
        json_path="$.properties.properties.hash_version", value="0000000000000")
    add_body_key_sanitizer(
        json_path="$.properties.properties.['azureml.git.dirty']", value="fake_git_dirty_value")
    add_general_regex_sanitizer(
        value="", regex=f"\\u0026tid={os.environ.get('ML_TENANT_ID')}")
    add_general_string_sanitizer(
        value="", target=f"&tid={os.environ.get('ML_TENANT_ID')}")
    add_general_regex_sanitizer(value="00000000000000000000000000000000",
                                regex="\\/LocalUpload\\/(\\S{32})\\/?", group_for_replace="1")
    add_general_regex_sanitizer(value="00000000000000000000000000000000",
                                regex="\\/az-ml-artifacts\\/(\\S{32})\\/", group_for_replace="1")


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
def mock_operation_config() -> OperationConfig:
    yield OperationConfig(True)


@pytest.fixture
def sanitized_environment_variables(environment_variables, fake_datastore_key) -> dict:
    sanitizings = {
        "ML_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000",
        "ML_RESOURCE_GROUP": "00000",
        "ML_WORKSPACE_NAME": "00000",
        "ML_TEST_STORAGE_ACCOUNT_NAME": "teststorageaccount",
        "ML_TEST_STORAGE_ACCOUNT_PRIMARY_KEY": fake_datastore_key,
        "ML_TEST_STORAGE_ACCOUNT_SECONDARY_KEY": fake_datastore_key,
    }
    return environment_variables.sanitize_batch(sanitizings)


@pytest.fixture
def mock_registry_scope() -> OperationScope:
    yield OperationScope(
        subscription_id=Test_Subscription,
        resource_group_name=Test_Resource_Group,
        workspace_name=Test_Workspace_Name,
        registry_name=Test_Registry_Name,
    )


@pytest.fixture
def mock_machinelearning_client(mocker: MockFixture) -> MLClient:
    # TODO(1628638): remove when 2022_02 api is available in ARM
    mocker.patch(
        "azure.ai.ml.operations.JobOperations._get_workspace_url", return_value="xxx")
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
def mock_aml_services_2022_06_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_06_01_preview")


@pytest.fixture
def mock_aml_services_run_history(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.runhistory")


@pytest.fixture
def mock_registry_discovery_client(mock_credential: DefaultAzureCredential) -> ServiceClientRegistryDiscovery:
    yield ServiceClientRegistryDiscovery(mock_credential)


@pytest.fixture
def mock_aml_services_2022_05_01(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_05_01")


@pytest.fixture
def randstr(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random string, e.g. test-xxx"""

    def generate_random_string(variable_name: str):
        random_string = f"test_{str(random.randint(1, 1000000000000))}"
        return variable_recorder.get_or_record(variable_name, random_string)

    return generate_random_string


@pytest.fixture
def rand_compute_name(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random compute name string, e.g. testxxx"""

    def generate_random_string(variable_name: str):
        random_string = f"test{str(random.randint(1, 1000000000000))}"
        return variable_recorder.get_or_record(variable_name, random_string)

    return generate_random_string


@pytest.fixture(scope="session")
def randint() -> Callable[[], int]:
    """returns a random int"""
    return lambda: random.randint(1, 10000000)


@pytest.fixture
def e2e_ws_scope(sanitized_environment_variables: dict) -> OperationScope:
    return OperationScope(
        subscription_id=sanitized_environment_variables["ML_SUBSCRIPTION_ID"],
        resource_group_name=sanitized_environment_variables["ML_RESOURCE_GROUP"],
        workspace_name=sanitized_environment_variables["ML_WORKSPACE_NAME"],
    )


@pytest.fixture
def client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        workspace_name=e2e_ws_scope.workspace_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        cloud="AzureCloud"
    )


@pytest.fixture
def registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        workspace_name=e2e_ws_scope.workspace_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="testFeed",
    )


@pytest.fixture
def only_registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="testFeed",
    )


@pytest.fixture
def crud_registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name=None,  # This must be set to None for CRUD operations
    )


@pytest.fixture
def resource_group_name(location: str) -> str:
    return f"test-rg-{location}-v2-{_get_week_format()}"


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
    model = Model(name=name, version="1",
                  path="tests/test_configs/batch_setup/batch_endpoint_model")

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
        job = load_job(source="./tests/test_configs/batch_setup/lgb.yml")
        job.name = job_name
        print(f"Starting new job with name {job_name}")
        job = client.jobs.create_or_update(job)
        job_status = job.status
        while job_status not in RunHistoryConstants.TERMINAL_STATUSES:
            print(
                f"Job status is {job_status}, waiting for 30 seconds for the job to finish.")
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
        client, path=test_folder /
        "./test_configs/dsl_pipeline/e2e_registered_components/train.yml"
    )


@pytest.fixture
def pipeline_samples_e2e_registered_score_components(client: MLClient) -> Component:
    return _load_or_create_component(
        client, path=test_folder /
        "./test_configs/dsl_pipeline/e2e_registered_components/score.yml"
    )


@pytest.fixture
def pipeline_samples_e2e_registered_eval_components(client: MLClient) -> Component:
    return _load_or_create_component(
        client, path=test_folder /
        "./test_configs/dsl_pipeline/e2e_registered_components/eval.yml"
    )


@pytest.fixture
def mock_code_hash(request, mocker: MockFixture) -> None:

    def generate_hash():
        return str(uuid.uuid4())

    if is_live_and_not_recording():
        mocker.patch(
            "azure.ai.ml._artifacts._artifact_utilities.get_object_hash", side_effect=generate_hash)
    elif not is_live():
        mocker.patch("azure.ai.ml._artifacts._artifact_utilities.get_object_hash",
                     return_value="00000000000000000000000000000000")


@pytest.fixture
def mock_asset_name(mocker: MockFixture):
    fake_uuid = "000000000000000000000"

    def generate_uuid(*args, **kwargs):
        real_uuid = str(uuid.uuid4())
        add_general_string_sanitizer(value=fake_uuid, target=real_uuid)
        return real_uuid

    if is_live():
        mocker.patch(
            "azure.ai.ml.entities._assets.asset._get_random_name", side_effect=generate_uuid)
    else:
        mocker.patch(
            "azure.ai.ml.entities._assets.asset._get_random_name", return_value=fake_uuid)


@pytest.fixture
def mock_component_hash(mocker: MockFixture):
    fake_component_hash = "000000000000000000000"

    def generate_compononent_hash(*args, **kwargs):
        dict_hash = hash_dict(*args, **kwargs)
        add_general_string_sanitizer(
            value=fake_component_hash, target=dict_hash)
        return dict_hash

    if is_live():
        mocker.patch("azure.ai.ml.entities._component.component.hash_dict",
                     side_effect=generate_compononent_hash)
    else:
        mocker.patch("azure.ai.ml.entities._component.component.hash_dict",
                     return_value=fake_component_hash)


@pytest.fixture
def mock_workspace_arm_template_deployment_name(mocker: MockFixture, variable_recorder: VariableRecorder):
    def generate_mock_workspace_deployment_name(name: str):
        deployment_name = get_deployment_name(name)
        return variable_recorder.get_or_record("deployment_name", deployment_name)

    mocker.patch(
        "azure.ai.ml.operations._workspace_operations.get_deployment_name",
        side_effect=generate_mock_workspace_deployment_name,
    )


@pytest.fixture
def mock_workspace_dependent_resource_name_generator(mocker: MockFixture, variable_recorder: VariableRecorder):
    def generate_mock_workspace_dependent_resource_name(workspace_name: str, resource_type: str):
        deployment_name = get_name_for_dependent_resource(
            workspace_name, resource_type)
        return variable_recorder.get_or_record(f"{resource_type}_name", deployment_name)

    mocker.patch(
        "azure.ai.ml.operations._workspace_operations.get_name_for_dependent_resource",
        side_effect=generate_mock_workspace_dependent_resource_name,
    )


@pytest.fixture(autouse=True)
def mock_job_name_generator(mocker: MockFixture):
    fake_job_name = "000000000000000000000"

    def generate_and_sanitize_job_name(*args, **kwargs):
        real_job_name = generate_job_name()
        add_general_string_sanitizer(value=fake_job_name, target=real_job_name)
        return real_job_name

    if is_live():
        mocker.patch(
            "azure.ai.ml.entities._job.to_rest_functions.generate_job_name", side_effect=generate_and_sanitize_job_name
        )
    else:
        mocker.patch("azure.ai.ml.entities._job.to_rest_functions.generate_job_name",
                     return_value=fake_job_name)


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


@pytest.fixture
def auth() -> Union[AzureCliCredential, ClientSecretCredential, FakeTokenCredential]:

    if is_live():
        tenant_id = os.environ.get("ML_TENANT_ID")
        sp_id = os.environ.get("ML_CLIENT_ID")
        sp_secret = os.environ.get("ML_CLIENT_SECRET")
        if not (sp_id or sp_secret):
            return AzureCliCredential()
        return ClientSecretCredential(tenant_id, sp_id, sp_secret)

    return FakeTokenCredential()


@pytest.fixture
def storage_account_name(sanitized_environment_variables: dict) -> str:
    return sanitized_environment_variables["ML_TEST_STORAGE_ACCOUNT_NAME"]


@pytest.fixture
def account_keys(sanitized_environment_variables) -> Tuple[str, str]:
    return (
        sanitized_environment_variables["ML_TEST_STORAGE_ACCOUNT_PRIMARY_KEY"],
        sanitized_environment_variables["ML_TEST_STORAGE_ACCOUNT_SECONDARY_KEY"],
    )


@pytest.fixture
def credentialless_datastore(client: MLClient, storage_account_name: str) -> AzureBlobDatastore:
    ds_name = "testcredentialless"
    container_name = "testblob"

    try:
        credentialless_ds = client.datastores.get(name=ds_name)
    except ResourceNotFoundError:
        ds = AzureBlobDatastore(
            name=ds_name, account_name=storage_account_name, container_name=container_name)
        credentialless_ds = client.datastores.create_or_update(ds)
        assert isinstance(credentialless_ds.credentials, NoneCredentialConfiguration)

    return credentialless_ds.name


# this works UNLESS you use vcr.use_cassette. Since we are using vcr.use_cassette to
# specify the cassette location, don't provide the vcr config here
# @pytest.fixture(scope='module')
# def vcr_config():
#     return {
#     }


@pytest.fixture()
def enable_pipeline_private_preview_features(mocker: MockFixture):
    mocker.patch(
        "azure.ai.ml.entities._job.pipeline.pipeline_job.is_private_preview_enabled", return_value=True)
    mocker.patch(
        "azure.ai.ml.dsl._pipeline_component_builder.is_private_preview_enabled", return_value=True)


@pytest.fixture()
def enable_environment_id_arm_expansion(mocker: MockFixture):
    mocker.patch(
        "azure.ai.ml.operations._operation_orchestrator.is_private_preview_enabled", return_value=False)


@pytest.fixture(autouse=True)
def remove_git_props(mocker: MockFixture):
    mocker.patch(
        "azure.ai.ml.operations._job_operations.get_git_properties", return_value={})


@pytest.fixture()
def enable_internal_components():
    from azure.ai.ml._utils.utils import try_enable_internal_components
    from azure.ai.ml.constants._common import \
        AZUREML_INTERNAL_COMPONENTS_ENV_VAR
    from azure.ai.ml.dsl._utils import environment_variable_overwrite

    with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "True"):
        # need to call _try_init_internal_components manually as environment variable is set after _internal is imported
        try_enable_internal_components()
