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
        path = item.fspath.strpath
        if "tests\\evaluation" in path or "tests/evaluation" in path:
            # test_human_evaluations.py is a pure unit test with no Microsoft Foundry
            # dependency, so it must keep running in the PR pipeline.
            if "test_human_evaluations" in os.path.basename(path):
                continue
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
    API_KEY = "sanitized-api-key"


@pytest.fixture(scope="session")
def sanitized_values():
    return {
        "subscription_id": f"{SanitizedValues.SUBSCRIPTION_ID}",
        "resource_group_name": f"{SanitizedValues.RESOURCE_GROUP_NAME}",
        "project_name": f"{SanitizedValues.PROJECT_NAME}",
        "account_name": f"{SanitizedValues.ACCOUNT_NAME}",
        "component_name": f"{SanitizedValues.COMPONENT_NAME}",
        "agents_api_version": f"{SanitizedValues.AGENTS_API_VERSION}",
        "api_key": f"{SanitizedValues.API_KEY}",
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

    # Sanitize per-recording random model name used by `.beta.models` sample tests.
    # Live re-recordings need a unique `<name>/<version>` namespace (Foundry's
    # asset store reserves it permanently after `delete`), so we use a random
    # suffix at recording time and normalize it here so playback URLs match.
    add_general_regex_sanitizer(regex=r"recsmplmdl[a-f0-9]+", value="recsmplmdl00000000")

    # Sanitize Foundry project-managed Azure Storage account hostnames returned
    # by `.beta.models.pending_upload` (shape: `sa<14 hex chars>.blob.core.windows.net`).
    add_general_regex_sanitizer(
        regex=r"sa[a-z0-9]{14,}\.blob\.core\.windows\.net",
        value="sanitized-storage-account.blob.core.windows.net",
    )

    # Sanitize the per-pending-upload container name returned by Foundry
    # (shape: `<prefix>-pr-<uuid>`).
    add_general_regex_sanitizer(
        regex=r"/[a-z0-9-]+-pr-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        value="/sanitized-pending-upload-container",
    )

    # Sanitize SAS-token query strings returned by `.beta.models.pending_upload`
    # (signed URLs to a Foundry-managed Storage container). Match conservatively
    # on the `sig=` parameter which is unique to SAS tokens and isn't used by
    # regular Azure API URLs.
    add_general_regex_sanitizer(
        regex=r"sig=[A-Za-z0-9%]+",
        value="sig=sanitized-sas-sig",
    )
    add_general_regex_sanitizer(
        regex=r"skoid=[A-Fa-f0-9\-]+",
        value="skoid=00000000-0000-0000-0000-000000000000",
    )
    add_general_regex_sanitizer(
        regex=r"sktid=[A-Fa-f0-9\-]+",
        value="sktid=00000000-0000-0000-0000-000000000000",
    )

    # Sanitize `/workspaces/<name>` URL segments (some Foundry asset-store URLs
    # reference the underlying ML workspace by name, which leaks the project
    # resource name).
    add_general_regex_sanitizer(
        regex=r"/workspaces/([-\w\._\(\)]+)",
        value=sanitized_values["account_name"],
        group_for_replace="1",
    )

    # Sanitize Foundry `azureai://` asset URIs whose `accounts/<name>` and
    # `projects/<name>` segments embed the project resource name.
    add_general_regex_sanitizer(
        regex=r"azureai://accounts/([^/]+)/projects/([^/]+)",
        value=f"azureai://accounts/{sanitized_values['account_name']}/projects/{sanitized_values['project_name']}",
    )

    # Sanitize the live Foundry project's account/project names anywhere they
    # appear in URLs, headers, or bodies. Derived from the live endpoint shape
    # `https://<account>.services.ai.azure.com/api/projects/<project>` so we
    # cover trailing leaks like `<workspace>@<project>@AML/...` asset IDs and
    # `publisherId` fields that aren't matched by URL-segment sanitizers.
    _live_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ.get("foundry_project_endpoint")
    if _live_endpoint:
        _ep_match = re.match(
            r"https?://(?P<account>[^.]+)\.[^/]+/api/projects/(?P<project>[^/?#]+)",
            _live_endpoint,
        )
        if _ep_match:
            _live_account = _ep_match.group("account")
            _live_project = _ep_match.group("project")
            # Order matters: the longer (account) name often contains the shorter
            # (project) name as a prefix; replace the longer one first.
            for _name, _placeholder in (
                (_live_account, sanitized_values["account_name"]),
                (_live_project, sanitized_values["project_name"]),
            ):
                add_general_regex_sanitizer(regex=re.escape(_name), value=_placeholder)
                add_body_string_sanitizer(target=_name, value=_placeholder)

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

    add_header_regex_sanitizer(key="api-key", value=SanitizedValues.API_KEY)

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
    add_body_key_sanitizer(json_path="credentials.key", value=SanitizedValues.API_KEY)

    # Sanitize GitHub personal access tokens that may appear in connection credentials
    add_general_regex_sanitizer(regex=r"github_pat_[A-Za-z0-9_]+", value="sanitized-github-pat")
    add_body_key_sanitizer(
        json_path="$..authorization",
        value="Bearer sanitized-github-pat",
        regex=r"(?i)^Bearer\s+github_pat_[A-Za-z0-9_]+$",
    )

    # Sanitize raw Entra-ID JWTs (no "Bearer " prefix) passed via MCPTool.authorization
    # to match the `fake_token` value the FakeTokenCredential returns during playback.
    add_body_key_sanitizer(
        json_path="$..authorization",
        value="fake_token",
        regex=r"^eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$",
    )

    # Sanitize Cognitive Services / Foundry account hostnames inside request and
    # response bodies (e.g. MCPTool.server_url built from FOUNDRY_PROJECT_ENDPOINT).
    # URL-path sanitizers above already redact /accounts/<x>, /projects/<x>, etc.,
    # but the host is built into body fields and needs its own redaction so
    # recordings match the playback FOUNDRY_PROJECT_ENDPOINT.
    add_body_regex_sanitizer(
        regex=r"https://[a-z0-9-]+\.services\.ai\.azure\.com",
        value=f"https://{SanitizedValues.ACCOUNT_NAME}.services.ai.azure.com",
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

    # Strip Content-Encoding so playback doesn't try to decompress a body that the test-proxy
    # has already stored decoded (notably brotli responses from openai endpoints which httpx
    # would otherwise fail to decode -> UnicodeDecodeError).
    add_remove_header_sanitizer(headers="Content-Encoding")

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
