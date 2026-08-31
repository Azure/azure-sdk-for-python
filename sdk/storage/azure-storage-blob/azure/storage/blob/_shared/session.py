# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
from typing_extensions import Protocol
from urllib.parse import urlparse

from azure.core.exceptions import AzureError, HttpResponseError

from .models import StorageErrorCode
from .._generated.models import CreateSessionConfiguration

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import
        PipelineRequest,
    )

_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc


def _analyze_request(request: "PipelineRequest") -> Optional[Tuple[str, str]]:
    http_request = request.http_request
    if http_request.method != "GET":
        return None
    parsed = urlparse(http_request.url)
    segments = [seg for seg in parsed.path.split("/") if seg]
    if len(segments) < 2:
        return None
    query = http_request.query
    if "comp" in query or query.get("restype") == "container":
        return None
    container_name = segments[0]
    container_url = f"{parsed.scheme}://{parsed.netloc}/{container_name}"
    return container_name, container_url


def _extract_session(response: Any) -> Tuple[str, str, datetime]:
    creds = getattr(response, "credentials", None)
    if not creds or not getattr(creds, "session_token", None) or not getattr(creds, "session_key", None):
        raise ValueError("CreateSession response missing SessionToken/SessionKey")
    session_token: str = creds.session_token
    session_key: str = creds.session_key
    expires_at = getattr(response, "expiration", None)
    if expires_at is None:
        expires_at = datetime.now(UTC) + timedelta(minutes=5)
    elif expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return session_token, session_key, expires_at


def _to_service_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _is_cooldown_error(status: Optional[int], error_code: str) -> bool:
    if status is None:
        return False
    if status >= 500 or status == 403:
        return True
    return status == 400 and error_code == StorageErrorCode.FEATURE_NOT_ENABLED


class Session:
    """A session entry."""

    __slots__ = ("session_token", "session_key", "expires_at", "is_fallback")

    REFRESH_BUFFER: timedelta = timedelta(seconds=30)
    """Buffer before proactive refresh is initiated."""

    def __init__(
        self,
        session_token: Optional[str],
        session_key: Optional[str],
        expires_at: datetime,
        is_fallback: bool = False,
    ) -> None:
        self.session_token = session_token
        self.session_key = session_key
        self.expires_at = expires_at
        self.is_fallback = is_fallback

    def expired(self, now: Optional[datetime] = None) -> bool:
        now = now if now is not None else datetime.now(UTC)
        diff = timedelta(seconds=0) if self.is_fallback else Session.REFRESH_BUFFER
        return now >= self.expires_at - diff


class SessionProvider(Protocol):
    """Creates, caches, and invalidates per-container sessions."""

    def is_request_eligible(self, request: "PipelineRequest") -> bool:
        ...

    def get_session(self, request: "PipelineRequest") -> Optional[Session]:
        ...

    def invalidate_session(self, request: "PipelineRequest", current: Session) -> None:
        ...


class SessionCache:
    """Thread-safe, container-level storage for sessions on the sync stack.

    Concurrency model
    -----------------
    * Reads (`get`) are lock-free. They perform a single dict.get and never
      mutate the cache, so concurrent readers never need to coordinate.
    * Writes (`put` / `put_fallback`) must be made under the lock returned by
      :meth:`lock_container`, which callers also use to single-flight CreateSession.
    * A single _locks_guard serializes only the *creation* of per-container
      locks, so two threads racing on a brand-new container can't build two
      different lock objects.
    """

    FALLBACK_COOLDOWN: timedelta = timedelta(minutes=5)
    """Cooldown applied to the fallback-to-bearer sentinel after an eligible create session failure."""

    def __init__(self) -> None:
        self._locks: Dict[str, Lock] = {}
        self._locks_guard: Lock = Lock()
        self._entry: Dict[str, Session] = {}

    def lock_container(self, container_url: str) -> Lock:
        """Return the per-container lock, creating it exactly once.

        :param str container_url: The container to get the lock for.
        :return: The single lock instance associated with the container.
        :rtype: ~threading.Lock
        """
        # Easy path: lock already exists, and on free threads it falls to slow path
        existing_lock = self._locks.get(container_url)
        if existing_lock is not None:
            return existing_lock
        # Slow path: create exactly one lock per container
        with self._locks_guard:
            return self._locks.setdefault(container_url, Lock())

    def get(self, container_url: str) -> Optional[Session]:
        """Return a live session for the container, or None.

        Lock-free and non-mutating. Expired entries are NOT deleted.
        Instead, they are simply treated as a cache miss and overwritten on the next refresh.

        :param str container_url: The container to look up.
        :return: A live (non-expired) session, or None on miss/expiry.
        :rtype: ~azure.storage.blob._shared.session.Session or None
        """
        cached = self._entry.get(container_url, None)
        if cached is None or cached.expired():
            return None
        return cached

    def put(self, container_url: str, session_token: str, session_key: str, expires_at: datetime) -> None:
        """Install a real session entry.

        Caller must hold the lock at the container-level.

        :param str container_url: The container the session belongs to.
        :param str session_token: The session token to send as a header.
        :param str session_key: The HMAC signing key for the session.
        :param ~datetime.datetime expires_at: When the session expires.
        """
        self._entry[container_url] = Session(session_token, session_key, expires_at, is_fallback=False)

    def put_fallback(self, container_url: str) -> None:
        """Install a fallback-to-bearer sentinel for the cooldown window.

        Caller must hold the lock at the container-level.

        :param str container_url: The container to mark for bearer fallback.
        """
        self._entry[container_url] = Session(
            None, None, datetime.now(UTC) + self.FALLBACK_COOLDOWN, is_fallback=True
        )

    def invalidate(self, container_url: str, session_token: Optional[str] = None) -> None:
        """Drop the cached session if it still matches the rejected token.

        :param str container_url: The container-scoped URL.
        :param str session_token: The rejected token, or None if unknown.
        """
        with self.lock_container(container_url):
            cached = self._entry.get(container_url, None)
            if cached is not None and cached.session_token == session_token:
                self._entry.pop(container_url, None)


class ContainerSessionProvider:
    """Creates, caches, and invalidates per-container sessions backed by a TokenCredential.

    A single provider may be shared across multiple clients to persist the session
    cache beyond the lifetime of any one of them. When no provider is supplied, each
    client creates one scoped to itself.

    :param str service_url: The blob service endpoint. Container and blob path segments
        and all query parameters are stripped.
    :param credential: The credential used to authorize CreateSession calls.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str api_version: The Storage API version to use for CreateSession.
    """

    def __init__(self, service_url: str, credential: "TokenCredential", **kwargs: Any) -> None:
        from .._blob_service_client import BlobServiceClient  # module-level import would cycle

        if not hasattr(credential, "get_token"):
            raise TypeError(
                f"ContainerSessionProvider requires a TokenCredential; received {type(credential).__name__}."
            )
        self._client = BlobServiceClient(_to_service_url(service_url), credential=credential, **kwargs)
        self._cache = SessionCache()

    def is_request_eligible(self, request: "PipelineRequest") -> bool:
        """Checks whether the request can be signed with a session token.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: True if the request is valid.
        :rtype: bool
        """
        return _analyze_request(request) is not None

    def get_session(self, request: "PipelineRequest") -> Optional[Session]:
        """Return a session, creating one on a miss.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: A session, or None if the caller should use bearer auth.
        :rtype: ~azure.storage.blob._shared.session.Session or None
        """
        analyzed = _analyze_request(request)
        if analyzed is None:
            return None

        session = self._cache.get(analyzed[1])
        if session is None:
            session = self._acquire(analyzed)
        if session is None or session.is_fallback:
            return None
        return session

    def invalidate_session(self, request: "PipelineRequest", current: Session) -> None:
        """Drop the cached session if it still matches the rejected one.

        :param ~azure.core.pipeline.PipelineRequest request: The rejected request.
        :param current: The session that was rejected.
        :type current: ~azure.storage.blob._shared.session.Session
        """
        analyzed = _analyze_request(request)
        if analyzed is not None:
            self._cache.invalidate(analyzed[1], current.session_token)

    def _acquire(self, analyzed: Tuple[str, str]) -> Optional[Session]:
        container_name, container_url = analyzed
        with self._cache.lock_container(container_url):
            existing = self._cache.get(container_url)
            if existing is not None:
                return existing
            try:
                token, key, expires_at = self._create_session(container_name)
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
                    self._cache.put_fallback(container_url)
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
            self._cache.put(container_url, token, key, expires_at)
            return self._cache.get(container_url)

    def _create_session(self, container_name: str) -> Tuple[str, str, datetime]:
        container_client = self._client.get_container_client(container_name)
        response = container_client._client.container.create_session(  # pylint: disable=protected-access
            create_session_configuration=CreateSessionConfiguration(authentication_type="HMAC")
        )
        return _extract_session(response)
