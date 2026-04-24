# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Platform HTTP header name constants used across the AgentServer packages.

These headers form the wire contract between the Foundry platform, agent
containers, and downstream storage services.  All header name constants
are defined here to eliminate scattered string literals and ensure
consistency across logging policies, middleware, and endpoint handlers.

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

# -- Storage diagnostics (response headers from Foundry) --------------------

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

ERROR_SOURCE_USER: str = "user"
"""Error source value indicating the caller's input is invalid.
The caller can fix the request and retry.
"""

ERROR_SOURCE_PLATFORM: str = "platform"
"""Error source value indicating the error was caused by the SDK, library,
or a platform dependency — not by the caller or the developer's handler.
"""

ERROR_SOURCE_UPSTREAM: str = "upstream"
"""Error source value indicating the developer's handler code or an external
service it called failed or returned incorrect behaviour.
"""

# -- Platform error tagging -------------------------------------------------

PLATFORM_ERROR_TAG: str = "Azure.AI.AgentServer.PlatformError"
"""Key for tagging exceptions as platform errors.

Infrastructure code sets this key on exceptions to signal that the error
originated from the SDK's own infrastructure (storage transport, auth,
persistence pipeline).  Exceptions with this tag are classified as
``platform``; all others default to ``upstream`` (developer handler code)
in the exception filter.
"""

# -- Error detail formatting ------------------------------------------------

MAX_ERROR_DETAIL_LENGTH: int = 2048
"""Maximum length for the ``x-platform-error-detail`` header value.

Keeps the header within safe limits for reverse proxies and load balancers
while preserving enough of the exception string to be diagnostically useful.
"""

# -- HttpContext item key ---------------------------------------------------

REQUEST_ID_ITEM_KEY: str = "agentserver.request_id"
"""Key used to store the resolved request ID in ASGI scope state.

Downstream handlers and middleware can read this value to correlate the
request ID without re-resolving it.
"""
