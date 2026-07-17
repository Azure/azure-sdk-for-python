# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for the customized (patched) ComputesOperations.begin_create_or_update.

These verify the behavior added to work around the async compute-create handling:
  - the create accepts a 202 (async "Accepted") response (the generated code rejected it),
  - the poller reads status from the ``list`` API (never the operation-status endpoint
    ``.../computeOperations/{id}``, which requires ``computeOperations/read``); ``list`` is used
    rather than ``get`` because a GET on a just-created compute returns 404 during provisioning,
  - the poller blocks until a terminal state and raises the compute's own error on failure, and
  - genuine non-2xx create errors still propagate.
"""
import json as _json
import time
import typing
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.polling import NoPolling
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.operations._patch import _ComputeListPolling, _encode_continuation_token

RESOURCE_URL = (
    "https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/rg/providers/Microsoft.CognitiveServices/accounts/acct"
    "/computes/test-compute?api-version=2026-05-15-preview"
)

ACCEPTED_BODY = {"name": "test-compute", "properties": {"provisioningState": "Accepted"}}


def _compute(name="test-compute", state="Succeeded", errors=None):
    """A minimal stand-in for a Compute model as returned by ComputesOperations.list()."""
    return SimpleNamespace(name=name, properties=SimpleNamespace(provisioning_state=state, errors=errors))


class _FakeHttpResponse:
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

    def read(self, *args, **kwargs):
        return self.content

    def iter_bytes(self, *args, **kwargs):
        return iter([self.content])

    def iter_raw(self, *args, **kwargs):
        return iter([self.content])


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


def test_create_uses_list_polling_not_computeoperations():
    """The poller is a _ComputeListPolling that reads status from list(), never computeOperations."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(return_value=[_compute(state="Succeeded")])

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)

    assert isinstance(poller._polling_method, _ComputeListPolling)
    result = poller.result()
    assert result.name == "test-compute"
    # Status came from the list API (scoped to the account), not the operation-status endpoint.
    computes.list.assert_called_with("rg", "acct")


def test_create_accepts_202_and_polls_list_until_succeeded():
    """A 202 create is accepted and the poller blocks, polling list() until provisioningState=Succeeded."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    # First poll: still scaling; second poll: succeeded. The poller must block across both.
    computes.list = MagicMock(side_effect=[[_compute(state="Scaling")], [_compute(state="Succeeded")]])

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = poller.result()

    assert result.name == "test-compute"
    assert result.properties.provisioning_state == "Succeeded"
    assert computes.list.call_count == 2  # it blocked past the non-terminal state


def test_create_surfaces_provisioning_failure():
    """A create that provisions to Failed must raise with the resource's own error detail."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(
        return_value=[
            _compute(state="Failed", errors=[{"code": "QuotaExceeded", "message": "exceeding subscription quota."}])
        ]
    )

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
    computes.list = MagicMock()

    with pytest.raises(HttpResponseError):
        computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    computes.list.assert_not_called()


def test_create_polling_false_uses_no_polling_escape_hatch():
    """Callers can still opt out of blocking with ``polling=False`` (returns the accepted resource)."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock()

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling=False)

    assert isinstance(poller._polling_method, NoPolling)
    result = poller.result()
    assert result.name == "test-compute"
    computes.list.assert_not_called()


def test_create_tolerates_compute_absent_from_list_then_appears():
    """Right after the 202 the compute may not be in list() yet; the poller must keep polling until it
    appears and reaches a terminal state, instead of failing the successful create."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(
        side_effect=[
            [],  # not visible yet
            [_compute(name="other")],  # visible, but a different compute
            [_compute(state="Succeeded")],  # finally our compute, terminal
        ]
    )

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    result = poller.result()

    assert result.name == "test-compute"
    assert computes.list.call_count == 3


def test_create_surfaces_persistent_absence(monkeypatch):
    """If the compute never appears in list(), the bounded grace expires and the poller gives up rather
    than hanging forever."""
    monkeypatch.setattr(_ComputeListPolling, "_NOT_FOUND_GRACE_SECONDS", -1)
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(return_value=[])

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        poller.result()


def test_public_overloads_are_preserved():
    """The generated method's three public overloads (Compute, JSON, IO[bytes]) must be retained so
    APIView and type checkers still see the original public signature."""
    get_overloads = getattr(typing, "get_overloads", None)
    if get_overloads is None:  # typing.get_overloads is Python 3.11+
        pytest.skip("typing.get_overloads requires Python 3.11+")
    from azure.mgmt.cognitiveservices.operations._patch import ComputesOperations as PatchedComputesOperations

    assert len(get_overloads(PatchedComputesOperations.begin_create_or_update)) == 3


def test_old_api_version_is_rejected():
    """The api-version validation guard on the generated method must be preserved: a client on an
    API version older than the method's introduction must raise instead of sending an unsupported PUT."""
    client = CognitiveServicesManagementClient(
        credential=_FakeCredential(), subscription_id="00000000-0000-0000-0000-000000000000", api_version="2020-01-01"
    )
    client.computes._client._pipeline.run = MagicMock()

    with pytest.raises(ValueError):
        client.computes.begin_create_or_update("rg", "acct", "test-compute", b"{}")
    client.computes._client._pipeline.run.assert_not_called()  # never sent the unsupported request


def test_continuation_token_does_not_send_new_create_request():
    """Resuming with a continuation_token must rebuild the poller, not re-issue the create PUT (which
    would mutate the resource again)."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock()
    computes.list = MagicMock(return_value=[_compute(state="Succeeded")])

    token = _encode_continuation_token("rg", "acct", "test-compute")
    poller = computes.begin_create_or_update(
        "rg", "acct", "test-compute", b"{}", continuation_token=token, polling_interval=0
    )
    poller.result()
    computes._client._pipeline.run.assert_not_called()  # no new create PUT on resume


def test_continuation_token_is_source_of_truth_for_scope():
    """The token (not the method arguments) decides which compute is resumed, so a token that encodes a
    different scope drives the list() poll to that scope."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock()
    computes.list = MagicMock(return_value=[_compute(name="real-compute", state="Succeeded")])

    token = _encode_continuation_token("real-rg", "real-acct", "real-compute")
    poller = computes.begin_create_or_update(
        "ignored-rg", "ignored-acct", "ignored-compute", b"{}", continuation_token=token, polling_interval=0
    )
    result = poller.result()

    assert result.name == "real-compute"
    computes.list.assert_called_with("real-rg", "real-acct")  # scope came from the token, not the args


def test_continuation_token_malformed_raises():
    """A malformed/unrelated continuation_token must fail loudly instead of silently resuming the wrong
    (current-argument) operation."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock()
    computes.list = MagicMock()

    with pytest.raises(ValueError):
        computes.begin_create_or_update(
            "rg", "acct", "test-compute", b"{}", continuation_token="not-a-valid-token", polling_interval=0
        )
    computes._client._pipeline.run.assert_not_called()
    computes.list.assert_not_called()


def test_create_preserves_canceled_status():
    """A compute that provisions to Canceled must be reported as ``Canceled`` (not collapsed to
    ``Failed``) so callers can inspect poller.status(), while still raising."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(return_value=[_compute(state="Canceled")])

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    with pytest.raises(HttpResponseError):
        poller.result()
    assert poller.status() == "Canceled"


def test_create_applies_cls_hook():
    """A caller-supplied ``cls`` must be applied to the final resource, preserving the generated
    method's ``cls=`` contract."""
    computes = _make_computes()
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(202, ACCEPTED_BODY))
    computes.list = MagicMock(return_value=[_compute(state="Succeeded")])

    sentinel = object()
    calls = []

    def cls(pipeline_response, deserialized, headers):
        calls.append((pipeline_response, deserialized, headers))
        return sentinel

    poller = computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", cls=cls, polling_interval=0)
    result = poller.result()

    assert result is sentinel  # the cls hook's return value is what the caller receives
    assert calls and calls[0][1].name == "test-compute"  # cls received the deserialized compute


def test_failed_initial_body_surfaces_error():
    """If the accepted initial body is already terminal-failed (a synchronous failure rather than the
    usual async 202), the resource's own error detail is surfaced without any polling."""
    computes = _make_computes()
    failed_body = {
        "name": "test-compute",
        "properties": {
            "provisioningState": "Failed",
            "errors": [{"code": "QuotaExceeded", "message": "exceeding subscription quota limits."}],
        },
    }
    computes._client._pipeline.run = MagicMock(return_value=_pipeline_response(200, failed_body))
    computes.list = MagicMock()

    with pytest.raises(HttpResponseError) as exc_info:
        computes.begin_create_or_update("rg", "acct", "test-compute", b"{}", polling_interval=0)
    assert "QuotaExceeded" in str(exc_info.value)
    computes.list.assert_not_called()  # failed synchronously; no polling needed
