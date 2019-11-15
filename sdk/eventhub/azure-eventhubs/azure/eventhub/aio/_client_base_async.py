# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import asyncio
import time
import datetime
import functools
from typing import Any, TYPE_CHECKING

from uamqp import (
    authentication,
    constants,
    errors,
    compat,
    Message,
    AMQPClientAsync
)

from .._common import EventHubSharedKeyCredential, EventHubSASTokenCredential
from .._client_base import ClientBase
from .._utils import parse_sas_token
from ..exceptions import EventHubError
from .._constants import JWT_TOKEN_SCOPE, MGMT_OPERATION, MGMT_PARTITION_OPERATION
from ._connection_manager_async import get_connection_manager
from ._error_async import _handle_exception

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class ClientBaseAsync(ClientBase):
    def __init__(self, host, event_hub_path, credential, **kwargs):
        super(ClientBaseAsync, self).__init__(host=host, event_hub_path=event_hub_path,
                                              credential=credential, **kwargs)
        self._conn_manager = get_connection_manager(**kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _create_auth(self):
        """
        Create an ~uamqp.authentication.cbs_auth_async.SASTokenAuthAsync instance to authenticate
        the session.

        """
        http_proxy = self._config.http_proxy
        transport_type = self._config.transport_type
        auth_timeout = self._config.auth_timeout

        if isinstance(self._credential, EventHubSharedKeyCredential):  # pylint:disable=no-else-return
            username = self._credential.policy
            password = self._credential.key
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self._host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAsync.from_shared_access_key(
                self._auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self._credential, EventHubSASTokenCredential):
            token = self._credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAsync(
                self._auth_uri, self._auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:
            get_jwt_token = functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE)
            return authentication.JWTTokenAsync(self._auth_uri, self._auth_uri,
                                                get_jwt_token, http_proxy=http_proxy,
                                                transport_type=transport_type)

    async def _close_connection(self):
        await self._conn_manager.reset_connection_if_broken()

    async def _try_delay(self, retried_times, last_exception, timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            await asyncio.sleep(backoff)
            log.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            log.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    async def _management_request(self, mgmt_msg, op_type):
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = AMQPClientAsync(self._mgmt_target, auth=mgmt_auth, debug=self._config.network_tracing)
            try:
                conn = await self._conn_manager.get_connection(self._host, mgmt_auth)
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
                await self._try_delay(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
            finally:
                await mgmt_client.close_async()
        log.info("%r returns an exception %r", self._container_id, last_exception)  # pylint:disable=specify-parameter-names-in-call
        raise last_exception

    async def get_properties(self):
        # type:() -> Dict[str, Any]
        """
        Get properties of the specified EventHub async.
        Keys in the details dictionary include:

            - path
            - created_at
            - partition_ids

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name})
        response = await self._management_request(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info = response.get_data()
        if eh_info:
            output['path'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = datetime.datetime.utcfromtimestamp(float(eh_info[b'created_at']) / 1000)
            output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
        return output

    async def get_partition_ids(self):
        # type:() -> List[str]
        """
        Get partition ids of the specified EventHub async.

        :rtype: list[str]
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        return (await self.get_properties())['partition_ids']

    async def get_partition_properties(self, partition):
        # type:(str) -> Dict[str, str]
        """
        Get properties of the specified partition async.
        Keys in the details dictionary include:

            - event_hub_path
            - id
            - beginning_sequence_number
            - last_enqueued_sequence_number
            - last_enqueued_offset
            - last_enqueued_time_utc
            - is_empty

        :param partition: The target partition id.
        :type partition: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name,
                                                   'partition': partition})
        response = await self._management_request(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
        partition_info = response.get_data()
        output = {}
        if partition_info:
            output['event_hub_path'] = partition_info[b'name'].decode('utf-8')
            output['id'] = partition_info[b'partition'].decode('utf-8')
            output['beginning_sequence_number'] = partition_info[b'begin_sequence_number']
            output['last_enqueued_sequence_number'] = partition_info[b'last_enqueued_sequence_number']
            output['last_enqueued_offset'] = partition_info[b'last_enqueued_offset'].decode('utf-8')
            output['last_enqueued_time_utc'] = datetime.datetime.utcfromtimestamp(
                float(partition_info[b'last_enqueued_time_utc'] / 1000))
            output['is_empty'] = partition_info[b'is_partition_empty']
        return output

    async def close(self):
        # type: () -> None
        await self._conn_manager.close_connection()


class ConsumerProducerMixin(object):

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _check_closed(self):
        if self.closed:
            raise EventHubError("{} has been closed. Please create a new one to handle event data.".format(self._name))

    def _create_handler(self):
        pass

    async def _open(self):
        """
        Open the EventHubConsumer using the supplied connection.

        """
        # pylint: disable=protected-access
        if not self.running:
            if self._handler:
                await self._handler.close_async()
            self._create_handler()
            await self._handler.open_async(connection=await self._client._conn_manager.get_connection(
                self._client._address.hostname,
                self._client._create_auth()
            ))
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            self._max_message_size_on_link = self._handler.message_handler._link.peer_max_message_size \
                                             or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access
            self.running = True

    async def _close_handler(self):
        if self._handler:
            await self._handler.close_async()  # close the link (sharing connection) or connection (not sharing)
        self.running = False

    async def _close_connection(self):
        await self._close_handler()
        await self._client._conn_manager.reset_connection_if_broken()  # pylint:disable=protected-access

    async def _handle_exception(self, exception):
        if not self.running and isinstance(exception, compat.TimeoutException):
            exception = errors.AuthenticationException("Authorization timeout.")
            return await _handle_exception(exception, self)

        return await _handle_exception(exception, self)

    async def _do_retryable_operation(self, operation, timeout=100000, **kwargs):
        # pylint:disable=protected-access
        # timeout equals to 0 means no timeout, set the value to be a large number.
        timeout_time = time.time() + (timeout if timeout else 100000)
        retried_times = 0
        last_exception = kwargs.pop('last_exception', None)
        operation_need_param = kwargs.pop('operation_need_param', True)

        while retried_times <= self._client._config.max_retries:
            try:
                if operation_need_param:
                    return await operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return await operation()
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await self._handle_exception(exception)
                await self._client._try_delay(retried_times=retried_times, last_exception=last_exception,
                                              timeout_time=timeout_time, entity_name=self._name)
                retried_times += 1

        log.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
        raise last_exception

    async def close(self):
        # type: () -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        self.running = False
        if self._handler:
            await self._handler.close_async()
        self.closed = True
