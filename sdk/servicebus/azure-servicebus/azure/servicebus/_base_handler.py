# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import uuid
import time
import threading
from datetime import timedelta
from typing import cast, Optional, Tuple, TYPE_CHECKING, Dict, Any, Callable, Union

try:
    from urllib.parse import quote_plus, urlparse
except ImportError:
    from urllib import quote_plus  # type: ignore
    from urlparse import urlparse  # type: ignore

from ._pyamqp import error as errors, utils
from ._pyamqp.message import Message, Properties
from ._pyamqp.authentication import JWTTokenAuth


from uamqp import compat


from azure.core.credentials import AccessToken, AzureSasCredential, AzureNamedKeyCredential
from azure.core.pipeline.policies import RetryMode

from ._common._configuration import Configuration
from .exceptions import (
    ServiceBusError,
    ServiceBusConnectionError,
    OperationTimeoutError,
    SessionLockLostError,
    _create_servicebus_exception,
)
from ._common.utils import create_properties, strip_protocol_from_uri, parse_sas_credential
from ._common.constants import (
    CONTAINER_PREFIX,
    MANAGEMENT_PATH_SUFFIX,
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME,
    TRACE_NAMESPACE_PROPERTY,
    TRACE_COMPONENT_PROPERTY,
    TRACE_COMPONENT,
    TRACE_PEER_ADDRESS_PROPERTY,
    TRACE_BUS_DESTINATION_PROPERTY,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


def _parse_conn_str(conn_str, check_case=False):
    # type: (str, Optional[bool]) -> Tuple[str, Optional[str], Optional[str], str, Optional[str], Optional[int]]
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None  # type: Optional[str]
    shared_access_signature = None  # type: Optional[str]
    shared_access_signature_expiry = None  # type: Optional[int]

    # split connection string into properties
    conn_properties = [s.split("=", 1) for s in conn_str.strip().rstrip(";").split(";")]
    if any(len(tup) != 2 for tup in conn_properties):
        raise ValueError("Connection string is either blank or malformed.")
    conn_settings = dict(conn_properties)   # type: ignore

    # case sensitive check when parsing for connection string properties
    if check_case:
        shared_access_key = conn_settings.get("SharedAccessKey")
        shared_access_key_name = conn_settings.get("SharedAccessKeyName")
        endpoint = conn_settings.get("Endpoint")
        entity_path = conn_settings.get("EntityPath")

    # non case sensitive check when parsing connection string for internal use
    for key, value in conn_settings.items():
        # only sas check is non case sensitive for both conn str properties and internal use
        if key.lower() == "sharedaccesssignature":
            shared_access_signature = value
            try:
                # Expiry can be stored in the "se=<timestamp>" clause of the token. ('&'-separated key-value pairs)
                shared_access_signature_expiry = int(
                    shared_access_signature.split("se=")[1].split("&")[0]   # type: ignore
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

    entity = cast(str, entity_path)

    # check that endpoint is valid
    if not endpoint:
        raise ValueError("Connection string is either blank or malformed.")
    parsed = urlparse(endpoint)
    if not parsed.netloc:
        raise ValueError("Invalid Endpoint on the Connection String.")
    host = cast(str, parsed.netloc.strip())

    if any([shared_access_key, shared_access_key_name]) and not all(
        [shared_access_key, shared_access_key_name]
    ):
        raise ValueError(
            "Connection string must have both SharedAccessKeyName and SharedAccessKey."
        )
    if shared_access_signature and shared_access_key:
        raise ValueError(
            "Only one of the SharedAccessKey or SharedAccessSignature must be present."
        )
    if not shared_access_signature and not shared_access_key:
        raise ValueError(
            "At least one of the SharedAccessKey or SharedAccessSignature must be present."
        )

    return (
        host,
        str(shared_access_key_name) if shared_access_key_name else None,
        str(shared_access_key) if shared_access_key else None,
        entity,
        str(shared_access_signature) if shared_access_signature else None,
        shared_access_signature_expiry,
    )


def _generate_sas_token(uri, policy, key, expiry=None):
    # type: (str, str, str, Optional[timedelta]) -> AccessToken
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = timedelta(hours=1)  # Default to 1 hour.

    abs_expiry = int(time.time()) + expiry.seconds
    token = utils.generate_sas_token(uri, policy, key, abs_expiry).encode("UTF-8")
    return AccessToken(token=token, expires_on=abs_expiry)

def _get_backoff_time(retry_mode, backoff_factor, backoff_max, retried_times):
    if retry_mode == RetryMode.Fixed:
        backoff_value = backoff_factor
    else:
        backoff_value = backoff_factor * (2 ** retried_times)
    return min(backoff_max, backoff_value)

class ServiceBusSASTokenCredential(object):
    """The shared access token credential used for authentication.
    :param str token: The shared access token string
    :param int expiry: The epoch timestamp
    """

    def __init__(self, token, expiry):
        # type: (str, int) -> None
        """
        :param str token: The shared access token string
        :param float expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        """
        This method is automatically called when token is about to expire.
        """
        return AccessToken(self.token, self.expiry)


class ServiceBusSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy, key):
        # type: (str, str) -> None
        self.policy = policy
        self.key = key
        self.token_type = TOKEN_TYPE_SASTOKEN

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class ServiceBusAzureNamedKeyTokenCredential(object):
    """The named key credential used for authentication.
    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential):
        # type: (AzureNamedKeyCredential) -> None
        self._credential = azure_named_key_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
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
    def __init__(self, azure_sas_credential):
        # type: (AzureSasCredential) -> None
        self._credential = azure_sas_credential
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> AccessToken
        """
        This method is automatically called when token is about to expire.
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class BaseHandler:  # pylint:disable=too-many-instance-attributes
    def __init__(self, fully_qualified_namespace, entity_name, credential, **kwargs):
        # type: (str, str, Union[TokenCredential, AzureSasCredential, AzureNamedKeyCredential], Any) -> None
        # If the user provided http:// or sb://, let's be polite and strip that.
        self.fully_qualified_namespace = strip_protocol_from_uri(
            fully_qualified_namespace.strip()
        )
        self._entity_name = entity_name

        subscription_name = kwargs.get("subscription_name")
        self._entity_path = self._entity_name + (
            ("/Subscriptions/" + subscription_name) if subscription_name else ""
        )
        self._mgmt_target = "{}{}".format(self._entity_path, MANAGEMENT_PATH_SUFFIX)
        if isinstance(credential, AzureSasCredential):
            self._credential = ServiceBusAzureSasTokenCredential(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = ServiceBusAzureNamedKeyTokenCredential(credential) # type: ignore
        else:
            self._credential = credential # type: ignore
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._config = Configuration(**kwargs)
        self._running = False
        self._handler = None  # type: uamqp.AMQPClient
        self._auth_uri = None
        self._properties = create_properties(self._config.user_agent)
        self._shutdown = threading.Event()

    @classmethod
    def _convert_connection_string_to_kwargs(cls, conn_str, **kwargs):
        # type: (str, Any) -> Dict[str, Any]
        host, policy, key, entity_in_conn_str, token, token_expiry = _parse_conn_str(
            conn_str
        )
        queue_name = kwargs.get("queue_name")
        topic_name = kwargs.get("topic_name")
        if not (queue_name or topic_name or entity_in_conn_str):
            raise ValueError(
                "Entity name is missing. Please specify `queue_name` or `topic_name`"
                " or use a connection string including the entity information."
            )

        if queue_name and topic_name:
            raise ValueError(
                "`queue_name` and `topic_name` can not be specified simultaneously."
            )

        entity_in_kwargs = queue_name or topic_name
        if (
            entity_in_conn_str
            and entity_in_kwargs
            and (entity_in_conn_str != entity_in_kwargs)
        ):
            raise ValueError(
                "The queue or topic name provided: {} which does not match the EntityPath in"
                " the connection string passed to the ServiceBusClient constructor: {}.".format(
                    entity_in_conn_str, entity_in_kwargs
                )
            )

        kwargs["fully_qualified_namespace"] = host
        kwargs["entity_name"] = entity_in_conn_str or entity_in_kwargs

        # Set the type to sync credentials, unless async credentials are passed in.
        token_cred_type = kwargs.pop("token_cred_type", ServiceBusSASTokenCredential)
        key_cred_type = kwargs.pop("key_cred_type", ServiceBusSharedKeyCredential)

        if token and token_expiry:
            kwargs["credential"] = token_cred_type(token, token_expiry)
        else:
            kwargs["credential"] = key_cred_type(policy, key)

        return kwargs

    def __enter__(self):
        if self._shutdown.is_set():
            raise ValueError(
                "The handler has already been shutdown. Please use ServiceBusClient to "
                "create a new instance."
            )

        self._open_with_retry()
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_exception(self, exception):
        # type: (BaseException) -> ServiceBusError
        # pylint: disable=protected-access, line-too-long
        error = _create_servicebus_exception(_LOGGER, exception)

        try:
            # If SessionLockLostError or ServiceBusConnectionError happen when a session receiver is running,
            # the receiver should no longer be used and should create a new session receiver
            # instance to receive from session. There are pitfalls WRT both next session IDs,
            # and the diversity of session failure modes, that motivates us to disallow this.
            if self._session and self._running and isinstance(error, (SessionLockLostError, ServiceBusConnectionError)):  # type: ignore
                self._session._lock_lost = True  # type: ignore
                self._close_handler()
                raise error
        except AttributeError:
            pass

        if error._shutdown_handler:
            self._close_handler()
        if not error._retryable:
            raise error

        return error

    def _check_live(self):
        """check whether the handler is alive"""
        # pylint: disable=protected-access
        if self._shutdown.is_set():
            raise ValueError(
                "The handler has already been shutdown. Please use ServiceBusClient to "
                "create a new instance."
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
            if self._session and (
                self._session._lock_lost or self._session._lock_expired
            ):
                raise SessionLockLostError(error=self._session.auto_renew_error)
        except AttributeError:
            pass

    def _do_retryable_operation(self, operation, timeout=None, **kwargs):
        # type: (Callable, Optional[float], Any) -> Any
        # pylint: disable=protected-access
        require_last_exception = kwargs.pop("require_last_exception", False)
        operation_requires_timeout = kwargs.pop("operation_requires_timeout", False)
        retried_times = 0
        max_retries = self._config.retry_total

        abs_timeout_time = (
            (time.time() + timeout)
            if (operation_requires_timeout and timeout)
            else None
        )

        while retried_times <= max_retries:
            try:
                if operation_requires_timeout and abs_timeout_time:
                    remaining_timeout = abs_timeout_time - time.time()
                    kwargs["timeout"] = remaining_timeout
                return operation(**kwargs)
            except StopIteration:
                raise
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = self._handle_exception(exception)
                if require_last_exception:
                    kwargs["last_exception"] = last_exception
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info(
                        "%r operation has exhausted retry. Last exception: %r.",
                        self._container_id,
                        last_exception,
                    )
                    raise last_exception
                self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    abs_timeout_time=abs_timeout_time,
                )

    def _backoff(
        self, retried_times, last_exception, abs_timeout_time=None, entity_name=None
    ):
        # type: (int, Exception, Optional[float], str) -> None
        entity_name = entity_name or self._container_id
        backoff = _get_backoff_time(
                    self._config.retry_mode,
                    self._config.retry_backoff_factor,
                    self._config.retry_backoff_max,
                    retried_times,
                )
        if backoff <= self._config.retry_backoff_max and (
            abs_timeout_time is None or (backoff + time.time()) <= abs_timeout_time
        ):  # pylint:disable=no-else-return
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
            raise last_exception

    def _mgmt_request_response(
        self,
        mgmt_operation,
        message,
        callback,
        keep_alive_associated_link=True,
        timeout=None,
        **kwargs
    ):
        # type: (bytes, Any, Callable, bool, Optional[float], Any) -> uamqp.Message
        """
        Execute an amqp management operation.

        :param bytes mgmt_operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :param message: The message to send in the management request.
        :paramtype message: Any
        :param callback: The callback which is used to parse the returning message.
        :paramtype callback: Callable[int, ~uamqp.message.Message, str]
        :param keep_alive_associated_link: A boolean flag for keeping associated amqp sender/receiver link alive when
         executing operation on mgmt links.
        :param timeout: timeout in seconds executing the mgmt operation.
        :rtype: None
        """
        self._open()
        application_properties = {}

        # Some mgmt calls do not support an associated link name (such as list_sessions).  Most do, so on by default.
        if keep_alive_associated_link:
            try:
                application_properties = {
                    ASSOCIATEDLINKPROPERTYNAME: self._handler._link.name  # pylint: disable=protected-access
                }
            except AttributeError:
                pass

        mgmt_msg = Message(
            value=message,
            properties=Properties(reply_to=self._mgmt_target, **kwargs),
            application_properties=application_properties,
        )
        try:
            return self._handler.mgmt_request(
                mgmt_msg,
                mgmt_operation,
                op_type=MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
                node=self._mgmt_target.encode(self._config.encoding),
                timeout=timeout * 1000 if timeout else None,
                callback=callback,
            )
        except Exception as exp:  # pylint: disable=broad-except
            if isinstance(exp, compat.TimeoutException):
                raise OperationTimeoutError(error=exp)
            raise

    def _mgmt_request_response_with_retry(
        self, mgmt_operation, message, callback, timeout=None, **kwargs
    ):
        # type: (bytes, Dict[str, Any], Callable, Optional[float], Any) -> Any
        return self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation.decode("UTF-8"),
            message=message,
            callback=callback,
            timeout=timeout,
            operation_requires_timeout=True,
            **kwargs
        )

    def _add_span_request_attributes(self, span):
        span.add_attribute(TRACE_COMPONENT_PROPERTY, TRACE_COMPONENT)
        span.add_attribute(TRACE_NAMESPACE_PROPERTY, TRACE_NAMESPACE_PROPERTY)
        span.add_attribute(TRACE_BUS_DESTINATION_PROPERTY, self._entity_path)
        span.add_attribute(TRACE_PEER_ADDRESS_PROPERTY, self.fully_qualified_namespace)

    def _open(self):  # pylint: disable=no-self-use
        raise ValueError("Subclass should override the method.")

    def _open_with_retry(self):
        return self._do_retryable_operation(self._open)

    def _close_handler(self):
        if self._handler:
            self._handler.close()
            self._handler = None
        self._running = False

    def close(self):
        # type: () -> None
        """Close down the handler links (and connection if the handler uses a separate connection).

        If the handler has already closed, this operation will do nothing.

        :rtype: None
        """
        self._close_handler()
        self._shutdown.set()
