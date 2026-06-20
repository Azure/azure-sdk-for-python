# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
from types import SimpleNamespace
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest
from azure.appconfiguration._azure_appconfiguration_requests import (
    AppConfigRequestsCredentialsPolicy,
)
from azure.appconfiguration._utils import parse_connection_string


def test_parse_connection_string_returns_http_endpoint():
    # An http (not https) endpoint to ensure scheme is preserved
    conn_str = "Endpoint=http://localhost:8483;Id=test-id;Secret=test-secret"
    endpoint, id_, secret = parse_connection_string(conn_str)
    assert endpoint == "http://localhost:8483"
    assert id_ == "test-id"
    assert secret == "test-secret"


def test_signed_request_with_http_endpoint():
    endpoint = "http://localhost:8483"
    request = HttpRequest("GET", endpoint + "/kv/foo?label=env")
    # Create pipeline request with placeholder context, then replace with a namespace that has a transport attr.
    pipeline_request = PipelineRequest(request, {})
    pipeline_request.context = SimpleNamespace(transport=object())

    key = base64.b64encode(b"secret").decode("utf-8")
    credential = AzureKeyCredential(key)
    policy = AppConfigRequestsCredentialsPolicy(credential, endpoint, "test-id")

    policy._signed_request(pipeline_request)  # pylint: disable=protected-access

    headers = pipeline_request.http_request.headers

    assert pipeline_request.http_request.url.startswith("http://")
    assert "x-ms-date" in headers
    assert "x-ms-content-sha256" in headers
    auth = headers.get("Authorization")
    assert auth is not None
    assert auth.startswith("HMAC-SHA256 ")
