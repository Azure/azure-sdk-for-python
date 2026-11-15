# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio  # pylint:disable=do-not-import-asyncio
import uuid
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, Dict, Union

from azure.core.credentials import AccessToken, AzureSasCredential, AzureNamedKeyCredential

from .._pyamqp.error import AMQPException
from ._transport._pyamqp_transport_async import PyamqpTransportAsync
from ._async_utils import await_with_deadline, close_handler_for_cleanup
from .._base_handler import _generate_sas_token, BaseHandler as BaseHandlerSync, _get_backoff_time, _attempt_handler
from .._common._configuration import Configuration
from .._common.utils import (
    create_properties,
    strip_protocol_from_uri,
    parse_sas_credential,
    get_server_timeout_ms,
    get_attempt_timeout,
    get_remaining_timeout,
)
from .._common.constants import (
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME,
    CONTAINER_PREFIX,
    MANAGEMENT_PATH_SUFFIX,
    REQUEST_RESPONSE_TIMEOUT,
    NEXT_AVAILABLE_SESSION,
)
from ..exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    SessionLockLostError,
    OperationTimeoutError,
)

if TYPE_CHECKING:
    try:
        from uamqp.async_ops.client_async import AMQPClientAsync as uamqp_AMQPClientAsync
    except ImportError:
        pass
    from .._pyamqp.aio._client_async import AMQPClientAsync as pyamqp_AMQPClientAsync
    from .._pyamqp.message import Message as pyamqp_Message
    from azure.core.credentials_async import AsyncTokenCredential

_LOGGER = logging.getLogger(__name__)


class ServiceBusSASTokenCredential(object):
    """The shared access token credential used for authentication.
    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token: str, expiry: int) -> None:
        """
        :param str token: The shared access token string
        :param int expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.
        :param any scopes: The list of scopes for which the token has to be fetched.
        :return: The access token.
        :rtype: ~azure.core.credentials.AccessToken
        """
        return AccessToken(self.token, self.expiry)


class ServiceBusSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str) -> None:
        self.policy = policy
        self.key = key
        self.token_type = TOKEN_TYPE_SASTOKEN

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class ServiceBusAzureNamedKeyTokenCredentialAsync(object):  # pylint:disable=name-too-long
    """The named key credential used for authentication.
    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential: AzureNamedKeyCredential) -> None:
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class ServiceBusAzureSasTokenCredentialAsync(object):
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.
    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential: AzureSasCredential) -> None:
        self._credential = azure_sas_credential
        self.token_type = TOKEN_TYPE_SASTOKEN

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.
        :param any scopes: The list of scopes for which the token has to be fetched.
        :return: The access token.
        :rtype: ~azure.core.credentials.AccessToken
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class BaseHandler:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace: str,
        entity_name: str,
        credential: Union["AsyncTokenCredential", AzureSasCredential, AzureNamedKeyCredential],
        **kwargs: Any,
    ) -> None:
        self._amqp_transport = kwargs.pop("amqp_transport", PyamqpTransportAsync)

        # Keep the port for the non-TLS emulator; strip scheme/port/path otherwise.
        self.fully_qualified_namespace: str = strip_protocol_from_uri(
            fully_qualified_namespace.strip(), strip_port=kwargs.get("use_tls", True)
        )
        self._entity_name = entity_name

        subscription_name = kwargs.get("subscription_name")
        self._entity_path = self._entity_name + (("/Subscriptions/" + subscription_name) if subscription_name else "")
        self._mgmt_target = f"{self._entity_path}{MANAGEMENT_PATH_SUFFIX}"
        if isinstance(credential, AzureSasCredential):
            self._credential = ServiceBusAzureSasTokenCredentialAsync(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = ServiceBusAzureNamedKeyTokenCredentialAsync(credential)  # type: ignore
        else:
            self._credential = credential  # type: ignore
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._config = Configuration(
            hostname=self.fully_qualified_namespace, amqp_transport=self._amqp_transport, **kwargs
        )
        self._running = False
        self._handler: Optional[Union["uamqp_AMQPClientAsync", "pyamqp_AMQPClientAsync"]] = None
        self._auth_uri = None
        self._properties = create_properties(
            self._config.user_agent,
            amqp_transport=self._amqp_transport,
        )
        self._shutdown = asyncio.Event()
        # Serializes reopening the handler and closing it after a failure; created on first use so it binds to the
        # running loop.
        self._handler_lock: Optional[asyncio.Lock] = None

    def _get_handler_lock(self) -> asyncio.Lock:
        if self._handler_lock is None:
            self._handler_lock = asyncio.Lock()
        return self._handler_lock

    @classmethod
    def _convert_connection_string_to_kwargs(cls, conn_str, **kwargs):
        # pylint:disable=protected-access
        return BaseHandlerSync._convert_connection_string_to_kwargs(
            conn_str,
            token_cred_type=ServiceBusSASTokenCredential,
            key_cred_type=ServiceBusSharedKeyCredential,
            **kwargs,
        )

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _closed_underneath(self, ran_on: Any) -> bool:
        # Whether another operation closed or replaced the handler the attempt ran on. Never after a user close or for
        # a session receiver.
        return (
            ran_on is not None
            and ran_on is not self._handler
            and not self._shutdown.is_set()
            and not getattr(self, "_session", None)
        )

    async def _handle_exception(self, exception, ran_on):
        """Convert a failure to a ServiceBusError and close the handler if the error requires it.

        :param Exception exception: The failure raised by the operation.
        :param any ran_on: The handler the failed attempt ran on, or None if it ran on none. Only that handler is
         closed: concurrent operations on this instance may have reopened meanwhile.
        :return: The retryable error.
        :rtype: ~azure.servicebus.exceptions.ServiceBusError
        """
        # pylint: disable=protected-access
        error = self._amqp_transport.create_servicebus_exception(
            _LOGGER, exception, custom_endpoint_address=self._config.custom_endpoint_address
        )

        try:
            # If SessionLockLostError or ServiceBusConnectionError happen when a session receiver is running,
            # the receiver should no longer be used and should create a new session receiver
            # instance to receive from session. There are pitfalls WRT both next session IDs,
            # and the diversity of session failure modes, that motivates us to disallow this.
            if self._session and self._running and isinstance(error, (SessionLockLostError, ServiceBusConnectionError)):
                self._session._lock_lost = True
                async with self._get_handler_lock():
                    await self._close_handler()
                raise error
        except AttributeError:
            pass

        if (
            type(error) is ServiceBusError  # pylint: disable=unidiomatic-typecheck
            and not isinstance(exception, (AMQPException, ServiceBusError, ValueError, TypeError))
            and self._closed_underneath(ran_on)
        ):
            # An unexpected error from a handler that another operation closed or replaced while this attempt ran on
            # it (pyamqp raises AttributeError for a request on a closed client) only shows that: retry on the new
            # handler. Errors with a definite meaning, from the service or from the caller's arguments, keep it. A
            # session receiver cannot get its session back this way.
            return ServiceBusConnectionError(
                message="The connection was closed by another operation; retrying.", error=exception
            )

        if error._shutdown_handler and ran_on is not None and self._handler is ran_on:
            async with self._get_handler_lock():
                if self._handler is ran_on:
                    await self._close_handler()
        if not error._retryable:
            raise error

        return error

    def _check_live(self):
        """check whether the handler is alive"""
        # pylint: disable=protected-access
        if self._shutdown.is_set():
            raise ValueError(
                "The handler has already been shutdown. Please use ServiceBusClient to create a new instance."
            )
        # The following client validation is for two purposes in a session receiver:
        # 1. self._session._lock_lost is set when a session receiver encounters a connection error,
        # once there's a connection error, we don't retry on the session entity and simply raise SessionlockLostError.
        # 2. self._session._lock_expired is a hot fix as client validation for session lock expiration.
        # Because currently uamqp doesn't have the ability to detect remote session lock lost.
        # Usually the service would send a detach frame once a session lock gets expired, however, in the edge case
        # when we drain messages in a queue and try to settle messages after lock expiration,
        # we are not able to receive the detach frame by calling uamqp connection.work(),
        # Eventually this should be a fix in the uamqp library.
        # see issue: https://github.com/Azure/azure-uamqp-python/issues/183
        try:
            if self._session and (self._session._lock_lost or self._session._lock_expired):
                raise SessionLockLostError(error=self._session.auto_renew_error)
        except AttributeError:
            pass

    async def _do_retryable_operation(self, operation: Callable, timeout: Optional[float] = None, **kwargs: Any) -> Any:
        require_last_exception = kwargs.pop("require_last_exception", False)
        operation_requires_timeout = kwargs.pop("operation_requires_timeout", False)
        # Opt-in per call site so long-poll operations stay bounded only by the caller.
        apply_try_timeout = kwargs.pop("apply_try_timeout", False)
        try_timeout = self._config.try_timeout if apply_try_timeout else None
        retried_times = 0
        max_retries = self._config.retry_total

        abs_timeout_time = (time.monotonic() + timeout) if (operation_requires_timeout and timeout) else None

        while retried_times <= max_retries:
            # The handler this attempt runs on, if one is running; _open records the one it opens or finds.
            token = _attempt_handler.set(self._handler if self._running else None)
            try:
                if operation_requires_timeout:
                    remaining_timeout = (abs_timeout_time - time.monotonic()) if abs_timeout_time else None
                    attempt_timeout = get_attempt_timeout(remaining_timeout, try_timeout)
                    if attempt_timeout is not None:
                        kwargs["timeout"] = attempt_timeout
                return await operation(**kwargs)
            except StopAsyncIteration:
                raise
            except ImportError:
                # If dependency is not installed, do not retry.
                raise
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = await self._handle_exception(exception, _attempt_handler.get())
                if require_last_exception:
                    kwargs["last_exception"] = last_exception
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info(
                        "%r operation has exhausted retry. Last exception: %r.",
                        self._container_id,
                        last_exception,
                    )
                    if isinstance(last_exception, OperationTimeoutError):
                        description = str(last_exception)
                        if getattr(self, "_session_id", None) == NEXT_AVAILABLE_SESSION:
                            description += (
                                " If trying to receive from NEXT_AVAILABLE_SESSION, use max_wait_time"
                                " on the ServiceBusReceiver to control the timeout."
                            )
                        error = OperationTimeoutError(
                            message=description,
                        )
                        raise error from last_exception
                    raise last_exception from None
                await self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    abs_timeout_time=abs_timeout_time,
                )
            finally:
                _attempt_handler.reset(token)

    async def _backoff(self, retried_times, last_exception, abs_timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = _get_backoff_time(
            self._config.retry_mode,
            self._config.retry_backoff_factor,
            self._config.retry_backoff_max,
            retried_times,
        )
        if backoff <= self._config.retry_backoff_max and (
            abs_timeout_time is None or (backoff + time.monotonic()) <= abs_timeout_time
        ):
            await asyncio.sleep(backoff)
            _LOGGER.info(
                "%r has an exception (%r). Retrying...",
                entity_name,
                last_exception,
            )
        else:
            _LOGGER.info(
                "%r operation has timed out. Last exception before timeout is (%r)",
                entity_name,
                last_exception,
            )
            if isinstance(last_exception, OperationTimeoutError):
                description = str(last_exception)
                if getattr(self, "_session_id", None) == NEXT_AVAILABLE_SESSION:
                    description += (
                        " If trying to receive from NEXT_AVAILABLE_SESSION, use max_wait_time"
                        " on the ServiceBusReceiver to control the timeout."
                    )
                error = OperationTimeoutError(
                    message=description,
                )
                raise error from last_exception
            raise last_exception

    async def _mgmt_request_response(
        self,
        mgmt_operation: bytes,
        message: Any,
        callback: Callable,
        keep_alive_associated_link: bool = True,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> "pyamqp_Message":
        """
        Execute an amqp management operation.

        :param bytes mgmt_operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param callback: The callback which is used to parse the returning message.
        :type callback: Callable[int, ~uamqp.message.Message, str]
        :param bool keep_alive_associated_link: A boolean flag for keeping
         associated amqp sender/receiver link alive when
         executing operation on mgmt links.
        :param float or None timeout: timeout in seconds for executing the mgmt operation.
        :return: The message response.
        :rtype: Message
        """
        attempt_started = time.monotonic()
        deadline = (attempt_started + timeout) if timeout is not None else None
        await self._open(timeout)
        # Pin the handler for the request and record it for this attempt, as in the sync client.
        handler = self._handler or _attempt_handler.get()
        _attempt_handler.set(handler)
        # Open and request share one attempt budget, so the request gets what is left.
        timeout = get_remaining_timeout(timeout, attempt_started)

        application_properties = {}
        # Some mgmt calls do not support an associated link name (such as list_sessions).  Most do, so on by default.
        if keep_alive_associated_link:
            try:
                application_properties = {
                    ASSOCIATEDLINKPROPERTYNAME: self._amqp_transport.get_handler_link_name(handler)
                }
            except AttributeError:
                pass

        application_properties[REQUEST_RESPONSE_TIMEOUT] = self._amqp_transport.AMQP_UINT_VALUE(
            get_server_timeout_ms(timeout)
        )

        mgmt_msg = self._amqp_transport.create_mgmt_msg(  # type: ignore  # TODO: fix mypy
            message=message,
            application_properties=application_properties,
            config=self._config,
            reply_to=self._mgmt_target,
            **kwargs,
        )

        try:
            return await await_with_deadline(
                self._amqp_transport.mgmt_client_request_async(
                    handler,
                    mgmt_msg,
                    operation=mgmt_operation,
                    operation_type=MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
                    node=self._mgmt_target.encode(self._config.encoding),
                    timeout=timeout,
                    callback=callback,
                ),
                deadline,
                "Timed out waiting for the management operation to complete.",
            )
        except Exception as exp:
            if isinstance(exp, self._amqp_transport.TIMEOUT_ERROR):
                raise OperationTimeoutError(error=exp) from exp
            raise

    async def _mgmt_request_response_with_retry(
        self,
        mgmt_operation: bytes,
        message: Dict[str, Any],
        callback: Callable,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        return await self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation,
            message=message,
            callback=callback,
            timeout=timeout,
            operation_requires_timeout=True,
            apply_try_timeout=True,
            **kwargs,
        )

    async def _open(self, timeout: Optional[float] = None):
        # Read before _running: if another operation closes the handler in between, the attempt still records the
        # handler it runs on, so its failure on the closed handler is retried.
        handler = self._handler
        if self._running and handler is not None:
            _attempt_handler.set(handler)
            return
        started = time.monotonic()
        lock = self._get_handler_lock()
        # Concurrent operations that find the handler closed share one reopen: the first creates and opens
        # the new handler, the others wait here, within their own timeout, and then find it running.
        # Acquiring in a separate task lets the wait end on timeout or cancellation without leaking the lock.
        acquire = asyncio.ensure_future(lock.acquire())
        try:
            await asyncio.wait((acquire,), timeout=None if timeout is None else max(timeout, 0))
        except BaseException:
            # Cancelled while waiting: give the lock back if it was granted meanwhile.
            if acquire.done() and not acquire.cancelled() and acquire.exception() is None:
                lock.release()
            else:
                acquire.cancel()
            raise
        if not acquire.done():
            # Cancelling a pending acquire never leaves the lock held.
            acquire.cancel()
            raise OperationTimeoutError(message="Timed out waiting for another operation to open the AMQP link.")
        # Raises, without the lock, if the acquire itself was cancelled.
        acquire.result()
        try:
            # A close() while this operation waited: the handler must not reopen.
            self._check_live()
            if not self._running or self._handler is None:
                # _running stays set while a detached handler is closing; clear it so _open_handler opens a new one.
                self._running = False
                if timeout is not None:
                    # Time spent waiting for another caller's open counts against this attempt.
                    timeout -= time.monotonic() - started
                try:
                    await self._open_handler(timeout)
                except BaseException as exception:
                    # A failure after the link came up (e.g. registering the session with the lock renewer) must not
                    # leave it running.
                    if self._running:
                        await close_handler_for_cleanup(self._close_handler(), None)
                    if isinstance(exception, Exception) and self._shutdown.is_set():
                        # A close() during the open made it fail.
                        self._check_live()
                    raise
                if self._shutdown.is_set():
                    # close() ran during the open, possibly before the new handler was attached: close that too.
                    await self._close_handler()
                    self._check_live()
            _attempt_handler.set(self._handler)
        finally:
            lock.release()

    async def _open_handler(self, timeout: Optional[float] = None):
        """Create and open a new handler. Called with the handler lock held.

        :param float or None timeout: The time left to open the handler, or None when unbounded.
        :return: None
        :rtype: None
        """
        raise ValueError("Subclass should override the method.")

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open, operation_requires_timeout=True, apply_try_timeout=True)

    async def _close_handler(self):
        # Detach the handler before closing it, so operations starting meanwhile reopen instead of using the closing
        # client. _running stays set until the close ends: settlement and lock renewal treat a receiver that is not
        # running as shut down.
        handler, self._handler = self._handler, None
        try:
            if handler:
                await handler.close_async()
        finally:
            self._running = False

    async def close(self) -> None:
        """Close down the handler connection.

        If the handler has already closed, this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :rtype: None
        """
        # Set first, so a failure on the closing handler is not retried on a new one.
        self._shutdown.set()
        await self._close_handler()
