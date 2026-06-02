# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hosted durable task provider — HTTP client for the Foundry Task Storage API.

Communicates with ``{FOUNDRY_PROJECT_ENDPOINT}/tasks`` via
``azure.core.AsyncPipelineClient`` with the standard Azure SDK policy
chain. Bearer tokens are obtained lazily by ``AsyncBearerTokenCredentialPolicy``;
call-site code never assembles ``Authorization`` headers directly.

**`ContentDecodePolicy` is intentionally excluded** from the policy
chain (spec 016 FR-030). The responses-storage gzip lesson: that policy
eagerly deserializes every body as JSON in middleware and crashes on
gzip / non-UTF-8 / gateway-HTML payloads before call-site code can
handle the response. Body parsing here happens at the call site with
defensive error handling (FR-033).

Every store-write call site funnels through :func:`_classify_store_write_error`
(spec 016 FR-006 / FR-032) so the manager can react uniformly to
transient / evicted / conflict / permanent outcomes without re-deriving
the classification per-site.
"""

from __future__ import annotations

import gzip
import json
import logging
from typing import Any, Literal

from azure.core import AsyncPipelineClient
from azure.core.configuration import Configuration
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import DecodeError
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    AsyncRetryPolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    RequestIdPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.rest import HttpRequest

from .._version import VERSION
from ._exceptions import TaskNotFound
from ._models import (
    TaskCreateRequest,
    TaskInfo,
    TaskPatchRequest,
    TaskStatus,
)
from ._task_api_logging_policy import TaskApiLoggingPolicy

logger = logging.getLogger("azure.ai.agentserver.durable")

_AUTH_SCOPE = "https://ai.azure.com/.default"
_API_VERSION = "v1"
_USER_AGENT = f"ai-agentserver-core/{VERSION}"
_BODY_PREFIX_LIMIT = 256  # truncation length for classified error bodies


# --------------------------------------------------------------------- #
# Classifier (spec 016 FR-006)
# --------------------------------------------------------------------- #


ClassifiedOutcome = Literal["transient", "evicted", "conflict", "permanent"]


class TransportClassifiedError(Exception):
    """Raised when a non-success response cannot be parsed safely.

    Carries enough metadata for operator triage without exposing
    bearer tokens or full response bodies. ``classification`` carries
    the FR-006 outcome label so callers can branch consistently.
    """

    def __init__(
        self,
        *,
        status: int,
        classification: ClassifiedOutcome,
        message: str,
        request_id: str | None = None,
        body_prefix: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.classification = classification
        self.request_id = request_id
        self.body_prefix = body_prefix


def _classify_store_write_error(  # pylint: disable=too-many-return-statements
    status_code: int, body: bytes | None
) -> ClassifiedOutcome:
    """Classify a non-success task-store response per spec 016 FR-006.

    Returns one of ``"transient"`` (retry), ``"evicted"`` (orphan-sandbox
    eviction; local cleanup sequence), ``"conflict"`` (etag mismatch or
    409-other), ``"permanent"`` (404 / 400 / unrecognised 4xx).

    Tolerant of non-JSON / empty / shape-unexpected bodies — never
    raises from inside the classifier; misshapen evictions are downgraded
    to ``"conflict"`` so the framework never invents an eviction event
    from noise (guard against false-positive evictions).

    :param status_code: HTTP status code from the response.
    :type status_code: int
    :param body: Raw response body bytes, or ``None`` if no body.
    :type body: bytes | None
    :return: Classification outcome for the response.
    :rtype: ClassifiedOutcome
    """
    # Transient: server-side problems, throttling, timeouts.
    if status_code in (408, 429) or 500 <= status_code < 600:
        return "transient"

    # 409: requires body inspection.
    if status_code == 409:
        if not body:
            return "conflict"
        try:
            payload = json.loads(body)
        except (ValueError, TypeError, UnicodeDecodeError):
            return "conflict"  # malformed 409 → safe default
        if not isinstance(payload, dict):
            return "conflict"
        err = payload.get("error")
        if isinstance(err, dict) and err.get("code") == "binding_mismatch":
            return "evicted"
        return "conflict"

    # 412 etag mismatch is a CAS conflict.
    if status_code == 412:
        return "conflict"

    # Everything else with 4xx is permanent (caller error).
    if 400 <= status_code < 500:
        return "permanent"

    # Anything else (e.g. 1xx, 3xx) — treat as permanent so callers
    # do not silently retry unexpected shapes.
    return "permanent"


def _body_prefix(body: bytes | None, limit: int = _BODY_PREFIX_LIMIT) -> str | None:
    """Return up to ``limit`` decoded characters of ``body``, or ``None`` if empty.

    Tolerant of non-UTF-8 (uses ``errors="replace"``) and non-bytes input.
    Used by the classified-error path so operators can see the start of a
    non-JSON response without dumping the whole body to logs.

    :param body: Raw bytes from the response, or ``None``.
    :type body: bytes | None
    :param limit: Maximum characters to include in the prefix.
    :type limit: int
    :return: A truncated decoded prefix, or ``None`` if ``body`` is empty.
    :rtype: str | None
    """
    if not body:
        return None
    try:
        text = bytes(body).decode("utf-8", errors="replace")
    except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        return None
    if len(text) > limit:
        return text[:limit] + "…"
    return text


def _maybe_decompress(body: bytes | None, headers: Any) -> bytes | None:
    """Decompress ``body`` if the response declares ``Content-Encoding: gzip``.

    Since ``ContentDecodePolicy`` is intentionally absent from the
    pipeline (FR-030), each call site is responsible for honoring
    ``Content-Encoding``. Returns ``body`` unchanged for other encodings
    so the caller's defensive JSON-parse can produce a useful error.

    :param body: Raw response bytes, or ``None``.
    :type body: bytes | None
    :param headers: Response headers (any mapping-like object).
    :type headers: Any
    :return: Decompressed body if applicable, otherwise ``body`` unchanged.
    :rtype: bytes | None
    """
    if not body or not headers:
        return body
    try:
        encoding = headers.get("Content-Encoding") or headers.get("content-encoding")
    except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        return body
    if not encoding:
        return body
    if encoding.lower().strip() == "gzip":
        try:
            return gzip.decompress(bytes(body))
        except (OSError, EOFError, ValueError):
            # Malformed gzip — let the caller's JSON-parse surface it.
            return body
    return body


def _parse_json_body(
    response: Any,
    *,
    method: str,
    url: str,
) -> Any:
    """Defensively decode a JSON body from the response.

    Spec 016 FR-033: catches ``UnicodeDecodeError``, ``json.JSONDecodeError``,
    ``azure.core.exceptions.DecodeError`` and raises
    :class:`TransportClassifiedError` carrying the classification, the
    request id (if any), and a truncated body prefix.

    :param response: The pipeline response object.
    :type response: Any
    :keyword method: HTTP method of the originating request (for error context).
    :paramtype method: str
    :keyword url: Request URL (for error context).
    :paramtype url: str
    :return: The parsed JSON value on success.
    :rtype: Any
    """
    status = getattr(response, "status_code", 0)
    headers = getattr(response, "headers", {}) or {}
    try:
        raw = response.body()
    except Exception as exc:  # noqa: BLE001
        raise TransportClassifiedError(
            status=status,
            classification=_classify_store_write_error(status, None),
            message=(
                f"task-store {method} {url}: failed to read response body: "
                f"{type(exc).__name__}: {exc}"
            ),
            request_id=str(headers.get("x-ms-request-id", "") or "") or None,
        ) from exc
    body = _maybe_decompress(raw, headers)
    try:
        text = bytes(body or b"").decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransportClassifiedError(
            status=status,
            classification=_classify_store_write_error(status, body),
            message=(
                f"task-store {method} {url}: response body not valid UTF-8 "
                f"(status={status}); body_prefix={_body_prefix(body)!r}"
            ),
            request_id=str(headers.get("x-ms-request-id", "") or "") or None,
            body_prefix=_body_prefix(body),
        ) from exc
    try:
        return json.loads(text)
    except (json.JSONDecodeError, DecodeError) as exc:
        raise TransportClassifiedError(
            status=status,
            classification=_classify_store_write_error(status, body),
            message=(
                f"task-store {method} {url}: response body not valid JSON "
                f"(status={status}); body_prefix={_body_prefix(body)!r}"
            ),
            request_id=str(headers.get("x-ms-request-id", "") or "") or None,
            body_prefix=_body_prefix(body),
        ) from exc


def _raise_classified(
    response: Any,
    *,
    method: str,
    url: str,
) -> None:
    """Inspect a response and raise :class:`TransportClassifiedError`.

    Replaces the legacy ``response.raise_for_status()`` call sites
    (spec 016 FR-032) so every non-success response funnels through
    the FR-006 classifier and carries the canonical outcome label.

    :param response: The pipeline response object.
    :type response: Any
    :keyword method: HTTP method of the originating request (for error context).
    :paramtype method: str
    :keyword url: Request URL (for error context).
    :paramtype url: str
    """
    status = getattr(response, "status_code", 0)
    headers = getattr(response, "headers", {}) or {}
    try:
        raw = response.body()
    except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        raw = None
    body = _maybe_decompress(raw, headers) if raw else None
    classification = _classify_store_write_error(status, body)
    raise TransportClassifiedError(
        status=status,
        classification=classification,
        message=(
            f"task-store {method} {url}: classified={classification} status={status}"
        ),
        request_id=str(headers.get("x-ms-request-id", "") or "") or None,
        body_prefix=_body_prefix(body),
    )


# --------------------------------------------------------------------- #
# HostedTaskProvider — azure.core.AsyncPipelineClient
# --------------------------------------------------------------------- #


def _build_default_policies(
    credential: AsyncTokenCredential,
) -> list[Any]:
    """Construct the canonical policy chain per spec 016 FR-030.

    Order: RequestIdPolicy, HeadersPolicy, UserAgentPolicy,
    AsyncRetryPolicy (retry on 5xx / 408 / 429 only — NEVER on 409),
    AsyncBearerTokenCredentialPolicy, TaskApiLoggingPolicy,
    DistributedTracingPolicy.

    ``ContentDecodePolicy`` is intentionally NOT included — see module
    docstring for the responses-storage gzip lesson.

    :param credential: Async token credential for the bearer-token policy.
    :type credential: AsyncTokenCredential
    :return: The default ordered policy chain.
    :rtype: list[Any]
    """
    return [
        RequestIdPolicy(),
        HeadersPolicy(base_headers={"Foundry-Features": "Routines=V1Preview"}),
        UserAgentPolicy(base_user_agent=_USER_AGENT),
        # Retry on 5xx and the standard transient HTTP statuses; 409
        # is explicitly NOT in retry_on_status_codes (FR-030) because
        # 409 carries application semantics (conflict / binding_mismatch)
        # that retry would silently mask.
        AsyncRetryPolicy(
            retry_total=3,
            retry_on_status_codes=[408, 429, 500, 502, 503, 504],
            retry_backoff_factor=0.5,
        ),
        AsyncBearerTokenCredentialPolicy(credential, _AUTH_SCOPE),
        TaskApiLoggingPolicy(),
        DistributedTracingPolicy(),
    ]


class HostedTaskProvider:
    """HTTP-backed provider for the Foundry Task Storage API.

    Built on :class:`azure.core.AsyncPipelineClient` with the standard
    policy chain (spec 016 FR-029..FR-034). ``ContentDecodePolicy`` is
    explicitly excluded; body parsing happens at the call site with
    defensive error handling.

    :param project_endpoint: The ``FOUNDRY_PROJECT_ENDPOINT`` base URL.
    :type project_endpoint: str
    :param credential: An async token credential supporting
        ``get_token(scope)`` (e.g.
        :class:`azure.identity.aio.DefaultAzureCredential`).
    :type credential: AsyncTokenCredential
    :keyword transport: Optional :class:`AsyncHttpTransport` override
        (used by tests for fake-transport injection per spec 016
        Conformance Test Map row 14).
    :paramtype transport: AsyncHttpTransport | None
    """

    def __init__(
        self,
        project_endpoint: str,
        credential: AsyncTokenCredential,
        *,
        transport: AsyncHttpTransport | None = None,
    ) -> None:
        self._base_url = f"{project_endpoint.rstrip('/')}/tasks"
        self._credential = credential
        config: Configuration = Configuration()
        config.user_agent_policy = UserAgentPolicy(base_user_agent=_USER_AGENT)
        self._policies: list[Any] = _build_default_policies(credential)
        self._client: AsyncPipelineClient = AsyncPipelineClient(
            base_url=self._base_url,
            config=config,
            policies=self._policies,
            transport=transport,
        )

    @property
    def policies(self) -> list[Any]:
        """The policy chain in order — used by tests for composition assertions.

        :return: A shallow copy of the configured policy chain.
        :rtype: list[Any]
        """
        return list(self._policies)

    async def _send(self, request: HttpRequest) -> Any:
        """Send ``request`` through the pipeline and return the HTTP response.

        The pipeline returns a ``PipelineResponse`` whose
        ``http_response`` is the wire response we operate on.

        :param request: The HTTP request to send.
        :type request: HttpRequest
        :return: The wire HTTP response.
        :rtype: Any
        """
        pipeline_response = await self._client._pipeline.run(request)  # pylint: disable=protected-access  # noqa: SLF001
        return pipeline_response.http_response

    async def create(self, request: TaskCreateRequest) -> TaskInfo:
        """Create a new task via POST /tasks.

        :param request: Task creation parameters.
        :type request: TaskCreateRequest
        :return: The created task record.
        :rtype: TaskInfo
        """
        params: dict[str, str] = {"api-version": _API_VERSION}
        if request.lease_owner is not None:
            params["lease_owner"] = request.lease_owner
        if request.lease_instance_id is not None:
            params["lease_instance_id"] = request.lease_instance_id
        if request.lease_duration_seconds is not None:
            params["lease_duration_seconds"] = str(request.lease_duration_seconds)

        body: dict[str, Any] = {
            "agent_name": request.agent_name,
            "session_id": request.session_id,
        }
        if request.id is not None:
            body["id"] = request.id
        if request.status != "pending":
            body["status"] = request.status
        if request.title is not None:
            body["title"] = request.title
        if request.description is not None:
            body["description"] = request.description
        if request.payload is not None:
            body["payload"] = request.payload
        if request.tags is not None:
            body["tags"] = request.tags
        if request.source is not None:
            body["source"] = request.source

        http_request = HttpRequest(
            "POST",
            self._base_url,
            params=params,
            json=body,
            headers={"Content-Type": "application/json"},
        )
        response = await self._send(http_request)
        if response.status_code >= 400:
            _raise_classified(response, method="POST", url=self._base_url)
        return TaskInfo.from_dict(_parse_json_body(response, method="POST", url=self._base_url))

    async def get(self, task_id: str) -> TaskInfo | None:
        """Get a task by ID via GET /tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The task record, or ``None`` if not found.
        :rtype: TaskInfo | None
        """
        url = f"{self._base_url}/{task_id}"
        http_request = HttpRequest(
            "GET",
            url,
            params={"api-version": _API_VERSION},
        )
        response = await self._send(http_request)
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            _raise_classified(response, method="GET", url=url)
        return TaskInfo.from_dict(_parse_json_body(response, method="GET", url=url))

    async def update(self, task_id: str, patch: TaskPatchRequest) -> TaskInfo:
        """Update a task via PATCH /tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :param patch: Fields to update.
        :type patch: TaskPatchRequest
        :return: The updated task record.
        :rtype: TaskInfo
        :raises TaskNotFound: If the task does not exist.
        """
        params: dict[str, str] = {"api-version": _API_VERSION}
        if patch.lease_owner is not None:
            params["lease_owner"] = patch.lease_owner
        if patch.lease_instance_id is not None:
            params["lease_instance_id"] = patch.lease_instance_id
        if patch.lease_duration_seconds is not None:
            params["lease_duration_seconds"] = str(patch.lease_duration_seconds)

        body: dict[str, Any] = {}
        if patch.status is not None:
            body["status"] = patch.status
        if patch.payload is not None:
            body["payload"] = patch.payload
        if patch.tags is not None:
            body["tags"] = patch.tags
        if patch.error is not None:
            body["error"] = patch.error
        if patch.suspension_reason is not None:
            body["suspension_reason"] = patch.suspension_reason

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if patch.if_match is not None:
            headers["If-Match"] = f'"{patch.if_match}"'

        url = f"{self._base_url}/{task_id}"
        http_request = HttpRequest(
            "PATCH",
            url,
            params=params,
            json=body,
            headers=headers,
        )
        response = await self._send(http_request)
        if response.status_code == 404:
            raise TaskNotFound(task_id)
        if response.status_code >= 400:
            _raise_classified(response, method="PATCH", url=url)
        return TaskInfo.from_dict(_parse_json_body(response, method="PATCH", url=url))

    async def delete(
        self,
        task_id: str,
        *,
        force: bool = False,
        cascade: bool = False,
    ) -> None:
        """Delete a task via DELETE /tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :keyword force: Release active lease before deleting.
        :paramtype force: bool
        :keyword cascade: Delete dependent tasks.
        :paramtype cascade: bool
        """
        params: dict[str, str] = {"api-version": _API_VERSION}
        if force:
            params["force"] = "true"
        if cascade:
            params["cascade"] = "true"

        url = f"{self._base_url}/{task_id}"
        http_request = HttpRequest(
            "DELETE",
            url,
            params=params,
        )
        response = await self._send(http_request)
        if response.status_code == 404:
            raise TaskNotFound(task_id)
        if response.status_code >= 400:
            _raise_classified(response, method="DELETE", url=url)

    async def list(
        self,
        *,
        agent_name: str,
        session_id: str,
        status: TaskStatus | None = None,
        lease_owner: str | None = None,
        tag: dict[str, str] | None = None,
        source_type: str | None = None,
    ) -> list[TaskInfo]:
        """List tasks via GET /tasks with automatic cursor pagination.

        :keyword agent_name: Filter to tasks owned by this agent name.
        :paramtype agent_name: str
        :keyword session_id: Filter to tasks for this session ID.
        :paramtype session_id: str
        :keyword status: Optional status filter (``pending``,
            ``in_progress``, ``suspended``, ``completed``).
        :paramtype status: TaskStatus | None
        :keyword lease_owner: Optional lease-owner string filter.
        :paramtype lease_owner: str | None
        :keyword tag: Optional tag-equality filter (all key/value pairs
            must match).
        :paramtype tag: dict[str, str] | None
        :keyword source_type: Optional source-type filter.
        :paramtype source_type: str | None
        :return: All matching tasks across all pages.
        :rtype: list[TaskInfo]
        """
        params: dict[str, str] = {
            "api-version": _API_VERSION,
            "agent_name": agent_name,
            "session_id": session_id,
            "limit": "100",
        }
        if status is not None:
            params["status"] = status
        if lease_owner is not None:
            params["lease_owner"] = lease_owner
        if tag:
            for key, value in tag.items():
                params[f"tag.{key}"] = value
        if source_type is not None:
            params["source_type"] = source_type

        all_tasks: list[TaskInfo] = []
        while True:
            http_request = HttpRequest("GET", self._base_url, params=params)
            response = await self._send(http_request)
            if response.status_code >= 400:
                _raise_classified(response, method="GET", url=self._base_url)
            data = _parse_json_body(response, method="GET", url=self._base_url)
            items: list[dict[str, Any]] = data.get("data", data.get("items", []))
            all_tasks.extend(TaskInfo.from_dict(item) for item in items)

            if not data.get("has_more", False):
                break
            last_id = data.get("last_id")
            if not last_id:
                break
            params["after"] = last_id

        return all_tasks

    async def close(self) -> None:
        """Close the underlying pipeline client."""
        await self._client.close()
