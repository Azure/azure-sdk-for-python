# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for the customized (patched) ComputesOperations.begin_create_or_update.

These verify the behavior added to work around the async compute-create handling:
  - the create accepts a 202 (async "Accepted") response (the generated code rejected it),
  - the poller polls the compute *resource* (GET on the resource URL, watching
    ``provisioningState``) via ``BodyContentPolling`` and never the operation-status endpoint
    (``.../computeOperations/{id}``, which requires ``computeOperations/read``),
  - the poller still blocks until a terminal state and raises on a genuine provisioning failure, and
  - genuine non-2xx create errors still propagate.
"""
import json as _json
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.polling import NoPolling
from azure.mgmt.core.polling.arm_polling import (
    ARMPolling,
    AzureAsyncOperationPolling,
    BodyContentPolling,
    LocationPolling,
    StatusCheckPolling,
)
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.operations._patch import _ComputeResourcePolling

RESOURCE_URL = (
    "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acct"
    "/computes/test-compute?api-version=2026-05-15-preview"
)

ACCEPTED_BODY = {"name": "test-compute", "properties": {"provisioningState": "Accepted"}}
SUCCEEDED_BODY = {
    "name": "test-compute",
    "type": "Microsoft.CognitiveServices/accounts/computes",
    "properties": {"provisioningState": "Succeeded"},
}
NOT_FOUND_BODY = {"error": {"code": "NotFound", "message": "Cluster not found."}}


class _FakeHttpResponse:
    """Minimal stand-in for an azure.core.rest HttpResponse used by the polling machinery."""

    def __init__(self, status_code, body, method="PUT", url=RESOURCE_URL, headers=None):
        self.status_code = status_code
        self._body = body
        self.request = SimpleNamespace(method=method, url=url, headers={"x-ms-client-request-id": "fake-request-id"})
        self.headers = headers or {}
        self.reason = "reason"
        self.content_type = "application/json"

    @property
    def content(self):  # presence of ``content`` makes azure-core treat this as a "rest" response
        return _json.dumps(self._body).encode("utf-8") if self._body is not None else b""

    def text(self, *args, **kwargs):
        return _json.dumps(self._body) if self._body is not None else ""

    def json(self):
        return self._body

    def read(self, *args, **kwargs):
        return self.content


def _pipeline_response(status_code, body, method="PUT", url=RESOURCE_URL):
    return SimpleNamespace(http_response=_FakeHttpResponse(status_code, body, method, url), context={})


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


def _make_computes():
    client = CognitiveServicesManagementClient(
        credential=_FakeCredential(), subscription_id="00000000-0000-0000-0000-000000000000"
    )
    return client.computes


def test_create_uses_resource_polling_not_computeoperations():
    """The poller is ARMPolling restricted to resource-based algorithms; the operation-status
    algorithms (which would hit ``computeOperations/read``) are excluded."""
    computes = _make_computes()
    # A terminal 200 lets the poller finish during initialize, so no background poll is needed here.
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(200, SUCCEEDED_BODY))

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)

    assert isinstance(poller._polling_method, ARMPolling)
    assert isinstance(poller._polling_method, _ComputeResourcePolling)
    algorithms = [type(a) for a in poller._polling_method._lro_algorithms]
    assert BodyContentPolling in algorithms
    assert StatusCheckPolling in algorithms
    # The whole point of the fix: never follow Azure-AsyncOperation / Location to computeOperations.
    assert AzureAsyncOperationPolling not in algorithms
    assert LocationPolling not in algorithms

    result = poller.result()
    assert result.name == "test-compute"


def test_create_accepts_202_and_polls_resource_until_succeeded():
    """A 202 create is accepted and the poller blocks, polling the resource URL until Succeeded."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = MagicMock(return_value=_pipeline_response(200, SUCCEEDED_BODY, method="GET"))

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = poller.result()

    assert result.name == "test-compute"
    assert result.properties.provisioning_state == "Succeeded"
    # The status was polled from the resource itself, not the operation-status endpoint.
    computes._client.send_request.assert_called()
    polled_url = computes._client.send_request.call_args[0][0].url
    assert "computeOperations" not in polled_url
    assert "/computes/test-compute" in polled_url


def test_create_surfaces_provisioning_failure():
    """A create that provisions to Failed must raise with the resource's own error detail (not the
    generic 'Operation returned an invalid status OK')."""
    computes = _make_computes()
    failed_body = {
        "name": "test-compute",
        "properties": {
            "provisioningState": "Failed",
            "errors": [{"code": "QuotaExceeded", "message": "exceeding subscription quota limits."}],
        },
    }
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = MagicMock(return_value=_pipeline_response(200, failed_body, method="GET"))

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError) as exc_info:
        poller.result()
    message = str(exc_info.value)
    assert "QuotaExceeded" in message  # the real reason is surfaced
    assert "invalid status" not in message  # not azure-core's generic fallback message


def test_create_propagates_non_2xx_error():
    """A genuine non-2xx create failure must still raise, without any polling."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(
        return_value=_pipeline_response(400, {"error": {"code": "Bad", "message": "bad"}})
    )
    computes._client.send_request = MagicMock()

    with pytest.raises(HttpResponseError):
        computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    computes._client.send_request.assert_not_called()


def test_create_polling_false_uses_no_polling_escape_hatch():
    """Callers can still opt out of blocking with ``polling=False`` (returns the accepted resource)."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = MagicMock()

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling=False)

    assert isinstance(poller._polling_method, NoPolling)
    result = poller.result()
    assert result.name == "test-compute"
    computes._client.send_request.assert_not_called()


def test_create_tolerates_read_after_write_404_then_succeeds():
    """Right after the 202, a GET on the compute can return 404 'Cluster not found' for ~20s. The
    poller must tolerate that window and keep polling instead of failing the successful create."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = MagicMock(
        side_effect=[
            _pipeline_response(404, NOT_FOUND_BODY, method="GET"),
            _pipeline_response(200, SUCCEEDED_BODY, method="GET"),
        ]
    )

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = poller.result()

    assert result.name == "test-compute"
    assert computes._client.send_request.call_count == 2  # it kept polling past the 404


def test_create_surfaces_persistent_not_found(monkeypatch):
    """If the resource never becomes queryable, the bounded grace expires and the 404 surfaces, so a
    genuinely missing resource does not hang forever."""
    monkeypatch.setattr(_ComputeResourcePolling, "_NOT_FOUND_GRACE_SECONDS", -1)
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = MagicMock(return_value=_pipeline_response(404, NOT_FOUND_BODY, method="GET"))

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        poller.result()
