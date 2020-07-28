# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio
import uuid
from typing import TYPE_CHECKING, Any

import uamqp
from uamqp.message import MessageProperties
from .._base_handler import _generate_sas_token
from .._common._configuration import Configuration
from .._common.utils import create_properties
from .._common.constants import (
    TOKEN_TYPE_SASTOKEN,
    MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
    ASSOCIATEDLINKPROPERTYNAME,
    CONTAINER_PREFIX, MANAGEMENT_PATH_SUFFIX)
from ..exceptions import (
    ServiceBusError,
    _create_servicebus_exception
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class ServiceBusSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str):
        self.policy = policy
        self.key = key
        self.token_type = TOKEN_TYPE_SASTOKEN

    async def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class BaseHandler:
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

    async def __aenter__(self):
        await self._open_with_retry()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _handle_exception(self, exception):
        error, error_need_close_handler, error_need_raise = _create_servicebus_exception(_LOGGER, exception, self)
        if error_need_close_handler:
            await self._close_handler()
        if error_need_raise:
            raise error

        return error

    async def _backoff(
            self,
            retried_times,
            last_exception,
            timeout=None,
            entity_name=None
    ):
        entity_name = entity_name or self._container_id
        backoff = self._config.retry_backoff_factor * 2 ** retried_times
        if backoff <= self._config.retry_backoff_max and (
                timeout is None or backoff <= timeout
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

    async def _do_retryable_operation(self, operation, timeout=None, **kwargs):
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
                return await operation(**kwargs)
            except StopAsyncIteration:
                raise
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = await self._handle_exception(exception)
                retried_times += 1
                if retried_times > max_retries:
                    break
                await self._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    timeout=timeout
                )

        _LOGGER.info(
            "%r operation has exhausted retry. Last exception: %r.",
            self._container_id,
            last_exception,
        )
        raise last_exception

    async def _mgmt_request_response(
            self, mgmt_operation, message, callback, keep_alive_associated_link=True, **kwargs
    ):
        await self._open()

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
                **kwargs),
            application_properties=application_properties)
        try:
            return await self._handler.mgmt_request_async(
                mgmt_msg,
                mgmt_operation,
                op_type=MGMT_REQUEST_OP_TYPE_ENTITY_MGMT,
                node=self._mgmt_target.encode(self._config.encoding),
                timeout=5000,
                callback=callback)
        except Exception as exp:  # pylint: disable=broad-except
            raise ServiceBusError("Management request failed: {}".format(exp), exp)

    async def _mgmt_request_response_with_retry(self, mgmt_operation, message, callback, **kwargs):
        return await self._do_retryable_operation(
            self._mgmt_request_response,
            mgmt_operation=mgmt_operation,
            message=message,
            callback=callback,
            **kwargs
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

    async def close(self):
        # type: () -> None
        """Close down the handler connection.

        If the handler has already closed, this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :rtype: None
        """
        await self._close_handler()
