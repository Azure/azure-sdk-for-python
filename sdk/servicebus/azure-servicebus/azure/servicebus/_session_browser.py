# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional, Union

from ._base_handler import BaseHandler
from ._common.utils import create_authentication
from ._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from ._common import mgmt_handlers
from ._pyamqp.types import AMQPTypes, TYPE, VALUE

_LOGGER = logging.getLogger(__name__)

# The service checks for DateTime.MaxValue (C# 9999-12-31T23:59:59.9999999) to switch
# between "active messages" mode and "updated since" mode. On the AMQP wire, timestamps
# have millisecond precision, so DateTime.MaxValue becomes 253402300799999 ms from epoch.
# Python's datetime.timestamp() float math rounds this up by 1ms, so we use the
# pre-computed constant directly for the sentinel.
_MAX_DATETIME_MS = 253402300799999
_MAX_DATETIME = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
_PAGE_SIZE = 100


def _amqp_int_value(value):
    return {TYPE: AMQPTypes.int, VALUE: value}


def _amqp_timestamp_value(value):
    """Convert a datetime to an AMQP timestamp (milliseconds since epoch)."""
    return {TYPE: AMQPTypes.timestamp, VALUE: int(value.timestamp() * 1000)}


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
        self._auth_uri = f"sb://{self.fully_qualified_namespace}/{self._entity_name}"
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
        updated_since: Optional[datetime] = None,
        timeout: Optional[float] = None,
    ) -> List[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime updated_since: If specified, only sessions whose state was
            updated after this time are returned. If not specified, returns sessions with
            active messages in the entity.
        :keyword float timeout: The total operation timeout in seconds.
        :returns: A list of session ID strings.
        :rtype: list[str]
        """
        # DateTime.MaxValue triggers "active messages" mode on the service side.
        # A real timestamp triggers "sessions updated since" mode.
        use_sentinel = updated_since is None
        last_updated_time_ms = (
            _MAX_DATETIME_MS if use_sentinel
            else int(updated_since.timestamp() * 1000)
        )

        all_session_ids: List[str] = []
        skip = 0

        while True:
            message = {
                b"last-updated-time": {TYPE: AMQPTypes.timestamp, VALUE: last_updated_time_ms},
                b"skip": _amqp_int_value(skip),
                b"top": _amqp_int_value(_PAGE_SIZE),
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
            all_session_ids.extend(result)
            if len(result) < _PAGE_SIZE:
                break
            skip += len(result)

        return all_session_ids
