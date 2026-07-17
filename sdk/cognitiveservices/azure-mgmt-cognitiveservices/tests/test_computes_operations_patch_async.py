# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async unit tests for the customized (patched) ComputesOperations.begin_create_or_update.

Mirror of the sync tests: the create accepts a 202, the poller reads status from the ``list`` API
(never ``computeOperations``, and not ``get`` which 404s during provisioning), blocks until terminal,
surfaces provisioning failures, and still propagates genuine non-2xx create errors.
"""
import json as _json
import time
import typing
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncNoPolling
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio.operations._patch import _AsyncComputeListPolling
from azure.mgmt.cognitiveservices.operations._patch import _encode_continuation_token

RESOURCE_URL = (
    "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acct"
    "/computes/test-compute?api-version=2026-05-15-preview"
)

ACCEPTED_BODY = {"name": "test-compute", "properties": {"provisioningState": "Accepted"}}


def _compute(name="test-compute", state="Succeeded", errors=None):
    """A minimal stand-in for a Compute model as returned by ComputesOperations.list()."""
    return SimpleNamespace(name=name, properties=SimpleNamespace(provisioning_state=state, errors=errors))


class _AsyncList:
    """An async-iterable stand-in for the AsyncItemPaged returned by the async list()."""

    def __init__(self, items):
        self._items = list(items)

    def __aiter__(self):
        async def gen():
            for item in self._items:
                yield item

        return gen()


def _list_mock(*pages):
    """A MagicMock whose successive calls return successive async-iterable pages."""
    return MagicMock(side_effect=[_AsyncList(page) for page in pages])


class _FakeAsyncHttpResponse:
    """Minimal stand-in for the streamed create (202) response used by _create_or_update_initial."""

    def __init__(self, status_code, body, method="PUT", url=RESOURCE_URL, headers=None):
        self.status_code = status_code
        self._body = body
        self.request = SimpleNamespace(method=method, url=url, headers={"x-ms-client-request-id": "fake-request-id"})
        self.headers = headers or {}
        self.reason = "reason"
        self.content_type = "application/json"

    @property
    def content(self):
        return _json.dumps(self._body).encode("utf-8") if self._body is not None else b""

    def text(self, *args, **kwargs):
        return _json.dumps(self._body) if self._body is not None else ""

    def json(self):
        return self._body

    async def read(self, *args, **kwargs):
        return self.content

    def iter_bytes(self, *args, **kwargs):
        return iter([self.content])

    def iter_raw(self, *args, **kwargs):
        return iter([self.content])


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
async def test_create_uses_list_polling_not_computeoperations():
    """The poller is an _AsyncComputeListPolling that reads status from list(), never computeOperations."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock([_compute(state="Succeeded")])

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)

    assert isinstance(poller._polling_method, _AsyncComputeListPolling)
    result = await poller.result()
    assert result.name == "test-compute"
    computes.list.assert_called_with("rg", "acct")


@pytest.mark.asyncio
async def test_create_accepts_202_and_polls_list_until_succeeded():
    """A 202 create is accepted and the poller blocks, polling list() until provisioningState=Succeeded."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock([_compute(state="Scaling")], [_compute(state="Succeeded")])

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = await poller.result()

    assert result.name == "test-compute"
    assert result.properties.provisioning_state == "Succeeded"
    assert computes.list.call_count == 2  # it blocked past the non-terminal state


@pytest.mark.asyncio
async def test_create_surfaces_provisioning_failure():
    """A create that provisions to Failed must raise with the resource's own error detail."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock(
        [_compute(state="Failed", errors=[{"code": "QuotaExceeded", "message": "exceeding subscription quota."}])]
    )

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError) as exc_info:
        await poller.result()
    message = str(exc_info.value)
    assert "QuotaExceeded" in message
    assert "invalid status" not in message


@pytest.mark.asyncio
async def test_create_propagates_non_2xx_error():
    """A genuine non-2xx create failure must still raise, without any polling."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(
        return_value=_pipeline_response(400, {"error": {"code": "Bad", "message": "bad"}})
    )
    computes.list = MagicMock()

    with pytest.raises(HttpResponseError):
        await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    computes.list.assert_not_called()


@pytest.mark.asyncio
async def test_create_polling_false_uses_no_polling_escape_hatch():
    """Callers can still opt out of blocking with ``polling=False`` (returns the accepted resource)."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock()

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling=False)

    assert isinstance(poller._polling_method, AsyncNoPolling)
    result = await poller.result()
    assert result.name == "test-compute"
    computes.list.assert_not_called()


@pytest.mark.asyncio
async def test_create_tolerates_compute_absent_from_list_then_appears():
    """Right after the 202 the compute may not be in list() yet; the poller must keep polling until it
    appears and reaches a terminal state, instead of failing the successful create."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock([], [_compute(name="other")], [_compute(state="Succeeded")])

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = await poller.result()

    assert result.name == "test-compute"
    assert computes.list.call_count == 3


@pytest.mark.asyncio
async def test_create_surfaces_persistent_absence(monkeypatch):
    """If the compute never appears in list(), the bounded grace expires and the poller gives up rather
    than hanging forever."""
    monkeypatch.setattr(_AsyncComputeListPolling, "_NOT_FOUND_GRACE_SECONDS", -1)
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(side_effect=lambda *a, **k: _AsyncList([]))

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        await poller.result()


def test_public_overloads_are_preserved():
    """The generated async method's three public overloads must be retained for APIView/type checkers."""
    get_overloads = getattr(typing, "get_overloads", None)
    if get_overloads is None:  # typing.get_overloads is Python 3.11+
        pytest.skip("typing.get_overloads requires Python 3.11+")
    from azure.mgmt.cognitiveservices.aio.operations._patch import ComputesOperations as PatchedComputesOperations

    assert len(get_overloads(PatchedComputesOperations.begin_create_or_update)) == 3


@pytest.mark.asyncio
async def test_old_api_version_is_rejected():
    """The api-version validation guard on the generated async method must be preserved."""
    client = CognitiveServicesManagementClient(
        credential=_FakeAsyncCredential(),
        subscription_id="00000000-0000-0000-0000-000000000000",
        api_version="2020-01-01",
    )
    client.computes._client._pipeline.run = AsyncMock()

    with pytest.raises(ValueError):
        await client.computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    client.computes._client._pipeline.run.assert_not_called()


@pytest.mark.asyncio
async def test_continuation_token_does_not_send_new_create_request():
    """Resuming with a continuation_token must rebuild the poller, not re-issue the create PUT."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock()
    computes.list = _list_mock([_compute(state="Succeeded")])

    token = _encode_continuation_token("rg", "acct", "test-compute")
    poller = await computes.begin_create_or_update(
        "rg", "acct", "test-compute", b"{}", continuation_token=token, polling_interval=0
    )
    await poller.result()
    computes._client._pipeline.run.assert_not_called()


@pytest.mark.asyncio
async def test_continuation_token_is_source_of_truth_for_scope():
    """The token (not the method arguments) decides which compute is resumed, so a token that encodes a
    different scope drives the list() poll to that scope."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock()
    computes.list = _list_mock([_compute(name="real-compute", state="Succeeded")])

    token = _encode_continuation_token("real-rg", "real-acct", "real-compute")
    poller = await computes.begin_create_or_update(
        "ignored-rg", "ignored-acct", "ignored-compute", b"{}", continuation_token=token, polling_interval=0
    )
    result = await poller.result()

    assert result.name == "real-compute"
    computes.list.assert_called_with("real-rg", "real-acct")  # scope came from the token, not the args


@pytest.mark.asyncio
async def test_continuation_token_malformed_raises():
    """A malformed/unrelated continuation_token must fail loudly instead of silently resuming the wrong
    (current-argument) operation."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock()
    computes.list = MagicMock()

    with pytest.raises(ValueError):
        await computes.begin_create_or_update(
            "rg", "acct", "test-compute", b"{}", continuation_token="not-a-valid-token", polling_interval=0
        )
    computes._client._pipeline.run.assert_not_called()
    computes.list.assert_not_called()


@pytest.mark.asyncio
async def test_create_preserves_canceled_status():
    """A compute that provisions to Canceled must be reported as ``Canceled`` (not collapsed to
    ``Failed``) so callers can inspect poller.status(), while still raising."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock([_compute(state="Canceled")])

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        await poller.result()
    assert poller.status() == "Canceled"


@pytest.mark.asyncio
async def test_create_applies_cls_hook():
    """A caller-supplied ``cls`` must be applied to the final resource, preserving the generated
    method's ``cls=`` contract."""
    computes = _make_computes()
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = _list_mock([_compute(state="Succeeded")])

    sentinel = object()
    calls = []

    def cls(pipeline_response, deserialized, headers):
        calls.append((pipeline_response, deserialized, headers))
        return sentinel

    poller = await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", cls=cls, polling_interval=0)
    result = await poller.result()

    assert result is sentinel  # the cls hook's return value is what the caller receives
    assert calls and calls[0][1].name == "test-compute"  # cls received the deserialized compute


@pytest.mark.asyncio
async def test_failed_initial_body_surfaces_error():
    """A synchronously terminal-failed initial body surfaces the resource's own error, without polling."""
    computes = _make_computes()
    failed_body = {
        "name": "test-compute",
        "properties": {
            "provisioningState": "Failed",
            "errors": [{"code": "QuotaExceeded", "message": "exceeding subscription quota limits."}],
        },
    }
    computes._client._pipeline.run = AsyncMock(return_value=_pipeline_response(200, failed_body))
    computes.list = MagicMock()

    with pytest.raises(HttpResponseError) as exc_info:
        await computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    assert "QuotaExceeded" in str(exc_info.value)
    computes.list.assert_not_called()
