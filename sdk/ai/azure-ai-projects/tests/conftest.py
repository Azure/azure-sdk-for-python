# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from devtools_testutils import (
    remove_batch_sanitizers,
    get_credential,
    test_proxy,
    add_general_regex_sanitizer,
    add_body_key_sanitizer,
)
from dotenv import load_dotenv, find_dotenv
from azure.ai.projects import AIProjectClient

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests.")


def pytest_collection_modifyitems(items):
    if os.environ.get("AZURE_TEST_RUN_LIVE") == "true":
        return
    for item in items:
        if "tests\\evaluation" in item.fspath.strpath or "tests/evaluation" in item.fspath.strpath:
            item.add_marker(
                pytest.mark.skip(
                    reason="Skip running Evaluations tests in PR pipeline until we can sort out the failures related to AI Foundry project settings"
                )
            )


class SanitizedValues:
    SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    RESOURCE_GROUP_NAME = "00000"
    WORKSPACE_NAME = "00000"
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


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, mock_project_scope, mock_dataset_name):

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

        # TODO (Darren): Check why this is needed in addition to the above
        add_general_regex_sanitizer(
            regex=r"%2Fsubscriptions%2F([-\w\._\(\)]+)",
            value=mock_project_scope["subscription_id"],
            group_for_replace="1",
        )

        # TODO (Darren): Check why this is needed in addition to the above
        add_general_regex_sanitizer(
            regex=r"%2Fresource[gG]roups%2F([-\w\._\(\)]+)",
            value=mock_project_scope["resource_group_name"],
            group_for_replace="1",
        )

    azure_workspace_triad_sanitizer()

    add_general_regex_sanitizer(regex=r"/runs/([-\w\._\(\)]+)", value="Sanitized", group_for_replace="1")

    add_general_regex_sanitizer(
        regex=r"/data/([-\w\._\(\)]+)", value=mock_dataset_name["dataset_name"], group_for_replace="1"
    )

    # Sanitize Application Insights connection string from service response (/tests/telemetry)
    add_body_key_sanitizer(
        json_path="properties.ConnectionString",
        value="InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://region.applicationinsights.azure.com/;LiveEndpoint=https://region.livediagnostics.monitor.azure.com/;ApplicationId=00000000-0000-0000-0000-000000000000",
    )

    # Sanitize API key from service response (/tests/connections)
    add_body_key_sanitizer(json_path="properties.credentials.key", value="Sanitized")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3493"])
    remove_batch_sanitizers(["AZSDK3430"])
