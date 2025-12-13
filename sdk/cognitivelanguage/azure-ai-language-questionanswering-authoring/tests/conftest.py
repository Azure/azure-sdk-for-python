import pytest
from devtools_testutils.sanitizers import (
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
)

ENV_ENDPOINT = "AZURE_QUESTIONANSWERING_ENDPOINT"
ENV_KEY = "AZURE_QUESTIONANSWERING_KEY"
ENV_PROJECT = "AZURE_QUESTIONANSWERING_PROJECT"

TEST_ENDPOINT = "https://test-resource.cognitiveservices.azure.com/"
TEST_KEY = "0000000000000000"
TEST_PROJECT = "test-project"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):  # type: ignore[name-defined]
    environment_variables.sanitize_batch(
        {
            ENV_ENDPOINT: TEST_ENDPOINT,
            ENV_KEY: TEST_KEY,
            ENV_PROJECT: TEST_PROJECT,
        }
    )
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def qna_authoring_creds(environment_variables):  # type: ignore[name-defined]
    yield {
        "endpoint": environment_variables.get(ENV_ENDPOINT),
        "key": environment_variables.get(ENV_KEY),
        "project": environment_variables.get(ENV_PROJECT),
    }
