# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import contextvars
import logging
import uuid
import time
import threading
from datetime import timedelta
from typing import cast, Optional, Tuple, TYPE_CHECKING, Dict, Any, Callable, Union
from azure.core.credentials import AccessToken, AzureSasCredential, AzureNamedKeyCredential
from azure.core.pipeline.policies import RetryMode

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from ._pyamqp.error import AMQPException
from ._pyamqp.utils import generate_sas_token
from ._transport._pyamqp_transport import PyamqpTransport

from ._common._configuration import Configuration
from .exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    OperationTimeoutError,
    SessionLockLostError,
)
from ._common.utils import (
    create_properties,
    strip_protocol_from_uri,
    parse_sas_credential,
    get_server_timeout_ms,
    get_attempt_timeout,
    get_remaining_timeout,
)
from ._common.constants import (
    CONTAINER_PREFIX,
    MANAGEMENT_PATH_SUFFIX,
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME,
    REQUEST_RESPONSE_TIMEOUT,
    NEXT_AVAILABLE_SESSION,
)

if TYPE_CHECKING:
    try:
        from uamqp import AMQPClient as uamqp_AMQPClientSync
    except ImportError:
        pass

    from ._pyamqp.message import Message as pyamqp_Message
    from ._pyamqp.client import AMQPClient as pyamqp_AMQPClientSync
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)

# The handler the current operation attempt runs on, so its failure closes only that handler: concurrent operations on
# the same instance may have reopened meanwhile, and closing their new handler would fail them.
_attempt_handler: contextvars.ContextVar[Any] = contextvars.ContextVar("servicebus_attempt_handler", default=None)


def _parse_conn_str(  # pylint:disable=too-many-statements
    conn_str: str, check_case: Optional[bool] = False
) -> Tuple[str, Optional[str], Optional[str], str, Optional[str], Optional[int], bool]:
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path: Optional[str] = None
    shared_access_signature: Optional[str] = None
    shared_access_signature_expiry: Optional[int] = None
    use_emulator: Optional[str] = None

    # split connection string into properties
    conn_properties = [s.split("=", 1) for s in conn_str.strip().rstrip(";").split(";")]
    if any(len(tup) != 2 for tup in conn_properties):
        raise ValueError("Connection string is either blank or malformed.")
    conn_settings = dict(conn_properties)  # type: ignore

    # case sensitive check when parsing for connection string properties
    if check_case:
        shared_access_key = conn_settings.get("SharedAccessKey")
        shared_access_key_name = conn_settings.get("SharedAccessKeyName")
        endpoint = conn_settings.get("Endpoint")
        entity_path = conn_settings.get("EntityPath")
        use_emulator = conn_settings.get("UseDevelopmentEmulator")

    # non case sensitive check when parsing connection string for internal use
    for key, value in conn_settings.items():
        # only sas check is non case sensitive for both conn str properties and internal use
        if key.lower() == "sharedaccesssignature":
            shared_access_signature = value
            try:
                # Expiry can be stored in the "se=<timestamp>" clause of the token. ('&'-separated key-value pairs)
                shared_access_signature_expiry = int(
                    shared_access_signature.split("se=")[1].split("&")[0]  # type: ignore
                )
            except (
                IndexError,
                TypeError,
                ValueError,
            ):  # Fallback since technically expiry is optional.
                # An arbitrary, absurdly large number, since you can't renew.
                shared_access_signature_expiry = int(time.time() * 2)
        if not check_case:
            if key.lower() == "endpoint":
                endpoint = value.rstrip("/")
            elif key.lower() == "hostname":
                endpoint = value.rstrip("/")
            elif key.lower() == "sharedaccesskeyname":
                shared_access_key_name = value
            elif key.lower() == "sharedaccesskey":
                shared_access_key = value
            elif key.lower() == "entitypath":
                entity_path = value
            elif key.lower() == "usedevelopmentemulator":
                use_emulator = value

    entity = cast(str, entity_path)

    # check that endpoint is valid
    if not endpoint:
        raise ValueError("Connection string is either blank or malformed.")
    parsed = urlparse(endpoint)
    if not parsed.netloc:
        raise ValueError("Invalid Endpoint on the Connection String.")
    host = cast(str, parsed.netloc.strip())

    emulator = use_emulator == "true"

    if any([shared_access_key, shared_access_key_name]) and not all([shared_access_key, shared_access_key_name]):
        raise ValueError("Connection string must have both SharedAccessKeyName and SharedAccessKey.")
    if shared_access_signature and shared_access_key:
        raise ValueError("Only one of the SharedAccessKey or SharedAccessSignature must be present.")
    if not shared_access_signature and not shared_access_key:
        raise ValueError("At least one of the SharedAccessKey or SharedAccessSignature must be present.")

    return (
        host,
        str(shared_access_key_name) if shared_access_key_name else None,
        str(shared_access_key) if shared_access_key else None,
        entity,
        str(shared_access_signature) if shared_access_signature else None,
        shared_access_signature_expiry,
        emulator,
    )


def _generate_sas_token(uri: str, policy: str, key: str, expiry: Optional[timedelta] = None) -> AccessToken:
    """Create a shared access signiture token as a string literal.
    :param str uri: The resource URI.
    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    :param ~datetime.timedelta or None expiry: The time period that the token is valid for.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = timedelta(hours=1)  # Default to 1 hour.

    abs_expiry = int(time.time()) + expiry.seconds
    token = generate_sas_token(uri, policy, key, abs_expiry)
    return AccessToken(token=token, expires_on=abs_expiry)


def _get_backoff_time(retry_mode, backoff_factor, backoff_max, retried_times):
    if retry_mode == RetryMode.Fixed:
        backoff_value = backoff_factor
    else:
        backoff_value = backoff_factor * (2**retried_times)
    return min(backoff_max, backoff_value)


class ServiceBusSASTokenCredential(object):
    """The shared access token credential used for authentication.
    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token: str, expiry: int) -> None:
        """
        :param str token: The shared access token string
        :param float expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.
        :param str scopes: The list of scopes for which the token has access.
        :return: AccessToken object
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

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class ServiceBusAzureNamedKeyTokenCredential(object):
    """The named key credential used for authentication.
    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential: AzureNamedKeyCredential) -> None:
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        name, key = self._credential.named_key
        return _generate_sas_token(scopes[0], name, key)


class ServiceBusAzureSasTokenCredential(object):
    """The shared access token credential used for authentication
    when AzureSasCredential is provided.
    :param azure_sas_credential: The credential to be used for authentication.
    :type azure_sas_credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(self, azure_sas_credential: AzureSasCredential) -> None:
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.
        :param str scopes: The list of scopes for which the token has access.
        :return: AccessToken object
        :rtype: ~azure.core.credentials.AccessToken
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class BaseHandler:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace: str,
        entity_name: str,
        credential: Union["TokenCredential", AzureSasCredential, AzureNamedKeyCredential],
        **kwargs: Any,
    ) -> None:
        self._amqp_transport = kwargs.pop("amqp_transport", PyamqpTransport)

        # Keep the port for the non-TLS emulator; strip scheme/port/path otherwise.
        self.fully_qualified_namespace: str = strip_protocol_from_uri(
            fully_qualified_namespace.strip(), strip_port=kwargs.get("use_tls", True)
        )
        self._entity_name = entity_name

        subscription_name = kwargs.get("subscription_name")
        self._entity_path = self._entity_name + (("/Subscriptions/" + subscription_name) if subscription_name else "")
        self._mgmt_target = f"{self._entity_path}{MANAGEMENT_PATH_SUFFIX}"
        if isinstance(credential, AzureSasCredential):
            self._credential = ServiceBusAzureSasTokenCredential(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = ServiceBusAzureNamedKeyTokenCredential(credential)  # type: ignore
        else:
            self._credential = credential  # type: ignore
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._config = Configuration(
            hostname=self.fully_qualified_namespace, amqp_transport=self._amqp_transport, **kwargs
        )
        self._running = False
        self._handler: Optional[Union["uamqp_AMQPClientSync", "pyamqp_AMQPClientSync"]] = None
        self._auth_uri = None
        self._properties = create_properties(
            self._config.user_agent,
            amqp_transport=self._amqp_transport,
        )
        self._shutdown = threading.Event()
        # Serializes reopening the handler and closing it after a failure.
        self._handler_lock = threading.RLock()

    @classmethod
    def _convert_connection_string_to_kwargs(cls, conn_str: str, **kwargs: Any) -> Dict[str, Any]:
        host, policy, key, entity_in_conn_str, token, token_expiry, emulator = _parse_conn_str(conn_str)
        queue_name = kwargs.get("queue_name")
        topic_name = kwargs.get("topic_name")
        if not (queue_name or topic_name or entity_in_conn_str):
            raise ValueError(
                "Entity name is missing. Please specify `queue_name` or `topic_name`"
                " or use a connection string including the entity information."
            )

        if queue_name and topic_name:
            raise ValueError("`queue_name` and `topic_name` can not be specified simultaneously.")

        entity_in_kwargs = queue_name or topic_name
        if entity_in_conn_str and entity_in_kwargs and (entity_in_conn_str != entity_in_kwargs):
            raise ValueError(
                f"The queue or topic name provided: {entity_in_conn_str} which does not match the EntityPath in"
                f" the connection string passed to the ServiceBusClient constructor: {entity_in_kwargs}."
            )

        kwargs["fully_qualified_namespace"] = host
        kwargs["entity_name"] = entity_in_conn_str or entity_in_kwargs
        # Check if emulator is in use, unset tls if it is
        if emulator:
            kwargs["use_tls"] = False

        # Set the type to sync credentials, unless async credentials are passed in.
        token_cred_type = kwargs.pop("token_cred_type", ServiceBusSASTokenCredential)
        key_cred_type = kwargs.pop("key_cred_type", ServiceBusSharedKeyCredential)

        if token and token_expiry:
            kwargs["credential"] = token_cred_type(token, token_expiry)
        else:
            kwargs["credential"] = key_cred_type(policy, key)

        return kwargs

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _closed_underneath(self, ran_on: Any) -> bool:
        # Whether another operation closed or replaced the handler the attempt ran on. Never after a user close or for
        # a session receiver.
        return (
            ran_on is not None
            and ran_on is not self._handler
            and not self._shutdown.is_set()
            and not getattr(self, "_session", None)
        )

    def _handle_exception(self, exception: BaseException, ran_on: Any) -> "ServiceBusError":
        """Convert a failure to a ServiceBusError and close the handler if the error requires it.

        :param Exception exception: The failure raised by the operation.
        :param any ran_on: The handler the failed attempt ran on, or None if it ran on none. Only that handler is
         closed: concurrent operations on this instance may have reopened meanwhile.
        :return: The retryable error.
        :rtype: ~azure.servicebus.exceptions.ServiceBusError
        """
        # pylint: disable=protected-access, line-too-long
        error = self._amqp_transport.create_servicebus_exception(
            _LOGGER, exception, custom_endpoint_address=self._config.custom_endpoint_address
        )

        try:
            # If SessionLockLostError or ServiceBusConnectionError happen when a
            # session receiver is running, the receiver should no longer be used and
            # should create a new session receiver instance to receive from session.
            # There are pitfalls WRT both next session IDs, and the diversity of session
            # failure modes, that motivates us to disallow this.
            if self._session and self._running and isinstance(error, (SessionLockLostError, ServiceBusConnectionError)):  # type: ignore
                self._session._lock_lost = True  # type: ignore
                with self._handler_lock:
                    self._close_handler()
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
            with self._handler_lock:
                if self._handler is ran_on:
                    self._close_handler()
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

    def _do_retryable_operation(  # pylint: disable=inconsistent-return-statements
        self, operation: Callable, timeout: Optional[float] = None, **kwargs: Any
    ) -> Any:
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
                return operation(**kwargs)
            except StopIteration:
                raise
            except ImportError:
                # If dependency is not installed, do not retry.
                raise
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = self._handle_exception(exception, _attempt_handler.get())
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
                        # Keep the original message: it identifies which phase timed out.
                        # The session hint only applies to NEXT_AVAILABLE_SESSION receivers.
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
                self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    abs_timeout_time=abs_timeout_time,
                )
            finally:
                _attempt_handler.reset(token)

    def _backoff(
        self,
        retried_times: int,
        last_exception: Exception,
        abs_timeout_time: Optional[float] = None,
        entity_name: Optional[str] = None,
    ) -> None:
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
            time.sleep(backoff)
            _LOGGER.info(
                "%r has an exception (%r). Retrying...",
                format(entity_name),
                last_exception,
            )
        else:
            _LOGGER.info(
                "%r operation has timed out. Last exception before timeout is (%r)",
                entity_name,
                last_exception,
            )
            if isinstance(last_exception, OperationTimeoutError):
                # Keep the original message: it identifies which phase timed out.
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

    def _mgmt_request_response(
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
        :type message: Any
        :param callback: The callback which is used to parse the returning message.
        :type callback: Callable[int, Union[~uamqp.message.Message, Message], str]
        :param bool keep_alive_associated_link: A boolean flag for keeping
         associated amqp sender/receiver link alive when
         executing operation on mgmt links.
        :param float or None timeout: timeout in seconds executing the mgmt operation.
        :return: The message response.
        :rtype: Message
        """
        attempt_started = time.monotonic()
        self._open(timeout)
        # Pin the handler for the request and record it for this attempt, as another thread may replace or close it
        # meanwhile; if it was closed, the request uses the closed one and its failure is retried.
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

        mgmt_msg = self._amqp_transport.create_mgmt_msg(
            message=message,
            application_properties=application_properties,
            config=self._config,
            reply_to=self._mgmt_target,
            **kwargs,
        )

        try:
            return self._amqp_transport.mgmt_client_request(
                handler,
                mgmt_msg,
                operation=mgmt_operation,
                operation_type=MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
                node=self._mgmt_target.encode(self._config.encoding),
                timeout=timeout,
                callback=callback,
            )
        except Exception as exp:
            if isinstance(exp, self._amqp_transport.TIMEOUT_ERROR):
                raise OperationTimeoutError(error=exp) from exp
            raise

    def _mgmt_request_response_with_retry(
        self,
        mgmt_operation: bytes,
        message: Dict[str, Any],
        callback: Callable,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        return self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation,
            message=message,
            callback=callback,
            timeout=timeout,
            operation_requires_timeout=True,
            apply_try_timeout=True,
            **kwargs,
        )

    def _open(self, timeout: Optional[float] = None):
        # Read before _running: if another operation closes the handler in between, the attempt still records the
        # handler it runs on, so its failure on the closed handler is retried.
        handler = self._handler
        if self._running and handler is not None:
            _attempt_handler.set(handler)
            return
        started = time.monotonic()
        # Concurrent operations that find the handler closed share one reopen: the first creates and opens
        # the new handler, the others wait here, within their own timeout, and then find it running.
        if not self._handler_lock.acquire(  # pylint: disable=consider-using-with
            timeout=-1 if timeout is None else max(timeout, 0)
        ):
            raise OperationTimeoutError(message="Timed out waiting for another operation to open the AMQP link.")
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
                    self._open_handler(timeout)
                except BaseException as exception:
                    # A failure after the link came up (e.g. registering the session with the lock renewer) must not
                    # leave it running.
                    if self._running:
                        try:
                            self._close_handler()
                        except Exception:  # pylint: disable=broad-except
                            _LOGGER.warning("Handler cleanup failed; preserving the original error.", exc_info=True)
                    if isinstance(exception, Exception) and self._shutdown.is_set():
                        # A close() during the open made it fail.
                        self._check_live()
                    raise
                if self._shutdown.is_set():
                    # close() ran during the open, possibly before the new handler was attached: close that too.
                    self._close_handler()
                    self._check_live()
            _attempt_handler.set(self._handler)
        finally:
            self._handler_lock.release()

    def _open_handler(self, timeout: Optional[float] = None):
        """Create and open a new handler. Called with the handler lock held.

        :param float or None timeout: The time left to open the handler, or None when unbounded.
        :return: None
        :rtype: None
        """
        raise ValueError("Subclass should override the method.")

    def _open_with_retry(self):
        return self._do_retryable_operation(self._open, operation_requires_timeout=True, apply_try_timeout=True)

    def _close_handler(self):
        # Detach the handler before closing it, so operations starting meanwhile reopen instead of using the closing
        # client. _running stays set until the close ends: settlement and lock renewal treat a receiver that is not
        # running as shut down.
        handler, self._handler = self._handler, None
        try:
            if handler:
                handler.close()
        finally:
            self._running = False

    def close(self) -> None:
        """Close down the handler links (and connection if the handler uses a separate connection).

        If the handler has already closed, this operation will do nothing.

        :rtype: None
        """
        # Set first, so a failure on the closing handler from another thread is not retried on a new one.
        self._shutdown.set()
        self._close_handler()
