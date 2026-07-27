# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio  # pylint:disable=do-not-import-asyncio
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator, Optional

from ._base_handler_async import BaseHandler as AsyncBaseHandler
from .._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from .._common import mgmt_handlers
from .._session_browser import _amqp_int_value, _EPOCH, _MAX_DATETIME_MS, _PAGE_SIZE
from .._pyamqp.types import AMQPTypes, TYPE, VALUE
from ..exceptions import OperationTimeoutError
from ._async_utils import create_authentication


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

    def _create_handler(self, auth):
        self._handler = self._amqp_transport.create_mgmt_client_async(
            config=self._config,
            auth=auth,
            properties=self._properties,
            retry_policy=self._error_policy,
            client_name=self._name,
        )

    async def _open(self):
        if self._running:
            return
        if self._handler:
            await self._handler.close_async()
        auth = None if self._connection else (await create_authentication(self))
        self._create_handler(auth)
        try:
            await self._handler.open_async(connection=self._connection)
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
            self._running = True
        except:
            await self._close_handler()
            raise

    async def list_sessions(
        self,
        *,
        state_updated_after: Optional[datetime] = None,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime state_updated_after: If specified, only sessions whose
            session state was set or updated after this time are returned. If not specified,
            returns sessions with active messages in the entity.
        :keyword float timeout: The total operation timeout in seconds.
        :returns: An async iterator of session ID strings.
        :rtype: AsyncIterator[str]

        .. note::

            Pagination uses skip-based indexing over a server-side snapshot. If sessions
            are added or removed between page requests, the iterator may yield duplicate
            session IDs or skip some. Callers should not assume uniqueness.
        """
        if state_updated_after is None:
            last_updated_time_ms = _MAX_DATETIME_MS
        else:
            # Normalize naive datetimes to UTC. Python's datetime.timestamp()
            # interprets naive values as local time, which would make the wire
            # value depend on the host's timezone. Treat naive values as UTC
            # (consistent with how naive datetimes are handled elsewhere in
            # this SDK) and convert aware values to UTC before serializing.
            if state_updated_after.tzinfo is None:
                normalized = state_updated_after.replace(tzinfo=timezone.utc)
            else:
                normalized = state_updated_after.astimezone(timezone.utc)
            # Compute milliseconds with integer timedelta arithmetic rather than
            # float `timestamp() * 1000`. The float path rounds the maximum
            # representable datetime up to _MAX_DATETIME_MS, which would silently
            # switch an explicit filter into active-messages mode, and truncates
            # pre-epoch fractional milliseconds toward zero. Floor division keeps
            # datetime.max at 253402300799999 and rounds consistently downward.
            last_updated_time_ms = (normalized - _EPOCH) // timedelta(milliseconds=1)

        skip = 0
        # `timeout` is the total operation budget across every page. Compute one
        # deadline up front and pass each page the remaining time, so a multi-page
        # enumeration cannot run for `timeout` seconds per page.
        deadline = None if timeout is None else time.monotonic() + timeout

        while True:
            # A paused iterator must not reopen the connection after the owning
            # ServiceBusClient has been closed. _check_live() raises once the
            # handler is shut down, before _open() could resurrect resources.
            self._check_live()
            if deadline is None:
                page_timeout = None
            else:
                page_timeout = deadline - time.monotonic()
                if page_timeout <= 0:
                    raise OperationTimeoutError(
                        message="Listing sessions did not complete within the specified timeout."
                    )
            message = {
                "last-updated-time": {TYPE: AMQPTypes.timestamp, VALUE: last_updated_time_ms},
                "skip": _amqp_int_value(skip),
                "top": _amqp_int_value(_PAGE_SIZE),
            }
            result = await self._mgmt_request_response_with_retry(
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op,
                keep_alive_associated_link=False,
                timeout=page_timeout,
            )
            if not result:
                break
            for sid in result:
                yield sid
            if len(result) < _PAGE_SIZE:
                break
            skip += len(result)
