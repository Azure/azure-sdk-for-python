# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import random
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, TYPE_CHECKING

from azure.core.exceptions import AzureError, StreamClosedError, StreamConsumedError
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    AsyncHTTPPolicy,
)

from .authentication import AzureSigningError, StorageHttpChallenge
from .constants import DEFAULT_OAUTH_SCOPE
from .models import StorageErrorCode
from .policies import (
    _analyze_request,
    _apply_session_auth,
    _prepare_content_validation,
    _validate_content_response,
    encode_base64,
    is_retry,
    StorageRetryPolicy,
)
from .streams_async import AsyncStructuredMessageDecoder
from .validation import (
    calculate_content_md5,
    is_md5_validation,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import
        PipelineRequest,
        PipelineResponse,
    )


_LOGGER = logging.getLogger(__name__)


async def retry_hook(settings, **kwargs):
    if settings["hook"]:
        if asyncio.iscoroutine(settings["hook"]):
            await settings["hook"](retry_count=settings["count"] - 1, location_mode=settings["mode"], **kwargs)
        else:
            settings["hook"](retry_count=settings["count"] - 1, location_mode=settings["mode"], **kwargs)


async def is_checksum_retry(response):
    validate_content = response.context.get("validate_content", False)
    if not validate_content:
        return False

    # Legacy code - evaluate retry only on validate_content=True
    if validate_content is True and response.http_response.headers.get("content-md5"):
        if hasattr(response.http_response, "load_body"):
            try:
                await response.http_response.load_body()  # Load the body in memory and close the socket
            except (StreamClosedError, StreamConsumedError):
                pass
        computed_md5 = response.http_request.headers.get("content-md5", None) or encode_base64(
            calculate_content_md5(response.http_response.body())
        )
        if response.http_response.headers["content-md5"] != computed_md5:
            return True
    return False


class AsyncContentValidationPolicy(AsyncHTTPPolicy):
    """A pipeline policy that performs content validation on uploads and downloads when enabled by the user.
    This is enabled by setting the "validate_content" key in the request context. When enabled, this policy will
    calculate and verify content checksums for uploads and downloads, and raise an exception if a mismatch is detected.
    """

    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        super().__init__()

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        _prepare_content_validation(request)

        response = await self.next.send(request)

        validate_content = response.context.get("validate_content", False)
        if validate_content and is_md5_validation(validate_content):
            if hasattr(response.http_response, "load_body"):
                try:
                    await response.http_response.load_body()
                except (StreamClosedError, StreamConsumedError):
                    pass

        _validate_content_response(request, response, AsyncStructuredMessageDecoder)

        return response


class AsyncStorageResponseHook(AsyncHTTPPolicy):

    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        super(AsyncStorageResponseHook, self).__init__()

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        # Values could be 0
        data_stream_total = request.context.get("data_stream_total")
        if data_stream_total is None:
            data_stream_total = request.context.options.pop("data_stream_total", None)
        download_stream_current = request.context.get("download_stream_current")
        if download_stream_current is None:
            download_stream_current = request.context.options.pop("download_stream_current", None)
        upload_stream_current = request.context.get("upload_stream_current")
        if upload_stream_current is None:
            upload_stream_current = request.context.options.pop("upload_stream_current", None)

        response_callback = request.context.get("response_callback") or request.context.options.pop(
            "raw_response_hook", self._response_callback
        )

        response = await self.next.send(request)
        will_retry = is_retry(response, request.context.options.get("mode")) or await is_checksum_retry(response)

        # Auth error could come from Bearer challenge, in which case this request will be made again
        is_auth_error = response.http_response.status_code == 401
        should_update_counts = not (will_retry or is_auth_error)

        if should_update_counts and download_stream_current is not None:
            download_stream_current += int(response.http_response.headers.get("Content-Length", 0))
            if data_stream_total is None:
                content_range = response.http_response.headers.get("Content-Range")
                if content_range:
                    data_stream_total = int(content_range.split(" ", 1)[1].split("/", 1)[1])
                else:
                    data_stream_total = download_stream_current
        elif should_update_counts and upload_stream_current is not None:
            upload_stream_current += int(response.http_request.headers.get("Content-Length", 0))
        for pipeline_obj in [request, response]:
            if hasattr(pipeline_obj, "context"):
                pipeline_obj.context["data_stream_total"] = data_stream_total
                pipeline_obj.context["download_stream_current"] = download_stream_current
                pipeline_obj.context["upload_stream_current"] = upload_stream_current
        if response_callback:
            if asyncio.iscoroutine(response_callback):
                await response_callback(response)  # type: ignore
            else:
                response_callback(response)
            request.context["response_callback"] = response_callback
        return response


class AsyncStorageRetryPolicy(StorageRetryPolicy):
    """
    The base class for Exponential and Linear retries containing shared code.
    """

    async def sleep(self, settings, transport):
        backoff = self.get_backoff_time(settings)
        if not backoff or backoff < 0:
            return
        await transport.sleep(backoff)

    async def send(self, request):
        retries_remaining = True
        response = None
        retry_settings = self.configure_retries(request)
        while retries_remaining:
            try:
                response = await self.next.send(request)
                if is_retry(response, retry_settings["mode"]) or await is_checksum_retry(response):
                    retries_remaining = self.increment(
                        retry_settings,
                        request=request.http_request,
                        response=response.http_response,
                    )
                    if retries_remaining:
                        await retry_hook(
                            retry_settings,
                            request=request.http_request,
                            response=response.http_response,
                            error=None,
                        )
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                break
            except AzureError as err:
                if isinstance(err, AzureSigningError):
                    raise
                retries_remaining = self.increment(retry_settings, request=request.http_request, error=err)
                if retries_remaining:
                    await retry_hook(
                        retry_settings,
                        request=request.http_request,
                        response=None,
                        error=err,
                    )
                    await self.sleep(retry_settings, request.context.transport)
                    continue
                raise err
        if retry_settings["history"]:
            response.context["history"] = retry_settings["history"]
        response.http_response.location_mode = retry_settings["mode"]
        return response


class ExponentialRetry(AsyncStorageRetryPolicy):
    """Exponential retry."""

    initial_backoff: int
    """The initial backoff interval, in seconds, for the first retry."""
    increment_base: int
    """The base, in seconds, to increment the initial_backoff by after the
    first retry."""
    random_jitter_range: int
    """A number in seconds which indicates a range to jitter/randomize for the back-off interval."""

    def __init__(
        self,
        initial_backoff: int = 15,
        increment_base: int = 3,
        retry_total: int = 3,
        retry_to_secondary: bool = False,
        random_jitter_range: int = 3,
        **kwargs,
    ) -> None:
        """
        Constructs an Exponential retry object. The initial_backoff is used for
        the first retry. Subsequent retries are retried after initial_backoff +
        increment_power^retry_count seconds. For example, by default the first retry
        occurs after 15 seconds, the second after (15+3^1) = 18 seconds, and the
        third after (15+3^2) = 24 seconds.

        :param int initial_backoff:
            The initial backoff interval, in seconds, for the first retry.
        :param int increment_base:
            The base, in seconds, to increment the initial_backoff by after the
            first retry.
        :param int max_attempts:
            The maximum number of retry attempts.
        :param bool retry_to_secondary:
            Whether the request should be retried to secondary, if able. This should
            only be enabled of RA-GRS accounts are used and potentially stale data
            can be handled.
        :param int random_jitter_range:
            A number in seconds which indicates a range to jitter/randomize for the back-off interval.
            For example, a random_jitter_range of 3 results in the back-off interval x to vary between x+3 and x-3.
        """
        self.initial_backoff = initial_backoff
        self.increment_base = increment_base
        self.random_jitter_range = random_jitter_range
        super(ExponentialRetry, self).__init__(retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings: Dict[str, Any]) -> float:
        """
        Calculates how long to sleep before retrying.

        :param Dict[str, Any] settings: The configurable values pertaining to the backoff time.
        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        backoff = self.initial_backoff + (0 if settings["count"] == 0 else pow(self.increment_base, settings["count"]))
        random_range_start = backoff - self.random_jitter_range if backoff > self.random_jitter_range else 0
        random_range_end = backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class LinearRetry(AsyncStorageRetryPolicy):
    """Linear retry."""

    initial_backoff: int
    """The backoff interval, in seconds, between retries."""
    random_jitter_range: int
    """A number in seconds which indicates a range to jitter/randomize for the back-off interval."""

    def __init__(
        self,
        backoff: int = 15,
        retry_total: int = 3,
        retry_to_secondary: bool = False,
        random_jitter_range: int = 3,
        **kwargs: Any,
    ) -> None:
        """
        Constructs a Linear retry object.

        :param int backoff:
            The backoff interval, in seconds, between retries.
        :param int max_attempts:
            The maximum number of retry attempts.
        :param bool retry_to_secondary:
            Whether the request should be retried to secondary, if able. This should
            only be enabled of RA-GRS accounts are used and potentially stale data
            can be handled.
        :param int random_jitter_range:
            A number in seconds which indicates a range to jitter/randomize for the back-off interval.
            For example, a random_jitter_range of 3 results in the back-off interval x to vary between x+3 and x-3.
        """
        self.backoff = backoff
        self.random_jitter_range = random_jitter_range
        super(LinearRetry, self).__init__(retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings: Dict[str, Any]) -> float:
        """
        Calculates how long to sleep before retrying.

        :param Dict[str, Any] settings: The configurable values pertaining to the backoff time.
        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        # the backoff interval normally does not change, however there is the possibility
        # that it was modified by accessing the property directly after initializing the object
        random_range_start = self.backoff - self.random_jitter_range if self.backoff > self.random_jitter_range else 0
        random_range_end = self.backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class AsyncStorageBearerTokenCredentialPolicy(AsyncBearerTokenCredentialPolicy):
    """Custom Bearer token credential policy for following Storage Bearer challenges"""

    def __init__(self, credential: "AsyncTokenCredential", audience: str, **kwargs: Any) -> None:
        super(AsyncStorageBearerTokenCredentialPolicy, self).__init__(credential, audience, **kwargs)

    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        try:
            auth_header = response.http_response.headers.get("WWW-Authenticate")
            challenge = StorageHttpChallenge(auth_header)
        except ValueError:
            return False

        scope = challenge.resource_id + DEFAULT_OAUTH_SCOPE
        await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)

        return True




class AsyncSessionCache(SessionCache):
    """Async variant of :class:`SessionCache`.

    Reuses the lock-free, non-mutating read path and the immutable
    Session snapshots from the sync cache, but serializes the
    per-container CreateSession single-flight with asynchronous locks.
    """

    def __init__(self) -> None:
        super().__init__()
        self._async_locks: Dict[str, asyncio.Lock] = {}

    def lock_container_async(self, container_name: str) -> asyncio.Lock:
        """Return the per-container asyncio lock, creating it exactly once.

        Lock creation is not awaited, so it is safe to do without holding a
        lock: the event loop guarantees this runs to completion without
        interleaving other coroutines.

        :param str container_name: The container to get the lock for.
        :return: The single asyncio lock associated with the container.
        :rtype: ~asyncio.Lock
        """
        existing = self._async_locks.get(container_name)
        if existing is not None:
            return existing
        return self._async_locks.setdefault(container_name, asyncio.Lock())


class AsyncStorageSessionPolicy(AsyncHTTPPolicy):
    """Constructs an AsyncStorageSessionPolicy.

    Eligible blob download GETs are authenticated with a per-container session
    token; everything else is delegated unchanged to the bearer credential
    policy that sits earlier in the pipeline.
    """

    def __init__(
        self,
        *,
        account_name: str,
        session_client_factory: Callable[[str], Any],
    ) -> None:
        """Constructs an AsyncStorageSessionPolicy.

        :keyword str account_name: Storage account name; used as the signer
            identity when signing session-authenticated requests.
        :keyword session_client_factory: A callable that, given a container URL,
            returns a session-disabled generated async client whose pipeline
            uses OAuth/bearer auth. Invoked (and awaited) to issue CreateSession.
        :paramtype session_client_factory: Callable[[str], Any]
        :raises ValueError: if account_name or session_client_factory is None.
        """
        if account_name is None or session_client_factory is None:
            raise ValueError("account_name and session_client_factory are required.")
        super().__init__()
        self._account_name = account_name
        self._session_client_factory = session_client_factory
        self._enabled = True
        self._cache = AsyncSessionCache()

    async def _create_session(self, container_url: str) -> Tuple[str, str, datetime]:
        config = CreateSessionConfiguration(authentication_type="HMAC")
        client = self._session_client_factory(container_url)
        response = await client.container.create_session(create_session_configuration=config)
        return _extract_session(response)

    async def _refresh_session_token(self, container_name: str, container_url: str) -> Optional[Session]:
        """Acquire (or re-use) a session under per-container async single-flight.

        :param str container_name: The container key for the cache and lock.
        :param str container_url: The container-scoped URL for the CreateSession call.
        :return: A live session, a fallback sentinel, or None if unusable.
        :rtype: ~azure.storage.blob._shared.policies.Session or None
        """
        async with self._cache.lock_container_async(container_name):
            existing = self._cache.get(container_name)
            if existing is not None and not existing.expired():
                return existing
            try:
                token, key, expires_at = await self._create_session(container_url)
                self._cache.put(container_name, token, key, expires_at)
            except (AzureError, ValueError):
                _LOGGER.warning(
                    "CreateSession failed for container '%s'; falling back to bearer for %d seconds.",
                    container_name,
                    int(SessionCache.FALLBACK_COOLDOWN.total_seconds()),
                    exc_info=True,
                )
                self._cache.put_fallback(container_name)
            return self._cache.get(container_name)

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Orchestrate session auth.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: The pipeline response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        container_name = await self.on_request(request)
        response = await self.next.send(request)
        return await self.on_response(request, response, container_name)

    async def on_request(self, request: "PipelineRequest") -> Optional[str]:
        """Stamp session auth if eligible, otherwise leave the bearer header intact.

        :param ~azure.core.pipeline.PipelineRequest request: The request to (maybe) sign.
        :return: The container name if a session was applied, else None.
        :rtype: str or None
        """
        if not self._enabled:
            return None
        analysis = _analyze_request(request)
        if analysis is None:
            return None
        container_name, container_url = analysis

        session = self._cache.get(container_name)
        if session is None:
            # True miss/expiry (a live fallback sentinel is returned by get(),
            # so we never reach refresh while the cooldown is active).
            session = await self._refresh_session_token(container_name, container_url)

        if session is None or session.is_fallback or not session.session_token or not session.session_key:
            return None

        _apply_session_auth(request, session.session_token, session.session_key, self._account_name)
        return container_name

    async def on_response(
        self,
        request: "PipelineRequest",
        response: "PipelineResponse",
        container_name: Optional[str],
    ) -> "PipelineResponse":
        """React to session-related failures: cooldown sentinel or one-shot re-acquire.

        :param ~azure.core.pipeline.PipelineRequest request: The original request.
        :param ~azure.core.pipeline.PipelineResponse response: The response to inspect.
        :param container_name: Container that was session-signed, or None if bearer was used.
        :type container_name: str or None
        :return: The final response (possibly from a one-shot retry).
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        if container_name is None:
            return response  # bearer was used; nothing session-related to react to

        status = response.http_response.status_code
        error_code = response.http_response.headers.get("x-ms-error-code", "")

        if error_code == StorageErrorCode.FEATURE_NOT_ENABLED:
            _LOGGER.info("Session feature not enabled on this account; disabling session auth.")
            self._enabled = False
            return response

        # Unavailable / 5xx → negative-cache cooldown.
        if error_code == StorageErrorCode.SESSIONS_UNAVAILABLE or status >= 500:
            _LOGGER.warning(
                "Session authentication: '%s' (HTTP %d) on container '%s'; bearer fallback for %d seconds.",
                error_code or "5xx",
                status,
                container_name,
                int(SessionCache.FALLBACK_COOLDOWN.total_seconds()),
            )
            async with self._cache.lock_container_async(container_name):
                self._cache.put_fallback(container_name)
            return response

        # 401 → invalidate + re-acquire ONCE, then resend.
        if status == 401 and not request.context.options.get(SESSION_RETRIED_CONTEXT_KEY):
            _LOGGER.info("Session authentication: HTTP 401 on '%s'; re-acquiring once.", container_name)
            used_token = _used_session_token(request)
            async with self._cache.lock_container_async(container_name):
                self._cache.invalidate(container_name, used_token)
            request.context.options[SESSION_RETRIED_CONTEXT_KEY] = True
            retried_container = await self.on_request(request)
            retried_response = await self.next.send(request)
            return await self.on_response(request, retried_response, retried_container)

        return response
