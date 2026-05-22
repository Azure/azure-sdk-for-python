# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import uuid
from datetime import datetime, timezone
from typing import Iterator, Optional

from ._base_handler import BaseHandler
from ._common.utils import create_authentication
from ._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from ._common import mgmt_handlers
from ._pyamqp.types import AMQPTypes, TYPE, VALUE

# The service checks `lastUpdatedTime != DateTime.MaxValue` (exact equality) to switch
# between "active messages" mode and "updated since" mode. The .NET AMQP library encodes
# DateTime.MaxValue as 253402300800000 ms (10000-01-01T00:00:00Z) due to double-to-long
# rounding in TimeSpan.TotalMilliseconds, and its decoder clamps values beyond
# DateTime.MaxValue.Ticks back to DateTime.MaxValue. This matches Track 1 Java's
# SessionBrowser.MAXDATE = new Date(253402300800000L).
_MAX_DATETIME_MS = 253402300800000
_PAGE_SIZE = 100


def _amqp_int_value(value):
    return {TYPE: AMQPTypes.int, VALUE: value}


class _SessionBrowser(BaseHandler):
    """Internal handler that opens an AMQP connection for management-only operations.

    Unlike ServiceBusSender/ServiceBusReceiver, this does NOT create a sender or
    receiver link. It only opens a connection and authenticates, then sends
    management requests to the $management endpoint.

    Used for entity-level management operations like get-message-sessions where
    a sender or receiver link is not needed.
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
        self._handler = self._amqp_transport.create_mgmt_client(
            config=self._config,
            auth=auth,
            properties=self._properties,
            retry_policy=self._error_policy,
            client_name=self._name,
        )

    def _open(self):
        if self._running:
            return
        if self._handler:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        try:
            self._handler.open(connection=self._connection)
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._running = True
        except:
            self._close_handler()
            raise

    def list_sessions(
        self,
        *,
        updated_after: Optional[datetime] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime updated_after: If specified, only sessions whose
            session state was set or updated after this time are returned. If not specified,
            returns sessions with active messages in the entity.
        :keyword float timeout: The total operation timeout in seconds.
        :returns: An iterator of session ID strings.
        :rtype: iterator[str]
        """
        # DateTime.MaxValue triggers "active messages" mode on the service side.
        # A real timestamp triggers "sessions updated since" mode.
        if updated_after is None:
            last_updated_time_ms = _MAX_DATETIME_MS
        else:
            # Normalize naive datetimes to UTC. Python's datetime.timestamp()
            # interprets naive values as local time, which would make the wire
            # value depend on the host's timezone. Treat naive values as UTC
            # (consistent with how naive datetimes are handled elsewhere in
            # this SDK) and convert aware values to UTC before serializing.
            if updated_after.tzinfo is None:
                normalized = updated_after.replace(tzinfo=timezone.utc)
            else:
                normalized = updated_after.astimezone(timezone.utc)
            last_updated_time_ms = int(normalized.timestamp() * 1000)

        skip = 0

        while True:
            message = {
                "last-updated-time": {TYPE: AMQPTypes.timestamp, VALUE: last_updated_time_ms},
                "skip": _amqp_int_value(skip),
                "top": _amqp_int_value(_PAGE_SIZE),
            }
            result = self._mgmt_request_response_with_retry(
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op,
                keep_alive_associated_link=False,
                timeout=timeout,
            )
            if not result:
                break
            yield from result
            if len(result) < _PAGE_SIZE:
                break
            skip += len(result)
