# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio  # pylint:disable=do-not-import-asyncio
import time
import uuid
from datetime import datetime
from typing import Callable, Optional, TYPE_CHECKING, Union

from azure.core.async_paging import AsyncItemPaged

from ._base_handler_async import BaseHandler as AsyncBaseHandler
from .._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from .._common import mgmt_handlers
from .._common.utils import get_link_ready_deadline, check_link_ready_deadline
from .._session_browser import _to_last_updated_ms, _page_request_body, _PAGE_SIZE
from ..exceptions import OperationTimeoutError
from ._async_utils import create_authentication

if TYPE_CHECKING:
    try:
        from uamqp.async_ops.client_async import AMQPClientAsync as uamqp_AMQPClientAsync
    except ImportError:
        pass
    from .._pyamqp.aio._client_async import AMQPClientAsync as pyamqp_AMQPClientAsync


class _SessionBrowserAsync(AsyncBaseHandler):
    """Async internal handler that opens an AMQP connection for management-only operations.

    Unlike ServiceBusSender/ServiceBusReceiver, this does NOT create a sender or
    receiver link. It only opens a connection and authenticates, then sends
    management requests to the $management endpoint.
    """

    def __init__(self, fully_qualified_namespace, entity_name, credential, **kwargs):
        super().__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=entity_name,
            credential=credential,
            **kwargs,
        )
        self._auth_uri = f"sb://{self.fully_qualified_namespace}/{self._entity_path}"
        self._error_policy = self._amqp_transport.create_retry_policy(self._config)
        self._name = f"SBSessionBrowser-{uuid.uuid4()}"
        self._connection = kwargs.get("connection")
        # _create_handler always assigns it, so narrow away the base class's Optional.
        self._handler: Union["uamqp_AMQPClientAsync", "pyamqp_AMQPClientAsync"]

    def _create_handler(self, auth):
        self._handler = self._amqp_transport.create_mgmt_client_async(
            config=self._config,
            auth=auth,
            properties=self._properties,
            retry_policy=self._error_policy,
            client_name=self._name,
        )

    async def _open(self, timeout: Optional[float] = None):
        if self._running:
            return
        deadline = get_link_ready_deadline(timeout)
        if self._handler:
            await self._handler.close_async()
            check_link_ready_deadline(deadline)

        auth = None if self._connection else (await create_authentication(self))
        self._create_handler(auth)
        try:
            # The token fetch can use the budget, and open_async() cannot be cancelled once entered.
            check_link_ready_deadline(deadline)
            await self._handler.open_async(connection=self._connection)
            while True:
                check_link_ready_deadline(deadline)
                if await self._handler.client_ready_async():
                    break
                await asyncio.sleep(0.05)
            check_link_ready_deadline(deadline)
            self._running = True
        except:
            await self._close_handler()
            raise

    def list_sessions(
        self,
        *,
        state_updated_after: Optional[datetime] = None,
        timeout: Optional[float] = None,
        _now: Callable[[], float] = time.monotonic,
    ) -> AsyncItemPaged[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime state_updated_after: If specified, only sessions whose
            session state was set or updated after this time are returned. If not specified,
            returns sessions with active messages or stored session state in the entity. Sessions
            with neither are excluded.
        :keyword float timeout: The total operation timeout in seconds, spent across
            every page of the enumeration.
        :keyword _now: Monotonic clock function, injectable for tests. Internal.
        :paramtype _now: callable
        :returns: A paged async iterable of session ID strings.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]

        .. note::

            Pagination uses skip-based indexing over a server-side snapshot. If sessions
            are added or removed between page requests, the iterator may yield duplicate
            session IDs or skip some. Callers should not assume uniqueness.
        """
        last_updated_time_ms = _to_last_updated_ms(state_updated_after)
        # `timeout` is the total budget across every page. AsyncItemPaged is lazy,
        # so establish the deadline on the first page fetch and share it, so a
        # multi-page enumeration cannot run for `timeout` seconds per page.
        deadline_state: list = [None]

        async def _get_next(continuation_token):
            skip = int(continuation_token) if continuation_token else 0
            # A paused iterator must not reopen the connection after the owning
            # ServiceBusClient has been closed. _check_live() raises once the
            # handler is shut down, before _open() could resurrect resources.
            self._check_live()
            if timeout is None:
                page_timeout = None
            else:
                if deadline_state[0] is None:
                    deadline_state[0] = _now() + timeout
                page_timeout = deadline_state[0] - _now()
                if page_timeout <= 0:
                    raise OperationTimeoutError(
                        message="Listing sessions did not complete within the specified timeout."
                    )
            message = _page_request_body(
                self._amqp_transport, last_updated_time_ms, skip
            )
            result = await self._mgmt_request_response_with_retry(
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op,
                keep_alive_associated_link=False,
                timeout=page_timeout,
            )
            return skip, (result or [])

        async def _extract_data(page_response):
            skip, page = page_response
            if not page or len(page) < _PAGE_SIZE:
                # Terminal page: eagerly release the connection for the common
                # full-enumeration case. A caller that abandons the iterator
                # early leaves cleanup to the owning client (which holds the
                # shared connection) and to garbage collection - the client's
                # handler set holds only a weak reference.
                await self.close()
                return None, iter(page)
            return str(skip + len(page)), iter(page)

        return AsyncItemPaged(_get_next, _extract_data)
