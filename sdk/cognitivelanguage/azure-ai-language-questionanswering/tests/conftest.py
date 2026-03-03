# coding=utf-8
# -------------------------------------------------------------------------
# Inference test configuration for Question Answering (authoring removed)
# -------------------------------------------------------------------------
import os
import uuid
from datetime import datetime, timezone

import pytest

from devtools_testutils.sanitizers import (
    add_header_regex_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering.authoring import models as _models

# Environment variable keys
ENV_ENDPOINT = "AZURE_QUESTIONANSWERING_ENDPOINT"
ENV_KEY = "AZURE_QUESTIONANSWERING_KEY"
ENV_PROJECT = "AZURE_QUESTIONANSWERING_PROJECT"
ENV_TEST_RUN_LIVE = "AZURE_TEST_RUN_LIVE"

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
    # Normalize dynamic live project names in recordings to a stable playback value.
    add_general_regex_sanitizer(
        regex=r"test-project-\d{14}-[0-9a-f]{8}",
        value=TEST_PROJECT,
    )
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")

    # Keep id fields (previously removed by AZSDK3430) since assertions validate them.
    remove_batch_sanitizers(["AZSDK3430"])  # ensure it's not applied


@pytest.fixture(scope="session")
def qna_creds_base(environment_variables):
    is_live = (os.environ.get(ENV_TEST_RUN_LIVE) or "").strip().lower() == "true"
    if is_live:
        yield {
            "qna_endpoint": os.environ.get(ENV_ENDPOINT),
            "qna_key": os.environ.get(ENV_KEY),
            "qna_project": os.environ.get(ENV_PROJECT),
        }
        return
    yield {
        "qna_endpoint": environment_variables.get(ENV_ENDPOINT),
        "qna_key": environment_variables.get(ENV_KEY),
        "qna_project": environment_variables.get(ENV_PROJECT),
    }


@pytest.fixture(scope="session")
def qna_seeded_project(environment_variables):
    """Create a unique test project, seed deterministic QnAs, deploy, then delete.

    This keeps inference tests stable and avoids cross-run project pollution.
    """
    is_live = (os.environ.get(ENV_TEST_RUN_LIVE) or "").strip().lower() == "true"
    if not is_live:
        # Playback path: use stable recorded values instead of live seeding.
        yield {
            "project_name": environment_variables.get(ENV_PROJECT) or TEST_PROJECT,
            "deployment_name": "production",
            "previous_question": "Meet Surface Pro 4",
            "previous_qna_id": 1,
            "qna_id_only": 2,
        }
        return

    endpoint = os.environ.get(ENV_ENDPOINT)
    key = os.environ.get(ENV_KEY)
    base_project = os.environ.get(ENV_PROJECT) or "qa"
    if not endpoint or not key:
        pytest.skip("Missing AZURE_QUESTIONANSWERING_ENDPOINT/KEY environment variables")

    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
    project_name = f"{base_project}-{suffix}"

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    try:
        client.create_project(
            project_name=project_name,
            options={
                "description": "Inference test project",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )

        update_qna_ops = [
            _models.UpdateQnaRecord(
                {
                    "op": "add",
                    "value": {
                        "id": 0,
                        "answer": "Meet Surface Pro 4 is a demo entry.",
                        "questions": ["Meet Surface Pro 4"],
                        "metadata": {"seed": "true"},
                    },
                }
            ),
            _models.UpdateQnaRecord(
                {
                    "op": "add",
                    "value": {
                        "id": 0,
                        "answer": "Ports and connectors are covered in the documentation.",
                        "questions": ["Ports and connectors"],
                        "metadata": {"seed": "true"},
                    },
                }
            ),
            _models.UpdateQnaRecord(
                {
                    "op": "add",
                    "value": {
                        "id": 0,
                        "answer": "Check the battery level in Settings.",
                        "questions": ["How do I check the battery level?"],
                        "metadata": {"explicitlytaggedheading": "check the battery level"},
                    },
                }
            ),
            _models.UpdateQnaRecord(
                {
                    "op": "add",
                    "value": {
                        "id": 0,
                        "answer": "To make your battery last, reduce screen brightness.",
                        "questions": ["Battery life"],
                        "metadata": {"explicitlytaggedheading": "make your battery last"},
                    },
                }
            ),
        ]
        poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=update_qna_ops,
            content_type="application/json",
        )
        poller.result()

        qnas = list(client.list_qnas(project_name=project_name))

        def _id_for_question(question: str) -> int:
            for qna in qnas:
                if question in (qna.get("questions") or []):
                    return int(qna["id"])
            raise AssertionError(f"Seeded QnA not found for question: {question}")

        seed = {
            "project_name": project_name,
            "deployment_name": "production",
            "previous_question": "Meet Surface Pro 4",
            "previous_qna_id": _id_for_question("Meet Surface Pro 4"),
            "qna_id_only": _id_for_question("Ports and connectors"),
        }

        # Service currently supports only the well-known 'production' deployment name.
        deploy_poller = client.begin_deploy_project(
            project_name=project_name,
            deployment_name=seed["deployment_name"],
        )
        deploy_poller.result()

        yield seed
    finally:
        try:
            delete_poller = client.begin_delete_project(project_name=project_name)
            delete_poller.result()
        except (ResourceNotFoundError, HttpResponseError):
            pass


@pytest.fixture(scope="session")
def qna_creds(qna_creds_base):
    # Endpoint/key are enough for get_answers_from_text tests.
    # Knowledgebase tests explicitly depend on qna_seeded_project for project name.
    yield qna_creds_base
