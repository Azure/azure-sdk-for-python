# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import collections
import logging
import uuid
import time
from datetime import timedelta
from typing import cast, Optional, Tuple, TYPE_CHECKING, Dict, Any, Callable, Type

try:
    from urllib import quote_plus  # type: ignore
except ImportError:
    from urllib.parse import quote_plus

import uamqp
from uamqp import utils
from uamqp.message import MessageProperties

from ._common._configuration import Configuration
from .exceptions import (
    ServiceBusError,
    ServiceBusAuthorizationError,
    _create_servicebus_exception
)
from ._common.utils import create_properties
from ._common.constants import (
    CONTAINER_PREFIX,
    MANAGEMENT_PATH_SUFFIX,
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME
)

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


def _convert_connection_string_to_kwargs(conn_str, shared_key_credential_type, **kwargs):
    # type: (str, Type, Any) -> Dict[str, Any]
    host, policy, key, entity_in_conn_str = _parse_conn_str(conn_str)
    queue_name = kwargs.get("queue_name")
    topic_name = kwargs.get("topic_name")
    if not (queue_name or topic_name or entity_in_conn_str):
        raise ValueError("Entity name is missing. Please specify `queue_name` or `topic_name`"
                         " or use a connection string including the entity information.")

    if queue_name and topic_name:
        raise ValueError("`queue_name` and `topic_name` can not be specified simultaneously.")

    entity_in_kwargs = queue_name or topic_name
    if entity_in_conn_str and entity_in_kwargs and (entity_in_conn_str != entity_in_kwargs):
        raise ServiceBusAuthorizationError(
            "Entity names do not match, the entity name in connection string is {};"
            " the entity name in parameter is {}.".format(entity_in_conn_str, entity_in_kwargs)
        )

    kwargs["fully_qualified_namespace"] = host
    kwargs["entity_name"] = entity_in_conn_str or entity_in_kwargs
    kwargs["credential"] = shared_key_credential_type(policy, key)
    return kwargs


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
        # type: (str, Any) -> _AccessToken
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class BaseHandler:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace,
        entity_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> None
        self.fully_qualified_namespace = fully_qualified_namespace
        self._entity_name = entity_name

        subscription_name = kwargs.get("subscription_name")
        self._mgmt_target = self._entity_name + (("/Subscriptions/" + subscription_name) if subscription_name else '')
        self._mgmt_target = "{}{}".format(self._mgmt_target, MANAGEMENT_PATH_SUFFIX)
        self._credential = credential
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._config = Configuration(**kwargs)
        self._running = False
        self._handler = None  # type: uamqp.AMQPClient
        self._auth_uri = None
        self._properties = create_properties(self._config.user_agent)

    def __enter__(self):
        self._open_with_retry()
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_exception(self, exception):
        # type: (BaseException) -> ServiceBusError
        error, error_need_close_handler, error_need_raise = _create_servicebus_exception(_LOGGER, exception, self)
        if error_need_close_handler:
            self._close_handler()
        if error_need_raise:
            raise error

        return error

    def _backoff(
        self,
        retried_times,
        last_exception,
        timeout=None,
        entity_name=None
    ):
        # type: (int, Exception, Optional[float], str) -> None
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
        # type: (Callable, Optional[float], Any) -> Any
        require_last_exception = kwargs.pop("require_last_exception", False)
        require_timeout = kwargs.pop("require_timeout", False)
        retried_times = 0
        max_retries = self._config.retry_total

        while retried_times <= max_retries:
            try:
                if require_timeout:
                    kwargs["timeout"] = timeout
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
                    timeout=timeout
                )

    def _mgmt_request_response(self, mgmt_operation, message, callback, keep_alive_associated_link=True, **kwargs):
        # type: (str, uamqp.Message, Callable, bool, Any) -> uamqp.Message
        self._open()
        application_properties = {}
        # Some mgmt calls do not support an associated link name (such as list_sessions).  Most do, so on by default.
        if keep_alive_associated_link:
            try:
                application_properties = {ASSOCIATEDLINKPROPERTYNAME:self._handler.message_handler.name}
            except AttributeError:
                pass

        mgmt_msg = uamqp.Message(
            body=message,
            properties=MessageProperties(
                reply_to=self._mgmt_target,
                encoding=self._config.encoding,
                **kwargs
            ),
            application_properties=application_properties
        )
        try:
            return self._handler.mgmt_request(
                mgmt_msg,
                mgmt_operation,
                op_type=MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
                node=self._mgmt_target.encode(self._config.encoding),
                timeout=5000,
                callback=callback
            )
        except Exception as exp:  # pylint: disable=broad-except
            raise ServiceBusError("Management request failed: {}".format(exp), exp)

    def _mgmt_request_response_with_retry(self, mgmt_operation, message, callback, **kwargs):
        # type: (bytes, Dict[str, Any], Callable, Any) -> Any
        return self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation,
            message=message,
            callback=callback,
            **kwargs
        )

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
