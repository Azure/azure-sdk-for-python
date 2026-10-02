# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared test fixtures for the resilient-task test suite.

Per  (Resilient-task primitive contract hardening), this module
hosts two reusable fixtures:

1. **``binding_mismatch_provider``** — a :class:`TaskProvider`-conforming
   stub that wraps an in-memory delegate and selectively raises a
   ``TransportClassifiedError(classification="evicted")`` on configured
   write operations (the same exception type the real
:class:`HostedTaskProvider` would raise after the  classifier
   maps an HTTP 409 / ``{"error": {"code": "binding_mismatch"}}``
   response). Used by ``test_split_brain_eviction.py``  and the
   SC-006 ``(scheduling primitive × steerable × lease state)``
   parametrized sweep cells. The unified exception type lets the
   framework's local-cleanup sequence run identically against the stub
   and the real hosted client without monkey-patching.

   Reference: spec.md §Conformance Test Map row 13.

2. **``fake_async_transport``** — a :class:`AsyncHttpTransport`-compatible
   fake that supports canned response sequences, captures sent
   requests for inspection, and provides a gzip-encoding helper for
   round-trip body tests. Used by ``test_hosted_provider_transport.py``
    to verify the ``azure.core.AsyncPipelineClient`` policy chain
   behavior end-to-end without a network.

   Reference: spec.md §Conformance Test Map row 14.

Both fixtures are documented inline at point of use; their public
signatures are stable for the duration of  implementation.
"""
from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import pytest

from azure.ai.agentserver.core.tasks._client import TransportClassifiedError


# --------------------------------------------------------------------- #
# Fixture 1 — binding_mismatch provider stub (/ SC-002 / SC-006)
# --------------------------------------------------------------------- #


@dataclass
class _BindingMismatchRejection(Exception):
    """Sentinel exception the stub raises in place of a real HTTP 409.

    Attributes mirror what the  classifier would extract from the
    real HTTP response:

    - ``status_code``: always 409 for this rejection.
    - ``error_code``: always ``"binding_mismatch"`` (the canonical
      orphan-sandbox protocol code).
    - ``message``: human-readable.

    The wrapping ``TaskProvider`` re-raises this from the targeted
    write op, allowing tests to assert framework behavior end-to-end
    through the classifier seam without any HTTP mocking.
    """

    status_code: int = 409
    error_code: str = "binding_mismatch"
    message: str = "Sandbox is no longer the authoritative owner of this task."

    def to_body(self) -> dict[str, Any]:
        """Render the canonical task-store error envelope."""
        return {"error": {"code": self.error_code, "message": self.message}}


class BindingMismatchProvider:
    """``TaskProvider``-conforming stub that selectively raises eviction.

    Wraps a real delegate provider (typically an in-memory or
    :class:`LocalFileTaskProvider` instance) and forwards every call
    through — except for write operations whose ``task_id`` (or the
    sentinel ``"*"`` for all tasks) appears in the configured set for
    that operation kind. Those raise :class:`_BindingMismatchRejection`.

    Configuration is per-operation-kind so a test can exercise, e.g.,
    "lease-renewal PATCH rejected with binding_mismatch but inline
    reclaim succeeds":

    .. code-block:: python

        stub = BindingMismatchProvider(delegate=local_provider)
        stub.reject_on(\"update\", task_id=\"t-evicted\")  # PATCH only

    Op kinds: ``\"create\"``, ``\"get\"``, ``\"update\"``, ``\"delete\"``,
    ``\"list\"``. Note: ``\"get\"`` and ``\"list\"`` are reads and are NOT
    rejected by the real platform's binding_mismatch path; including
    them is allowed for negative-case tests (the framework must still
    not crash if the platform misbehaves).
    """

    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate
        self._reject: dict[str, set[str]] = {
            "create": set(),
            "get": set(),
            "update": set(),
            "delete": set(),
            "list": set(),
        }

    def reject_on(self, op: str, *, task_id: str = "*") -> None:
        """Configure the stub to raise binding_mismatch on ``op`` for ``task_id``.

        Pass ``task_id=\"*\"`` to reject every call to ``op`` regardless
        of task identity.
        """
        if op not in self._reject:
            raise ValueError(f"unknown op {op!r}; expected one of {sorted(self._reject)}")
        self._reject[op].add(task_id)

    def _maybe_reject(self, op: str, task_id: str) -> None:
        if task_id in self._reject[op] or "*" in self._reject[op]:
            # Raise the SAME typed exception the real HostedTaskProvider
            # would raise after the  classifier maps an HTTP 409 /
            # binding_mismatch response. Using the unified type means the
            # framework's local-cleanup sequence  runs identically
            # against the stub and the real wire path.
            raise TransportClassifiedError(
                status=409,
                classification="evicted",
                message=(
                    f"task-store {op} {task_id}: classified=evicted "
                    f"(binding_mismatch; sandbox is no longer the "
                    f"authoritative owner of this task)"
                ),
                request_id=None,
                body_prefix='{"error":{"code":"binding_mismatch"}}',
            )

    async def create(self, request: Any) -> Any:
        self._maybe_reject("create", getattr(request, "id", ""))
        return await self._delegate.create(request)

    async def get(self, task_id: str) -> Any:
        self._maybe_reject("get", task_id)
        return await self._delegate.get(task_id)

    async def update(self, task_id: str, patch: Any) -> Any:
        self._maybe_reject("update", task_id)
        return await self._delegate.update(task_id, patch)

    async def delete(self, task_id: str, *, force: bool = False, cascade: bool = False) -> None:
        self._maybe_reject("delete", task_id)
        await self._delegate.delete(task_id, force=force, cascade=cascade)

    async def list(self, **kwargs: Any) -> Any:
        # list() has no single task_id; reject only on "*"
        self._maybe_reject("list", "*")
        return await self._delegate.list(**kwargs)


@pytest.fixture
def binding_mismatch_provider_factory() -> Callable[[Any], BindingMismatchProvider]:
    """Factory yielding a :class:`BindingMismatchProvider` wrapping a delegate.

    Test usage:

    .. code-block:: python

        def test_eviction_during_renewal(binding_mismatch_provider_factory, local_provider):
            stub = binding_mismatch_provider_factory(local_provider)
            stub.reject_on(\"update\", task_id=\"t-1\")
            manager = TaskManager(provider=stub, ...)
            ...
    """
    return BindingMismatchProvider


# --------------------------------------------------------------------- #
#  — CapturingProvider for etag CAS / write queue tests
# --------------------------------------------------------------------- #


class CapturingProvider:
    """``TaskProvider``-conforming spy that records every PATCH issued.

    Wraps a delegate provider, forwards all calls, and records each
    ``update()`` call's ``(task_id, patch)`` for assertion. Used by
     Area A tests to verify etag plumbing (``if_match`` carried
    on every PATCH after the first) and to count PATCHes for the
    dynamic-cadence lease-renewal shadow check (, SC-3).

    The spy is transparent: no error injection (use
    :class:`BindingMismatchProvider` for that). Read calls are NOT
    recorded — only writes (``create``, ``update``, ``delete``) so
    tests can assert "write count" without polluting it with reads.
    """

    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate
        self.create_calls: list[Any] = []
        # Each entry: (task_id, patch, if_match)
        self.update_calls: list[tuple[str, Any, str | None]] = []
        self.delete_calls: list[tuple[str, dict[str, Any]]] = []
        self.list_calls: list[dict[str, Any]] = []

    async def create(self, request: Any) -> Any:
        self.create_calls.append(request)
        return await self._delegate.create(request)

    async def get(self, task_id: str) -> Any:
        return await self._delegate.get(task_id)

    async def update(self, task_id: str, patch: Any) -> Any:
        self.update_calls.append((task_id, patch, getattr(patch, "if_match", None)))
        return await self._delegate.update(task_id, patch)

    async def delete(self, task_id: str, *, force: bool = False, cascade: bool = False) -> None:
        self.delete_calls.append((task_id, {"force": force, "cascade": cascade}))
        await self._delegate.delete(task_id, force=force, cascade=cascade)

    async def list(self, **kwargs: Any) -> Any:
        self.list_calls.append(dict(kwargs))
        return await self._delegate.list(**kwargs)


@pytest.fixture
def capturing_provider_factory() -> Callable[[Any], CapturingProvider]:
    """Factory yielding a :class:`CapturingProvider` wrapping a delegate."""
    return CapturingProvider


# --------------------------------------------------------------------- #
#  — Conflicting412Provider for terminal-write three-branch tests
# --------------------------------------------------------------------- #


class Conflicting412Provider:
    """``TaskProvider`` stub that raises ``EtagConflict`` on N updates.

    Wraps a delegate. Each ``update`` call counts up; if the call
    number is in the configured ``conflict_on`` set, the wrapper
    raises ``EtagConflict`` BEFORE delegating. Otherwise the call
    is delegated normally.

    Optionally, before raising the configured conflict, the stub may
    mutate the underlying record (via the delegate) to simulate a
    concurrent cross-process writer landing changes between our
    pre-PATCH read and our PATCH (e.g., another worker reclaiming the
    lease). This is what drives  terminal-write three-branch
    test cases:

    - lease-lost branch: mutate to a different ``lease_instance_id``
      before raising 412; framework's RE-READ shows lease no longer
      ours → ABANDON.
    - already-terminal branch: mutate the status to ``completed``
      before raising; framework's RE-READ shows terminal → ABANDON.
    - retry branch: don't mutate (or mutate something harmless);
      framework's RE-READ shows our lease still active, status
      ``in_progress`` → retry the terminal PATCH against the new etag,
      which then succeeds.
    """

    def __init__(self, delegate: Any) -> None:
        from azure.ai.agentserver.core.tasks._exceptions import EtagConflict

        self._delegate = delegate
        self._EtagConflict = EtagConflict
        self._next_update_index = 0
        # update_index → "lease_lost" | "already_terminal" | "etag_only"
        self._conflicts: dict[int, str] = {}

    def conflict_on(self, *, update_index: int, mode: str) -> None:
        """Configure a conflict at the ``update_index``-th update call.

        :keyword update_index: zero-indexed position of the update call
            (counted across this stub's lifetime).
        :keyword mode: one of ``"lease_lost"`` (mutate to a different
            ``lease_instance_id`` before raising), ``"already_terminal"``
            (mutate ``status="completed"`` before raising), or
            ``"etag_only"`` (don't mutate; just raise — simulates a
            cross-process append whose effect is harmless to re-merge).
        """
        if mode not in {"lease_lost", "already_terminal", "etag_only"}:
            raise ValueError(f"unknown conflict mode: {mode!r}")
        self._conflicts[update_index] = mode

    async def create(self, request: Any) -> Any:
        return await self._delegate.create(request)

    async def get(self, task_id: str) -> Any:
        return await self._delegate.get(task_id)

    async def update(self, task_id: str, patch: Any) -> Any:
        idx = self._next_update_index
        self._next_update_index += 1
        mode = self._conflicts.pop(idx, None)
        if mode is None:
            return await self._delegate.update(task_id, patch)
        # Mutate the underlying record before raising, then 412.
        from azure.ai.agentserver.core.tasks._models import TaskPatchRequest

        if mode == "lease_lost":
            await self._delegate.update(
                task_id,
                TaskPatchRequest(
                    lease_owner=f"other-{idx}",
                    lease_instance_id=f"other-instance-{idx}",
                    lease_duration_seconds=60,
                ),
            )
        elif mode == "already_terminal":
            await self._delegate.update(
                task_id,
                TaskPatchRequest(status="completed"),
            )
        # "etag_only" — make no mutation; just bump the etag by
        # touching tags with a harmless write.
        else:
            await self._delegate.update(
                task_id,
                TaskPatchRequest(tags={"_task_streams_harmless": "x"}),
            )
        raise self._EtagConflict(task_id, message="injected by Conflicting412Provider")

    async def delete(self, task_id: str, *, force: bool = False, cascade: bool = False) -> None:
        await self._delegate.delete(task_id, force=force, cascade=cascade)

    async def list(self, **kwargs: Any) -> Any:
        return await self._delegate.list(**kwargs)


@pytest.fixture
def conflicting_412_provider_factory() -> Callable[[Any], Conflicting412Provider]:
    """Factory yielding a :class:`Conflicting412Provider` wrapping a delegate."""
    return Conflicting412Provider


# --------------------------------------------------------------------- #
# Fixture 2 — fake AsyncHttpTransport (/ SC-016 / SC-017)
# --------------------------------------------------------------------- #


@dataclass
class FakeResponse:
    """Canned response the fake transport returns for one request.

    Construct directly or via the :meth:`json_response` / :meth:`gzip_json_response`
    convenience constructors.
    """

    status_code: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""

    @classmethod
    def json_response(
        cls,
        payload: Any,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "FakeResponse":
        body = json.dumps(payload).encode("utf-8")
        h = dict(headers or {})
        h.setdefault("Content-Type", "application/json")
        h.setdefault("Content-Length", str(len(body)))
        return cls(status_code=status_code, headers=h, body=body)

    @classmethod
    def gzip_json_response(
        cls,
        payload: Any,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "FakeResponse":
        raw = json.dumps(payload).encode("utf-8")
        gz = gzip.compress(raw)
        h = dict(headers or {})
        h["Content-Type"] = "application/json"
        h["Content-Encoding"] = "gzip"
        h["Content-Length"] = str(len(gz))
        return cls(status_code=status_code, headers=h, body=gz)

    @classmethod
    def html_response(cls, body: str, *, status_code: int = 200) -> "FakeResponse":
        b = body.encode("utf-8")
        return cls(
            status_code=status_code,
            headers={"Content-Type": "text/html", "Content-Length": str(len(b))},
            body=b,
        )


@dataclass
class CapturedRequest:
    """Record of a single request the fake transport saw."""

    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


class FakeAsyncHttpTransport:
    """An :class:`azure.core.pipeline.transport.AsyncHttpTransport`-compatible fake.

        Configure with a sequence of :class:`FakeResponse` instances; the
        transport pops one per request. If the sequence is exhausted and
        no fallback is configured, ``IndexError`` is raised — tests
        explicitly assert their expected request count.

        All sent requests are captured in :attr:`requests` (a list of
        :class:`CapturedRequest`) for after-the-fact assertions on headers,
        URLs, and bodies.

        The fake intentionally implements only the surface area the
        :class:`azure.core.pipeline.AsyncPipeline` actually exercises: an
        async ``send`` returning an object with ``http_response`` (and the
        nested ``status_code`` / ``headers`` / ``body`` properties), plus
        ``open()`` / ``close()`` / ``__aenter__`` / ``__aexit__``. The
        consumer pipeline must NOT include ``ContentDecodePolicy`` for the
        gzip-round-trip assertions to mean what we want them to mean (per
    , the policy chain explicitly excludes
        ``ContentDecodePolicy``).
    """

    def __init__(self, responses: Sequence[FakeResponse] = ()) -> None:
        self._responses: list[FakeResponse] = list(responses)
        self.requests: list[CapturedRequest] = []
        self._opened = False
        self._closed = False

    def append_response(self, response: FakeResponse) -> None:
        """Add another canned response to the tail of the queue."""
        self._responses.append(response)

    def extend_responses(self, responses: Sequence[FakeResponse]) -> None:
        """Bulk-add canned responses."""
        self._responses.extend(responses)

    async def __aenter__(self) -> "FakeAsyncHttpTransport":
        await self.open()
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.close()

    async def open(self) -> None:
        self._opened = True

    async def close(self) -> None:
        self._closed = True

    async def send(self, request: Any, **kwargs: Any) -> Any:  # noqa: ARG002
        """Pop the next canned response, recording the sent request.

        Returns an :class:`AsyncHttpResponse`-shaped object (NOT a
        :class:`PipelineResponse` — the surrounding pipeline wraps the
        returned http response into a PipelineResponse on its way back
        through the policy chain).
        """

        if not self._responses:
            raise IndexError(
                f"FakeAsyncHttpTransport: no canned response left for "
                f"{getattr(request, 'method', '?')} {getattr(request, 'url', '?')}. "
                f"Saw {len(self.requests)} request(s) total; the test under-configured "
                f"the response queue or the consumer over-sent."
            )
        response_data = self._responses.pop(0)
        body = getattr(request, "body", None) or getattr(request, "data", None)
        if body is None:
            body = getattr(request, "content", None)
            if callable(body):
                body = body()
        if body is None:
            body = getattr(request, "_data", None) or getattr(request, "_body", None)
        if isinstance(body, str):
            body = body.encode("utf-8")
        if body is not None and not isinstance(body, (bytes, bytearray)):
            try:
                body = bytes(body)
            except Exception:  # noqa: BLE001
                body = None
        self.requests.append(
            CapturedRequest(
                method=getattr(request, "method", ""),
                url=str(getattr(request, "url", "")),
                headers=dict(getattr(request, "headers", {}) or {}),
                body=body,
            )
        )
        # Construct a minimal response-shaped object that
        # azure.core.pipeline.transport expects. We lazy-import to avoid
        # adding hard test-time dependencies until the consumer code
        # itself depends on azure.core.
        from azure.core.pipeline.transport._base_async import AsyncHttpResponse  # type: ignore

        class _FakeResp(AsyncHttpResponse):  # type: ignore[misc]
            def __init__(self_inner) -> None:  # noqa: N805
                super().__init__(request, None)
                self_inner.status_code = response_data.status_code
                self_inner.headers = dict(response_data.headers)
                self_inner.reason = "OK" if response_data.status_code < 400 else "ERR"
                self_inner.content_type = response_data.headers.get("Content-Type", "")
                self_inner._body_bytes = response_data.body  # noqa: SLF001

            def body(self_inner) -> bytes:  # noqa: N805
                return self_inner._body_bytes  # noqa: SLF001

            async def load_body(self_inner) -> None:  # noqa: N805
                return None

            def stream_download(self_inner, pipeline, **_kwargs: Any) -> Any:  # noqa: ARG002, N805
                async def _gen() -> Any:
                    yield self_inner._body_bytes  # noqa: SLF001

                return _gen()

        return _FakeResp()


@pytest.fixture
def fake_async_transport() -> Callable[..., FakeAsyncHttpTransport]:
    """Factory fixture yielding :class:`FakeAsyncHttpTransport` instances.

    Test usage:

    .. code-block:: python

        def test_retry_on_503(fake_async_transport):
            transport = fake_async_transport([
                FakeResponse(status_code=503, headers={}, body=b\"\"),
                FakeResponse.json_response({\"id\": \"t-1\"}, status_code=200),
            ])
            client = HostedTaskProvider(endpoint=\"...\", credential=..., transport=transport)
            ...
            # Assert exactly 2 requests sent for one-retry-success.
            assert len(transport.requests) == 2
    """
    return FakeAsyncHttpTransport
