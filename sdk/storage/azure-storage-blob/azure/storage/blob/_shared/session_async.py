# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

from typing_extensions import Protocol

from azure.core.exceptions import AzureError, HttpResponseError

from .session import (
    Session,
    _extract_container,
    _extract_session,
    _is_cooldown_error,
    _to_service_url,
)
from .._generated.models import CreateSessionConfiguration, CreateSessionResponse

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest

_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc


class AsyncSessionProvider(Protocol):
    """Creates, caches, and invalidates per-container sessions."""

    def is_request_eligible(self, request: "PipelineRequest") -> bool: ...

    async def get_session(self, request: "PipelineRequest") -> Optional[Session]: ...

    async def invalidate_session(self, request: "PipelineRequest", current: Session) -> None: ...


class AsyncSessionCache:
    """Container-level storage for sessions on the async stack.

    Concurrency model
    -----------------
    * Reads (`get`) never await and never mutate, so concurrent readers need no coordination.
    * Writes (`put` / `put_fallback`) must be made while holding the lock returned by
      :meth:`lock_container`, which callers also use to single-flight CreateSession.
    * No guard lock is needed around lock creation: `lock_container` contains no await
      point, so the coroutine cannot be suspended between the lookup and the insert.
    """

    FALLBACK_COOLDOWN: timedelta = timedelta(minutes=5)
    """Cooldown applied to the fallback-to-bearer sentinel after an eligible create session failure."""

    def __init__(self) -> None:
        self._locks: Dict[str, asyncio.Lock] = {}
        self._entry: Dict[str, Session] = {}

    def lock_container(self, container_name: str) -> asyncio.Lock:
        """Return the per-container lock, creating it exactly once.

        :param str container_name: The container name to get the lock for.
        :return: The single lock instance associated with the container.
        :rtype: ~asyncio.Lock
        """
        existing_lock = self._locks.get(container_name)
        if existing_lock is not None:
            return existing_lock
        return self._locks.setdefault(container_name, asyncio.Lock())

    def get(self, container_name: str) -> Optional[Session]:
        """Return a live session for the container, or None.

        Non-mutating. Expired entries are NOT deleted. Instead, they are simply
        treated as a cache miss and overwritten on the next refresh.

        :param str container_name: The container name to look up.
        :return: A live (non-expired) session, or None on miss/expiry.
        :rtype: ~azure.storage.blob._shared.session.Session or None
        """
        cached = self._entry.get(container_name, None)
        if cached is None or cached.expired():
            return None
        return cached

    def put(self, container_name: str, session: Session) -> None:
        """Install a real session entry.

        Caller must hold the lock at the container-level.

        :param str container_name: The container name the session belongs to.
        :param session: The session to cache.
        :type session: ~azure.storage.blob._shared.session.Session
        """
        self._entry[container_name] = session

    def put_fallback(self, container_name: str) -> None:
        """Install a fallback-to-bearer sentinel for the cooldown window.

        Caller must hold the lock at the container-level.

        :param str container_name: The container name to mark for bearer fallback.
        """
        self._entry[container_name] = Session(None, None, datetime.now(UTC) + self.FALLBACK_COOLDOWN, is_fallback=True)

    async def invalidate(self, container_name: str, session_token: Optional[str] = None) -> None:
        """Drop the cached session if it still matches the rejected token.

        :param str container_name: The container name.
        :param str session_token: The rejected token, or None if unknown.
        """
        async with self.lock_container(container_name):
            cached = self._entry.get(container_name, None)
            if cached is not None and cached.session_token == session_token:
                self._entry.pop(container_name, None)


class AsyncContainerSessionProvider:
    """Creates, caches, and invalidates per-container sessions backed by an AsyncTokenCredential.

    A single provider may be shared across multiple clients to persist the session
    cache beyond the lifetime of any one of them. When no provider is supplied, each
    client creates one scoped to itself. A provider must not be shared across event loops.

    :param str service_url: The blob service endpoint. Container and blob path segments
        and all query parameters are stripped.
    :param credential: The credential used to authorize CreateSession calls.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Storage API version to use for CreateSession.
    """

    def __init__(self, service_url: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        from ..aio._blob_service_client_async import BlobServiceClient  # module-level import would cycle

        if not hasattr(credential, "get_token"):
            raise TypeError(
                f"AsyncContainerSessionProvider requires an AsyncTokenCredential; "
                f"received {type(credential).__name__}."
            )
        self._client = BlobServiceClient(_to_service_url(service_url), credential=credential, **kwargs)
        self._cache = AsyncSessionCache()

    def is_request_eligible(self, request: "PipelineRequest") -> bool:
        """Checks whether the request can be signed with a session token.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: True if the request is valid.
        :rtype: bool
        """
        return _extract_container(request) is not None

    async def get_session(self, request: "PipelineRequest") -> Optional[Session]:
        """Return a session, creating one on a miss.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: A session, or None if the caller should use bearer auth.
        :rtype: ~azure.storage.blob._shared.session.Session or None
        """
        container_name = _extract_container(request)
        if container_name is None:
            return None

        session = self._cache.get(container_name)
        if session is None:
            session = await self._acquire(container_name)
        if session is None or session.is_fallback:
            return None
        return session

    async def invalidate_session(self, request: "PipelineRequest", current: Session) -> None:
        """Drop the cached session if it still matches the rejected one.

        :param ~azure.core.pipeline.PipelineRequest request: The rejected request.
        :param current: The session that was rejected.
        :type current: ~azure.storage.blob._shared.session.Session
        """
        container_name = _extract_container(request)
        if container_name is not None:
            await self._cache.invalidate(container_name, current.session_token)

    async def _acquire(self, container_name: str) -> Optional[Session]:
        async with self._cache.lock_container(container_name):
            existing = self._cache.get(container_name)
            if existing is not None:
                return existing
            try:
                token, key, expires_at = await self._create_session(container_name)
            except HttpResponseError as error:
                headers = getattr(error.response, "headers", {})
                error_code = headers.get("x-ms-error-code", "")
                if _is_cooldown_error(error.status_code, error_code):
                    _LOGGER.warning(
                        "CreateSession failed for container '%s' (HTTP %s, %s); "
                        "falling back to bearer for %d seconds.",
                        container_name,
                        error.status_code,
                        error_code,
                        int(self._cache.FALLBACK_COOLDOWN.total_seconds()),
                    )
                    self._cache.put_fallback(container_name)
                else:
                    _LOGGER.warning(
                        "CreateSession failed for container '%s'; using bearer for this request.",
                        container_name,
                        exc_info=True,
                    )
                return None
            except (AzureError, ValueError):
                _LOGGER.warning(
                    "CreateSession failed for container '%s'; using bearer for this request.",
                    container_name,
                    exc_info=True,
                )
                return None
            session = Session(token, key, expires_at)
            self._cache.put(container_name, session)
            return session

    async def _create_session(self, container_name: str) -> Tuple[str, str, datetime]:
        container_client = self._client.get_container_client(container_name)
        response: CreateSessionResponse = (
            await container_client._client.container.create_session(  # pylint: disable=protected-access
                create_session_configuration=CreateSessionConfiguration(authentication_type="HMAC")
            )
        )
        return _extract_session(response)
