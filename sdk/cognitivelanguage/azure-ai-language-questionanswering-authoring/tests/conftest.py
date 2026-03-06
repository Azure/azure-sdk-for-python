import sys
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

package_root = Path(__file__).resolve().parent.parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

import pytest
from devtools_testutils.sanitizers import (
    add_header_regex_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

ENV_ENDPOINT = "AZURE_QUESTIONANSWERING_ENDPOINT"
ENV_KEY = "AZURE_QUESTIONANSWERING_KEY"
ENV_PROJECT = "AZURE_QUESTIONANSWERING_PROJECT"
ENV_TEST_RUN_LIVE = "AZURE_TEST_RUN_LIVE"

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
    # Normalize dynamic live project names in recordings to a stable playback value.
    add_general_regex_sanitizer(
        regex=r"test-project-\d{14}-[0-9a-f]{8}",
        value=TEST_PROJECT,
    )
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def qna_authoring_creds_base(environment_variables):  # type: ignore[name-defined]
    is_live = (os.environ.get(ENV_TEST_RUN_LIVE) or "").strip().lower() == "true"
    if is_live:
        endpoint = os.environ.get(ENV_ENDPOINT)
        key = os.environ.get(ENV_KEY)
        base_project = os.environ.get(ENV_PROJECT)
        if not endpoint or not key:
            pytest.skip("Missing AZURE_QUESTIONANSWERING_ENDPOINT/KEY environment variables")
    else:
        endpoint = environment_variables.get(ENV_ENDPOINT)
        key = environment_variables.get(ENV_KEY)
        base_project = environment_variables.get(ENV_PROJECT)

    yield {
        "endpoint": endpoint,
        "key": key,
        "project": base_project,
    }


@pytest.fixture(scope="session")
def authoring_project_name(qna_authoring_creds_base):
    """Return a unique project name for this test session.

    We derive from AZURE_QUESTIONANSWERING_PROJECT if present, but always append a unique suffix
    to avoid cross-run interference. Cleanup is best-effort.
    """
    is_live = (os.environ.get(ENV_TEST_RUN_LIVE) or "").strip().lower() == "true"
    if not is_live:
        yield qna_authoring_creds_base["project"]
        return

    base = os.environ.get(ENV_PROJECT) or "qa"
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
    project_name = f"{base}-{suffix}"
    yield project_name

    endpoint = qna_authoring_creds_base["endpoint"]
    key = qna_authoring_creds_base["key"]
    if not endpoint or not key:
        return
    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    try:
        delete_poller = client.begin_delete_project(project_name=project_name)
        delete_poller.result()
    except (ResourceNotFoundError, HttpResponseError):
        pass


@pytest.fixture(scope="session")
def qna_authoring_creds(qna_authoring_creds_base, authoring_project_name):
    qna_authoring_creds_base["project"] = authoring_project_name
    yield qna_authoring_creds_base
