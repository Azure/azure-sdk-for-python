# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import collections
import functools
import logging
import uuid
import time
import datetime
from datetime import timedelta
from typing import cast, Optional, Tuple, TYPE_CHECKING

try:
    from urlparse import urlparse
    from urllib import quote_plus  # type: ignore
except ImportError:
    from urllib.parse import urlparse, quote_plus


from uamqp import (
    authentication,
    utils,
    errors,
    constants,
    Source
)
from .common._configuration import Configuration
from .common.errors import (
    _ServiceBusErrorPolicy,
    OperationTimeoutError,
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError
)
from .common.constants import (
    ReceiveSettleMode,
    NEXT_AVAILABLE,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    SESSION_FILTER,
    JWT_TOKEN_SCOPE
)
from .common.message import Message

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_AccessToken = collections.namedtuple("AccessToken", "token expires_on")
_LOGGER = logging.getLogger(__name__)


def _parse_conn_str(conn_str):
    # type: (str) -> Tuple[str, str, str, str]
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None  # type: Optional[str]
    for element in conn_str.split(";"):
        key, _, value = element.partition("=")
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
    if not all([endpoint, shared_access_key_name, shared_access_key]):
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>"
        )
    entity = cast(str, entity_path)
    left_slash_pos = cast(str, endpoint).find("//")
    if left_slash_pos != -1:
        host = cast(str, endpoint)[left_slash_pos + 2:]
    else:
        host = str(endpoint)
    return host, str(shared_access_key_name), str(shared_access_key), entity


def _generate_sas_token(uri, policy, key, expiry=None):
    # type: (str, str, str, Optional[timedelta]) -> _AccessToken
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = timedelta(hours=1)  # Default to 1 hour.

    abs_expiry = int(time.time()) + expiry.seconds
    encoded_uri = quote_plus(uri).encode("utf-8")  # pylint: disable=no-member
    encoded_policy = quote_plus(policy).encode("utf-8")  # pylint: disable=no-member
    encoded_key = key.encode("utf-8")

    token = utils.create_sas_token(encoded_policy, encoded_key, encoded_uri, expiry)
    return _AccessToken(token=token, expires_on=abs_expiry)


class ServiceBusSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy, key):
        # type: (str, str) -> None
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (str, Any) -> _AccessToken
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class SenderReceiverMixin(object):
    def _create_attribute_for_sender(self):
        self._entity_path = self._entity_name
        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._error_policy = _ServiceBusErrorPolicy(max_retries=self._config.retry_total)
        self._name = "SBSender-{}".format(uuid.uuid4())

    def _create_attribute_for_receiver(self, **kwargs):
        if kwargs.get("subscription_name"):
            self.subscription_name = kwargs.get("subscription_name")
            self._is_subscription = True
            self._entity_path = self._entity_name + "/Subscriptions/" + self.subscription_name
        else:
            self._entity_path = self._entity_name

        self._session_id = kwargs.get("session_id")
        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._mode = kwargs.get("mode", ReceiveSettleMode.PeekLock)
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total,
            is_session=(True if self._session_id else False)
        )
        self._name = "SBReceiver-{}".format(uuid.uuid4())

    def _receiver_build_message(self, received, message_type=Message):
        message = message_type(None, message=received)
        message._receiver = self  # pylint: disable=protected-access
        self._last_received_sequenced_number = message.sequence_number
        return message

    def _sender_set_msg_timeout(self, timeout=None, last_exception=None):
        if not timeout:
            return
        timeout_time = time.time() + timeout
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                error = last_exception
            else:
                error = OperationTimeoutError("Send operation timed out")
            _LOGGER.info("%r send operation timed out. (%r)", self._name, error)
            raise error
        self._handler._msg_timeout = remaining_time * 1000  # type: ignore  # pylint: disable=protected-access

    def _receiver_get_source_for_session_entity(self):
        source = Source(self._entity_uri)
        session_filter = None if self._session == NEXT_AVAILABLE else self._session
        source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
        return source

    def _receiver_on_attach_for_session_entity(self, source, target, properties, error):  # pylint: disable=unused-argument
        if str(source) == self.endpoint:
            self.session_start = datetime.datetime.now()
            expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (expiry_in_seconds - DATETIMEOFFSET_EPOCH)/10000000
                self.locked_until = datetime.datetime.fromtimestamp(expiry_in_seconds)
            session_filter = source.get_filter(name=SESSION_FILTER)
            self.session_id = session_filter.decode(self.encoding)


class ClientBase(object):
    def __init__(
        self,
        fully_qualified_namespace,
        entity_name,
        credential,
        **kwargs
    ):
        self.fully_qualified_namespace = fully_qualified_namespace
        self._entity_name = entity_name
        self._credential = credential
        self._container_id = "servicebus.pysdk-" + str(uuid.uuid4())[:8]
        self._config = Configuration(**kwargs)
        self._idle_timeout = kwargs.get("idle_timeout", None)
        self._running = False
        self._handler = None
        self._error = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _create_auth(self):
        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type    # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            auth = authentication.JWTTokenAuth(
                self._auth_uri,
                self._auth_uri,
                functools.partial(self._credential.get_token, self._auth_uri),
                token_type=token_type,
                timeout=self._config.auth_timeout,
                http_proxy=self._config.http_proxy,
                transport_type=self._config.transport_type,
            )
            auth.update_token()
            return auth
        return authentication.JWTTokenAuth(
            self._auth_uri,
            self._auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            timeout=self._config.auth_timeout,
            http_proxy=self._config.http_proxy,
            transport_type=self._config.transport_type,
        )

    def _reconnect(self):
        """Reconnect the handler.

        If the handler was disconnected from the service with
        a retryable error - attempt to reconnect.
        This method will be called automatically for most retryable errors.
        """
        if self._handler:
            self._handler.close()
            self._handler = None
        self._running = False
        self._open()

    def _handle_exception(self, exception):
        if isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
            if exception.action and exception.action.retry and self._config.auto_reconnect:
                _LOGGER.info("Handler detached. Attempting reconnect.")
                self._reconnect()
            elif exception.condition == constants.ErrorCodes.UnauthorizedAccess:
                _LOGGER.info("Handler detached. Shutting down.")
                error = ServiceBusAuthorizationError(str(exception), exception)
                self.close(exception=error)
                raise error
            else:
                _LOGGER.info("Handler detached. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                self.close(exception=error)
                raise error
        elif isinstance(exception, errors.MessageHandlerError):
            if self._config.auto_reconnect:
                _LOGGER.info("Handler error. Attempting reconnect.")
                self._reconnect()
            else:
                _LOGGER.info("Handler error. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                self.close(exception=error)
                raise error
        elif isinstance(exception, errors.AMQPConnectionError):
            message = "Failed to open handler: {}".format(exception)
            raise ServiceBusConnectionError(message, exception)
        else:
            _LOGGER.info("Unexpected error occurred (%r). Shutting down.", exception)
            error = ServiceBusError("Handler failed: {}".format(exception))
            self.close(exception=error)
            raise error

    @staticmethod
    def _from_connection_string(conn_str, **kwargs):
        # type: (str, Any) -> Dict[str, Any]
        host, policy, key, entity_in_conn_str = _parse_conn_str(conn_str)
        queue_name = kwargs.get("queue_name")
        topic_name = kwargs.get("topic_name")
        if not (queue_name or topic_name or entity_in_conn_str):
            raise ValueError("Queue/Topic name is missing. Please specify queue_name/topic_name"
                             " or use a connection string including the entity information.")

        if queue_name and topic_name:
            raise ValueError("Queue/Topic name can not be specified simultaneously.")

        entity_in_kwargs = queue_name or topic_name
        if entity_in_conn_str and entity_in_kwargs and (entity_in_conn_str != entity_in_kwargs):
            raise ValueError("Entity names do not match, the entity name in connection string is {}; the"
                             " entity name in parameter is {}.".format(entity_in_conn_str, entity_in_kwargs))

        kwargs["fully_qualified_namespace"] = host
        kwargs["entity_name"] = entity_in_conn_str or entity_in_kwargs
        kwargs["credential"] = ServiceBusSharedKeyCredential(policy, key)
        kwargs["from_connection_str"] = True
        return kwargs

    def _backoff(
        self,
        retried_times,
        last_exception,
        timeout=None,
        entity_name=None
    ):
        # type: (int, Exception, Optional[int], Optional[str]) -> None
        entity_name = entity_name or self._container_id
        backoff = self._config.retry_backoff_factor * 2 ** retried_times
        if backoff <= self._config.retry_backoff_max and (
            timeout is None or backoff <= timeout
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

    def _do_retryable_operation(self, operation, timeout=None, **kwargs):
        require_last_exception = kwargs.pop("require_last_exception", False)
        require_timeout = kwargs.pop("require_timeout", False)
        retried_times = 0
        last_exception = None
        max_retries = self._config.retry_total

        while retried_times <= max_retries:
            try:
                if require_last_exception:
                    kwargs["last_exception"] = last_exception
                if require_timeout:
                    kwargs["timeout"] = timeout
                return operation(**kwargs)
            except Exception as exception:
                last_exception = self._handle_exception(exception)
                self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    timeout=timeout
                )
                retried_times += 1

        _LOGGER.info(
            "%r operation has exhausted retry. Last exception: %r.",
            self._container_id,
            last_exception,
        )
        raise last_exception

    def close(self, exception=None):
        if self._error:
            return
        if isinstance(exception, ServiceBusError):
            self._error = exception
        elif exception:
            self._error = ServiceBusError(str(exception))
        else:
            self._error = ServiceBusError("This message handler is now closed.")
        self._handler.close()
        self._running = False
