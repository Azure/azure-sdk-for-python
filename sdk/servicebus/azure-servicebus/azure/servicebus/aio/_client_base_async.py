# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio
import time
import functools
from typing import TYPE_CHECKING, Any, Dict, List, Callable, Optional, Union, cast

from uamqp import (
    authentication,
    constants,
    errors,
    compat,
    Message,
    AMQPClientAsync,
)

from .._client_base import ClientBase, _generate_sas_token
from ..common.constants import JWT_TOKEN_SCOPE
from ..common.errors import (
    _ServiceBusErrorPolicy,
    InvalidHandlerState,
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class EventHubSharedKeyCredential(object):
    """The shared access key credential used for authentication.

    :param str policy: The name of the shared access policy.
    :param str key: The shared access key.
    """

    def __init__(self, policy: str, key: str):
        self.policy = policy
        self.key = key
        self.token_type = b"servicebus.windows.net:sastoken"

    async def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError("No token scope provided.")
        return _generate_sas_token(scopes[0], self.policy, self.key)


class ClientBaseAsync(ClientBase):
    def __init__(
        self,
        fully_qualified_namespace: str,
        entity_name: str,
        credential: "TokenCredential",
        **kwargs: Any
    ) -> None:
        self._loop = kwargs.pop("loop", None)
        super(ClientBaseAsync, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=entity_name,
            credential=credential,
            **kwargs
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _create_auth_async(self):
        try:
            # ignore mypy's warning because token_type is Optional
            token_type = self._credential.token_type    # type: ignore
        except AttributeError:
            token_type = b"jwt"
        if token_type == b"servicebus.windows.net:sastoken":
            auth = authentication.JWTTokenAsync(
                self._auth_uri,
                self._auth_uri,
                functools.partial(self._credential.get_token, self._auth_uri),
                token_type=token_type,
                timeout=self._config.auth_timeout,
                http_proxy=self._config.http_proxy,
                transport_type=self._config.transport_type,
            )
            await auth.update_token()
            return auth
        return authentication.JWTTokenAsync(
            self._auth_uri,
            self._auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            timeout=self._config.auth_timeout,
            http_proxy=self._config.http_proxy,
            transport_type=self._config.transport_type,
        )

    async def _reconnect_async(self):
        if self._handler:
            await self._handler.close()
            self._handler = None
        self._running = False
        await self._open()

    async def _handle_exception_async(self, exception):
        if isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
            if exception.action and exception.action.retry and self._config.auto_reconnect:
                _LOGGER.info("Handler detached. Attempting reconnect.")
                await self._reconnect_async()
            elif exception.condition == constants.ErrorCodes.UnauthorizedAccess:
                _LOGGER.info("Handler detached. Shutting down.")
                error = ServiceBusAuthorizationError(str(exception), exception)
                await self.close(exception=error)
                raise error
            else:
                _LOGGER.info("Handler detached. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                await self.close(exception=error)
                raise error
        elif isinstance(exception, errors.MessageHandlerError):
            if self._config.auto_reconnect:
                _LOGGER.info("Handler error. Attempting reconnect.")
                await self._reconnect_async()
            else:
                _LOGGER.info("Handler error. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                await self.close(exception=error)
                raise error
        elif isinstance(exception, errors.AMQPConnectionError):
            message = "Failed to open handler: {}".format(exception)
            raise ServiceBusConnectionError(message, exception)
        else:
            _LOGGER.info("Unexpected error occurred (%r). Shutting down.", exception)
            error = ServiceBusError("Handler failed: {}".format(exception))
            await self.close(exception=error)
            raise error

    async def _backoff_async(
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
            await asyncio.sleep(backoff)
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

    async def _do_retryable_operation_async(self, operation, timeout=None, **kwargs):
        require_last_exception = kwargs.pop("require_last_exception", False)
        require_timeout = kwargs.pop("require_need_timeout", False)
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
            except Exception as exception:
                last_exception = await self._handle_exception_async(exception)
                await self._backoff_async(
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

    async def close(self, exception=None):
        if self._error:
            return
        if isinstance(exception, ServiceBusError):
            self._error = exception
        elif exception:
            self._error = ServiceBusError(str(exception))
        else:
            self._error = ServiceBusError("This message handler is now closed.")
        await self._handler.close()
        self._running = False
