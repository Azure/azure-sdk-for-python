# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared helpers for recorded Cognitive Services connection tests."""

import logging
import re
from uuid import UUID

from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import models
from devtools_testutils import add_body_key_sanitizer, add_general_string_sanitizer, add_header_regex_sanitizer

API_VERSION = "2025-06-01"
SANITIZED_CONNECTION_NAME = "sanitized-connection"
CONNECTION_TARGET = "https://example.invalid/sdk-connection-test"
TEST_CREDENTIAL = "sdk-connection-test-secret"

_LOGGER = logging.getLogger(__name__)
_REQUEST_ID_HEADERS = ("x-ms-request-id", "x-ms-correlation-request-id", "x-ms-routing-request-id")
_LRO_HEADERS = ("azure-asyncoperation", "operation-location", "location")


def custom_keys_properties(revision):
    return models.CustomKeysConnectionProperties(
        category=models.ConnectionCategory.CUSTOM_KEYS,
        target=CONNECTION_TARGET,
        metadata={"revision": revision},
        credentials=models.CustomKeys(keys_property={"test-key": TEST_CREDENTIAL}),
    )


def connection_resource(revision):
    return models.ConnectionPropertiesV2BasicResource(properties=custom_keys_properties(revision))


def add_connection_sanitizers(connection_name):
    add_general_string_sanitizer(
        target=connection_name,
        value=SANITIZED_CONNECTION_NAME,
        function_scoped=True,
    )
    add_general_string_sanitizer(
        target=TEST_CREDENTIAL,
        value="sanitized-test-credential",
        function_scoped=True,
    )
    add_body_key_sanitizer(
        json_path="$..value[*].name",
        value="Sanitized",
        regex=rf"^(?!(?:{re.escape(connection_name)}|{re.escape(SANITIZED_CONNECTION_NAME)})$).+$",
        function_scoped=True,
    )
    for json_path in (
        "$..value[*].id",
        "$..value[*].properties.group",
        "$..value[*].properties.sharedUserList[*]",
        "$..value[*].properties.target",
        "$..value[*].properties.metadata.ResourceId",
        "$..correlation.operation",
        "$..correlation.request",
    ):
        add_body_key_sanitizer(json_path=json_path, value="Sanitized", function_scoped=True)
    add_header_regex_sanitizer(key="Request-Context", value="Sanitized", function_scoped=True)
    add_header_regex_sanitizer(key="X-MSEdge-Ref", value="Sanitized", function_scoped=True)


def assert_connection(connection, expected_name, resource_type, expected_metadata, expected_id_suffix, is_live):
    assert connection.name == expected_name
    assert connection.type == resource_type
    assert connection.id
    if is_live:
        assert connection.id.rstrip("/").lower().endswith(expected_id_suffix.lower())
    assert connection.properties.auth_type == models.ConnectionAuthType.CUSTOM_KEYS
    assert connection.properties.category == models.ConnectionCategory.CUSTOM_KEYS
    assert connection.properties.target == CONNECTION_TARGET
    assert connection.properties.metadata["revision"] == expected_metadata


def log_create_failure(error: HttpResponseError, api_version: str) -> None:
    """Log allowlisted response metadata without exposing headers or response bodies."""
    response = error.response
    if response is None:
        return

    headers = response.headers
    request_ids = {}
    for header in _REQUEST_ID_HEADERS:
        value = headers.get(header)
        if value:
            try:
                request_ids[header] = str(UUID(value))
            except (ValueError, TypeError, AttributeError):
                continue

    lro_header_presence = {header: header in headers for header in _LRO_HEADERS}
    retry_after = headers.get("retry-after")
    if retry_after is not None and not re.fullmatch(r"\d+", str(retry_after)):
        retry_after = None

    _LOGGER.error(
        "Cognitive Services connection create failed: status=%s api_version=%s "
        "request_ids=%s lro_headers=%s retry_after=%s",
        response.status_code,
        api_version,
        request_ids,
        lro_header_presence,
        retry_after,
    )
