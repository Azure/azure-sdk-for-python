# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Platform HTTP header name constants used across the AgentServer packages.

Defines the HTTP header names used across the AgentServer platform.
These headers form the wire contract between the Foundry platform, agent
containers, and downstream storage services.

**Response headers** (set by the server on every response):

- :data:`REQUEST_ID` — request correlation ID.
- :data:`SERVER_VERSION` — server SDK identity.
- :data:`SESSION_ID` — resolved session ID (when applicable).

**Error response headers** (set on 4xx/5xx responses):

- :data:`ERROR_SOURCE` — classifies error origin (``user``, ``platform``, or ``upstream``).
- :data:`ERROR_DETAIL` — internal diagnostic detail for platform telemetry.

**Request headers** (set by the platform or client):

- :data:`REQUEST_ID` — client-provided correlation ID (echoed back on the response).
- :data:`USER_ID` — platform per-user (global, cross-agent) identity header.
- :data:`FOUNDRY_CALL_ID` — platform per-request opaque call identifier (protocol ``2.0.0``).
- :data:`CLIENT_HEADER_PREFIX` — prefix for pass-through client headers.
- :data:`TRACEPARENT` — W3C Trace Context propagation header.
- :data:`CLIENT_REQUEST_ID` — Azure SDK client correlation header.
"""

from __future__ import annotations

# -- Response/request correlation -------------------------------------------

REQUEST_ID: str = "x-request-id"
"""The ``x-request-id`` header — carries the request correlation ID.

On responses, the server always sets this header
(OTEL trace ID → incoming header → UUID).
On requests, clients may set it to provide their own correlation ID.
"""

SERVER_VERSION: str = "x-platform-server"
"""The ``x-platform-server`` header — identifies the server SDK stack
(hosting version, protocol versions, language, and runtime).
Set on every response by ``_PlatformHeaderMiddleware``.
"""

SESSION_ID: str = "x-agent-session-id"
"""The ``x-agent-session-id`` header — the resolved session ID for the request.
Set on responses by protocol-specific session resolution logic.
"""

# -- Platform identity ------------------------------------------------------

USER_ID: str = "x-agent-user-id"
"""The ``x-agent-user-id`` header — the platform-injected global,
cross-agent partition key for per-user state.

The same user yields the same value regardless of which agent they
interact with.  Use it as the primary partition key for per-user data
(profiles, preferences, OAuth tokens, memory).  Present on protocol
requests (not health probes); absent during local development.
"""

FOUNDRY_CALL_ID: str = "x-agent-foundry-call-id"
"""The ``x-agent-foundry-call-id`` header — the platform-minted opaque
per-request call identifier.

Present only when the agent definition declares container protocol
version ``2.0.0``.  The container **MUST** forward this value on all
outbound calls to Foundry platform services (Storage, Toolboxes/MCP
proxy, A2A) so that 1P services can resolve the server-side-stored
caller context.  The container never parses it.  Absent under protocol
version ``1.0.0`` or local development.
"""

# -- Client pass-through ---------------------------------------------------

CLIENT_HEADER_PREFIX: str = "x-client-"
"""The prefix ``x-client-`` for pass-through client headers.

All request headers starting with this prefix are extracted and forwarded
to the handler via the invocation context.
"""

# -- Tracing & diagnostics -------------------------------------------------

TRACEPARENT: str = "traceparent"
"""The ``traceparent`` header — W3C Trace Context propagation header.
Used for distributed tracing correlation on outbound storage requests.
"""

CLIENT_REQUEST_ID: str = "x-ms-client-request-id"
"""The ``x-ms-client-request-id`` header — Azure SDK client correlation header.
Logged for diagnostic correlation with upstream Azure SDK callers.
"""

APIM_REQUEST_ID: str = "apim-request-id"
"""The ``apim-request-id`` header — APIM gateway correlation header.
Extracted from Foundry storage responses for diagnostic logging.
"""

# -- Error source classification --------------------------------------------

ERROR_SOURCE: str = "x-platform-error-source"
"""The ``x-platform-error-source`` header — classifies every error response
so the platform can route actionable errors to the right team.
Present on all 4xx/5xx responses from protocol endpoints.
Values: ``user``, ``platform``, ``upstream``.
"""

ERROR_DETAIL: str = "x-platform-error-detail"
"""The ``x-platform-error-detail`` header — internal diagnostic detail
for platform telemetry.  Not intended for end-user display.
Present on error responses when additional diagnostic context is available.
"""

# -- Error tagging ----------------------------------------------------------

PLATFORM_ERROR_TAG: str = "Azure.AI.AgentServer.PlatformError"
"""Dynamic attribute name set on exceptions to mark them as platform
infrastructure errors (as opposed to user or upstream errors).  Used by
the error source classification logic in the protocol packages.
"""

MAX_ERROR_DETAIL_LENGTH: int = 2048
"""Maximum character length for the ``x-platform-error-detail`` header value.
Values longer than this are truncated with a ``...[truncated]`` suffix.
"""
