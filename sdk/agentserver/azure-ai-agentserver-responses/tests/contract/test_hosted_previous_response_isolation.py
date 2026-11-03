# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for ``previous_response_id`` chain isolation in a hosted environment.

A hosted agent container (``FOUNDRY_HOSTING_ENVIRONMENT`` set) auto-activates
:class:`~azure.ai.agentserver.responses.store._foundry_provider.FoundryStorageProvider`,
so every response / input-item / history read is delegated to the Foundry storage
service, which owns partition enforcement.  These tests pin that contract for the
``previous_response_id`` traversal specifically: a caller must never be able to
reach another caller's input items by pointing ``previous_response_id`` at a
response they do not own — neither at creation time (history resolution) nor on a
later ``GET /responses/{id}/input_items`` read.

The Foundry storage service is replaced by :class:`_FakeFoundryStorage`, an
in-process stand-in that mirrors the server-side isolation rules: every stored
record is owned by the caller resolved from the platform-minted
``x-agent-foundry-call-id`` header and is invisible to every other caller,
including through a ``previous_response_id`` chain.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import azure.identity.aio
import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core.platform_headers import FOUNDRY_CALL_ID, USER_ID

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.hosting import _orchestrator as _orch
from azure.ai.agentserver.responses.store._foundry_errors import raise_for_storage_error
from azure.ai.agentserver.responses.store._foundry_provider import FoundryStorageProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream

_PROJECT_ENDPOINT = "https://hosted-isolation-test.foundry.example.com"

# (user id key, platform-minted call id) pairs for the two callers.
_VICTIM = ("user_victim", "call_victim")
_ATTACKER = ("user_attacker", "call_attacker")

_VICTIM_SECRET = "victim-private-input-do-not-leak"


# ── Fake Foundry storage service ─────────────────────────────


class _FakeHttpResponse:
    """Minimal ``HttpResponse`` stand-in understood by the Foundry provider."""

    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self._body = json.dumps(body)

    def text(self, *args: Any, **kwargs: Any) -> str:
        return self._body


def _error_body(message: str) -> dict[str, Any]:
    return {"error": {"message": message, "type": "invalid_request_error", "code": "not_found", "param": None}}


class _FakeFoundryStorage:
    """In-process stand-in for the Foundry storage service.

    Ownership is resolved from ``x-agent-foundry-call-id`` (the only identity
    header the container forwards) and enforced on every read, mirroring the
    service-side ``IsolationContext`` checks.
    """

    def __init__(self, call_id_to_user: dict[str, str]) -> None:
        self._users = dict(call_id_to_user)
        # response_id -> {owner, response, history_item_ids, input_item_ids, output_item_ids}
        self.responses: dict[str, dict[str, Any]] = {}
        # item_id -> {owner, item}
        self.items: dict[str, dict[str, Any]] = {}

    # -- transport entry point --------------------------------

    async def send(self, request: Any) -> _FakeHttpResponse:
        """Route an outbound storage request and return a fake HTTP response.

        :param request: The outbound ``HttpRequest`` built by the provider.
        :type request: ~azure.core.rest.HttpRequest
        :returns: The fake HTTP response for the routed operation.
        :rtype: _FakeHttpResponse
        """
        caller = self._users.get(request.headers.get(FOUNDRY_CALL_ID, ""))
        parsed = urlparse(request.url)
        path = unquote(parsed.path.split("/storage/", 1)[-1]).strip("/")
        query = parse_qs(parsed.query)
        raw_body = getattr(request, "content", None)
        if isinstance(raw_body, (bytes, bytearray)):
            raw_body = raw_body.decode("utf-8")
        body = json.loads(raw_body) if raw_body else {}

        status, payload = self._dispatch(request.method, path, query, body, caller)
        response = _FakeHttpResponse(status, payload)
        # This stands in for the whole of ``_send_storage_request`` (which is
        # replaced wholesale), so the status → exception mapping it performs
        # has to happen here too.
        raise_for_storage_error(response)
        return response

    # -- routing ----------------------------------------------

    def _dispatch(
        self,
        method: str,
        path: str,
        query: dict[str, list[str]],
        body: dict[str, Any],
        caller: str | None,
    ) -> tuple[int, Any]:
        segments = path.split("/")
        if method == "POST" and path == "responses":
            return self._create(body, caller)
        if method == "POST" and path == "items/batch/retrieve":
            return self._batch_retrieve(body, caller)
        if method == "GET" and path == "history/item_ids":
            return self._history_item_ids(query, caller)
        if segments[:1] == ["responses"] and len(segments) == 2:
            if method == "GET":
                return self._read(segments[1], caller)
            if method == "POST":
                return self._update(segments[1], body, caller)
            if method == "DELETE":
                return self._delete(segments[1], caller)
        if method == "GET" and len(segments) == 3 and segments[0] == "responses" and segments[2] == "input_items":
            return self._input_items(segments[1], caller)
        return 404, _error_body(f"unsupported route {method} {path}")

    # -- operations -------------------------------------------

    def _owned(self, response_id: str, caller: str | None) -> dict[str, Any] | None:
        entry = self.responses.get(response_id)
        if entry is None or entry["owner"] != caller:
            return None
        return entry

    def _index_items(self, items: Any, caller: str | None) -> list[str]:
        item_ids: list[str] = []
        for item in items or []:
            item_id = item.get("id") if isinstance(item, dict) else None
            if not isinstance(item_id, str):
                continue
            self.items[item_id] = {"owner": caller, "item": item}
            item_ids.append(item_id)
        return item_ids

    def _create(self, body: dict[str, Any], caller: str | None) -> tuple[int, Any]:
        response = body.get("response") or {}
        response_id = str(response.get("id"))
        if response_id in self.responses:
            return 409, _error_body(f"response '{response_id}' already exists")
        # Defence in depth, matching the service: history references the caller
        # cannot see are dropped rather than trusted from the container.
        history_item_ids = [
            item_id
            for item_id in (body.get("history_item_ids") or [])
            if self.items.get(item_id, {}).get("owner") == caller
        ]
        self.responses[response_id] = {
            "owner": caller,
            "response": response,
            "history_item_ids": history_item_ids,
            "input_item_ids": self._index_items(body.get("input_items"), caller),
            "output_item_ids": self._index_items(response.get("output"), caller),
        }
        return 200, {}

    def _read(self, response_id: str, caller: str | None) -> tuple[int, Any]:
        entry = self._owned(response_id, caller)
        if entry is None:
            return 404, _error_body(f"response '{response_id}' not found")
        return 200, entry["response"]

    def _update(self, response_id: str, body: dict[str, Any], caller: str | None) -> tuple[int, Any]:
        entry = self._owned(response_id, caller)
        if entry is None:
            return 404, _error_body(f"response '{response_id}' not found")
        entry["response"] = body
        entry["output_item_ids"] = self._index_items(body.get("output"), caller)
        return 200, {}

    def _delete(self, response_id: str, caller: str | None) -> tuple[int, Any]:
        entry = self._owned(response_id, caller)
        if entry is None:
            return 404, _error_body(f"response '{response_id}' not found")
        del self.responses[response_id]
        return 200, {}

    def _input_items(self, response_id: str, caller: str | None) -> tuple[int, Any]:
        entry = self._owned(response_id, caller)
        if entry is None:
            return 404, _error_body(f"response '{response_id}' not found")
        item_ids = [*entry["history_item_ids"], *entry["input_item_ids"]]
        return 200, {"data": [self.items[i]["item"] for i in item_ids if i in self.items]}

    def _batch_retrieve(self, body: dict[str, Any], caller: str | None) -> tuple[int, Any]:
        result = []
        for item_id in body.get("item_ids") or []:
            record = self.items.get(item_id)
            result.append(record["item"] if record is not None and record["owner"] == caller else None)
        return 200, result

    def _history_item_ids(self, query: dict[str, list[str]], caller: str | None) -> tuple[int, Any]:
        previous_response_id = query.get("previous_response_id", [None])[0]
        limit = int(query.get("limit", ["100"])[0])
        resolved: list[str] = []
        if previous_response_id is not None:
            entry = self._owned(previous_response_id, caller)
            if entry is None:
                # The chain anchor is invisible to this caller — the whole
                # request fails rather than silently resolving another
                # partition's items.
                return 404, _error_body(f"response '{previous_response_id}' not found")
            resolved = [
                *entry["history_item_ids"],
                *entry["input_item_ids"],
                *entry["output_item_ids"],
            ]
        return 200, (resolved[:limit] if limit > 0 else [])


class _FakeCredential:
    """Async credential stub — the transport is faked, so no token is issued."""

    async def get_token(self, *scopes: str, **kwargs: Any) -> Any:  # pragma: no cover - never called
        raise AssertionError("no token should be requested by the faked transport")

    async def close(self) -> None:
        return None


# ── Fixtures / helpers ───────────────────────────────────────


@pytest.fixture()
def hosted_storage(monkeypatch: pytest.MonkeyPatch) -> _FakeFoundryStorage:
    """Run the host as a hosted container backed by a fake Foundry storage service."""
    storage = _FakeFoundryStorage({_VICTIM[1]: _VICTIM[0], _ATTACKER[1]: _ATTACKER[0]})

    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "1")
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", _PROJECT_ENDPOINT)
    monkeypatch.setattr(azure.identity.aio, "DefaultAzureCredential", _FakeCredential)

    # The in-process TestClient never runs the ASGI lifespan, so no resilient
    # task manager is installed.  Hosted deployments treat that as a platform
    # failure (durability is mandatory) — orthogonal to storage isolation, so
    # the durability gate is neutralized to let the handler run in-process.
    # This only gates the ``TaskManagerNotInitialized`` branch; store selection
    # reads ``AgentConfig.is_hosted`` from the env vars set above, so the host
    # still resolves its provider to FoundryStorageProvider.
    monkeypatch.setattr(_orch, "_is_hosted_environment", lambda: False)

    async def _send(_self: FoundryStorageProvider, request: Any) -> _FakeHttpResponse:
        return await storage.send(request)

    monkeypatch.setattr(FoundryStorageProvider, "_send_storage_request", _send)
    return storage


async def _handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
    """Handler that emits a minimal created → completed lifecycle.

    Emitting ``response.created`` is what drives persistence through the
    provider (and the eager eviction that follows the terminal event), so the
    later ``GET`` reads are served by the hosted storage provider rather than
    by in-process runtime state.
    """

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _build_client() -> TestClient:
    host = ResponsesAgentServerHost()
    host.response_handler(_handler)
    return TestClient(host)


def _headers(identity: tuple[str, str]) -> dict[str, str]:
    return {USER_ID: identity[0], FOUNDRY_CALL_ID: identity[1]}


def _create(
    client: TestClient,
    identity: tuple[str, str],
    *,
    text: str = "hello",
    previous_response_id: str | None = None,
) -> Any:
    payload: dict[str, Any] = {
        "model": "gpt-4o-mini",
        "stream": False,
        "store": True,
        "background": False,
        "input": text,
    }
    if previous_response_id is not None:
        payload["previous_response_id"] = previous_response_id
    return client.post("/responses", json=payload, headers=_headers(identity))


def _create_ok(client: TestClient, identity: tuple[str, str], **kwargs: Any) -> str:
    response = _create(client, identity, **kwargs)
    assert response.status_code == 200, response.text
    response_id = response.json().get("id")
    assert isinstance(response_id, str)
    return response_id


def _input_items(client: TestClient, response_id: str, identity: tuple[str, str]) -> Any:
    return client.get(f"/responses/{response_id}/input_items", headers=_headers(identity))


# ── Tests ────────────────────────────────────────────────────


def test_hosted_environment_resolves_foundry_storage_provider(hosted_storage: _FakeFoundryStorage) -> None:
    """Hosted mode must delegate persistence to the partition-enforcing storage service."""
    host = ResponsesAgentServerHost()
    host.response_handler(_handler)

    assert isinstance(host._endpoint._provider, FoundryStorageProvider)


def test_hosted_same_user_chain_resolves_ancestor_items(hosted_storage: _FakeFoundryStorage) -> None:
    """Positive control: the chain really does surface ancestor items for their owner."""
    client = _build_client()

    first_id = _create_ok(client, _VICTIM, text=_VICTIM_SECRET)
    second_id = _create_ok(client, _VICTIM, text="follow-up", previous_response_id=first_id)

    response = _input_items(client, second_id, _VICTIM)
    assert response.status_code == 200, response.text
    assert _VICTIM_SECRET in response.text


def test_hosted_cross_user_previous_response_id_is_rejected(hosted_storage: _FakeFoundryStorage) -> None:
    """A chain anchored on another user's response must not create a response."""
    client = _build_client()

    victim_id = _create_ok(client, _VICTIM, text=_VICTIM_SECRET)

    response = _create(client, _ATTACKER, text="attacker turn", previous_response_id=victim_id)

    assert response.status_code == 404, response.text
    assert _VICTIM_SECRET not in response.text
    # Nothing was persisted for the attacker, so no ancestor items can be
    # baked into an attacker-owned record.
    assert [entry for entry in hosted_storage.responses.values() if entry["owner"] == _ATTACKER[0]] == []


def test_hosted_cross_user_input_items_read_is_rejected(hosted_storage: _FakeFoundryStorage) -> None:
    """Reading another user's input items directly must stay a 404."""
    client = _build_client()

    victim_id = _create_ok(client, _VICTIM, text=_VICTIM_SECRET)

    owner_view = _input_items(client, victim_id, _VICTIM)
    assert owner_view.status_code == 200, owner_view.text
    assert _VICTIM_SECRET in owner_view.text

    attacker_view = _input_items(client, victim_id, _ATTACKER)
    assert attacker_view.status_code == 404, attacker_view.text
    assert _VICTIM_SECRET not in attacker_view.text


def test_hosted_attacker_own_chain_never_includes_other_users_items(
    hosted_storage: _FakeFoundryStorage,
) -> None:
    """An attacker-owned chain only ever resolves the attacker's own items."""
    client = _build_client()

    victim_id = _create_ok(client, _VICTIM, text=_VICTIM_SECRET)
    attacker_first_id = _create_ok(client, _ATTACKER, text="attacker first")
    attacker_second_id = _create_ok(
        client,
        _ATTACKER,
        text="attacker second",
        previous_response_id=attacker_first_id,
    )

    response = _input_items(client, attacker_second_id, _ATTACKER)
    assert response.status_code == 200, response.text
    assert _VICTIM_SECRET not in response.text
    assert "attacker first" in response.text
    assert "attacker second" in response.text

    # The victim's record is untouched and still owned by the victim.
    assert hosted_storage.responses[victim_id]["owner"] == _VICTIM[0]
