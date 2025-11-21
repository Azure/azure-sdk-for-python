# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
from dotenv import load_dotenv, find_dotenv
from devtools_testutils import remove_batch_sanitizers, add_general_regex_sanitizer, add_body_key_sanitizer

# Skip loading .env if explicitly disabled (e.g., during parallel test runs)
# When running multiple projects in parallel, each should use its own env vars
# passed via subprocess, not load from a shared .env file
if os.environ.get("AZURE_AI_PROJECTS_SKIP_DOTENV") != "true":
    if not load_dotenv(find_dotenv(), override=True):
        print("Did not find a .env file. Using default environment variable values for tests.")
else:
    print("Skipping .env file loading (AZURE_AI_PROJECTS_SKIP_DOTENV is set)")


def pytest_collection_modifyitems(items):
    if os.environ.get("AZURE_TEST_RUN_LIVE") == "true":
        return
    for item in items:
        if "tests\\evaluation" in item.fspath.strpath or "tests/evaluation" in item.fspath.strpath:
            item.add_marker(
                pytest.mark.skip(
                    reason="Skip running Evaluations tests in PR pipeline until we can sort out the failures related to Microsoft Foundry project settings"
                )
            )


class SanitizedValues:
    SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    RESOURCE_GROUP_NAME = "sanitized-resource-group-name"
    ACCOUNT_NAME = "sanitized-account-name"
    PROJECT_NAME = "sanitized-project-name"
    COMPONENT_NAME = "sanitized-component-name"
    AGENTS_API_VERSION = "sanitized-api-version"


@pytest.fixture(scope="session")
def sanitized_values():
    return {
        "subscription_id": f"{SanitizedValues.SUBSCRIPTION_ID}",
        "resource_group_name": f"{SanitizedValues.RESOURCE_GROUP_NAME}",
        "project_name": f"{SanitizedValues.PROJECT_NAME}",
        "account_name": f"{SanitizedValues.ACCOUNT_NAME}",
        "component_name": f"{SanitizedValues.COMPONENT_NAME}",
        "agents_api_version": f"{SanitizedValues.AGENTS_API_VERSION}",
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

        # azure-ai-projects package takes dependency on azure-ai-agents package, but does not specify exactly what
        # version. When you do the local test recordings, you may have one version of azure-ai-agents installed.
        # When the tests run in CI pipeline, it will use latest stable version, which may or may not match the
        # local version you installed. We have tests that return an Agents client, then makes a call. So we want to
        # remove the api-version from the recordings.
        add_general_regex_sanitizer(
            regex=r"/assistants.*?api-version=(.*)", value=sanitized_values["agents_api_version"], group_for_replace="1"
        )

    sanitize_url_paths()

    # Sanitize API key from service response (this includes Application Insights connection string)
    add_body_key_sanitizer(json_path="credentials.key", value="sanitized-api-key")

    # Sanitize SAS URI from Datasets get credential response
    add_body_key_sanitizer(json_path="blobReference.credential.sasUri", value="sanitized-sas-uri")
    add_body_key_sanitizer(json_path="blobReferenceForConsumption.credential.sasUri", value="sanitized-sas-uri")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3493"])
    remove_batch_sanitizers(["AZSDK3430"])
