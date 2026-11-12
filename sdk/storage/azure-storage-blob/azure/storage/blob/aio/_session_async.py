# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio  # pylint: disable=do-not-import-asyncio
import copy
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, cast, Dict, Optional, Tuple, TYPE_CHECKING

from typing_extensions import Protocol

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.pipeline.policies import AsyncHTTPPolicy

from .._generated.models import CreateSessionConfiguration, CreateSessionResponse
from .._session import (
    SESSION_BEARER_AUTH_KEY,
    Session,
    _apply_session_auth,
    _extract_container,
    _extract_session,
    _is_cooldown_error,
    _to_service_url,
)
from .._shared.base_client_async import AsyncTransportWrapper

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse
    from azure.core.pipeline.transport import AsyncHttpTransport
    from .._shared.base_client_async import AsyncStorageAccountHostsMixin

_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc


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
        client: "AsyncStorageAccountHostsMixin",
        credential: Any,
        transport: "AsyncHttpTransport",
        audience: Optional[str],
        pipeline_kwargs: Dict[str, Any],
    ) -> AsyncStorageSessionPolicy:
        provider = session_provider
        if provider is None:
            sub_kwargs = dict(pipeline_kwargs)
            sub_kwargs.pop("_configuration", None)
            sub_kwargs.pop("pipeline", None)
            sub_kwargs.pop("sdk_moniker", None)
            sub_kwargs["transport"] = AsyncTransportWrapper(transport)
            if sub_kwargs.get("retry_policy") is not None:
                sub_kwargs["retry_policy"] = copy.copy(sub_kwargs["retry_policy"])
            sub_kwargs.pop("_additional_pipeline_policies", None)
            provider = ContainerSessionProvider(
                f"{client.scheme}://{client.primary_hostname}",
                cast("AsyncTokenCredential", credential),
                audience=audience,
                **sub_kwargs,
            )
        return AsyncStorageSessionPolicy(
            account_name=session_account_name or client.account_name,
            session_provider=provider,
        )

    kwargs["_session_policy_factory"] = _factory


class SessionProvider(Protocol):
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

    async def invalidate(self, container_name: str, session_token: Optional[str] = None) -> None:
        """Drop the cached session if it still matches the rejected token.

        :param str container_name: The container name.
        :param str session_token: The rejected token, or None if unknown.
        """
        async with self.lock_container(container_name):
            cached = self._entry.get(container_name, None)
            if cached is not None and cached.session_token == session_token:
                self._entry.pop(container_name, None)


class ContainerSessionProvider:
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
        from ._blob_service_client_async import BlobServiceClient  # module-level import would cycle

        if not hasattr(credential, "get_token"):
            raise TypeError(
                f"ContainerSessionProvider requires an AsyncTokenCredential; " f"received {type(credential).__name__}."
            )
        kwargs["logging_body"] = False
        self._client = BlobServiceClient(_to_service_url(service_url), credential=credential, **kwargs)
        self._cache = AsyncSessionCache()

    async def __aenter__(self) -> "ContainerSessionProvider":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the client used to issue CreateSession calls.

        Only meaningful for a provider you constructed yourself; one created by a
        client shares that client's transport and closing it is a no-op.
        """
        await self._client.close()

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
        :rtype: Session or None
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
        :type current: Session
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


class AsyncStorageSessionPolicy(AsyncHTTPPolicy):
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
        """Constructs an AsyncStorageSessionPolicy.

        :keyword str account_name: Storage account name; used as the signer
            identity when signing session-authenticated requests.
        :keyword session_provider: Creates, caches, and invalidates per-container sessions.
        :paramtype session_provider: ~azure.storage.blob.aio._session_async.SessionProvider
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

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Orchestrate session auth.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: The pipeline response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        session = await self.on_request(request)
        response = await self.next.send(request)
        return await self.on_response(request, response, session)

    async def on_request(self, request: "PipelineRequest") -> Optional[Session]:
        """Stamp session auth if eligible, otherwise leave the bearer header intact.

        :param ~azure.core.pipeline.PipelineRequest request: The request to (maybe) sign.
        :return: The session that was applied, else None.
        :rtype: ~azure.storage.blob._session.Session or None
        """
        session = await self._session_provider.get_session(request)
        if session is None or not session.session_token or not session.session_key:
            return None

        # Kept so a 401 can serve this request with bearer instead of re-signing.
        request.context[SESSION_BEARER_AUTH_KEY] = request.http_request.headers.get("Authorization")
        _apply_session_auth(request, session.session_token, session.session_key, self._account_name)
        return session

    async def on_response(
        self,
        request: "PipelineRequest",
        response: "PipelineResponse",
        session: Optional[Session],
    ) -> "PipelineResponse":
        """On 401, invalidate the cached session and serve the request with bearer.

        :param ~azure.core.pipeline.PipelineRequest request: The original request.
        :param ~azure.core.pipeline.PipelineResponse response: The response to inspect.
        :param session: The session that signed the request, or `None` if bearer was used.
        :type session: ~azure.storage.blob._session.Session or None
        :return: The final response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        if session is None:
            return response  # bearer was used; nothing session-related to react to

        if response.http_response.status_code == 401:
            _LOGGER.info("Session authentication: HTTP 401; invalidating session and retrying with bearer.")
            await self._session_provider.invalidate_session(request, session)
            bearer = request.context.get(SESSION_BEARER_AUTH_KEY)
            if bearer:
                request.http_request.headers["Authorization"] = bearer
                await response.http_response.close()
                return await self.next.send(request)

        return response
