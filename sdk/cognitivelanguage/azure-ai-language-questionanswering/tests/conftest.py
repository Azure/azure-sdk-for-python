# coding=utf-8
# -------------------------------------------------------------------------
# Runtime test configuration for Question Answering (authoring removed)
# -------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import (
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)

# Environment variable keys
ENV_ENDPOINT = "AZURE_QUESTIONANSWERING_ENDPOINT"
ENV_KEY = "AZURE_QUESTIONANSWERING_KEY"
ENV_PROJECT = "AZURE_QUESTIONANSWERING_PROJECT"

# Fake values for playback
TEST_ENDPOINT = "https://test-resource.cognitiveservices.azure.com/"
TEST_KEY = "0000000000000000"
TEST_PROJECT = "test-project"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):  # pylint: disable=unused-argument
    """Configure sanitization for recordings.

    We intentionally keep project name visible for routing but sanitize endpoint & key.
    Removed subscription/tenant/client credentials since authoring/AAD management tests are not here.
    """
    sanitization_mapping = {
        ENV_ENDPOINT: TEST_ENDPOINT,
        ENV_KEY: TEST_KEY,
        ENV_PROJECT: TEST_PROJECT,
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")

    # Keep id fields (previously removed by AZSDK3430) since assertions validate them.
    remove_batch_sanitizers(["AZSDK3430"])  # ensure it's not applied


@pytest.fixture(scope="session")
def qna_creds(environment_variables):
    yield {
        "qna_endpoint": environment_variables.get(ENV_ENDPOINT),
        "qna_key": environment_variables.get(ENV_KEY),
        "qna_project": environment_variables.get(ENV_PROJECT),
    }
