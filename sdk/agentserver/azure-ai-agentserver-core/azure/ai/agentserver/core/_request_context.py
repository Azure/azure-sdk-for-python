# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Request-scoped platform context for AgentServer containers.

On container protocol version ``2.0.0`` the platform delivers a per-request
opaque call identifier (``x-agent-foundry-call-id``) plus a global per-user
identity header (``x-agent-user-id``).  The container **MUST** forward these on
all outbound calls to Foundry platform services (Storage, Toolboxes/MCP proxy,
A2A) routed through ``FOUNDRY_PROJECT_ENDPOINT``.

This module stores those values in a :class:`~contextvars.ContextVar` so that
they are available to any code running during request processing — including
handler code making raw ``httpx`` calls and the SDK's own HTTP pipeline — without
threading them through every call signature.

Inbound protocol endpoints populate the context via :func:`set_request_context`
(internal); handler/tool code reads it via :func:`get_request_context` (public),
mirroring the hero samples in the container protocol spec::

    from azure.ai.agentserver.core import get_request_context

    ctx = get_request_context()
    headers = {"x-agent-foundry-call-id": ctx.call_id} if ctx.call_id else {}
"""

from __future__ import annotations

from contextvars import ContextVar, Token

from ._platform_headers import FOUNDRY_CALL_ID

__all__ = [
    "FoundryAgentRequestContext",
    "get_request_context",
    "set_request_context",
    "reset_request_context",
]


class FoundryAgentRequestContext:
    """Platform-supplied, request-scoped identity context.

    Populated by the protocol endpoint from inbound platform headers on every
    request.  All fields are ``None`` when the corresponding header was absent
    (e.g. local development, or ``call_id`` under protocol version ``1.0.0``).

    :ivar call_id: Opaque per-request call identifier from ``x-agent-foundry-call-id``
        (protocol version ``2.0.0`` only).  Forward verbatim on outbound Foundry
        calls; never parse it.
    :vartype call_id: str | None
    :ivar user_id: Global, cross-agent per-user identity from ``x-agent-user-id``.
    :vartype user_id: str | None
    :ivar session_id: The resolved session ID for the request, when available.
    :vartype session_id: str | None
    """

    __slots__ = ("call_id", "user_id", "session_id")

    def __init__(
        self,
        *,
        call_id: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        self.call_id = call_id
        self.user_id = user_id
        self.session_id = session_id

    def platform_headers(self) -> dict[str, str]:
        """Build the platform identity headers to forward on outbound 1P calls.

        Only ``x-agent-foundry-call-id`` is forwarded: 1P services resolve the
        caller context server-side from the opaque call ID. ``x-agent-user-id``
        is **not** forwarded — it is not accepted/trusted by 1P services and is
        only consumed container-side for per-user state partitioning. The call ID
        is included only when present (non-``None``). The managed-identity
        ``Authorization`` header is unaffected — this is an **additional** header
        for caller-identity context.

        :return: A mapping of header name to value, suitable for merging into an
            outbound request's headers.
        :rtype: dict[str, str]
        """
        headers: dict[str, str] = {}
        if self.call_id is not None:
            headers[FOUNDRY_CALL_ID] = self.call_id
        return headers


_EMPTY = FoundryAgentRequestContext()

_request_context_var: ContextVar[FoundryAgentRequestContext] = ContextVar("agentserver_request_context")


def get_request_context() -> FoundryAgentRequestContext:
    """Return the platform context for the current request.

    Safe to call from anywhere during request processing.  When no context has
    been established (e.g. outside a request, or local development), an empty
    :class:`FoundryAgentRequestContext` with all-``None`` fields is returned.

    :return: The current request-scoped platform context.
    :rtype: FoundryAgentRequestContext
    """
    return _request_context_var.get(_EMPTY)


def set_request_context(context: FoundryAgentRequestContext) -> Token[FoundryAgentRequestContext]:
    """Bind ``context`` as the current request context (internal).

    Called by protocol endpoints at the start of request handling.  The returned
    token should be passed to :func:`reset_request_context` when the request
    completes to avoid leaking context across requests on the same task.

    :param context: The request context to bind.
    :type context: FoundryAgentRequestContext
    :return: A reset token for restoring the previous value.
    :rtype: ~contextvars.Token
    """
    return _request_context_var.set(context)


def reset_request_context(token: Token[FoundryAgentRequestContext]) -> None:
    """Restore the request context to its previous value (internal).

    :param token: The token returned by :func:`set_request_context`.
    :type token: ~contextvars.Token
    """
    _request_context_var.reset(token)
