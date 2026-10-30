# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Reuse a caller credential's access tokens across model requests.

Developer credentials such as ``AzureCliCredential`` start a process for every token request, so evaluations that
requested a token for each model call were slow and, when concurrent, could fail. A token is kept per credential and
scope until shortly before it expires, as azure-core's bearer token policy does. Credentials are keyed by identity
through a weak reference and never kept alive; a credential that cannot be weakly referenced, or a token without a
numeric expiry, is not cached.
"""

import hashlib
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
    """One credential's cached token for one scope, the lock for its token requests and its latest failed request."""

    def __init__(self, reference: Any) -> None:
        self.reference = reference
        self.token: Any = None
        self.lock = threading.Lock()
        self.attempts = 0
        self.failure: Optional[Dict[str, Any]] = None
        # The digest of the latest token a service rejected, so a request that was still awaiting that same token
        # cannot store it again.
        self.rejected: Optional[str] = None


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class CredentialTokenCache:
    """Share each caller credential's token for a scope across requests until shortly before it expires.

    Concurrent requests that share a synchronous credential wait for one token request. A caller can also ask that
    requests which waited on a failed token request share its failure instead of each requesting a token again.
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

    def store(self, credential: Any, scope: str, token: Any) -> None:
        entry = self._entry(credential, scope, create=True) if _is_fresh(token) else None
        if entry is not None:
            with self._guard:
                if entry.rejected != _digest(token.token):
                    entry.token = token

    def discard(self, credential: Any, scope: str, token: str) -> None:
        entry = self._entry(credential, scope, create=True)
        if entry is not None:
            with self._guard:
                entry.rejected = _digest(token)
                if entry.token is not None and entry.token.token == token:
                    entry.token = None

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
        credential.
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
            if describe_failure is not None:
                with self._guard:
                    failure = entry.failure if entry.attempts != queued_after else None
                if failure is not None:
                    raise failure_type(**failure)
            try:
                token = credential.get_token(scope)
            except Exception as error:
                with self._guard:
                    entry.attempts += 1
                    entry.failure = describe_failure(error) if describe_failure is not None else None
                raise
            with self._guard:
                entry.attempts += 1
                entry.failure = None
            if not inspect.isawaitable(token):
                self.store(credential, scope, token)
            return token
        finally:
            entry.lock.release()


TOKENS = CredentialTokenCache()
