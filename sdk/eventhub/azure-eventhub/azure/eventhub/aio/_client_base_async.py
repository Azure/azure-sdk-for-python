# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

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
    AMQPClientAsync
)

from .._client_base import ClientBase, _generate_sas_token, _parse_conn_str
from .._utils import utc_from_timestamp
from ..exceptions import ClientClosedError
from .._constants import JWT_TOKEN_SCOPE, MGMT_OPERATION, MGMT_PARTITION_OPERATION
from ._connection_manager_async import get_connection_manager
from ._error_async import _handle_exception

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

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
            eventhub_name: str,
            credential: 'TokenCredential',
            **kwargs: Any
            ) -> None:
        super(ClientBaseAsync, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            credential=credential,
            **kwargs
        )
        self._conn_manager = get_connection_manager(**kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @staticmethod
    def _from_connection_string(conn_str: str, **kwargs) -> Dict[str, Any]:
        host, policy, key, entity = _parse_conn_str(conn_str, kwargs)
        kwargs['fully_qualified_namespace'] = host
        kwargs['eventhub_name'] = entity
        kwargs['credential'] = EventHubSharedKeyCredential(policy, key)
        return kwargs

    async def _create_auth(self) -> authentication.JWTTokenAsync:
        """
        Create an ~uamqp.authentication.SASTokenAuthAsync instance to authenticate
        the session.

        """
        try:
            token_type = self._credential.token_type
        except AttributeError:
            token_type = b'jwt'
        if token_type == b"servicebus.windows.net:sastoken":
            auth = authentication.JWTTokenAsync(
                self._auth_uri,
                self._auth_uri,
                functools.partial(self._credential.get_token, self._auth_uri),
                token_type=token_type,
                timeout=self._config.auth_timeout,
                http_proxy=self._config.http_proxy,
                transport_type=self._config.transport_type)
            await auth.update_token()
            return auth
        return authentication.JWTTokenAsync(
            self._auth_uri,
            self._auth_uri,
            functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            timeout=self._config.auth_timeout,
            http_proxy=self._config.http_proxy,
            transport_type=self._config.transport_type)

    async def _close_connection(self) -> None:
        await self._conn_manager.reset_connection_if_broken()

    async def _backoff(
            self,
            retried_times: int,
            last_exception: Exception,
            timeout_time: Optional[int] = None,
            entity_name: Optional[str] = None
            ) -> None:
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            await asyncio.sleep(backoff)
            _LOGGER.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            _LOGGER.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    async def _management_request(self, mgmt_msg: Message, op_type: bytes) -> Any:
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = await self._create_auth()
            mgmt_client = AMQPClientAsync(self._mgmt_target, auth=mgmt_auth, debug=self._config.network_tracing)
            try:
                conn = await self._conn_manager.get_connection(self._address.hostname, mgmt_auth)
                await mgmt_client.open_async(connection=conn)
                response = await mgmt_client.mgmt_request_async(
                    mgmt_msg,
                    constants.READ_OPERATION,
                    op_type=op_type,
                    status_code_field=b'status-code',
                    description_fields=b'status-description')
                return response
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await _handle_exception(exception, self)
                await self._backoff(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info("%r returns an exception %r", self._container_id, last_exception)
                    raise last_exception
            finally:
                await mgmt_client.close_async()

    async def get_eventhub_properties(self) -> Dict[str, Any]:
        """Get properties of the Event Hub.

        Keys in the returned dictionary include:

            - `eventhub_name` (str)
            - `created_at` (UTC datetime.datetime)
            - `partition_ids` (list[str])

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eventhub_name})
        response = await self._management_request(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info = response.get_data()  # type: Dict[bytes, Any]
        if eh_info:
            output['eventhub_name'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = utc_from_timestamp(float(eh_info[b'created_at']) / 1000)
            output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
        return output

    async def get_partition_ids(self) -> List[str]:
        """Get partition IDs of the Event Hub.

        :rtype: list[str]
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        return (await self.get_eventhub_properties())['partition_ids']

    async def get_partition_properties(self, partition_id: str) -> Dict[str, Any]:
        """Get properties of the specified partition.

        Keys in the properties dictionary include:

            - `eventhub_name` (str)
            - `id` (str)
            - `beginning_sequence_number` (int)
            - `last_enqueued_sequence_number` (int)
            - `last_enqueued_offset` (str)
            - `last_enqueued_time_utc` (UTC datetime.datetime)
            - `is_empty` (bool)

        :param partition_id: The target partition ID.
        :type partition_id: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eventhub_name,
                                                   'partition': partition_id})
        response = await self._management_request(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
        partition_info = response.get_data()  # type: Dict[bytes, Union[bytes, int]]
        output = {}  # type: Dict[str, Any]
        if partition_info:
            output['eventhub_name'] = cast(bytes, partition_info[b'name']).decode('utf-8')
            output['id'] = cast(bytes, partition_info[b'partition']).decode('utf-8')
            output['beginning_sequence_number'] = cast(int, partition_info[b'begin_sequence_number'])
            output['last_enqueued_sequence_number'] = cast(int, partition_info[b'last_enqueued_sequence_number'])
            output['last_enqueued_offset'] = cast(bytes, partition_info[b'last_enqueued_offset']).decode('utf-8')
            output['is_empty'] = partition_info[b'is_partition_empty']
            output['last_enqueued_time_utc'] = utc_from_timestamp(
                float(cast(int, partition_info[b'last_enqueued_time_utc']) / 1000)
            )
        return output

    async def close(self) -> None:
        await self._conn_manager.close_connection()


class ConsumerProducerMixin(object):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _check_closed(self) -> None:
        if self.closed:
            raise ClientClosedError(
                "{} has been closed. Please create a new one to handle event data.".format(self._name)  # type: ignore
            )

    async def _open(self) -> None:
        """
        Open the EventHubConsumer using the supplied connection.

        """
        # pylint: disable=protected-access,line-too-long
        # TODO: Properly resolve type hinting
        if not self.running:  # type: ignore
            if self._handler:  # type: ignore
                await self._handler.close_async()  # type: ignore
            auth = await self._client._create_auth()  # type: ignore
            self._create_handler(auth)  # type: ignore
            await self._handler.open_async(  # type: ignore
                connection=await self._client._conn_manager.get_connection(self._client._address.hostname, auth)  # type: ignore
            )
            while not await self._handler.client_ready_async():  # type: ignore
                await asyncio.sleep(0.05)
            self._max_message_size_on_link = self._handler.message_handler._link.peer_max_message_size or constants.MAX_MESSAGE_LENGTH_BYTES  # type: ignore
            self.running = True

    async def _close_handler(self) -> None:
        # TODO: Propertly resolve type hinting
        if self._handler:  # type: ignore
            # close the link (shared connection) or connection (not shared)
            await self._handler.close_async()  # type: ignore
        self.running = False

    async def _close_connection(self) -> None:
        await self._close_handler()
        await self._client._conn_manager.reset_connection_if_broken()  # type: ignore # pylint:disable=protected-access

    async def _handle_exception(self, exception: Exception) -> Exception:
        if not self.running and isinstance(exception, compat.TimeoutException):
            exception = errors.AuthenticationException("Authorization timeout.")
            return await _handle_exception(exception, self)

        return await _handle_exception(exception, self)

    async def _do_retryable_operation(
            self,
            operation: Callable[..., Any],
            timeout: Optional[int] = None,
            **kwargs: Any
            ) -> Optional[Any]:
        # pylint:disable=protected-access,line-too-long
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop('last_exception', None)
        operation_need_param = kwargs.pop('operation_need_param', True)
        max_retries = self._client._config.max_retries  # type: ignore

        while retried_times <= max_retries:
            try:
                if operation_need_param:
                    return await operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return await operation()
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await self._handle_exception(exception)
                await self._client._backoff(  # type: ignore
                    retried_times=retried_times,
                    last_exception=last_exception,
                    timeout_time=timeout_time,
                    entity_name=self._name  # type: ignore
                )
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)  # type: ignore
                    raise last_exception
        return None

    async def close(self) -> None:
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        await self._close_handler()
        self.closed = True
