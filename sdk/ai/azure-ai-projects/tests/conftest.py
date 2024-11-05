# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from devtools_testutils import remove_batch_sanitizers, get_credential
from dotenv import load_dotenv, find_dotenv
from azure.ai.projects import AIProjectClient

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests.")


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])

@pytest.fixture()
def project_client():
    project_client = AIProjectClient.from_connection_string(
        conn_str=os.environ["AZURE_AI_PROJECTS_CONNECTION_STRING"],
        credential=get_credential()
    )
    return project_client
