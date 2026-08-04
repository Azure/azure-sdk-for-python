# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Unit tests for the content validation pipeline policy.

These tests exercise ``StorageContentValidation.on_response`` directly with
synthetic request/response objects. They require no network access or live
storage account, so they run deterministically and in milliseconds.
"""

import pytest
from azure.core.exceptions import AzureError

from azure.storage.filedatalake._shared.policies import (
    SM_HEADER,
    SM_HEADER_V1_CRC64,
    StorageContentValidation,
)


class _FakeHttpRequest:
    def __init__(self, method, headers):
        self.method = method
        self.headers = headers


class _FakeHttpResponse:
    def __init__(self, status_code, headers, body=b""):
        self.status_code = status_code
        self.headers = headers
        self._body = body

    def body(self):
        return self._body


class _FakePipelineRequest:
    def __init__(self, http_request, context):
        self.http_request = http_request
        self.context = context


class _FakePipelineResponse:
    def __init__(self, http_request, http_response, context):
        self.http_request = http_request
        self.http_response = http_response
        self.context = context


def _build_request_response(validate_content, request_headers, response_status, response_headers):
    # Request and response share a single pipeline context, as in the real pipeline.
    context = {"validate_content": validate_content}
    http_request = _FakeHttpRequest(method="PATCH", headers=request_headers)
    http_response = _FakeHttpResponse(status_code=response_status, headers=response_headers)
    request = _FakePipelineRequest(http_request, context)
    response = _FakePipelineResponse(http_request, http_response, context)
    return request, response


def test_crc64_validation_masks_error_response():
    """Repro: on a non-2xx response the crc64 branch raises a misleading structured-message
    error instead of surfacing the real service error (e.g. OperationTimedOut).

    This reproduces the pipeline symptom for ``validate_content="crc64"`` where the 500
    ``OperationTimedOut`` response has no ``x-ms-structured-body`` header, so the policy
    compares the request header against ``None`` and raises.
    """
    policy = StorageContentValidation()
    request, response = _build_request_response(
        validate_content="crc64",
        request_headers={SM_HEADER: SM_HEADER_V1_CRC64},
        response_status=500,  # OperationTimedOut
        response_headers={"x-ms-error-code": "OperationTimedOut"},  # no SM_HEADER on error
    )

    with pytest.raises(AzureError, match="Expected structured message header in response does not match request"):
        policy.on_response(request, response)


def test_md5_validation_skips_error_response():
    """Contrast: the md5 branch only runs when the response carries a ``content-md5``
    header, so a 500 error response (which has none) passes through untouched and the
    real service error is allowed to surface downstream.
    """
    policy = StorageContentValidation()
    request, response = _build_request_response(
        validate_content="md5",
        request_headers={},
        response_status=500,  # OperationTimedOut
        response_headers={"x-ms-error-code": "OperationTimedOut"},  # no content-md5 on error
    )

    # Should not raise.
    policy.on_response(request, response)


def test_crc64_validation_passes_on_matching_headers():
    """Sanity: when the response echoes the structured-message header (success path),
    the crc64 branch does not raise.
    """
    policy = StorageContentValidation()
    request, response = _build_request_response(
        validate_content="crc64",
        request_headers={SM_HEADER: SM_HEADER_V1_CRC64},
        response_status=202,
        response_headers={SM_HEADER: SM_HEADER_V1_CRC64},
    )

    # Should not raise.
    policy.on_response(request, response)
