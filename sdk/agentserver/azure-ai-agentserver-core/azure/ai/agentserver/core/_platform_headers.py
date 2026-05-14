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
- :data:`USER_ISOLATION_KEY` / :data:`CHAT_ISOLATION_KEY` — platform isolation keys.
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

# -- Platform isolation -----------------------------------------------------

USER_ISOLATION_KEY: str = "x-agent-user-isolation-key"
"""The ``x-agent-user-isolation-key`` header — the platform-injected
partition key for user-private state.
"""

CHAT_ISOLATION_KEY: str = "x-agent-chat-isolation-key"
"""The ``x-agent-chat-isolation-key`` header — the platform-injected
partition key for conversation-scoped state.
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
