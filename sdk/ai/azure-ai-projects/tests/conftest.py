# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from devtools_testutils import remove_batch_sanitizers, get_credential, test_proxy, add_general_regex_sanitizer, add_body_key_sanitizer
from dotenv import load_dotenv, find_dotenv
from azure.ai.projects import AIProjectClient

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests.")


class SanitizedValues:
    SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    RESOURCE_GROUP_NAME = "00000"
    WORKSPACE_NAME = "00000"
    CONNECTION_NAME = "00000"
    DATASET_NAME = "00000"
    TENANT_ID = "00000000-0000-0000-0000-000000000000"
    USER_OBJECT_ID = "00000000-0000-0000-0000-000000000000"
    API_KEY = "00000000000000000000000000000000000000000000000000000000000000000000"


@pytest.fixture(scope="session")
def mock_project_scope():
    return {
        "subscription_id": f"{SanitizedValues.SUBSCRIPTION_ID}",
        "resource_group_name": f"{SanitizedValues.RESOURCE_GROUP_NAME}",
        "project_name": f"{SanitizedValues.WORKSPACE_NAME}",
    }


@pytest.fixture(scope="session")
def mock_dataset_name():
    return {
        "dataset_name": f"{SanitizedValues.DATASET_NAME}",
    }


@pytest.fixture(scope="session")
def mock_connection_name():
    return {
        "connection_name": f"{SanitizedValues.CONNECTION_NAME}",
    }


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, mock_project_scope, mock_dataset_name, mock_connection_name):
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name

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
            regex=r"/connections/([-\w\._\(\)]+)", value=mock_connection_name["connection_name"], group_for_replace="1"
        )

        add_general_regex_sanitizer(
            regex=r"/data/([-\w\._\(\)]+)", value=mock_dataset_name["dataset_name"], group_for_replace="1"
        )

        add_general_regex_sanitizer(regex=r"/runs/([-\w\._\(\)]+)", value="Sanitized", group_for_replace="1")

        add_body_key_sanitizer(json_path="$..key", value="Sanitized")

    azure_workspace_triad_sanitizer()

    remove_batch_sanitizers(["AZSDK3493"])
