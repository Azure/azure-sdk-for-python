from .__openai_patcher import TestProxyConfig, TestProxyHttpxClientBase  # isort: split

import re
import os
import json
import multiprocessing
import time
from datetime import datetime, timedelta
import jwt
from copy import deepcopy
from logging import Logger
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Final, Generator, Mapping, Literal, Optional
from unittest.mock import patch

import pytest
from ci_tools.variables import in_ci
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    is_live,
    remove_batch_sanitizers,
    add_remove_header_sanitizer,
)
from devtools_testutils.config import PROXY_URL
from devtools_testutils.fake_credentials import FakeTokenCredential
from devtools_testutils.helpers import get_recording_id
from devtools_testutils.proxy_testcase import transform_request
from filelock import FileLock
from promptflow.client import PFClient
from promptflow.executor._line_execution_process_pool import _process_wrapper
from promptflow.executor._process_manager import create_spawned_fork_process_manager
from pytest_mock import MockerFixture

from azure.ai.evaluation import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._common.utils import ensure_nltk_data_downloaded
from azure.ai.evaluation._azure._clients import LiteMLClient
from azure.core.credentials import TokenCredential

PROMPTFLOW_ROOT = Path(__file__, "..", "..", "..").resolve()
CONNECTION_FILE = (PROMPTFLOW_ROOT / "azure-ai-evaluation" / "connections.json").resolve()
RECORDINGS_TEST_CONFIGS_ROOT = Path(PROMPTFLOW_ROOT / "azure-ai-evaluation/tests/test_configs").resolve()
ZERO_GUID: Final[str] = "00000000-0000-0000-0000-000000000000"


def pytest_configure(config: pytest.Config) -> None:
    # register Azure test markers to reduce spurious warnings on test runs
    config.addinivalue_line("markers", "azuretest: mark test as an Azure test.")
    config.addinivalue_line("markers", "localtest: mark test as a local test.")
    config.addinivalue_line("markers", "unittest: mark test as a unit test.")
    config.addinivalue_line("markers", "performance_test: mark test as a performance test.")

    # suppress deprecation warnings for now
    config.addinivalue_line("filterwarnings", "ignore::DeprecationWarning")


class SanitizedValues:
    SUBSCRIPTION_ID = ZERO_GUID
    RESOURCE_GROUP_NAME = "00000"
    WORKSPACE_NAME = "00000"
    TENANT_ID = ZERO_GUID
    USER_OBJECT_ID = ZERO_GUID
    IMAGE_NAME = "00000000.png"


@pytest.fixture(scope="session", autouse=True)
def ensure_nltk_data() -> None:
    """Ensures that nltk data has been downloaded."""

    def try_download_nltk():
        for _ in range(3):
            ensure_nltk_data_downloaded()

    if in_ci():
        with FileLock(Path.home() / "azure_ai_evaluation_nltk_data.txt"):
            try_download_nltk()
    else:
        try_download_nltk()


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(
    test_proxy,
    mock_model_config: AzureOpenAIModelConfiguration,
    mock_project_scope: Dict[str, str],
    connection_file: Dict[str, Any],
) -> None:
    def azureopenai_connection_sanitizer():
        """Sanitize the openai deployment name."""
        mock_deployment = mock_model_config["azure_deployment"]

        add_general_regex_sanitizer(
            regex=r"/openai/deployments/([^\/&#\"]+)", value=mock_deployment, group_for_replace="1"
        )
        add_body_key_sanitizer(json_path="$.model", value=mock_deployment)

    def azure_workspace_triad_sanitizer():
        """Sanitize subscription, resource group, and workspace."""
        add_general_regex_sanitizer(
            regex=r"/subscriptions/([-\w\._\(\)]+)",
            value=mock_project_scope["subscription_id"],
            group_for_replace="1",
        )
        add_general_regex_sanitizer(
            regex=r"/resource[gG]roups/([-\w\._\(\)]+)",
            value=mock_project_scope["resource_group_name"],
            group_for_replace="1",
        )
        add_general_regex_sanitizer(
            regex=r"/workspaces/([-\w\._\(\)]+)", value=mock_project_scope["project_name"], group_for_replace="1"
        )
        add_general_regex_sanitizer(
            regex=r"image_understanding/([-\w\._\(\)/]+)", value=mock_project_scope["image_name"], group_for_replace="1"
        )

    def openai_stainless_default_headers():
        """Sanitize the default headers added by the stainless SDK generator to every request.

        The headers are meant as telemetry, so their values shouldn't matter

          .. note::

              The openai SDK is generated with Stainless

          .. see-also::

              https://app.stainlessapi.com/docs/guides/configure#default-headers
        """

        replacements = [
            ("Package-Version", "vX.X.X"),
            ("OS", "Other:XXX"),
            ("Arch", "x64"),
            ("Runtime", "CPython"),
            ("Runtime-Version", "3.X.X"),
            ("Async", "async:asyncio"),
        ]

        for header_suffix, value in replacements:
            add_header_regex_sanitizer(key=f"X-Stainless-{header_suffix}", regex="^.*$", value=value)

    def azure_ai_generative_sanitizer():
        """Sanitize header values from azure-ai-generative"""
        add_header_regex_sanitizer(key="X-CV", regex="^.*$", value=ZERO_GUID)
        add_body_key_sanitizer(json_path="$.headers.X-CV", value=ZERO_GUID)

    def live_connection_file_values():
        """Sanitize the live values from connections.json"""

        if not connection_file:
            return

        project_scope = connection_file[KEY_AZURE_PROJECT_SCOPE]["value"]
        model_config = connection_file[KEY_AZURE_MODEL_CONFIG]["value"]

        add_general_regex_sanitizer(regex=project_scope["subscription_id"], value=SanitizedValues.SUBSCRIPTION_ID)
        add_general_regex_sanitizer(
            regex=project_scope["resource_group_name"], value=SanitizedValues.RESOURCE_GROUP_NAME
        )
        add_general_regex_sanitizer(regex=project_scope["project_name"], value=SanitizedValues.WORKSPACE_NAME)
        add_general_regex_sanitizer(regex=model_config["azure_endpoint"], value=mock_model_config["azure_endpoint"])

    def promptflow_root_run_id_sanitizer():
        """Sanitize the promptflow service isolation values."""
        add_general_regex_sanitizer(
            value="root_run_id",
            regex=r'"root_run_id": "azure_ai_evaluation_evaluators_common_base_eval_asyncevaluatorbase_[^"]+"',
            replacement='"root_run_id": "azure_ai_evaluation_evaluators_common_base_eval_asyncevaluatorbase_SANITIZED"',
        )

    def evaluatation_run_sanitizer() -> None:
        # By default, the test proxy will sanitize all "key" values in a JSON body to "Sanitized". Unfortunately,
        # when retrieving the datastore secrets, the key that comes back needs to be a valid Base64 encoded string.
        # So we disable this default rule, and add a replacement rule to santize to MA== (which is "0")
        remove_batch_sanitizers(["AZSDK3447"])
        add_body_key_sanitizer(json_path="$.key", value="MA==")

        # Sanitize the start_time, timestamp, and end_time to a fixed value in recordings
        convert = lambda dt: str(int(dt.timestamp() * 1000))
        start = datetime(2024, 11, 1, 0, 0, 0)
        mid = start + timedelta(seconds=10)
        end = start + timedelta(minutes=1)
        add_body_key_sanitizer(json_path="$..start_time", value=convert(start))
        add_body_key_sanitizer(json_path="$..timestamp", value=convert(mid))
        add_body_key_sanitizer(json_path="$..end_time", value=convert(end))

        # Since we use a santizied configuration when in playback mode, force the dataPath.dataStoreName in the
        # register request in the eval run
        add_body_key_sanitizer(json_path="$.dataPath.dataStoreName", value="Sanitized")

        # In the eval run history, sanitize additional values such as the upn (which contains the user's email)
        add_body_key_sanitizer(json_path="$..userObjectId", value=ZERO_GUID)
        add_body_key_sanitizer(json_path="$..userPuId", value="0000000000000000")
        add_body_key_sanitizer(json_path="$..userIss", value="https://sts.windows.net/" + ZERO_GUID)
        add_body_key_sanitizer(json_path="$..userTenantId", value=ZERO_GUID)
        add_body_key_sanitizer(json_path="$..upn", value="Sanitized")

        # removes some headers since they are causing some unnecessary mismatches in recordings
        headers_to_ignore = [
            "ms-azure-ai-promptflow",
            "ms-azure-ai-promptflow-called-from",
            "x-ms-useragent",
            "x-stainless-retry-count",
            "x-stainless-read-timeout",
        ]
        add_remove_header_sanitizer(headers=",".join(headers_to_ignore))

    azure_workspace_triad_sanitizer()
    azureopenai_connection_sanitizer()
    openai_stainless_default_headers()
    azure_ai_generative_sanitizer()
    live_connection_file_values()
    promptflow_root_run_id_sanitizer()
    evaluatation_run_sanitizer()


@pytest.fixture
def redirect_asyncio_requests_traffic() -> Generator[None, Any, None]:
    """Redirects requests sent through AsyncioRequestsTransport to the test proxy.

    .. note::

    This implementation is taken verbatim from devtools_testutils/proxy_fixtures.py

    It's necessary for two reasons:
        * The only async transport that gets patched is AioHttpTransport
        * The test infra selectively patches the Sync/Async implementations based on whether the test is sync/async
    """
    import urllib.parse as url_parse

    from azure.core.pipeline.transport import AsyncioRequestsTransport

    original_transport_func = AsyncioRequestsTransport.send
    recording_id = get_recording_id()

    def transform_args(*args, **kwargs):
        copied_positional_args = list(args)
        request = copied_positional_args[1]

        transform_request(request, recording_id)

        return tuple(copied_positional_args), kwargs

    async def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
        result = await original_transport_func(*adjusted_args, **adjusted_kwargs)

        # make the x-recording-upstream-base-uri the URL of the request
        # this makes the request look like it was made to the original endpoint instead of to the proxy
        # without this, things like LROPollers can get broken by polling the wrong endpoint
        parsed_result = url_parse.urlparse(result.request.url)
        upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
        upstream_uri_dict = {"scheme": upstream_uri.scheme, "netloc": upstream_uri.netloc}
        original_target = parsed_result._replace(**upstream_uri_dict).geturl()

        result.request.url = original_target
        return result

    AsyncioRequestsTransport.send = combined_call

    yield

    AsyncioRequestsTransport.send = original_transport_func


@pytest.fixture
def simple_conversation():
    return {
        "messages": [
            {
                "content": "What is the capital of France?`''\"</>{}{{]",
                "role": "user",
                "context": "Customer wants to know the capital of France",
            },
            {"content": "Paris", "role": "assistant", "context": "Paris is the capital of France"},
            {
                "content": "What is the capital of Hawaii?",
                "role": "user",
                "context": "Customer wants to know the capital of Hawaii",
            },
            {"content": "Honolulu", "role": "assistant", "context": "Honolulu is the capital of Hawaii"},
        ],
        "context": "Global context",
    }


@pytest.fixture
def redirect_openai_requests():
    """Route requests from the openai package to the test proxy."""
    config = TestProxyConfig(
        recording_id=get_recording_id(), recording_mode="record" if is_live() else "playback", proxy_url=PROXY_URL
    )

    with TestProxyHttpxClientBase.record_with_proxy(config):
        yield


@pytest.fixture
def recorded_test(recorded_test, redirect_openai_requests, redirect_asyncio_requests_traffic):
    return recorded_test


@pytest.fixture(scope="session")
def connection_file() -> Dict[str, Any]:
    if not CONNECTION_FILE.exists():
        return {}

    with open(CONNECTION_FILE) as f:
        return json.load(f)


def get_config(
    connection_file: Mapping[str, Any], key: str, defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if is_live():
        assert key in connection_file, f"Connection '{key}' not found in dev connections."

    config = deepcopy(connection_file.get(key, {}).get("value", {}))

    for k, v in (defaults or {}).items():
        config.setdefault(k, v)

    return config


@pytest.fixture(scope="session")
def mock_model_config() -> AzureOpenAIModelConfiguration:
    return AzureOpenAIModelConfiguration(
        azure_endpoint="https://Sanitized.cognitiveservices.azure.com",
        api_key="aoai-api-key",
        api_version="2024-08-01-preview",
        azure_deployment="aoai-deployment",
    )


@pytest.fixture(scope="session")
def mock_project_scope() -> Dict[str, str]:
    return {
        "subscription_id": f"{SanitizedValues.SUBSCRIPTION_ID}",
        "resource_group_name": f"{SanitizedValues.RESOURCE_GROUP_NAME}",
        "project_name": f"{SanitizedValues.WORKSPACE_NAME}",
        "image_name": f"{SanitizedValues.IMAGE_NAME}",
    }


KEY_AZURE_MODEL_CONFIG = "azure_openai_model_config"
KEY_OPENAI_MODEL_CONFIG = "openai_model_config"
KEY_AZURE_PROJECT_SCOPE = "azure_ai_project_scope"


@pytest.fixture(scope="session")
def model_config(
    connection_file: Dict[str, Any], mock_model_config: AzureOpenAIModelConfiguration
) -> AzureOpenAIModelConfiguration:
    if not is_live():
        return mock_model_config

    config = get_config(connection_file, KEY_AZURE_MODEL_CONFIG)
    model_config = AzureOpenAIModelConfiguration(**config)
    AzureOpenAIModelConfiguration.__repr__ = lambda self: "<sensitive data redacted>"

    return model_config


@pytest.fixture
def non_azure_openai_model_config(connection_file: Mapping[str, Any]) -> OpenAIModelConfiguration:
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
    config = get_config(
        connection_file,
        KEY_OPENAI_MODEL_CONFIG,
        {
            "api_key": "openai-api-key",
            "model": "gpt-35-turbo",
            "base_url": "https://api.openai.com/v1",
        },
    )
    model_config = OpenAIModelConfiguration(**config)
    OpenAIModelConfiguration.__repr__ = lambda self: "<sensitive data redacted>"

    return model_config


@pytest.fixture
def project_scope(connection_file: Mapping[str, Any], mock_project_scope: Dict[str, Any]) -> Dict[str, Any]:
    config = get_config(connection_file, KEY_AZURE_PROJECT_SCOPE) if is_live() else mock_project_scope
    return config


@pytest.fixture
def datastore_project_scopes(connection_file, project_scope, mock_project_scope) -> Dict[str, Any]:
    keys = {"none": "azure_ai_entra_id_project_scope", "private": "azure_ai_private_connection_project_scope"}

    scopes: Dict[str, Any] = {
        "sas": project_scope,
    }

    if not is_live():
        for key in keys.keys():
            scopes[key] = mock_project_scope
    else:
        for key, value in keys.items():
            if value not in connection_file:
                raise ValueError(f"Connection '{value}' not found in dev connections.")
            scopes[key] = connection_file[value]["value"]

    return scopes


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
def azure_ml_client(project_scope: dict, azure_cred: TokenCredential) -> LiteMLClient:
    """The fixture, returning LiteMLClient."""
    return LiteMLClient(
        subscription_id=project_scope["subscription_id"],
        resource_group=project_scope["resource_group_name"],
        logger=Logger("azure_ml_client"),
        credential=azure_cred,
    )


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
    multiprocessing.get_context("spawn").Process = MockSpawnProcess  # type: ignore
    if "spawn" == multiprocessing.get_start_method():
        multiprocessing.Process = MockSpawnProcess

    try:
        yield
    finally:
        multiprocessing.get_context("spawn").Process = original_process_class  # type: ignore
        if "spawn" == multiprocessing.get_start_method():
            multiprocessing.Process = original_process_class


def _mock_process_wrapper(*args, **kwargs):
    return _process_wrapper(*args, **kwargs)


def _mock_create_spawned_fork_process_manager(*args, **kwargs):
    return create_spawned_fork_process_manager(*args, **kwargs)


@pytest.fixture
def azure_cred() -> TokenCredential:
    from azure.identity import AzureCliCredential, DefaultAzureCredential

    """get credential for azure tests"""
    # resolve requests
    if not is_live():
        return FakeTokenCredential()

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
def user_object_id(azure_cred: TokenCredential) -> str:
    if not is_live():
        return SanitizedValues.USER_OBJECT_ID
    access_token = azure_cred.get_token("https://management.azure.com/.default")
    decoded_token = jwt.decode(access_token.token, options={"verify_signature": False})
    return decoded_token["oid"]


@pytest.fixture
def tenant_id(azure_cred: TokenCredential) -> str:
    if not is_live():
        return SanitizedValues.TENANT_ID
    access_token = azure_cred.get_token("https://management.azure.com/.default")
    decoded_token = jwt.decode(access_token.token, options={"verify_signature": False})
    return decoded_token["tid"]


@pytest.fixture()
def mock_token():
    expiration_time = time.time() + 3600  # 1 hour in the future
    return jwt.encode({"exp": expiration_time}, "secret", algorithm="HS256")


@pytest.fixture()
def mock_expired_token():
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


def pytest_sessionfinish() -> None:
    def stop_promptflow_service() -> None:
        """Ensure that the promptflow service is stopped when pytest exits.

        .. note::

            The azure-sdk-for-python CI performs a cleanup step that deletes
            the python environment that the tests run in.

            At time of writing, at least one test starts the promptflow service
            (served from `waitress-serve`). The promptflow service is a separate
            process that gets orphaned by pytest.

            Crucially, that process has a handles on files in the python environment.
            On Windows, this causes the cleanup step to fail with a permission issue
            since the OS disallows deletion of files in use by a process.
        """
        from promptflow._cli._pf._service import stop_service

        stop_service()

    stop_promptflow_service()


@pytest.fixture
def run_from_temp_dir(tmp_path):
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(original_cwd)
