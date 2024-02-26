import asyncio
import base64
import os
from typing import Dict

import pytest
from packaging import version
from typing import Callable
import random

from devtools_testutils import (
    FakeTokenCredential,
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_remove_header_sanitizer,
    is_live,
    set_custom_default_matcher,
)
from devtools_testutils.proxy_fixtures import (
    EnvironmentVariableSanitizer,
    VariableRecorder
)

from azure.ai.resources.client import AIClient
from azure.ai.ml import MLClient
from azure.core.credentials import TokenCredential
from azure.identity import AzureCliCredential, ClientSecretCredential

@pytest.fixture
def rand_num(variable_recorder: VariableRecorder) -> Callable[[str], str]:
    """return a random number string between 1 and 10000000"""

    def generate_random_string():
        random_string = f"{str(random.randint(1, 10000000))}"
        return variable_recorder.get_or_record("00000000", random_string)

    return generate_random_string



@pytest.fixture()
def ai_client(
    e2e_subscription_id: str,
    e2e_resource_group: str,
    e2e_project_name: str,
    e2e_ai_resource_name: str,
    credential: TokenCredential,
) -> AIClient:
    return AIClient(
        subscription_id=e2e_subscription_id,
        resource_group_name=e2e_resource_group,
        project_name=e2e_project_name,
        ai_resource_name=e2e_ai_resource_name,
        credential=credential,
    )


@pytest.fixture()
def ml_client(ai_client: AIClient) -> MLClient:
    return ai_client._ml_client


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


@pytest.fixture(scope="session")
def fake_datastore_key() -> str:
    fake_key = "this is fake key"
    b64_key = base64.b64encode(fake_key.encode("ascii"))
    return str(b64_key, "ascii")


@pytest.fixture(autouse=True)
def add_sanitizers(test_proxy, fake_datastore_key):
    """Register recording sanitizers for the function under test"""
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
    add_general_regex_sanitizer(value="", regex=f"\\u0026tid={os.environ.get('AI_TENANT_ID')}")
    add_general_string_sanitizer(value="", target=f"&tid={os.environ.get('AI_TENANT_ID')}")
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
    feature_store_name = os.environ.get("AI_FEATURE_STORE_NAME", "env_feature_store_name_note_present")
    add_general_regex_sanitizer(regex=feature_store_name, value="00000")
    # masks signature in SAS uri
    add_general_regex_sanitizer(value="000000000000000000000000000000000000", regex=_query_param_regex("sig"))


@pytest.fixture()
def sanitized_environment_variables(
    environment_variables: EnvironmentVariableSanitizer, fake_datastore_key: str
) -> Dict[str, str]:
    """Register sanitizers for environment variables, return sanitized environment variables"""
    return environment_variables.sanitize_batch(
        {
            "AI_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000",
            "AI_RESOURCE_GROUP": "00000",
            "AI_RESOURCE_NAME": "00000",
            "AI_PROJECT_NAME": "00000",
            "AI_FEATURE_STORE_NAME": "00000",
            "AI_TEST_STORAGE_ACCOUNT_NAME": "teststorageaccount",
            "AI_TEST_STORAGE_ACCOUNT_PRIMARY_KEY": fake_datastore_key,
            "AI_TEST_STORAGE_ACCOUNT_SECONDARY_KEY": fake_datastore_key,
            "OPENAI_API_BASE": "fake_openai_api_base",
            "OPENAI_API_KEY": "fake_openai_api_key",
            "AZURE_OPENAI_ENDPOINT": "fake_openai_api_base",
            "AZURE_OPENAI_KEY": "fake_openai_api_key",
            "AI_OPENAI_COMPLETION_DEPLOYMENT_NAME": "fake_completion_deployment_name",
            "AI_OPENAI_COMPLETION_MODEL_NAME": "fake_completion_model_name"
        }
    )


@pytest.fixture()
def e2e_subscription_id(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the subscription ID to use for end-to-end tests"""
    return sanitized_environment_variables["AI_SUBSCRIPTION_ID"]


@pytest.fixture()
def e2e_resource_group(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the resource group to use for end-to-end tests"""
    return sanitized_environment_variables["AI_RESOURCE_GROUP"]

@pytest.fixture()
def e2e_project_name(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the project name to use for end-to-end tests"""
    return sanitized_environment_variables["AI_PROJECT_NAME"]

@pytest.fixture()
def e2e_ai_resource_name(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the ai resource name to use for end-to-end tests"""
    return sanitized_environment_variables["AI_RESOURCE_NAME"]


@pytest.fixture()
def e2e_openai_api_base(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the OpenAI API Base to use for end-to-end tests"""
    import openai
    return sanitized_environment_variables["OPENAI_API_BASE"] if version.parse(openai.version.VERSION) >= version.parse("1.0.0") else sanitized_environment_variables["AZURE_OPENAI_ENDPOINT"]

@pytest.fixture()
def e2e_openai_api_key(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the OpenAI API Key to use for end-to-end tests"""
    import openai
    return sanitized_environment_variables["OPENAI_API_KEY"] if version.parse(openai.version.VERSION) >= version.parse("1.0.0") else sanitized_environment_variables["AZURE_OPENAI_KEY"]

@pytest.fixture()
def e2e_openai_completion_deployment_name(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the OpenAI API Key to use for end-to-end tests"""
    return sanitized_environment_variables["AI_OPENAI_COMPLETION_DEPLOYMENT_NAME"]

@pytest.fixture()
def e2e_openai_completion_model_name(sanitized_environment_variables: Dict[str, str]) -> str:
    """Return the OpenAI API Key to use for end-to-end tests"""
    return sanitized_environment_variables["AI_OPENAI_COMPLETION_MODEL_NAME"]

@pytest.fixture()
def credential() -> TokenCredential:
    if is_live():
        tenant_id = os.environ.get("AI_TENANT_ID")
        sp_id = os.environ.get("AI_CLIENT_ID")
        sp_secret = os.environ.get("AI_CLIENT_SECRET")
        if not (sp_id or sp_secret):
            return AzureCliCredential()
        return ClientSecretCredential(tenant_id, sp_id, sp_secret)

    return FakeTokenCredential()
