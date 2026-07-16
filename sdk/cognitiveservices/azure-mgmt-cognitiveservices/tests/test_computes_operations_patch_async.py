# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async unit tests for the customized (patched) ComputesOperations.begin_create_or_update.

Mirror of the sync tests: the create accepts a 202, the poller polls the compute *resource*
(never ``computeOperations``), blocks until terminal, surfaces provisioning failures, and still
propagates genuine non-2xx create errors.
"""
import json as _json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncNoPolling
from azure.mgmt.core.polling.arm_polling import (
    AzureAsyncOperationPolling,
    BodyContentPolling,
    LocationPolling,
    StatusCheckPolling,
)
from azure.mgmt.core.polling.async_arm_polling import AsyncARMPolling
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio.operations._patch import _AsyncComputeResourcePolling

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


class _FakeAsyncHttpResponse:
    """Minimal stand-in for an azure.core.rest AsyncHttpResponse used by the polling machinery."""

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

    async def read(self, *args, **kwargs):
        return self.content


def _pipeline_response(status_code, body, method="PUT", url=RESOURCE_URL):
    return SimpleNamespace(http_response=_FakeAsyncHttpResponse(status_code, body, method, url), context={})


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        return AccessToken("fake-token", int(time.time()) + 3600)


def _make_computes():
    client = CognitiveServicesManagementClient(
        credential=_FakeAsyncCredential(), subscription_id="00000000-0000-0000-0000-000000000000"
    )
    return client.computes


@pytest.mark.asyncio
async def test_create_uses_resource_polling_not_computeoperations():
    """The poller is AsyncARMPolling restricted to resource-based algorithms; the operation-status
    algorithms (which would hit ``computeOperations/read``) are excluded."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(200, SUCCEEDED_BODY))

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)

    assert isinstance(poller._polling_method, AsyncARMPolling)
    assert isinstance(poller._polling_method, _AsyncComputeResourcePolling)
    algorithms = [type(a) for a in poller._polling_method._lro_algorithms]
    assert BodyContentPolling in algorithms
    assert StatusCheckPolling in algorithms
    assert AzureAsyncOperationPolling not in algorithms
    assert LocationPolling not in algorithms

    result = await poller.result()
    assert result.name == "test-compute"


@pytest.mark.asyncio
async def test_create_accepts_202_and_polls_resource_until_succeeded():
    """A 202 create is accepted and the poller blocks, polling the resource URL until Succeeded."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = AsyncMock(return_value=_pipeline_response(200, SUCCEEDED_BODY, method="GET"))

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = await poller.result()

    assert result.name == "test-compute"
    assert result.properties.provisioning_state == "Succeeded"
    computes._client.send_request.assert_called()
    polled_url = computes._client.send_request.call_args[0][0].url
    assert "computeOperations" not in polled_url
    assert "/computes/test-compute" in polled_url


@pytest.mark.asyncio
async def test_create_surfaces_provisioning_failure():
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
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = AsyncMock(return_value=_pipeline_response(200, failed_body, method="GET"))

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError) as exc_info:
        await poller.result()
    message = str(exc_info.value)
    assert "QuotaExceeded" in message  # the real reason is surfaced
    assert "invalid status" not in message  # not azure-core's generic fallback message


@pytest.mark.asyncio
async def test_create_propagates_non_2xx_error():
    """A genuine non-2xx create failure must still raise, without any polling."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(
        return_value=_pipeline_response(400, {"error": {"code": "Bad", "message": "bad"}})
    )
    computes._client.send_request = AsyncMock()

    with pytest.raises(HttpResponseError):
        await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    computes._client.send_request.assert_not_called()


@pytest.mark.asyncio
async def test_create_polling_false_uses_no_polling_escape_hatch():
    """Callers can still opt out of blocking with ``polling=False`` (returns the accepted resource)."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = AsyncMock()

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling=False)

    assert isinstance(poller._polling_method, AsyncNoPolling)
    result = await poller.result()
    assert result.name == "test-compute"
    computes._client.send_request.assert_not_called()


@pytest.mark.asyncio
async def test_create_tolerates_read_after_write_404_then_succeeds():
    """Right after the 202, a GET on the compute can return 404 'Cluster not found' for ~20s. The
    poller must tolerate that window and keep polling instead of failing the successful create."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = AsyncMock(
        side_effect=[
            _pipeline_response(404, NOT_FOUND_BODY, method="GET"),
            _pipeline_response(200, SUCCEEDED_BODY, method="GET"),
        ]
    )

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = await poller.result()

    assert result.name == "test-compute"
    assert computes._client.send_request.call_count == 2  # it kept polling past the 404


@pytest.mark.asyncio
async def test_create_surfaces_persistent_not_found(monkeypatch):
    """If the resource never becomes queryable, the bounded grace expires and the 404 surfaces, so a
    genuinely missing resource does not hang forever."""
    monkeypatch.setattr(_AsyncComputeResourcePolling, "_NOT_FOUND_GRACE_SECONDS", -1)
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes._client.send_request = AsyncMock(return_value=_pipeline_response(404, NOT_FOUND_BODY, method="GET"))

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        await poller.result()
