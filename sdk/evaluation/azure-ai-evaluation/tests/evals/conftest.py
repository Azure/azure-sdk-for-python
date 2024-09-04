import json
import multiprocessing
import time
from enum import Enum
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest
from devtools_testutils import is_live
from promptflow.client import PFClient
from promptflow.core import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from promptflow.executor._line_execution_process_pool import _process_wrapper
from promptflow.executor._process_manager import create_spawned_fork_process_manager
from pytest_mock import MockerFixture


# Import of optional packages
AZURE_INSTALLED = True
try:
    import jwt
    from azure.ai.ml._ml_client import MLClient
except ImportError:
    AZURE_INSTALLED = False

PROMPTFLOW_ROOT = Path(__file__) / "../../../.."
CONNECTION_FILE = (PROMPTFLOW_ROOT / "azure-ai-evaluation/connections.json").resolve().absolute().as_posix()
RECORDINGS_TEST_CONFIGS_ROOT = Path(PROMPTFLOW_ROOT / "azure-ai-evaluation/tests/test_configs").resolve()

class SanitizedValues(str, Enum):
    SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    RESOURCE_GROUP_NAME = "00000"
    WORKSPACE_NAME = "00000"
    TENANT_ID = "00000000-0000-0000-0000-000000000000"
    USER_OBJECT_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def mock_model_config() -> dict:
    return AzureOpenAIModelConfiguration(
        azure_endpoint="aoai-api-endpoint",
        api_key="aoai-api-key",
        api_version="2023-07-01-preview",
        azure_deployment="aoai-deployment",
    )


@pytest.fixture
def mock_project_scope() -> dict:
    return {
        "subscription_id": "subscription-id",
        "resource_group_name": "resource-group-name",
        "project_name": "project-name",
    }


@pytest.fixture
def model_config() -> dict:
    conn_name = "azure_openai_model_config"

    with open(
        file=CONNECTION_FILE,
        mode="r",
    ) as f:
        dev_connections = json.load(f)

    if conn_name not in dev_connections:
        raise ValueError(f"Connection '{conn_name}' not found in dev connections.")

    model_config = AzureOpenAIModelConfiguration(**dev_connections[conn_name]["value"])
    # Default to gpt-35-turbo for capacity reasons
    model_config.azure_deployment = "gpt-35-turbo"

    AzureOpenAIModelConfiguration.__repr__ = lambda self: "<sensitive data redacted>"

    return model_config


@pytest.fixture
def non_azure_openai_model_config() -> dict:
    """Requires the following in your local connections.json file. If not present, ask around the team.


        "openai_model_config": {
            "value": {
                "api_key": "<Actual API key>,
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-35-turbo"
            }
        }
    }
    """
    conn_name = "openai_model_config"

    with open(
        file=CONNECTION_FILE,
        mode="r",
    ) as f:
        dev_connections = json.load(f)

    if conn_name not in dev_connections:
        raise ValueError(f"Connection '{conn_name}' not found in dev connections.")

    model_config = OpenAIModelConfiguration(**dev_connections[conn_name]["value"])

    OpenAIModelConfiguration.__repr__ = lambda self: "<sensitive data redacted>"

    return model_config


@pytest.fixture
def project_scope(request) -> dict:
    if not is_live() and "recorded_test" in request.fixturenames:

        return {
            "subscription_id": SanitizedValues.SUBSCRIPTION_ID,
            "resource_group_name": SanitizedValues.RESOURCE_GROUP_NAME,
            "project_name": SanitizedValues.WORKSPACE_NAME,
        }

    conn_name = "azure_ai_project_scope"

    with open(
        file=CONNECTION_FILE,
        mode="r",
    ) as f:
        dev_connections = json.load(f)

    if conn_name not in dev_connections:
        raise ValueError(f"Connection '{conn_name}' not found in dev connections.")

    return dev_connections[conn_name]["value"]


@pytest.fixture
def mock_trace_destination_to_cloud(project_scope: dict):
    """Mock trace destination to cloud."""

    subscription_id = project_scope["subscription_id"]
    resource_group_name = project_scope["resource_group_name"]
    workspace_name = project_scope["project_name"]

    trace_destination = (
        f"azureml://subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
    )
    with patch("promptflow._sdk._configuration.Configuration.get_trace_destination", return_value=trace_destination):
        yield


@pytest.fixture
def mock_validate_trace_destination():
    """Mock validate trace destination config to use in unit tests."""

    with patch("promptflow._sdk._tracing.TraceDestinationConfig.validate", return_value=None):
        yield


@pytest.fixture
def azure_ml_client(project_scope: Dict):
    """The fixture, returning MLClient"""
    if AZURE_INSTALLED:
        return MLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group_name=project_scope["resource_group_name"],
            workspace_name=project_scope["project_name"],
            credential=get_cred(),
        )
    else:
        return None


@pytest.fixture
def pf_client() -> PFClient:
    """The fixture, returning PRClient"""
    return PFClient()


# ==================== Recording injection ====================
# To inject patches in subprocesses, add new mock method in setup_recording_injection_if_enabled
# in fork mode, this is automatically enabled.
# in spawn mode, we need to declare recording in each process separately.

SpawnProcess = multiprocessing.get_context("spawn").Process


class MockSpawnProcess(SpawnProcess):
    def __init__(self, group=None, target=None, *args, **kwargs):
        if target == _process_wrapper:
            target = _mock_process_wrapper
        if target == create_spawned_fork_process_manager:
            target = _mock_create_spawned_fork_process_manager
        super().__init__(group, target, *args, **kwargs)


@pytest.fixture
def recording_injection(mocker: MockerFixture):
    original_process_class = multiprocessing.get_context("spawn").Process
    multiprocessing.get_context("spawn").Process = MockSpawnProcess
    if "spawn" == multiprocessing.get_start_method():
        multiprocessing.Process = MockSpawnProcess


    try:
        yield
    finally:
        multiprocessing.get_context("spawn").Process = original_process_class
        if "spawn" == multiprocessing.get_start_method():
            multiprocessing.Process = original_process_class


def _mock_process_wrapper(*args, **kwargs):
    return _process_wrapper(*args, **kwargs)


def _mock_create_spawned_fork_process_manager(*args, **kwargs):
    return create_spawned_fork_process_manager(*args, **kwargs)


def package_scope_in_live_mode() -> str:
    """Determine the scope of some expected sharing fixtures.

    We have many tests against flows and runs, and it's very time consuming to create a new flow/run
    for each test. So we expect to leverage pytest fixture concept to share flows/runs across tests.
    However, we also have replay tests, which require function scope fixture as it will locate the
    recording YAML based on the test function info.

    Use this function to determine the scope of the fixtures dynamically. For those fixtures that
    will request dynamic scope fixture(s), they also need to be dynamic scope.
    """
    # package-scope should be enough for Azure tests
    return "package" if is_live() else "function"


def get_cred():
    from azure.identity import AzureCliCredential, DefaultAzureCredential

    """get credential for azure tests"""
    # resolve requests
    try:
        credential = AzureCliCredential()
        token = credential.get_token("https://management.azure.com/.default")
    except Exception:
        credential = DefaultAzureCredential()
        # ensure we can get token
        token = credential.get_token("https://management.azure.com/.default")

    assert token is not None
    return credential


@pytest.fixture
def azure_cred():
    return get_cred()


@pytest.fixture(scope=package_scope_in_live_mode())
def user_object_id() -> str:
    if not AZURE_INSTALLED:
        return ""
    if not is_live():

        return SanitizedValues.USER_OBJECT_ID
    credential = get_cred()
    access_token = credential.get_token("https://management.azure.com/.default")
    decoded_token = jwt.decode(access_token.token, options={"verify_signature": False})
    return decoded_token["oid"]


@pytest.fixture(scope=package_scope_in_live_mode())
def tenant_id() -> str:
    if not AZURE_INSTALLED:
        return ""
    if not is_live():

        return SanitizedValues.TENANT_ID
    credential = get_cred()
    access_token = credential.get_token("https://management.azure.com/.default")
    decoded_token = jwt.decode(access_token.token, options={"verify_signature": False})
    return decoded_token["tid"]


@pytest.fixture()
def mock_token(scope=package_scope_in_live_mode()):
    expiration_time = time.time() + 3600  # 1 hour in the future
    return jwt.encode({"exp": expiration_time}, "secret", algorithm="HS256")


@pytest.fixture()
def mock_expired_token(scope=package_scope_in_live_mode()):
    expiration_time = time.time() - 3600  # 1 hour in the past
    return jwt.encode({"exp": expiration_time}, "secret", algorithm="HS256")


def pytest_collection_modifyitems(items):
    parents = {}
    for item in items:
        # Check if parent contains 'localtest' marker and remove it.
        if any(mark.name == "localtest" for mark in item.parent.own_markers) or id(item.parent) in parents:
            if id(item.parent) not in parents:
                item.parent.own_markers = [
                    marker for marker in item.own_markers if getattr(marker, "name", None) != "localtest"
                ]
                parents[id(item.parent)] = item.parent
            if not item.get_closest_marker("azuretest"):
                # If item's parent was marked as 'localtest', mark the child as such, but not if
                # it was marked as 'azuretest'.
                item.add_marker(pytest.mark.localtest)
