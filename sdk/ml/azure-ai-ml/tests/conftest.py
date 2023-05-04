import base64
import hashlib
import json
import os
import random
import re
import shutil
import time
import uuid
from collections import namedtuple
from datetime import datetime
from functools import partial
from importlib import reload
from os import getenv
from pathlib import Path
from typing import Callable, Optional, Tuple, Union
from unittest.mock import Mock, patch

import pytest
from _pytest.fixtures import FixtureRequest
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import HttpTransport
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_remove_header_sanitizer,
    is_live,
    set_bodiless_matcher,
    set_custom_default_matcher,
)
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils.helpers import is_live_and_not_recording
from devtools_testutils.proxy_fixtures import VariableRecorder
from pytest_mock import MockFixture
from test_utilities.constants import Test_Registry_Name, Test_Resource_Group, Test_Subscription, Test_Workspace_Name
from test_utilities.utils import reload_schema_for_nodes_in_pipeline_job

from azure.ai.ml import MLClient, load_component, load_job
from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml._utils._asset_utils import IgnoreFile
from azure.ai.ml._utils.utils import hash_dict
from azure.ai.ml.constants._common import (
    ANONYMOUS_COMPONENT_NAME,
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
    SINGULARITY_ID_FORMAT,
)
from azure.ai.ml.entities import AzureBlobDatastore, Component
from azure.ai.ml.entities._assets import Data, Model
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration
from azure.ai.ml.entities._job.job_name_generator import generate_job_name
from azure.ai.ml.operations._run_history_constants import RunHistoryConstants
from azure.ai.ml.operations._workspace_operations_base import get_deployment_name, get_name_for_dependent_resource

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


def _query_param_regex(name, *, only_value=True) -> str:
    """Builds a regex that matches against a query parameter of the form
         (?|&)name=value

    :param: name - The name of the query parameter to match against
    :param: only_value (Optional) - Whether the regex match should just
            match the value of the query param (instead of the name and value)
    """
    # Character that marks the end of a query string value
    QUERY_STRING_DELIMETER = "&#"
    value_regex = rf'[^{QUERY_STRING_DELIMETER}"\s]*'
    name_regex = rf"(?<=[?&]){name}="
    if only_value:
        name_regex = rf"(?<={name_regex})"

    return rf'{name_regex}{value_regex}(?=[{QUERY_STRING_DELIMETER}"\s]|$)'


@pytest.fixture(autouse=True)
def add_sanitizers(test_proxy, fake_datastore_key):
    add_remove_header_sanitizer(headers="x-azureml-token,Log-URL,Authorization")
    set_custom_default_matcher(
        # compare_bodies=False,
        excluded_headers="x-ms-meta-name, x-ms-meta-version,x-ms-blob-type,If-None-Match,Content-Type,Content-MD5,Content-Length",
        ignored_query_parameters="api-version",
    )
    add_body_key_sanitizer(json_path="$.key", value=fake_datastore_key)
    add_body_key_sanitizer(json_path="$....key", value=fake_datastore_key)
    add_body_key_sanitizer(json_path="$.properties.properties.['mlflow.source.git.repoURL']", value="fake_git_url")
    add_body_key_sanitizer(json_path="$.properties.properties.['mlflow.source.git.branch']", value="fake_git_branch")
    add_body_key_sanitizer(json_path="$.properties.properties.['mlflow.source.git.commit']", value="fake_git_commit")
    add_body_key_sanitizer(json_path="$.properties.properties.hash_sha256", value="0000000000000")
    add_body_key_sanitizer(json_path="$.properties.properties.hash_version", value="0000000000000")
    add_body_key_sanitizer(json_path="$.properties.properties.['azureml.git.dirty']", value="fake_git_dirty_value")
    add_body_key_sanitizer(json_path="$.accessToken", value="Sanitized")
    add_general_regex_sanitizer(value="", regex=f"\\u0026tid={os.environ.get('ML_TENANT_ID')}")
    add_general_string_sanitizer(value="", target=f"&tid={os.environ.get('ML_TENANT_ID')}")
    add_general_regex_sanitizer(
        value="00000000000000000000000000000000", regex="\\/LocalUpload\\/(\\S{32})\\/?", group_for_replace="1"
    )
    add_general_regex_sanitizer(
        value="00000000000000000000000000000000", regex="\\/az-ml-artifacts\\/(\\S{32})\\/", group_for_replace="1"
    )
    # for internal code whose upload_hash is of length 36
    add_general_regex_sanitizer(
        value="000000000000000000000000000000000000", regex='\\/LocalUpload\\/([^/\\s"]{36})\\/?', group_for_replace="1"
    )
    add_general_regex_sanitizer(
        value="000000000000000000000000000000000000",
        regex='\\/az-ml-artifacts\\/([^/\\s"]{36})\\/',
        group_for_replace="1",
    )
    feature_store_name = os.environ.get("ML_FEATURE_STORE_NAME", "env_feature_store_name_note_present")
    add_general_regex_sanitizer(regex=feature_store_name, value="00000")
    # masks signature in SAS uri
    add_general_regex_sanitizer(value="000000000000000000000000000000000000", regex=_query_param_regex("sig"))


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
    yield OperationConfig(show_progress=True, enable_telemetry=True)


@pytest.fixture
def mock_operation_config_no_progress() -> OperationConfig:
    yield OperationConfig(show_progress=False, enable_telemetry=True)


@pytest.fixture
def sanitized_environment_variables(environment_variables, fake_datastore_key) -> dict:
    sanitizings = {
        "ML_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000",
        "ML_RESOURCE_GROUP": "00000",
        "ML_WORKSPACE_NAME": "00000",
        "ML_FEATURE_STORE_NAME": "00000",
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
        workspace_name=None,
        registry_name=Test_Registry_Name,
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
def mock_machinelearning_registry_client(mocker: MockFixture) -> MLClient:
    mock_response = json.dumps(
        {
            "registryName": "testFeed",
            "primaryRegionResourceProviderUri": "https://cert-master.experiments.azureml-test.net/",
            "resourceGroup": "resourceGroup",
            "subscriptionId": "subscriptionId",
        }
    )
    mocker.patch(
        "azure.ai.ml._restclient.registry_discovery.operations._registry_management_non_workspace_operations.RegistryManagementNonWorkspaceOperations.registry_management_non_workspace",
        return_val=mock_response,
    )
    yield MLClient(
        credential=Mock(spec_set=DefaultAzureCredential),
        subscription_id=Test_Subscription,
        resource_group_name=Test_Resource_Group,
        registry_name=Test_Registry_Name,
    )


@pytest.fixture
def mock_aml_services_2022_10_01(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_10_01")


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
def mock_aml_services_2021_10_01_dataplanepreview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2021_10_01_dataplanepreview")


@pytest.fixture
def mock_aml_services_2022_10_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_10_01_preview")


@pytest.fixture
def mock_aml_services_2022_12_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2022_12_01_preview")


@pytest.fixture
def mock_aml_services_2023_02_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2023_02_01_preview")


@pytest.fixture
def mock_aml_services_2023_04_01_preview(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ai.ml._restclient.v2023_04_01_preview")


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
def rand_batch_name(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random batch endpoint name string  e.g. batch-ept-xxx"""

    def generate_random_string(variable_name: str):
        random_string = f"batch-ept-{uuid.uuid4().hex[:15]}"
        return variable_recorder.get_or_record(variable_name, random_string)

    return generate_random_string


@pytest.fixture
def rand_batch_deployment_name(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random batch deployment name string  e.g. batch-dpm-xxx"""

    def generate_random_string(variable_name: str):
        random_string = f"batch-dpm-{uuid.uuid4().hex[:15]}"
        return variable_recorder.get_or_record(variable_name, random_string)

    return generate_random_string


@pytest.fixture
def rand_online_name(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random online endpoint name string  e.g. online-ept-xxx"""

    def generate_random_string(variable_name: str):
        random_string = f"online-ept-{uuid.uuid4().hex[:15]}"
        return variable_recorder.get_or_record(variable_name, random_string)

    return generate_random_string


@pytest.fixture
def rand_online_deployment_name(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random online deployment name string  e.g. online-dpm-xxx"""

    def generate_random_string(variable_name: str):
        random_string = f"online-dpm-{uuid.uuid4().hex[:15]}"
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
def e2e_fs_scope(sanitized_environment_variables: dict) -> OperationScope:
    return OperationScope(
        subscription_id=sanitized_environment_variables["ML_SUBSCRIPTION_ID"],
        resource_group_name=sanitized_environment_variables["ML_RESOURCE_GROUP"],
        workspace_name=sanitized_environment_variables["ML_FEATURE_STORE_NAME"],
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
        cloud="AzureCloud",
    )


@pytest.fixture
def feature_store_client(e2e_fs_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing feature store"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_fs_scope.subscription_id,
        resource_group_name=e2e_fs_scope.resource_group_name,
        workspace_name=e2e_fs_scope.workspace_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        cloud="AzureCloud",
    )


@pytest.fixture
def registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="testFeed",
    )


@pytest.fixture
def data_asset_registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
        subscription_id=e2e_ws_scope.subscription_id,
        resource_group_name=e2e_ws_scope.resource_group_name,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="UnsecureTest-testFeed",
    )


@pytest.fixture
def only_registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    return MLClient(
        credential=auth,
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
def pipelines_registry_client(e2e_ws_scope: OperationScope, auth: ClientSecretCredential) -> MLClient:
    """return a machine learning client using in Pipelines end-to-end tests."""
    return MLClient(
        credential=auth,
        logging_enable=getenv(E2E_TEST_LOGGING_ENABLED),
        registry_name="sdk-test",
    )


@pytest.fixture
def ipp_registry_client(auth: ClientSecretCredential) -> MLClient:
    "return a machine learning client to use for IPP asset registration"
    return MLClient(
        credential=auth, logging_enable=getenv(E2E_TEST_LOGGING_ENABLED), registry_name="UnsecureTest-hello-world"
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
    model = Model(name=name, version="1", path="tests/test_configs/batch_setup/batch_endpoint_model")

    try:
        model = client.models.get(name, "1")
    except ResourceNotFoundError:
        # Create the data version if not exits
        model._base_path = "."
        model = client.models.create_or_update(model)

    return model


@pytest.fixture
def light_gbm_model(client: MLClient, variable_recorder: VariableRecorder) -> Model:
    job_name = variable_recorder.get_or_record("job_name", "light_gbm_job_" + uuid.uuid4().hex)
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
def mock_code_hash(request, mocker: MockFixture) -> None:
    def generate_hash(*args, **kwargs):
        return str(uuid.uuid4())

    if "disable_mock_code_hash" not in request.keywords and is_live_and_not_recording():
        mocker.patch("azure.ai.ml._artifacts._artifact_utilities.get_object_hash", side_effect=generate_hash)
    elif not is_live():
        mocker.patch(
            "azure.ai.ml._artifacts._artifact_utilities.get_object_hash",
            return_value="00000000000000000000000000000000",
        )


@pytest.fixture
def snapshot_hash_sanitizer(test_proxy):
    # masks hash value in URIs
    add_general_regex_sanitizer(
        value="000000000000000000000000000000000000",
        regex=_query_param_regex("hash"),
        function_scoped=True,
    )


@pytest.fixture
def mock_anon_component_version(mocker: MockFixture):

    fake_uuid = "000000000000000000000"

    def generate_name_version(*args, **kwargs):
        real_uuid = str(uuid.uuid4())
        add_general_string_sanitizer(value=fake_uuid, target=real_uuid)
        return ANONYMOUS_COMPONENT_NAME, real_uuid

    def fake_name_version(*args, **kwargs):
        return ANONYMOUS_COMPONENT_NAME, fake_uuid

    if is_live():
        mocker.patch(
            "azure.ai.ml.entities._component.component.Component._get_anonymous_component_name_version",
            side_effect=generate_name_version,
        )
    else:
        mocker.patch(
            "azure.ai.ml.entities._component.component.Component._get_anonymous_component_name_version",
            side_effect=fake_name_version,
        )


@pytest.fixture
def mock_asset_name(mocker: MockFixture):
    fake_uuid = "000000000000000000000"

    def generate_uuid(*args, **kwargs):
        real_uuid = str(uuid.uuid4())
        add_general_string_sanitizer(value=fake_uuid, target=real_uuid)
        return real_uuid

    if is_live():
        mocker.patch("azure.ai.ml.entities._assets.asset._get_random_name", side_effect=generate_uuid)
    else:
        mocker.patch("azure.ai.ml.entities._assets.asset._get_random_name", return_value=fake_uuid)


def normalized_arm_id_in_object(items):
    """Replace the arm id in the object with a normalized value."""
    regex = re.compile(
        r"/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/"
        r"Microsoft\.MachineLearningServices/workspaces/([^/]+)/"
    )
    replacement = (
        "/subscriptions/00000000-0000-0000-0000-000000000/resourceGroups/"
        "00000/providers/Microsoft.MachineLearningServices/workspaces/00000/"
    )

    if isinstance(items, dict):
        for key, value in items.items():
            if isinstance(value, str):
                items[key] = regex.sub(replacement, value)
            else:
                normalized_arm_id_in_object(value)
    elif isinstance(items, list):
        for i, value in enumerate(items):
            if isinstance(value, str):
                items[i] = regex.sub(replacement, value)
            else:
                normalized_arm_id_in_object(value)


def normalized_hash_dict(items: dict, keys_to_omit=None):
    """Normalize items with sanitized value and return hash."""
    normalized_arm_id_in_object(items)
    return hash_dict(items, keys_to_omit)


def generate_component_hash(*args, **kwargs):
    """Normalize component dict with sanitized value and return hash."""
    dict_hash = hash_dict(*args, **kwargs)
    normalized_dict_hash = normalized_hash_dict(*args, **kwargs)
    add_general_string_sanitizer(value=normalized_dict_hash, target=dict_hash)
    return dict_hash


def get_client_hash_with_request_node_name(
    subscription_id: Optional[str],
    resource_group_name: Optional[str],
    workspace_name: Optional[str],
    registry_name: Optional[str],
    random_seed: str,
):
    """Generate a hash for the client."""
    object_hash = hashlib.sha256()
    for s in [
        subscription_id,
        resource_group_name,
        workspace_name,
        registry_name,
        random_seed,
    ]:
        object_hash.update(str(s).encode("utf-8"))
    return object_hash.hexdigest()


def clear_on_disk_cache(cached_resolver):
    """Clear on disk cache for current client."""
    cached_resolver._lock.acquire()
    shutil.rmtree(cached_resolver._on_disk_cache_dir, ignore_errors=True)
    cached_resolver._lock.release()


@pytest.fixture
def mock_component_hash(mocker: MockFixture, request: FixtureRequest):
    """Mock the component hash function.

    In playback mode, workspace information in returned arm_id will be normalized like this:
    /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/.../codes/xxx/versions/xxx
    =>
    /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/.../codes/xxx/versions/xxx
    So the component hash will be different from the recorded one.
    In this mock, we replace the original hash in recordings with the same hash in playback mode.

    Note that component hash value in playback mode can be different from the one in live mode,
    so tests that check component hash directly should be skipped if not is_live.
    """
    if is_live() and not is_live_and_not_recording():
        mocker.patch("azure.ai.ml.entities._component.component.hash_dict", side_effect=generate_component_hash)
        mocker.patch(
            "azure.ai.ml.entities._component.pipeline_component.hash_dict", side_effect=generate_component_hash
        )

    # On-disk cache can't be shared among different tests in playback mode or when recording.
    # When doing recording:
    # 1) Recorded requests may be impacted by the order to run tests. Tests run later will reuse
    #    the cached result from tests run earlier, so we won't found enough recordings when
    #    running tests in reversed order.
    # In playback mode:
    # 1) We can't guarantee that server-side will return the same version for 2 anonymous component
    #   with the same on-disk hash.
    # 2) Server-side may return different version for the same anonymous component in different workspace,
    #   while workspace information will be normalized in recordings. If we record test1 in workspace A
    #   and test2 in workspace B, the version in recordings can be different.
    # So we use a random (probably unique) on-disk cache base directory for each test, and on-disk cache operations
    # will be thread-safe when concurrently running different tests.
    mocker.patch(
        "azure.ai.ml._utils._cache_utils.CachedNodeResolver._get_client_hash",
        side_effect=partial(get_client_hash_with_request_node_name, random_seed=uuid.uuid4().hex),
    )

    # Collect involved resolvers before yield, as fixtures may be destroyed after yield.
    from azure.ai.ml._utils._cache_utils import CachedNodeResolver

    involved_resolvers = []
    for client_fixture_name in ["client", "registry_client"]:
        if client_fixture_name not in request.fixturenames:
            continue
        client: MLClient = request.getfixturevalue(client_fixture_name)
        involved_resolvers.append(
            CachedNodeResolver(
                resolver=None,
                subscription_id=client.subscription_id,
                resource_group_name=client.resource_group_name,
                workspace_name=client.workspace_name,
                registry_name=client._operation_scope.registry_name,
            )
        )

    yield

    # clear on-disk cache after each test
    for resolver in involved_resolvers:
        clear_on_disk_cache(resolver)


@pytest.fixture
def mock_workspace_arm_template_deployment_name(mocker: MockFixture, variable_recorder: VariableRecorder):
    def generate_mock_workspace_deployment_name(name: str):
        deployment_name = get_deployment_name(name)
        return variable_recorder.get_or_record("deployment_name", deployment_name)

    mocker.patch(
        "azure.ai.ml.operations._workspace_operations_base.get_deployment_name",
        side_effect=generate_mock_workspace_deployment_name,
    )


@pytest.fixture
def mock_workspace_dependent_resource_name_generator(mocker: MockFixture, variable_recorder: VariableRecorder):
    def generate_mock_workspace_dependent_resource_name(workspace_name: str, resource_type: str):
        deployment_name = get_name_for_dependent_resource(workspace_name, resource_type)
        return variable_recorder.get_or_record(f"{resource_type}_name", deployment_name)

    mocker.patch(
        "azure.ai.ml.operations._workspace_operations_base.get_name_for_dependent_resource",
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
        mocker.patch("azure.ai.ml.entities._job.to_rest_functions.generate_job_name", return_value=fake_job_name)


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
        ds = AzureBlobDatastore(name=ds_name, account_name=storage_account_name, container_name=container_name)
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
    mocker.patch("azure.ai.ml.entities._job.pipeline.pipeline_job.is_private_preview_enabled", return_value=True)
    mocker.patch("azure.ai.ml._schema.pipeline.pipeline_component.is_private_preview_enabled", return_value=True)
    mocker.patch("azure.ai.ml.entities._schedule.schedule.is_private_preview_enabled", return_value=True)
    mocker.patch("azure.ai.ml.dsl._pipeline_decorator.is_private_preview_enabled", return_value=True)
    mocker.patch("azure.ai.ml._utils._cache_utils.is_private_preview_enabled", return_value=True)


@pytest.fixture()
def enable_private_preview_schema_features():
    """Schemas will be imported at the very beginning, so need to reload related classes."""
    from azure.ai.ml._internal._setup import _registered, enable_internal_components_in_pipeline
    from azure.ai.ml._schema.component import command_component as command_component_schema
    from azure.ai.ml._schema.component import component as component_schema
    from azure.ai.ml._schema.component import input_output
    from azure.ai.ml._schema.pipeline import pipeline_component as pipeline_component_schema
    from azure.ai.ml._schema.pipeline import pipeline_job as pipeline_job_schema
    from azure.ai.ml.entities._component import command_component as command_component_entity
    from azure.ai.ml.entities._component import pipeline_component as pipeline_component_entity
    from azure.ai.ml.entities._job.pipeline import pipeline_job as pipeline_job_entity

    def _reload_related_classes():
        reload(input_output)
        reload(component_schema)
        reload(command_component_schema)
        reload(pipeline_component_schema)
        reload(pipeline_job_schema)

        command_component_entity.CommandComponentSchema = command_component_schema.CommandComponentSchema
        pipeline_component_entity.PipelineComponentSchema = pipeline_component_schema.PipelineComponentSchema
        pipeline_job_entity.PipelineJobSchema = pipeline_job_schema.PipelineJobSchema

        # check internal flag after reload, force register if it is set as True
        if _registered:
            enable_internal_components_in_pipeline(force=True)

    with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "True"}):
        _reload_related_classes()
        yield
    _reload_related_classes()


@pytest.fixture()
def enable_environment_id_arm_expansion(mocker: MockFixture):
    mocker.patch("azure.ai.ml._utils.utils.is_private_preview_enabled", return_value=False)


@pytest.fixture(autouse=True)
def remove_git_props(mocker: MockFixture):
    mocker.patch("azure.ai.ml.operations._job_operations.get_git_properties", return_value={})


@pytest.fixture()
def enable_internal_components():
    from azure.ai.ml._utils.utils import try_enable_internal_components
    from azure.ai.ml.constants._common import AZUREML_INTERNAL_COMPONENTS_ENV_VAR
    from azure.ai.ml.dsl._utils import environment_variable_overwrite

    with environment_variable_overwrite(AZUREML_INTERNAL_COMPONENTS_ENV_VAR, "True"):
        # need to call _try_init_internal_components manually as environment variable is set after _internal is imported
        try_enable_internal_components()
        yield  # run test with env var overwritten


@pytest.fixture()
def bodiless_matching(test_proxy):
    set_bodiless_matcher()


@pytest.fixture(autouse=True)
def skip_sleep_for_playback():
    """Mock time.sleep() for playback mode.
    time.sleep() is usually used to wait for long-running operations to complete.
    While in playback mode, we don't need wait as no actual remote operations are being performed.

    Works on sync requests only for now. Need to mock asyncio.sleep and
    trio.sleep if we want to apply this to async requests.

    Please disable this fixture if you want to use time.sleep() for other reason.
    """
    if not is_live():
        time.sleep = lambda *_: None


def skip_sleep_in_lro_polling():
    """A less aggressive version of skip_sleep_for_playback. Mock time.sleep() only for sync LRO polling.
    You may use this fixture and utils.sleep_if_live() together when you disabled skip_sleep_for_playback.
    """
    if not is_live():
        HttpTransport.sleep = lambda *_, **__: None


def pytest_configure(config):
    # register customized pytest markers
    for marker, description in [
        ("e2etest", "marks tests as end to end tests, which involve requests to the server"),
        ("unittest", "marks tests as unit tests, which do not involve requests to the server"),
        ("pipeline_test", "marks tests as pipeline tests, which will create pipeline jobs during testing"),
        ("automl_test", "marks tests as automl tests, which will create automl jobs during testing"),
        ("core_sdk_test", "marks tests as core sdk tests"),
        ("production_experiences_test", "marks tests as production experience tests"),
        ("training_experiences_test", "marks tests as training experience tests"),
        ("data_experiences_test", "marks tests as data experience tests"),
        ("data_import_test", "marks tests as data import tests"),
        ("local_endpoint_local_assets", "marks tests as local_endpoint_local_assets"),
        ("local_endpoint_byoc", "marks tests as local_endpoint_byoc"),
        ("virtual_cluster_test", "marks tests as virtual cluster tests"),
    ]:
        config.addinivalue_line("markers", f"{marker}: {description}")

    config.addinivalue_line("markers", f"{marker}: {description}")


@pytest.fixture()
def enable_private_preview_pipeline_node_types():
    with reload_schema_for_nodes_in_pipeline_job():
        yield


@pytest.fixture()
def disable_internal_components():
    """Some global changes are made in enable_internal_components, so we need to explicitly disable it.
    It's not recommended to use this fixture along with other related fixtures like enable_internal_components
    and enable_private_preview_features, as the execution order of fixtures is not guaranteed.
    """
    from azure.ai.ml._internal._schema.component import NodeType
    from azure.ai.ml._internal._setup import _set_registered
    from azure.ai.ml.entities._component.component_factory import component_factory
    from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

    for _type in NodeType.all_values():
        pipeline_node_factory._create_instance_funcs.pop(_type, None)  # pylint: disable=protected-access
        pipeline_node_factory._load_from_rest_object_funcs.pop(_type, None)  # pylint: disable=protected-access
        component_factory._create_instance_funcs.pop(_type, None)  # pylint: disable=protected-access
        component_factory._create_schema_funcs.pop(_type, None)  # pylint: disable=protected-access

    _set_registered(False)

    with reload_schema_for_nodes_in_pipeline_job(revert_after_yield=False):
        yield


@pytest.fixture()
def federated_learning_components_folder() -> Path:
    return Path("./tests/test_configs/components/fl_test_components")


@pytest.fixture()
def federated_learning_local_data_folder() -> Path:
    return Path("./tests/test_configs/fl-e2e-test-data")


@pytest.fixture()
def mock_set_headers_with_user_aml_token(mocker: MockFixture):
    if not is_live() or not is_live_and_not_recording():
        mocker.patch("azure.ai.ml.operations._job_operations.JobOperations._set_headers_with_user_aml_token")


@pytest.fixture
def mock_singularity_arm_id(environment_variables, e2e_ws_scope: OperationScope) -> str:
    # Singularity ARM id contains information like subscription id and resource group,
    # we prefer not exposing these to public, so make this a fixture.

    # During local development, set ML_SINGULARITY_ARM_ID in environment variables to configure Singularity.
    singularity_compute_id_in_environ = environment_variables.get("ML_SINGULARITY_ARM_ID")
    if singularity_compute_id_in_environ is not None:
        return singularity_compute_id_in_environ
    # If not set, concatenate fake Singularity ARM id from subscription id and resource group name;
    # note that this does not affect job submission, but the created pipeline job shall not complete.
    return SINGULARITY_ID_FORMAT.format(
        e2e_ws_scope.subscription_id, e2e_ws_scope.resource_group_name, "SingularityTestVC"
    )


SingularityVirtualCluster = namedtuple("SingularityVirtualCluster", ["subscription_id", "resource_group_name", "name"])


@pytest.fixture
def singularity_vc(client: MLClient) -> SingularityVirtualCluster:
    """Returns a valid Singularity VC, NOT use this fixture for recording for potential information leak."""
    # according to virtual cluster end-to-end test, client here should have available Singularity computes.
    for vc in client._virtual_clusters.list():
        return SingularityVirtualCluster(
            subscription_id=vc["subscriptionId"], resource_group_name=vc["resourceGroup"], name=vc["name"]
        )


@pytest.fixture
def use_python_amlignore_during_upload(mocker: MockFixture) -> None:
    """Makes _upload_to_datastore default to using an ignore file that ignores
    non-essential python files (e.g. .pyc)
    """
    IGNORE_FILE_DIR = Path(__file__).parent / "test_configs" / "_ignorefiles"
    py_ignore = IGNORE_FILE_DIR / "Python.amlignore"
    # Meant to influence azure.ai.ml._artifacts._artifact_utilities._upload_to_datastore when an ignore file isn't provided
    mocker.patch("azure.ai.ml._artifacts._artifact_utilities.get_ignore_file", return_value=IgnoreFile(py_ignore))
