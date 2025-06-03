# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
from dotenv import load_dotenv, find_dotenv
from devtools_testutils import (remove_batch_sanitizers, add_general_regex_sanitizer, add_body_key_sanitizer)

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.filled.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests. This is expected if running in ADO pipeline.")


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
    RESOURCE_GROUP_NAME = "sanitized-resource-group-name"
    ACCOUNT_NAME = "sanitized-account-name"
    PROJECT_NAME = "sanitized-project-name"
    #DATASET_NAME = "sanitized-dataset-name"
    COMPONENT_NAME = "sanitized-component-name"
    #API_KEY = "00000000000000000000000000000000000000000000000000000000000000000000"


@pytest.fixture(scope="session")
def sanitized_values():
    return {
        "subscription_id": f"{SanitizedValues.SUBSCRIPTION_ID}",
        "resource_group_name": f"{SanitizedValues.RESOURCE_GROUP_NAME}",
        "project_name": f"{SanitizedValues.PROJECT_NAME}",
        "account_name": f"{SanitizedValues.ACCOUNT_NAME}",
        "component_name": f"{SanitizedValues.COMPONENT_NAME}",
    }


# From: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#start-the-test-proxy-server
# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep streamline tests by disabling wait times during LRO polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, sanitized_values):

    def sanitize_url_paths():

        add_general_regex_sanitizer(
            regex=r"/subscriptions/([-\w\._\(\)]+)",
            value=sanitized_values["subscription_id"],
            group_for_replace="1",
        )

        add_general_regex_sanitizer(
            regex=r"/resource[gG]roups/([-\w\._\(\)]+)",
            value=sanitized_values["resource_group_name"],
            group_for_replace="1",
        )

        add_general_regex_sanitizer(
            regex=r"/projects/([-\w\._\(\)]+)", value=sanitized_values["project_name"], group_for_replace="1"
        )

        add_general_regex_sanitizer(
            regex=r"/accounts/([-\w\._\(\)]+)", value=sanitized_values["account_name"], group_for_replace="1"
        )

        add_general_regex_sanitizer(
            regex=r"/components/([-\w\._\(\)]+)", value=sanitized_values["component_name"], group_for_replace="1"
        )

    sanitize_url_paths()

    #add_general_regex_sanitizer(
    #    regex=r"/data/([-\w\._\(\)]+)", value=mock_dataset_name["dataset_name"], group_for_replace="1"
    #)

    # Sanitize Application Insights connection string from service response
    add_body_key_sanitizer(
        json_path="properties.ConnectionString",
        value="InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://region.applicationinsights.azure.com/;LiveEndpoint=https://region.livediagnostics.monitor.azure.com/;ApplicationId=00000000-0000-0000-0000-000000000000",
    )

    # Sanitize API key from service response 
    add_body_key_sanitizer(json_path="properties.credentials.key", value="Sanitized-api-key")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3493"])
    remove_batch_sanitizers(["AZSDK3430"])
