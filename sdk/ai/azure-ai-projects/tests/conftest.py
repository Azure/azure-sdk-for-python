# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# Register MIME types before any other imports to ensure consistent Content-Type detection
# across Windows, macOS, and Linux when uploading files in tests
import mimetypes

mimetypes.add_type("text/csv", ".csv")
mimetypes.add_type("text/markdown", ".md")

import os
import re
import pytest
from dotenv import find_dotenv, load_dotenv
from devtools_testutils import (
    remove_batch_sanitizers,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_body_regex_sanitizer,
    add_body_string_sanitizer,
    add_body_key_sanitizer,
    add_remove_header_sanitizer,
)

if not load_dotenv(find_dotenv(), override=True):
    print("Did not find a .env file. Using default environment variable values for tests.")


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

    # Sanitize fine-tuning job IDs in URLs and response bodies
    add_general_regex_sanitizer(regex=r"ftjob-[a-f0-9]+", value="sanitized-ftjob-id")

    # Sanitize deployment names that are derived from job IDs (e.g., test-6158cfe2)
    add_general_regex_sanitizer(regex=r"test-[a-f0-9]{8}", value="test-ftjob-id")

    # Sanitize file IDs in URLs and response bodies
    add_general_regex_sanitizer(regex=r"file-[a-f0-9]+", value="sanitized-file-id")

    # Sanitize checkpoint IDs in URLs and response bodies
    add_general_regex_sanitizer(regex=r"ftchkpt-[a-f0-9]+", value="sanitized-checkpoint-id")

    # Sanitize eval dataset names with timestamps (e.g., eval-data-2026-01-19_040648_UTC)
    add_general_regex_sanitizer(regex=r"eval-data-\d{4}-\d{2}-\d{2}_\d{6}_UTC", value="eval-data-sanitized-timestamp")

    # Sanitize Unix timestamps in eval names (from sample_redteam_evaluations.py)
    # Pattern 1: "Red Team Agent Safety Evaluation -<timestamp>"
    add_general_regex_sanitizer(regex=r"Evaluation -\d{10}", value="Evaluation -SANITIZED-TS")
    # Pattern 2: "Eval Run for <agent_name> -<timestamp>" (agent name already sanitized)
    add_general_regex_sanitizer(regex=r"sanitized-agent-name -\d{10}", value="sanitized-agent-name -SANITIZED-TS")

    # Sanitize image-generation deployment name from live env when present.
    # This value is commonly emitted in request headers (for example
    # `x-ms-oai-image-generation-deployment`) and may come from either
    # upper/lowercase environment variable naming paths.
    image_generation_models = {
        value
        for value in (
            os.environ.get("IMAGE_GENERATION_MODEL_DEPLOYMENT_NAME"),
            os.environ.get("image_generation_model_deployment_name"),
        )
        if value
    }
    for image_generation_model in image_generation_models:
        add_general_regex_sanitizer(regex=re.escape(image_generation_model), value="sanitized-gpt-image")
        add_header_regex_sanitizer(
            key="x-ms-oai-image-generation-deployment",
            regex=re.escape(image_generation_model),
            value="sanitized-gpt-image",
        )
        add_body_string_sanitizer(target=image_generation_model, value="sanitized-gpt-image")

    # Deterministic fallback sanitization for image generation deployment/model values.
    # These do not depend on environment variables and ensure recordings are redacted even
    # when runtime values come from unexpected sources.
    add_header_regex_sanitizer(
        key="x-ms-oai-image-generation-deployment",
        regex=r".+",
        value="sanitized-gpt-image",
    )
    add_body_regex_sanitizer(
        regex=r'"model"\s*:\s*"gpt-image[^"]*"',
        value='"model": "sanitized-gpt-image"',
    )

    # Sanitize API key from service response (this includes Application Insights connection string)
    add_body_key_sanitizer(json_path="credentials.key", value="sanitized-api-key")

    # Sanitize GitHub personal access tokens that may appear in connection credentials
    add_general_regex_sanitizer(regex=r"github_pat_[A-Za-z0-9_]+", value="sanitized-github-pat")
    add_body_key_sanitizer(
        json_path="$..authorization",
        value="Bearer sanitized-github-pat",
        regex=r"(?i)^Bearer\s+github_pat_[A-Za-z0-9_]+$",
    )

    # Sanitize Azure Blob account host while preserving container path and SAS shape.
    # This avoids creating inconsistent recordings where sasUri points to a different
    # container than the corresponding blob RequestUri entries.
    add_general_regex_sanitizer(
        regex=r"https://([a-z0-9-]+)\.blob\.core\.windows\.net",
        value="Sanitized",
        group_for_replace="1",
    )

    add_body_key_sanitizer(
        json_path="$..project_connection_id",
        value="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/connections/connector-name",
    )

    # Sanitize print output from sample validation to prevent replay failures when print statements change
    # Only targets the validation Responses API call by matching the unique input prefix
    add_body_key_sanitizer(
        json_path="$.input",
        value="sanitized-print-output",
        regex=r"(?s)print contents array = .*",
    )

    # Remove Stainless headers from OpenAI client requests, since they include platform and OS specific info, which we can't have in recorded requests.
    # Here is an example of all the `x-stainless` headers from a Responses call:
    #   x-stainless-arch: other:amd64
    #   x-stainless-async: false
    #   x-stainless-lang: python
    #   x-stainless-os: Windows
    #   x-stainless-package-version: 2.8.1
    #   x-stainless-read-timeout: 600
    #   x-stainless-retry-count: 0
    #   x-stainless-runtime: CPython
    #   x-stainless-runtime-version: 3.14.0
    # Note that even though the doc string for `add_remove_header_sanitizer` says `condition` is supported, it is not implemented. So we can't do this:
    #   add_remove_header_sanitizer(condition='{"uriRegex": "(?i)^x-stainless-.*$"}')
    # We have to explicitly list all the headers to remove:
    add_remove_header_sanitizer(
        headers="x-stainless-arch, x-stainless-async, x-stainless-lang, x-stainless-os, x-stainless-package-version, x-stainless-read-timeout, x-stainless-retry-count, x-stainless-runtime, x-stainless-runtime-version"
    )

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3493"])
    remove_batch_sanitizers(["AZSDK3430"])

    # Sanitize ARM operation headers that contain certificates and identifiers
    add_general_regex_sanitizer(regex=r"[?&]t=[0-9]+", value="&t=sanitized-timestamp")
    add_general_regex_sanitizer(regex=r"[?&]c=[^&\"]+", value="&c=sanitized-certificate")
    add_general_regex_sanitizer(regex=r"[?&]s=[^&\"]+", value="&s=sanitized-signature")
    add_general_regex_sanitizer(regex=r"[?&]h=[^&\"]+", value="&h=sanitized-hash")
    add_general_regex_sanitizer(regex=r"operationResults/[a-f0-9\-]+", value="operationResults/sanitized-operation-id")
    add_general_regex_sanitizer(regex=r"https://management\.azure\.com/", value="https://sanitized.azure.com/")
