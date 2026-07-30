# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Typed resilient-recovery boundary for the responses resilience surface.

This module models the **single** thing that crosses the cross-process crash
boundary as resilient-task input: :class:`ResilientResponseInput`. It is the typed,
fail-closed boundary for the resilient-task input (Spec 033 §3.1).

Design invariants (Spec 033 §3.1 / FR-001..004):

* **One producer / one consumer.** :meth:`ResilientResponseInput.to_task_input` is
  the only serializer of the resilient-task input; :meth:`from_task_input` is the
  only deserializer. The persisted field set cannot drift between write and read.
* **Input embedded once.** The full ``CreateResponse`` request is persisted once
  (it carries ``.input``); there is no separate ``input_items`` copy — input is
  re-derived from ``request.input`` on recovery exactly as at fresh entry.
* **Fail-closed.** Every field is a declared JSON-serializable value;
  :meth:`to_task_input` asserts JSON-safety and carries no runtime object
  reference. Process-local references live in the separate :class:`RuntimeRefs`
  cache and are **never** serialized — so the persisted boundary physically
  cannot hold a non-serializable ref.
* **One platform-context derivation.** :meth:`platform_context` is the single source.

The handler-facing request metadata ``client_headers`` / ``query_parameters`` are
persisted here so a recovered handler observes the *identical* request metadata it
would on fresh entry (Spec 033 FR-002b — fixes the prior drop-to-``{}`` bug).
"""

from __future__ import annotations

import json
from typing import Any, cast

from ..models._generated import CreateResponse
from .._response_context import PlatformContext


# Keys emitted by :meth:`ResilientResponseInput.to_task_input` / consumed by
# :meth:`from_task_input`. Kept as named constants so the single producer and
# single consumer reference the exact same wire keys.
_K_REQUEST = "request"
_K_RESPONSE_ID = "response_id"
_K_DISPOSITION = "disposition"
_K_AGENT_REFERENCE = "agent_reference"
_K_AGENT_SESSION_ID = "agent_session_id"
_K_USER_ID_KEY = "user_id_key"
_K_CALL_ID = "call_id"
_K_CLIENT_HEADERS = "client_headers"
_K_QUERY_PARAMETERS = "query_parameters"


def platform_context_from_params(params: dict[str, Any]) -> PlatformContext:
    """Build the platform context from a persisted resilient-task input dict.

    The single platform-context derivation site (Spec 033 FR-003 / protocol
    ``2.0.0``): every recovery reader — full reconstruction and the mark-failed
    path — routes through this one function (directly, or via
    :meth:`ResilientResponseInput.platform_context`) so the partition identity
    cannot be derived inconsistently.

    Both the ``user_id_key`` and the ``call_id`` are captured on the originating
    ``CreateResponse`` call and persisted here because crash-recovery re-invokes
    the handler with no inbound request — there is no fresh ``call_id`` to source,
    so the persisted create-time value is replayed for the recovered process's
    storage operations (the storage service retains the originating call record
    for a started response, so it still resolves). This replay is specific to the
    recovery path; request-driven operations forward the current request's
    ``call_id``. ``user_id`` is the stable, deterministically-hashed end-user
    identity that anchors the ``(user_id, agentGuid)`` storage partition; ``call_id``
    is a per-request identity handle that resolves to it. They are persisted as
    durable task input so recovery can reconstruct the caller context.

    :param params: The persisted resilient-task input dict.
    :type params: dict[str, Any]
    :returns: The platform context.
    :rtype: PlatformContext
    """
    return PlatformContext(
        user_id_key=params.get(_K_USER_ID_KEY),
        call_id=params.get(_K_CALL_ID),
    )


def _normalize_agent_reference(agent_reference: Any) -> dict[str, Any]:
    """Normalize an ``AgentReference`` (or mapping) to a plain JSON-safe dict.

    The hosted gateway injects ``agent_reference`` as an ``AgentReference`` model,
    which is a Mapping but is NOT ``json.dumps``-serializable. Normalizing it to a
    plain dict here is what keeps the typed resilient input fail-closed (the prior
    code special-cased this at the strip site after the ``AgentReference``
    ``TypeError`` recovery bug).

    :param agent_reference: An ``AgentReference`` model, a mapping, or ``None``.
    :type agent_reference: Any
    :returns: A JSON-safe dict (``{}`` when absent).
    :rtype: dict[str, Any]
    """
    if agent_reference is None:
        return {}
    if isinstance(agent_reference, dict):
        return dict(agent_reference)
    as_dict = getattr(agent_reference, "as_dict", None)
    if callable(as_dict):
        return cast("dict[str, Any]", as_dict())
    try:
        return dict(agent_reference)
    except (TypeError, ValueError):
        return {
            "type": getattr(agent_reference, "type", "agent_reference"),
            "name": getattr(agent_reference, "name", None),
            "version": getattr(agent_reference, "version", None),
        }


def _serialize_request(request: Any) -> Any:
    """Serialize the ``CreateResponse`` request to a JSON-safe representation.

    :param request: The ``CreateResponse`` model (or an already-serialized dict).
    :type request: Any
    :returns: A JSON-safe representation.
    :rtype: Any
    """
    if request is None:
        return None
    if isinstance(request, dict):
        return dict(request)
    if hasattr(request, "as_dict") and callable(request.as_dict):
        return request.as_dict()
    return request


class RuntimeRefs:
    """Process-local object references for an in-flight resilient response.

    These cannot be JSON-serialized for cross-process recovery, so they are kept
    in a process-local cache keyed by ``response_id`` and are **never** part of
    :class:`ResilientResponseInput`. On same-process re-entry the task body reads
    them from the cache; on cross-process recovery the cache entry is absent and
    the body rebuilds state from the persisted :class:`ResilientResponseInput`.
    """

    def __init__(
        self,
        *,
        record: Any = None,
        context: Any = None,
        parsed: Any = None,
        cancel: Any = None,
        runtime_state: Any = None,
    ) -> None:
        self.record = record
        self.context = context
        self.parsed = parsed
        self.cancel = cancel
        self.runtime_state = runtime_state


class ResilientResponseInput:
    """The ONLY value persisted as resilient-task input for a response.

    Typed + fail-closed: every field is a declared, JSON-serializable value; no
    runtime references. See the module docstring for the design invariants.
    """

    def __init__(
        self,
        *,
        request: CreateResponse,
        response_id: str,
        disposition: str,
        agent_reference: Any = None,
        agent_session_id: str | None = None,
        user_id_key: str | None = None,
        call_id: str | None = None,
        client_headers: dict[str, str] | None = None,
        query_parameters: dict[str, str] | None = None,
    ) -> None:
        self.request = request
        self.response_id = response_id
        self.disposition = disposition
        # Normalized to a plain dict at construction so the object is always
        # serialization-safe (no leaked ``AgentReference`` model).
        self.agent_reference: dict[str, Any] = _normalize_agent_reference(agent_reference)
        self.agent_session_id = agent_session_id
        self.user_id_key = user_id_key
        self.call_id = call_id
        self.client_headers: dict[str, str] = dict(client_headers or {})
        self.query_parameters: dict[str, str] = dict(query_parameters or {})

    def platform_context(self) -> PlatformContext:
        """Return the platform context — the single derivation site.

        :returns: The platform context built from the persisted ``user_id_key``
            and ``call_id`` — the identity pair captured at response creation and
            replayed for every storage operation over the response's lifetime.
        :rtype: PlatformContext
        """
        return PlatformContext(
            user_id_key=self.user_id_key,
            call_id=self.call_id,
        )

    def to_task_input(self) -> dict[str, Any]:
        """Serialize to the resilient-task input dict — the single producer.

        Asserts JSON-safety + ref-freeness: a non-serializable field raises
        ``TypeError`` here rather than silently leaking into the task store.

        :returns: A JSON-serializable dict suitable for the resilient-task input.
        :rtype: dict[str, Any]
        :raises TypeError: If any field is not JSON-serializable.
        """
        params: dict[str, Any] = {
            _K_RESPONSE_ID: self.response_id,
            _K_DISPOSITION: self.disposition,
            _K_REQUEST: _serialize_request(self.request),
            _K_AGENT_REFERENCE: _normalize_agent_reference(self.agent_reference),
            _K_AGENT_SESSION_ID: self.agent_session_id,
            _K_USER_ID_KEY: self.user_id_key,
            _K_CALL_ID: self.call_id,
            _K_CLIENT_HEADERS: dict(self.client_headers),
            _K_QUERY_PARAMETERS: dict(self.query_parameters),
        }
        # Fail-closed guard: prove the boundary is JSON-serializable and ref-free.
        json.dumps(params)
        return params

    @classmethod
    def from_task_input(cls, params: dict[str, Any]) -> "ResilientResponseInput":
        """Deserialize a resilient-task input dict — the single consumer.

        Fail-closed: a missing required field (``response_id`` or ``request``)
        raises ``ValueError`` so the recovery path can abandon/mark-failed
        deterministically rather than re-invoking with partial input.

        :param params: The persisted resilient-task input dict.
        :type params: dict[str, Any]
        :returns: The typed resilient response input.
        :rtype: ResilientResponseInput
        :raises ValueError: If a required field is missing or malformed.
        """
        if not isinstance(params, dict):
            raise ValueError("ResilientResponseInput.from_task_input requires a dict")

        response_id = params.get(_K_RESPONSE_ID)
        if not response_id or not isinstance(response_id, str):
            raise ValueError("ResilientResponseInput missing required 'response_id'")

        raw_request = params.get(_K_REQUEST)
        if raw_request is None:
            raise ValueError("ResilientResponseInput missing required 'request'")
        request = cast(CreateResponse, raw_request) if isinstance(raw_request, dict) else raw_request

        return cls(
            request=request,
            response_id=response_id,
            disposition=params.get(_K_DISPOSITION) or "re-invoke",
            agent_reference=params.get(_K_AGENT_REFERENCE),
            agent_session_id=params.get(_K_AGENT_SESSION_ID),
            user_id_key=params.get(_K_USER_ID_KEY),
            call_id=params.get(_K_CALL_ID),
            client_headers=params.get(_K_CLIENT_HEADERS),
            query_parameters=params.get(_K_QUERY_PARAMETERS),
        )
