# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared configuration, assertions, and allowlisted project LRO diagnostics."""

import logging
import os
import re
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import pytest

from azure.mgmt.cognitiveservices import models
from azure.mgmt.cognitiveservices._configuration import CognitiveServicesManagementClientConfiguration
from devtools_testutils import add_general_regex_sanitizer, add_general_string_sanitizer

LOGGER = logging.getLogger("cognitiveservices.project_contract")
# Live runs use the installed SDK's default; playback reuses the version stored in the recording.
DEFAULT_API_VERSION = CognitiveServicesManagementClientConfiguration(
    credential=object(), subscription_id="x"
).api_version
RESOURCE_TYPE = "Microsoft.CognitiveServices/accounts/projects"
SANITIZED_PROJECT_NAME = "sanitized-test-project"
_VERSION = re.compile(r"\d{4}-\d{2}-\d{2}(?:-preview)?")
_UUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")


def api_version(test_case, variables):
    if test_case.is_live:
        version = os.environ.get("AZURE_COGNITIVE_SERVICES_API_VERSION") or DEFAULT_API_VERSION
    else:
        version = (variables or {}).get("api_version", "")
    if not _VERSION.fullmatch(version):
        pytest.fail(
            "Set AZURE_COGNITIVE_SERVICES_API_VERSION to YYYY-MM-DD[-preview], "
            "or re-record so the recording stores api_version."
        )
    return version


def configuration(test_case, variables):
    add_general_regex_sanitizer(
        regex=r'[?&](?:c|s|h)=([^&"]+)',
        value="sanitized",
        group_for_replace="1",
        function_scoped=True,
    )
    if test_case.is_live:
        names = ("AZURE_RESOURCE_GROUP", "AZURE_COGNITIVE_SERVICES_ACCOUNT", "AZURE_COGNITIVE_SERVICES_LOCATION")
        missing = [name for name in ("AZURE_SUBSCRIPTION_ID", *names) if not os.environ.get(name)]
        if missing:
            pytest.fail("Set these variables before recording project tests: " + ", ".join(missing))
        project_name = test_case.get_resource_name("sdkproj") + uuid4().hex[:12]
        add_general_string_sanitizer(target=project_name, value=SANITIZED_PROJECT_NAME, function_scoped=True)
        return (*(os.environ[name] for name in names), project_name)
    if not variables or variables.get("project_name") != SANITIZED_PROJECT_NAME or not variables.get("location"):
        pytest.fail("Re-record the project lifecycle test with sanitized project_name and location variables.")
    return "sanitized-resource-group", "sanitized-cognitive-account", variables["location"], variables["project_name"]


def project_body(location, description):
    return models.Project(
        location=location,
        identity=models.Identity(type="SystemAssigned"),
        properties=models.ProjectProperties(display_name="SDK contract test", description=description),
    )


def assert_project(project, expected_id, location, description, is_live):
    assert project.id.lower() == (expected_id if is_live else "Sanitized").lower(), project.id
    # Nested ARM resources may report their name as "<account>/<project>".
    assert project.name.rsplit("/", 1)[-1] == expected_id.rsplit("/", 1)[-1], project.name
    assert project.type.lower() == RESOURCE_TYPE.lower(), project.type
    assert project.location.lower() == location.lower(), project.location
    assert project.properties.provisioning_state == "Succeeded", project.properties.provisioning_state
    assert project.properties.display_name == "SDK contract test", project.properties.display_name
    assert project.properties.description == description, project.properties.description


class ResponseDiagnostics:
    """A raw_response_hook that runs before generated status validation, including on errors."""

    def __init__(self, version, phase):
        self.version = version
        self.phase = phase
        self.responses = []

    def __call__(self, response):
        request = response.http_request
        http_response = response.http_response
        versions = parse_qs(urlsplit(request.url).query).get("api-version", [])
        headers = {key.lower(): value for key, value in http_response.headers.items()}
        safe_headers = {}
        for key in ("azure-asyncoperation", "operation-location", "location"):
            if key in headers:
                # Polling URLs can contain resource identities or query-string credentials.
                safe_headers[key] = "<present; URL redacted>"
        for key in ("x-ms-request-id", "x-ms-client-request-id", "x-ms-correlation-request-id"):
            value = headers.get(key)
            if value is not None:
                safe_headers[key] = value if _UUID.fullmatch(value) else "<redacted>"
        if "retry-after" in headers:
            value = headers["retry-after"]
            safe_headers["retry-after"] = value if re.fullmatch(r"\d{1,6}", value) else "<redacted>"
        event = {
            "phase": self.phase,
            "method": request.method,
            "status": http_response.status_code,
            "api_version": self.version,
            "request_api_version": (
                versions[0] if len(versions) == 1 and _VERSION.fullmatch(versions[0]) else "<absent>"
            ),
            "headers": safe_headers,
        }
        self.responses.append(event)
        LOGGER.info("Project contract response: %s", event)


def cleanup_failed(error, original_error):
    # Do not log exception text: service errors can contain unrestricted response bodies.
    LOGGER.error(
        "Project cleanup failed: exception=%s status=%s", type(error).__name__, getattr(error, "status_code", None)
    )
    if not original_error:
        raise error
