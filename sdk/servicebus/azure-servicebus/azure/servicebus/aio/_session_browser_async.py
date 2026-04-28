# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio  # pylint:disable=do-not-import-asyncio
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from ._base_handler_async import BaseHandler as AsyncBaseHandler
from .._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from .._common import mgmt_handlers
from .._session_browser import _amqp_int_value, _MAX_DATETIME_MS, _PAGE_SIZE
from .._pyamqp.types import AMQPTypes, TYPE, VALUE
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
        updated_since: Optional[datetime] = None,
        timeout: Optional[float] = None,
    ) -> List[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime updated_since: If specified, only sessions whose last update
            (state change or message activity) is after this time are returned. If not specified,
            returns sessions with active messages in the entity.
        :keyword float timeout: The total operation timeout in seconds.
        :returns: A list of session ID strings.
        :rtype: list[str]
        """
        if updated_since is None:
            last_updated_time_ms = _MAX_DATETIME_MS
        else:
            # Normalize naive datetimes to UTC. Python's datetime.timestamp()
            # interprets naive values as local time, which would make the wire
            # value depend on the host's timezone. Treat naive values as UTC
            # (consistent with how naive datetimes are handled elsewhere in
            # this SDK) and convert aware values to UTC before serializing.
            if updated_since.tzinfo is None:
                normalized = updated_since.replace(tzinfo=timezone.utc)
            else:
                normalized = updated_since.astimezone(timezone.utc)
            last_updated_time_ms = int(normalized.timestamp() * 1000)

        all_session_ids: List[str] = []
        skip = 0

        while True:
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
                timeout=timeout,
            )
            if not result:
                break
            all_session_ids.extend(result)
            if len(result) < _PAGE_SIZE:
                break
            skip += len(result)

        return all_session_ids
