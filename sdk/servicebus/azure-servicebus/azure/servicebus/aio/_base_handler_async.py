# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio
import uuid
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, Dict, Union

import uamqp
from uamqp import compat
from uamqp.message import MessageProperties

from azure.core.credentials import (
    AccessToken,
    AzureSasCredential,
    AzureNamedKeyCredential,
)

from .._base_handler import (
    _generate_sas_token,
    BaseHandler as BaseHandlerSync,
    _get_backoff_time,
)
from .._common._configuration import Configuration
from .._common.utils import (
    create_properties,
    strip_protocol_from_uri,
    parse_sas_credential,
)
from .._common.constants import (
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME,
    CONTAINER_PREFIX,
    MANAGEMENT_PATH_SUFFIX,
)
from ..exceptions import (
    ServiceBusConnectionError,
    SessionLockLostError,
    OperationTimeoutError,
    _create_servicebus_exception,
)

if TYPE_CHECKING:
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

    async def get_token(
        self, *scopes: str, **kwargs: Any  # pylint:disable=unused-argument
    ) -> AccessToken:
        """
        This method is automatically called when token is about to expire.
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

    async def get_token(
        self, *scopes: str, **kwargs: Any  # pylint:disable=unused-argument
    ) -> AccessToken:
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class ServiceBusAzureNamedKeyTokenCredentialAsync(object):
    """The named key credential used for authentication.
    :param credential: The AzureNamedKeyCredential that should be used.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, azure_named_key_credential):
        # type: (AzureNamedKeyCredential) -> None
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

    async def get_token(
        self, *scopes: str, **kwargs: Any
    ) -> AccessToken:  # pylint:disable=unused-argument
        """
        This method is automatically called when token is about to expire.
        """
        signature, expiry = parse_sas_credential(self._credential)
        return AccessToken(signature, expiry)


class BaseHandler:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        fully_qualified_namespace: str,
        entity_name: str,
        credential: Union[
            "AsyncTokenCredential", AzureSasCredential, AzureNamedKeyCredential
        ],
        **kwargs: Any
    ) -> None:
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
            self._credential = ServiceBusAzureSasTokenCredentialAsync(credential)
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential = ServiceBusAzureNamedKeyTokenCredentialAsync(credential)  # type: ignore
        else:
            self._credential = credential  # type: ignore
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._config = Configuration(**kwargs)
        self._running = False
        self._handler = None  # type: uamqp.AMQPClientAsync
        self._auth_uri = None
        self._properties = create_properties(self._config.user_agent)
        self._shutdown = asyncio.Event()

    @classmethod
    def _convert_connection_string_to_kwargs(cls, conn_str, **kwargs):
        # pylint:disable=protected-access
        return BaseHandlerSync._convert_connection_string_to_kwargs(
            conn_str,
            token_cred_type=ServiceBusSASTokenCredential,
            key_cred_type=ServiceBusSharedKeyCredential,
            **kwargs
        )

    async def __aenter__(self):
        if self._shutdown.is_set():
            raise ValueError(
                "The handler has already been shutdown. Please use ServiceBusClient to "
                "create a new instance."
            )
        await self._open_with_retry()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _handle_exception(self, exception):
        # pylint: disable=protected-access
        error = _create_servicebus_exception(_LOGGER, exception)

        try:
            # If SessionLockLostError or ServiceBusConnectionError happen when a session receiver is running,
            # the receiver should no longer be used and should create a new session receiver
            # instance to receive from session. There are pitfalls WRT both next session IDs,
            # and the diversity of session failure modes, that motivates us to disallow this.
            if (
                self._session
                and self._running
                and isinstance(error, (SessionLockLostError, ServiceBusConnectionError))
            ):
                self._session._lock_lost = True
                await self._close_handler()
                raise error
        except AttributeError:
            pass

        if error._shutdown_handler:
            await self._close_handler()
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

    async def _do_retryable_operation(self, operation, timeout=None, **kwargs):
        # type: (Callable, Optional[float], Any) -> Any
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
                return await operation(**kwargs)
            except StopAsyncIteration:
                raise
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = await self._handle_exception(exception)
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
                await self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    abs_timeout_time=abs_timeout_time,
                )

    async def _backoff(
        self, retried_times, last_exception, abs_timeout_time=None, entity_name=None
    ):
        entity_name = entity_name or self._container_id
        backoff = _get_backoff_time(
            self._config.retry_mode,
            self._config.retry_backoff_factor,
            self._config.retry_backoff_max,
            retried_times,
        )
        if backoff <= self._config.retry_backoff_max and (
            abs_timeout_time is None or (backoff + time.time()) <= abs_timeout_time
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
            raise last_exception

    async def _mgmt_request_response(
        self,
        mgmt_operation,
        message,
        callback,
        keep_alive_associated_link=True,
        timeout=None,
        **kwargs
    ):
        # type: (bytes, uamqp.Message, Callable, bool, Optional[float], Any) -> uamqp.Message
        """
        Execute an amqp management operation.

        :param bytes mgmt_operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :param message: The message to send in the management request.
        :paramtype message: ~uamqp.message.Message
        :param callback: The callback which is used to parse the returning message.
        :paramtype callback: Callable[int, ~uamqp.message.Message, str]
        :param keep_alive_associated_link: A boolean flag for keeping associated amqp sender/receiver link alive when
         executing operation on mgmt links.
        :param timeout: timeout in seconds for executing the mgmt operation.
        :rtype: None
        """
        await self._open()

        application_properties = {}
        # Some mgmt calls do not support an associated link name (such as list_sessions).  Most do, so on by default.
        if keep_alive_associated_link:
            try:
                application_properties = {
                    ASSOCIATEDLINKPROPERTYNAME: self._handler.message_handler.name
                }
            except AttributeError:
                pass

        mgmt_msg = uamqp.Message(
            body=message,
            properties=MessageProperties(
                reply_to=self._mgmt_target, encoding=self._config.encoding, **kwargs
            ),
            application_properties=application_properties,
        )
        try:
            return await self._handler.mgmt_request_async(
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

    async def _mgmt_request_response_with_retry(
        self, mgmt_operation, message, callback, timeout=None, **kwargs
    ):
        # type: (bytes, Dict[str, Any], Callable, Optional[float], Any) -> Any
        return await self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation,
            message=message,
            callback=callback,
            timeout=timeout,
            operation_requires_timeout=True,
            **kwargs
        )

    async def _add_span_request_attributes(self, span):
        return BaseHandlerSync._add_span_request_attributes(  # pylint: disable=protected-access
            self, span
        )

    async def _open(self):  # pylint: disable=no-self-use
        raise ValueError("Subclass should override the method.")

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open)

    async def _close_handler(self):
        if self._handler:
            await self._handler.close_async()
            self._handler = None
        self._running = False

    async def close(self) -> None:
        """Close down the handler connection.

        If the handler has already closed, this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :rtype: None
        """
        await self._close_handler()
        self._shutdown.set()
