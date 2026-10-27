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
from dataclasses import dataclass
import re
from typing import Mapping
from urllib.parse import quote, unquote

from ._experimental import experimental
from ._platform_headers import FOUNDRY_CALL_ID

__all__ = [
    "FoundryOriginalSubject",
    "FoundryAgentRequestContext",
    "get_request_context",
    "set_request_context",
    "reset_request_context",
]

# Draft RFC 9651 dictionary profile: only these string members, without parameters.
_ORIGINAL_SUBJECT_HEADER = "x-ms-original-subject"
_FOUNDRY_BAGGAGE_HEADER = "x-ms-foundry-baggage"
_ORIGINAL_SUBJECT_BAGGAGE = "foundry.original_subject"
_MAX_ORIGINAL_SUBJECT_LENGTH = 256
_MAX_FOUNDRY_BAGGAGE_LENGTH = 1024
_ORIGINAL_SUBJECT_MEMBER = re.compile(r'(oid|tid|idtype)="((?:[\x20-\x21\x23-\x5b\x5d-\x7e]|\\["\\])*)"')


@experimental
@dataclass(frozen=True, repr=False)
class FoundryOriginalSubject:
    """Invocation-local original-subject assertions, separate from model authentication.

    These values are not proof of identity. The receiving model service must
    establish provenance and invocation binding before using them. This draft
    does not change model authorization or enable budget enforcement.

    :ivar oid: Original subject object ID, not the agent or session owner's ID.
    :vartype oid: str | None
    :ivar tid: Original subject tenant ID.
    :vartype tid: str | None
    :ivar idtype: Original subject classification, preserved without inference.
    :vartype idtype: str | None
    """

    oid: str | None = None
    tid: str | None = None
    idtype: str | None = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> FoundryOriginalSubject | None:
        """Snapshot the proposed platform dictionary without interpreting user-state IDs.

        Absent headers, omitted keys, and empty string values remain distinct.
        Only oid/tid/idtype string members are accepted, in any order. Duplicate
        fields/keys, unknown members, parameters, and malformed syntax raise.

        :param headers: Case-insensitive inbound HTTP headers.
        :type headers: Mapping[str, str]
        :return: Subject assertions, or ``None`` if the header is absent.
        :rtype: FoundryOriginalSubject or None
        :raises ValueError: The header does not match the draft dictionary profile.
        """
        fields = [value for name, value in headers.items() if name.lower() == _ORIGINAL_SUBJECT_HEADER]
        if not fields:
            return None
        if len(fields) != 1:
            raise ValueError("Original-subject attribution requires a single header field.")

        remaining = fields[0].strip(" \t")
        values: dict[str, str] = {}
        while remaining:
            member = _ORIGINAL_SUBJECT_MEMBER.match(remaining)
            if member is None or member[1] in values:
                raise ValueError("Original-subject attribution requires unique oid/tid/idtype string members.")
            values[member[1]] = re.sub(r'\\(["\\])', r"\1", member[2])
            remaining = remaining[member.end() :].lstrip(" \t")
            if not remaining:
                break
            if not remaining.startswith(",") or not remaining[1:].strip(" \t"):
                raise ValueError("Original-subject attribution requires comma-separated dictionary members.")
            remaining = remaining[1:].lstrip(" \t")
        if not values:
            raise ValueError("Original-subject attribution requires a nonempty dictionary.")
        return cls(oid=values.get("oid"), tid=values.get("tid"), idtype=values.get("idtype"))


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
    :ivar original_subject: Optional invocation-local attribution assertions.
    :vartype original_subject: FoundryOriginalSubject | None
    """

    __slots__ = ("call_id", "user_id", "session_id", "original_subject")

    def __init__(
        self,
        *,
        call_id: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        original_subject: FoundryOriginalSubject | None = None,
    ) -> None:
        self.call_id = call_id
        self.user_id = user_id
        self.session_id = session_id
        self.original_subject = original_subject

    @experimental
    def model_attribution_headers(self, headers: Mapping[str, str] | None = None) -> dict[str, str]:
        """Build draft headers for an explicitly supported model integration.

        Pass the result as per-call headers, never shared client defaults. Only
        use this for a model endpoint whose owner has enabled this contract.
        Do not send these assertions to external/BYO endpoints, storage, tools,
        or arbitrary URLs. No client is patched automatically.

        Existing headers and unrelated baggage are copied, not mutated. Reserved
        subject assertions are replaced case-insensitively, or removed when the
        invocation has no subject. The full quoted dictionary is emitted only
        in one baggage member, percent-encoded once. Standalone subject headers
        are inbound platform metadata and are not forwarded to the model.

        Partial, empty, HTTP-unsafe, or oversized tuples raise instead of silently
        becoming an unattributed model call. The quoted tuple is limited to 256
        characters and merged baggage to 1024 when a subject is supplied. Values,
        including non-user/unknown classifications, are not normalized here.
        Durable restore and detached work have no attribution support in this draft.

        :param headers: Optional existing per-call headers, including Foundry baggage.
        :type headers: Mapping[str, str] or None
        :return: A fresh per-call header mapping; model credentials are unchanged.
        :rtype: dict[str, str]
        :raises ValueError: The supplied tuple is incomplete, HTTP-unsafe, or
            exceeds the subject or merged baggage transport limit.
        """
        result: dict[str, str] = {}
        baggage: list[str] = []
        for name, value in (headers or {}).items():
            lowered = name.lower()
            if lowered == _FOUNDRY_BAGGAGE_HEADER:
                for member in value.split(","):
                    member = member.strip()
                    key = unquote(member.split(";", 1)[0].split("=", 1)[0].strip()).lower()
                    if (
                        not member
                        or key == _ORIGINAL_SUBJECT_BAGGAGE
                        or key.startswith(_ORIGINAL_SUBJECT_BAGGAGE + ".")
                    ):
                        continue
                    baggage.append(member)
            elif (
                lowered != _ORIGINAL_SUBJECT_HEADER
                and not lowered.startswith(_ORIGINAL_SUBJECT_HEADER + "-")
                and lowered != FOUNDRY_CALL_ID
            ):
                result[name] = value
        subject = self.original_subject
        if subject is None:
            if baggage:
                result[_FOUNDRY_BAGGAGE_HEADER] = ",".join(baggage)
            return result
        members = []
        for name, value in (("oid", subject.oid), ("tid", subject.tid), ("idtype", subject.idtype)):
            if not value or any(character < "!" or character > "~" for character in value):
                raise ValueError("Original-subject attribution requires a complete, HTTP-safe tuple.")
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            members.append(f'{name}="{escaped}"')
        value = ", ".join(members)
        if len(value) > _MAX_ORIGINAL_SUBJECT_LENGTH:
            raise ValueError("Original-subject attribution requires a quoted tuple of at most 256 characters.")
        # Reserve attribution space before unrelated members can expand during normalization.
        baggage.insert(0, f"{_ORIGINAL_SUBJECT_BAGGAGE}={quote(value, safe='')}")
        merged_baggage = ",".join(baggage)
        if len(merged_baggage) > _MAX_FOUNDRY_BAGGAGE_LENGTH:
            raise ValueError("Original-subject attribution requires merged baggage of at most 1024 characters.")
        result[_FOUNDRY_BAGGAGE_HEADER] = merged_baggage
        if self.call_id is not None:
            result[FOUNDRY_CALL_ID] = self.call_id
        return result

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
