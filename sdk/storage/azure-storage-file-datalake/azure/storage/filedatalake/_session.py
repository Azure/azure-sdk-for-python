# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import copy
import logging
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import time
from typing import Any, cast, Dict, Optional, Tuple, TYPE_CHECKING
from urllib.parse import unquote, urlparse
from wsgiref.handlers import format_date_time

from typing_extensions import Protocol

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.pipeline.policies import HTTPPolicy
from azure.storage.blob._generated.models import CreateSessionConfiguration, CreateSessionResponse

from ._shared import sign_string
from ._shared.authentication import AzureSigningError, _storage_header_sort
from ._shared.models import StorageErrorCode

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse
    from azure.core.pipeline.transport import HttpTransport
    from ._shared.base_client import StorageAccountHostsMixin

SESSION_BEARER_AUTH_KEY = "_session_bearer_auth"
_SESSION_SIGNED_HEADERS = (
    "content-encoding",
    "content-language",
    "content-length",
    "content-md5",
    "content-type",
    "date",
    "if-modified-since",
    "if-match",
    "if-none-match",
    "if-unmodified-since",
    "byte_range",
)
_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc


def _extract_container(request: "PipelineRequest") -> Optional[str]:
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
    return container_name


def _extract_session(response: "CreateSessionResponse") -> Tuple[str, str, datetime]:
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
    if status >= 500 and status != 503 or status == 403:
        return True
    return status == 400 and error_code == StorageErrorCode.FEATURE_NOT_ENABLED


def _apply_session_auth(request: "PipelineRequest", session_token: str, session_key: str, account_name: str) -> None:
    """Sign an eligible request with the SharedKey protocol under the Session scheme.

    Shared by the sync and async session policies; ``account_name`` is passed in
    rather than read from ``self`` so neither policy needs to instantiate the other.

    :param ~azure.core.pipeline.PipelineRequest request: The request to sign in place.
    :param str session_token: The session token to embed in the Authorization header.
    :param str session_key: The HMAC signing key for the session.
    :param str account_name: Storage account name; the signer identity.
    :raises AzureSigningError: if signing fails.
    """
    http_request = request.http_request
    http_request.headers["x-ms-date"] = format_date_time(time())

    # 1) Standard headers. Storage omits content-length when it is "0".
    headers = {name.lower(): value for name, value in http_request.headers.items() if value}
    if headers.get("content-length") == "0":
        del headers["content-length"]
    signed_headers = "\n".join(headers.get(h, "") for h in _SESSION_SIGNED_HEADERS) + "\n"

    # 2) Canonicalized x-ms-* headers, sorted by the service-emulating comparator.
    x_ms_headers = _storage_header_sort(
        [(n.lower(), v) for n, v in http_request.headers.items() if n.lower().startswith("x-ms-")]
    )
    canonicalized_headers = "".join(f"{n}:{v}\n" for n, v in x_ms_headers if v is not None)

    # 3) Canonicalized resource + query (query values must be url-decoded).
    canonicalized_resource = "/" + account_name + urlparse(http_request.url).path
    canonicalized_resource += "".join(
        f"\n{n.lower()}:{unquote(v)}" for n, v in sorted(http_request.query.items()) if v is not None
    )

    string_to_sign = http_request.method + "\n" + signed_headers + canonicalized_headers + canonicalized_resource

    try:
        signature = sign_string(session_key, string_to_sign)
    except Exception as ex:  # pylint: disable=broad-except
        raise AzureSigningError(str(ex)) from ex
    http_request.headers["Authorization"] = f"Session {session_token}:{signature}"


def _configure_session(kwargs: Dict[str, Any]) -> None:
    """Pop the session keywords and, if enabled, register a session policy factory for the pipeline.

    :param Dict[str, Any] kwargs: The client constructor keyword arguments. Modified in place.
    """
    use_session = bool(kwargs.pop("use_session", False))
    session_provider: Optional[SessionProvider] = kwargs.pop("session_provider", None)
    session_account_name: Optional[str] = kwargs.pop("session_account_name", None)
    if not use_session:
        return

    def _factory(
        client: "StorageAccountHostsMixin",
        credential: Any,
        transport: "HttpTransport",
        audience: Optional[str],
        pipeline_kwargs: Dict[str, Any],
    ) -> StorageSessionPolicy:
        provider = session_provider
        if provider is None:
            sub_kwargs = dict(pipeline_kwargs)
            sub_kwargs.pop("_configuration", None)
            sub_kwargs.pop("pipeline", None)
            sub_kwargs.pop("sdk_moniker", None)
            sub_kwargs["transport"] = transport
            if sub_kwargs.get("retry_policy") is not None:
                sub_kwargs["retry_policy"] = copy.copy(sub_kwargs["retry_policy"])
            sub_kwargs.pop("_additional_pipeline_policies", None)
            provider = ContainerSessionProvider(
                f"{client.scheme}://{client.primary_hostname}".replace(".dfs.", ".blob.", 1),
                cast("TokenCredential", credential),
                audience=audience,
                **sub_kwargs,
            )
        return StorageSessionPolicy(
            account_name=session_account_name or client.account_name,
            session_provider=provider,
        )

    kwargs["_session_policy_factory"] = _factory


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

    def expired(self) -> bool:
        diff = timedelta(seconds=0) if self.is_fallback else Session.REFRESH_BUFFER
        return datetime.now(UTC) >= self.expires_at - diff


class SessionProvider(Protocol):
    """Creates, caches, and invalidates per-container sessions."""

    def is_request_eligible(self, request: "PipelineRequest") -> bool: ...

    def get_session(self, request: "PipelineRequest") -> Optional[Session]: ...

    def invalidate_session(self, request: "PipelineRequest", current: Session) -> None: ...


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

    def lock_container(self, container_name: str) -> Lock:
        """Return the per-container lock, creating it exactly once.

        :param str container_name: The container name to get the lock for.
        :return: The single lock instance associated with the container.
        :rtype: ~threading.Lock
        """
        # Easy path: lock already exists, and on free threads it falls to slow path
        existing_lock = self._locks.get(container_name)
        if existing_lock is not None:
            return existing_lock
        # Slow path: create exactly one lock per container
        with self._locks_guard:
            return self._locks.setdefault(container_name, Lock())

    def get(self, container_name: str) -> Optional[Session]:
        """Return a live session for the container, or None.

        Lock-free and non-mutating. Expired entries are NOT deleted.
        Instead, they are simply treated as a cache miss and overwritten on the next refresh.

        :param str container_name: The container name to look up.
        :return: A live (non-expired) session, or None on miss/expiry.
        :rtype: Session or None
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
        :type session: Session
        """
        self._entry[container_name] = session

    def put_fallback(self, container_name: str) -> None:
        """Install a fallback-to-bearer sentinel for the cooldown window.

        Caller must hold the lock at the container-level.

        :param str container_name: The container name to mark for bearer fallback.
        """
        self._entry[container_name] = Session(None, None, datetime.now(UTC) + self.FALLBACK_COOLDOWN, is_fallback=True)

    def invalidate(self, container_name: str, session_token: Optional[str] = None) -> None:
        """Drop the cached session if it still matches the rejected token.

        :param str container_name: The container name.
        :param str session_token: The rejected token, or None if unknown.
        """
        with self.lock_container(container_name):
            cached = self._entry.get(container_name, None)
            if cached is not None and cached.session_token == session_token:
                self._entry.pop(container_name, None)


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
        from azure.storage.blob import BlobServiceClient  # module-level import would cycle

        if not hasattr(credential, "get_token"):
            raise TypeError(
                f"ContainerSessionProvider requires a TokenCredential; received {type(credential).__name__}."
            )
        kwargs["logging_body"] = False
        self._client = BlobServiceClient(_to_service_url(service_url), credential=credential, **kwargs)
        self._cache = SessionCache()

    def is_request_eligible(self, request: "PipelineRequest") -> bool:
        """Checks whether the request can be signed with a session token.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: True if the request is valid.
        :rtype: bool
        """
        return _extract_container(request) is not None

    def get_session(self, request: "PipelineRequest") -> Optional[Session]:
        """Return a session, creating one on a miss.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: A session, or None if the caller should use bearer auth.
        :rtype: Session or None
        """
        container_name = _extract_container(request)
        if container_name is None:
            return None

        session = self._cache.get(container_name)
        if session is None:
            session = self._acquire(container_name)
        if session is None or session.is_fallback:
            return None
        return session

    def invalidate_session(self, request: "PipelineRequest", current: Session) -> None:
        """Drop the cached session if it still matches the rejected one.

        :param ~azure.core.pipeline.PipelineRequest request: The rejected request.
        :param current: The session that was rejected.
        :type current: Session
        """
        container_name = _extract_container(request)
        if container_name is not None:
            self._cache.invalidate(container_name, current.session_token)

    def _acquire(self, container_name: str) -> Optional[Session]:
        with self._cache.lock_container(container_name):
            existing = self._cache.get(container_name)
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

    def _create_session(self, container_name: str) -> Tuple[str, str, datetime]:
        container_client = self._client.get_container_client(container_name)
        response = container_client._client.container.create_session(  # pylint: disable=protected-access
            create_session_configuration=CreateSessionConfiguration(authentication_type="HMAC")
        )
        return _extract_session(response)


class StorageSessionPolicy(HTTPPolicy):
    """
    A pipeline policy that selects between session token and bearer token authentication.

    Eligible requests are authenticated with a session token obtained from the
    session provider. Everything else is left to the bearer token policy that
    sits earlier in the pipeline.
    """

    def __init__(
        self,
        *,
        account_name: Optional[str],
        session_provider: SessionProvider,
    ) -> None:
        """Constructs a StorageSessionPolicy.

        :keyword str account_name: Storage account name; used as the signer
            identity when signing session-authenticated requests.
        :keyword session_provider: Creates, caches, and invalidates per-container sessions.
        :paramtype session_provider: SessionProvider
        :raises ValueError: if `account_name` is `None`.
        """
        if account_name is None:
            raise ValueError(
                "Unable to determine the account name from the service URL. "
                "Supply session_account_name when using a custom endpoint."
            )
        super().__init__()
        self._account_name = account_name
        self._session_provider = session_provider

    def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Orchestrate session auth.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: The pipeline response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        session = self.on_request(request)
        response = self.next.send(request)
        return self.on_response(request, response, session)

    def on_request(self, request: "PipelineRequest") -> Optional[Session]:
        """Stamp session auth if eligible, otherwise leave the bearer header intact.

        :param ~azure.core.pipeline.PipelineRequest request: The request to (maybe) sign.
        :return: The session that was applied, else None.
        :rtype: Session or None
        """
        session = self._session_provider.get_session(request)
        if session is None or not session.session_token or not session.session_key:
            return None

        # Kept so a 401 can serve this request with bearer instead of re-signing.
        request.context[SESSION_BEARER_AUTH_KEY] = request.http_request.headers.get("Authorization")
        _apply_session_auth(request, session.session_token, session.session_key, self._account_name)
        return session

    def on_response(
        self,
        request: "PipelineRequest",
        response: "PipelineResponse",
        session: Optional[Session],
    ) -> "PipelineResponse":
        """On 401, invalidate the cached session and serve the request with bearer.

        :param ~azure.core.pipeline.PipelineRequest request: The original request.
        :param ~azure.core.pipeline.PipelineResponse response: The response to inspect.
        :param session: The session that signed the request, or `None` if bearer was used.
        :type session: Session or None
        :return: The final response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        if session is None:
            return response  # bearer was used; nothing session-related to react to

        status = response.http_response.status_code

        # 401 → drop the cached session and serve this request with bearer.
        if status == 401:
            _LOGGER.info("Session authentication: HTTP 401; invalidating session and retrying with bearer.")
            self._session_provider.invalidate_session(request, session)
            bearer = request.context.get(SESSION_BEARER_AUTH_KEY)
            if bearer:
                request.http_request.headers["Authorization"] = bearer
                response.http_response.close()
                return self.next.send(request)
            return response

        return response
