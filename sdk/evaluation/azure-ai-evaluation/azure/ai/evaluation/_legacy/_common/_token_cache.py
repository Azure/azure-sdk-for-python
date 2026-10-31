# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Reuse a caller credential's access tokens across model requests.

Developer credentials such as ``AzureCliCredential`` start a process for every token request, so evaluations that
requested a token for each model call were slow and, when concurrent, could fail. A token is kept per credential and
scope until shortly before it expires, as azure-core's bearer token policy does. Credentials are keyed by identity
through a weak reference and never kept alive; a credential that cannot be weakly referenced, or a token without a
numeric expiry, is not cached. A token that a service rejected is dropped, and a token whose acquisition began before
that rejection is not stored, so a rejected token never re-enters the cache through a slower request. Requests that
waited on such an acquisition use its token instead of each requesting another one.
"""

import inspect
import math
import threading
import time
import weakref
from typing import Any, Callable, Dict, Optional, Tuple

from azure.core.exceptions import ClientAuthenticationError

from azure.ai.evaluation._exceptions import EvaluationException

# A token is reused until this many seconds before it expires, like azure-core's bearer token policy.
TOKEN_REFRESH_SECONDS = 300
# How often a request waiting for another request's token checks whether it was abandoned.
TOKEN_WAIT_INTERVAL_SECONDS = 0.05


def _is_fresh(token: Any) -> bool:
    expires_on = getattr(token, "expires_on", None)
    if isinstance(expires_on, bool) or not isinstance(expires_on, (int, float)):
        return False
    try:
        return (
            isinstance(getattr(token, "token", None), str)
            and math.isfinite(expires_on)
            and expires_on - time.time() > TOKEN_REFRESH_SECONDS
        )
    except OverflowError:
        return False


def describe_credential_failure(error: BaseException) -> Optional[Dict[str, Any]]:
    """Describe a credential's authentication failure by its message, or return None for any other failure.

    Requests that waited on an authentication failure share it as a ``ClientAuthenticationError``. Any other failure,
    such as a token service outage, is not shared, so each waiting request makes its own attempt and raises the
    credential's own error type. The description never keeps the error or its traceback.
    """
    if isinstance(error, ClientAuthenticationError):
        return {"message": str(error) or type(error).__name__}
    return None


class _CredentialTokens:
    """One credential's cached token for one scope, the lock for its token requests, the outcome of its latest token
    request and the count of rejections that invalidates acquisitions begun before them."""

    def __init__(self, reference: Any) -> None:
        self.reference = reference
        self.token: Any = None
        self.lock = threading.Lock()
        self.attempts = 0
        self.failure: Optional[Dict[str, Any]] = None
        # The latest token request's token when a rejection kept it out of the cache, for the requests that waited on
        # that request. It is never cached.
        self.unstored: Any = None
        # Incremented when a service rejects a token. An acquisition that began before the latest rejection may
        # return the rejected token, so a token is stored only under the generation its acquisition began with.
        self.generation = 0


class CredentialTokenCache:
    """Share each caller credential's token for a scope across requests until shortly before it expires.

    Concurrent requests that share a synchronous credential wait for one token request. A caller can also ask that
    requests which waited on a failed token request share its failure instead of each requesting a token again. A
    token a service rejected is discarded; the credential's next token is cached again, even when it is the same
    token, while an acquisition that began before the rejection is never stored. Requests that waited on such an
    acquisition use its token instead of each requesting another one.
    """

    def __init__(self) -> None:
        self._entries: Dict[Tuple[int, str], _CredentialTokens] = {}
        # Reentrant because a weak reference callback can run while a lookup holds the lock.
        self._guard = threading.RLock()

    def _entry(self, credential: Any, scope: str, create: bool = False) -> Optional[_CredentialTokens]:
        key = (id(credential), scope)
        with self._guard:
            entry = self._entries.get(key)
            if entry is not None and entry.reference() is credential:
                return entry
            if not create:
                return None

            def forget(reference: Any) -> None:
                with self._guard:
                    current = self._entries.get(key)
                    if current is not None and current.reference is reference:
                        del self._entries[key]

            try:
                entry = _CredentialTokens(weakref.ref(credential, forget))
            except TypeError:
                return None
            self._entries[key] = entry
            return entry

    def cached(self, credential: Any, scope: str) -> Any:
        entry = self._entry(credential, scope)
        with self._guard:
            token = entry.token if entry is not None else None
        return token if _is_fresh(token) else None

    def generation(self, credential: Any, scope: str) -> int:
        """Return the rejection generation to pass to ``store`` for a token acquisition that begins now."""
        entry = self._entry(credential, scope)
        with self._guard:
            return entry.generation if entry is not None else 0

    def store(self, credential: Any, scope: str, token: Any, generation: Optional[int] = None) -> bool:
        """Keep a fresh token for reuse and return whether it was kept.

        ``generation`` is what ``generation`` returned when the acquisition began. A token acquired before a later
        rejection is not stored, because it may be the rejected token; without a generation the token is stored.
        """
        entry = self._entry(credential, scope, create=True) if _is_fresh(token) else None
        if entry is not None:
            with self._guard:
                if generation is None or generation == entry.generation:
                    entry.token = token
                    return True
        return False

    def discard(self, credential: Any, scope: str, token: str) -> None:
        """Stop reusing a token a service rejected, and invalidate acquisitions that began before the rejection."""
        entry = self._entry(credential, scope, create=True)
        if entry is not None:
            with self._guard:
                entry.generation += 1
                if entry.token is not None and entry.token.token == token:
                    entry.token = None
                if entry.unstored is not None and entry.unstored.token == token:
                    entry.unstored = None

    def fetch(
        self,
        credential: Any,
        scope: str,
        *,
        abandoned: Optional[threading.Event] = None,
        deadline: Optional[float] = None,
        describe_failure: Optional[Callable[[BaseException], Optional[Dict[str, Any]]]] = None,
        failure_type: Callable[..., BaseException] = EvaluationException,
    ) -> Any:
        """Request a synchronous credential's token once for concurrent requests.

        Returns None, without requesting a token, when the request was abandoned or its monotonic ``deadline`` passed
        while it waited for another request's token. With ``describe_failure``, requests that waited on a failed
        request raise ``failure_type`` built from its description instead of each requesting a token again; a None
        description is not shared. The description must not keep the error, whose traceback references the
        credential. Requests that waited on a request whose token a rejection kept out of the cache use that token.
        """
        entry = self._entry(credential, scope, create=True)
        if entry is None:
            return None if abandoned is not None and abandoned.is_set() else credential.get_token(scope)
        with self._guard:
            queued_after = entry.attempts
        # Wait in short steps so an abandoned request stops waiting promptly.
        while True:
            remaining = math.inf if deadline is None else deadline - time.monotonic()
            if (abandoned is not None and abandoned.is_set()) or remaining <= 0:
                return None
            if entry.lock.acquire(timeout=min(remaining, TOKEN_WAIT_INTERVAL_SECONDS)):
                break
        try:
            token = self.cached(credential, scope)
            if (
                token is not None
                or (abandoned is not None and abandoned.is_set())
                or (deadline is not None and time.monotonic() >= deadline)
            ):
                return token
            with self._guard:
                waited = entry.attempts != queued_after
                failure = entry.failure if waited and describe_failure is not None else None
                unstored = entry.unstored if waited else None
            if failure is not None:
                raise failure_type(**failure)
            if _is_fresh(unstored):
                # Issued for the request this one waited on and not rejected since it was shared, so use it rather
                # than request another token.
                return unstored
            with self._guard:
                generation = entry.generation
            try:
                token = credential.get_token(scope)
            except Exception as error:
                with self._guard:
                    entry.attempts += 1
                    entry.failure = describe_failure(error) if describe_failure is not None else None
                    entry.unstored = None
                raise
            stored = inspect.isawaitable(token) or self.store(credential, scope, token, generation)
            with self._guard:
                entry.attempts += 1
                entry.failure = None
                entry.unstored = token if not stored and _is_fresh(token) else None
            return token
        finally:
            entry.lock.release()


TOKENS = CredentialTokenCache()
