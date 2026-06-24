# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Typed durable-recovery boundary for the responses durability surface.

This module models the **single** thing that crosses the cross-process crash
boundary as durable-task input: :class:`DurableResponseInput`. It is the typed,
fail-closed replacement for the previous hand-synced ``ctx_params`` dict +
``_split_runtime_refs`` strip-allowlist (Spec 033 §3.1).

Design invariants (Spec 033 §3.1 / FR-001..004):

* **One producer / one consumer.** :meth:`DurableResponseInput.to_task_input` is
  the only serializer of the durable-task input; :meth:`from_task_input` is the
  only deserializer. The persisted field set cannot drift between write and read.
* **Input embedded once.** The full ``CreateResponse`` request is persisted once
  (it carries ``.input``); there is no separate ``input_items`` copy — input is
  re-derived from ``request.input`` on recovery exactly as at fresh entry.
* **Fail-closed.** Every field is a declared JSON-serializable value;
  :meth:`to_task_input` asserts JSON-safety and carries no runtime object
  reference. Process-local references live in the separate :class:`RuntimeRefs`
  cache and are **never** serialized — so the persisted boundary physically
  cannot hold a non-serializable ref.
* **One isolation derivation.** :meth:`isolation` is the single source.

The handler-facing request metadata ``client_headers`` / ``query_parameters`` are
persisted here so a recovered handler observes the *identical* request metadata it
would on fresh entry (Spec 033 FR-002b — fixes the prior drop-to-``{}`` bug).
"""

from __future__ import annotations

import json
from typing import Any

from ..models._generated import CreateResponse
from .._response_context import IsolationContext


# Keys emitted by :meth:`DurableResponseInput.to_task_input` / consumed by
# :meth:`from_task_input`. Kept as named constants so the single producer and
# single consumer reference the exact same wire keys.
_K_REQUEST = "request"
_K_RESPONSE_ID = "response_id"
_K_DISPOSITION = "disposition"
_K_AGENT_REFERENCE = "agent_reference"
_K_AGENT_SESSION_ID = "agent_session_id"
_K_USER_ISOLATION_KEY = "user_isolation_key"
_K_CHAT_ISOLATION_KEY = "chat_isolation_key"
_K_CLIENT_HEADERS = "client_headers"
_K_QUERY_PARAMETERS = "query_parameters"


def isolation_from_params(params: dict[str, Any]) -> IsolationContext:
    """Build the isolation context from a persisted durable-task input dict.

    The single isolation derivation site (Spec 033 FR-003): every recovery
    reader — full reconstruction and the mark-failed path — routes through this
    one function (directly, or via :meth:`DurableResponseInput.isolation`) so the
    partition keys cannot be derived inconsistently.

    :param params: The persisted durable-task input dict.
    :type params: dict[str, Any]
    :returns: The isolation context.
    :rtype: IsolationContext
    """
    return IsolationContext(
        user_key=params.get(_K_USER_ISOLATION_KEY),
        chat_key=params.get(_K_CHAT_ISOLATION_KEY),
    )


def _normalize_agent_reference(agent_reference: Any) -> dict[str, Any]:
    """Normalize an ``AgentReference`` (or mapping) to a plain JSON-safe dict.

    The hosted gateway injects ``agent_reference`` as an ``AgentReference`` model,
    which is a Mapping but is NOT ``json.dumps``-serializable. Normalizing it to a
    plain dict here is what keeps the typed durable input fail-closed (the prior
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
    if hasattr(agent_reference, "as_dict") and callable(agent_reference.as_dict):
        return agent_reference.as_dict()
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
    """Process-local object references for an in-flight durable response.

    These cannot be JSON-serialized for cross-process recovery, so they are kept
    in a process-local cache keyed by ``response_id`` and are **never** part of
    :class:`DurableResponseInput`. On same-process re-entry the task body reads
    them from the cache; on cross-process recovery the cache entry is absent and
    the body rebuilds state from the persisted :class:`DurableResponseInput`.
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


class DurableResponseInput:
    """The ONLY value persisted as durable-task input for a response.

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
        user_isolation_key: str | None = None,
        chat_isolation_key: str | None = None,
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
        self.user_isolation_key = user_isolation_key
        self.chat_isolation_key = chat_isolation_key
        self.client_headers: dict[str, str] = dict(client_headers or {})
        self.query_parameters: dict[str, str] = dict(query_parameters or {})

    def isolation(self) -> IsolationContext:
        """Return the isolation context — the single derivation site.

        :returns: The isolation context built from the persisted isolation keys.
        :rtype: IsolationContext
        """
        return IsolationContext(
            user_key=self.user_isolation_key,
            chat_key=self.chat_isolation_key,
        )

    def to_task_input(self) -> dict[str, Any]:
        """Serialize to the durable-task input dict — the single producer.

        Asserts JSON-safety + ref-freeness: a non-serializable field raises
        ``TypeError`` here rather than silently leaking into the durable store.

        :returns: A JSON-serializable dict suitable for the durable-task input.
        :rtype: dict[str, Any]
        :raises TypeError: If any field is not JSON-serializable.
        """
        params: dict[str, Any] = {
            _K_RESPONSE_ID: self.response_id,
            _K_DISPOSITION: self.disposition,
            _K_REQUEST: _serialize_request(self.request),
            _K_AGENT_REFERENCE: _normalize_agent_reference(self.agent_reference),
            _K_AGENT_SESSION_ID: self.agent_session_id,
            _K_USER_ISOLATION_KEY: self.user_isolation_key,
            _K_CHAT_ISOLATION_KEY: self.chat_isolation_key,
            _K_CLIENT_HEADERS: dict(self.client_headers),
            _K_QUERY_PARAMETERS: dict(self.query_parameters),
        }
        # Fail-closed guard: prove the boundary is JSON-serializable and ref-free.
        json.dumps(params)
        return params

    @classmethod
    def from_task_input(cls, params: dict[str, Any]) -> "DurableResponseInput":
        """Deserialize a durable-task input dict — the single consumer.

        Fail-closed: a missing required field (``response_id`` or ``request``)
        raises ``ValueError`` so the recovery path can abandon/mark-failed
        deterministically rather than re-invoking with partial input.

        :param params: The persisted durable-task input dict.
        :type params: dict[str, Any]
        :returns: The typed durable response input.
        :rtype: DurableResponseInput
        :raises ValueError: If a required field is missing or malformed.
        """
        if not isinstance(params, dict):
            raise ValueError("DurableResponseInput.from_task_input requires a dict")

        response_id = params.get(_K_RESPONSE_ID)
        if not response_id or not isinstance(response_id, str):
            raise ValueError("DurableResponseInput missing required 'response_id'")

        raw_request = params.get(_K_REQUEST)
        if raw_request is None:
            raise ValueError("DurableResponseInput missing required 'request'")
        request = CreateResponse(raw_request) if isinstance(raw_request, dict) else raw_request

        return cls(
            request=request,
            response_id=response_id,
            disposition=params.get(_K_DISPOSITION) or "re-invoke",
            agent_reference=params.get(_K_AGENT_REFERENCE),
            agent_session_id=params.get(_K_AGENT_SESSION_ID),
            user_isolation_key=params.get(_K_USER_ISOLATION_KEY),
            chat_isolation_key=params.get(_K_CHAT_ISOLATION_KEY),
            client_headers=params.get(_K_CLIENT_HEADERS),
            query_parameters=params.get(_K_QUERY_PARAMETERS),
        )
