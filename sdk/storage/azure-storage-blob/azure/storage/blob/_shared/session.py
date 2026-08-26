# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Callable, Dict, Optional, Tuple, TYPE_CHECKING
from typing_extensions import Protocol
from urllib.parse import urlparse

if TYPE_CHECKING:
    from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import
        PipelineRequest,
    )

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
    """Thread-safe, container-level session provider for the sync stack.

    Concurrency model
    -----------------
    * Reads (`get`) are lock-free. They perform a single dict.get and never
      mutate the cache, so concurrent readers never need to coordinate.
    * Writes (`put` / `put_fallback`) and the CreateSession single-flight are
      serialized per-container via the lock returned by :meth:`lock_container`.
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
        :rtype: ~azure.storage.blob._shared.policies.Session or None
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
