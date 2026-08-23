# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional

from azure.core.paging import ItemPaged

from ._base_handler import BaseHandler
from ._common.utils import (
    create_authentication,
    get_link_ready_deadline,
    check_link_ready_deadline,
)
from ._common.constants import (
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
)
from ._common import mgmt_handlers
from .exceptions import OperationTimeoutError

# The service checks `lastUpdatedTime != DateTime.MaxValue` (exact equality) to switch
# between default listing mode and updated-since mode. Default listing mode returns sessions
# with active messages or stored session state. The .NET AMQP library encodes
# DateTime.MaxValue as 253402300800000 ms (10000-01-01T00:00:00Z) due to double-to-long
# rounding in TimeSpan.TotalMilliseconds, and its decoder clamps values beyond
# DateTime.MaxValue.Ticks back to DateTime.MaxValue. This matches Track 1 Java's
# SessionBrowser.MAXDATE = new Date(253402300800000L).
_MAX_DATETIME_MS = 253402300800000
_PAGE_SIZE = 100
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _to_last_updated_ms(state_updated_after: Optional[datetime]) -> int:
    """Convert an optional filter datetime to the wire millisecond value.

    Returns the DateTime.MaxValue sentinel (default listing mode) when no filter
    is given; otherwise the UTC-normalized millisecond timestamp.

    :param state_updated_after: The optional filter datetime.
    :type state_updated_after: ~datetime.datetime or None
    :return: The millisecond value to send as ``last-updated-time``.
    :rtype: int
    """
    if state_updated_after is None:
        # DateTime.MaxValue triggers default listing mode on the service side.
        return _MAX_DATETIME_MS
    # Normalize naive datetimes to UTC. Python's datetime.timestamp() interprets
    # naive values as local time, which would make the wire value depend on the
    # host's timezone. Treat naive values as UTC (consistent with how naive
    # datetimes are handled elsewhere in this SDK) and convert aware values to
    # UTC before serializing.
    if state_updated_after.tzinfo is None:
        normalized = state_updated_after.replace(tzinfo=timezone.utc)
    else:
        normalized = state_updated_after.astimezone(timezone.utc)
    # Compute milliseconds with integer timedelta arithmetic rather than float
    # `timestamp() * 1000`. The float path rounds the maximum representable
    # datetime up to _MAX_DATETIME_MS, which would silently switch an explicit
    # filter into default listing mode, and truncates pre-epoch fractional
    # milliseconds toward zero. Floor division keeps datetime.max at
    # 253402300799999 and rounds consistently downward.
    return (normalized - _EPOCH) // timedelta(milliseconds=1)


def _page_request_body(
    amqp_transport: Any, last_updated_time_ms: int, skip: int
) -> Dict[str, Any]:
    """Build the get-message-sessions request body with transport-neutral value
    factories.

    Both the pyamqp and uamqp encoders then tag each field with its AMQP type.
    A hand-built pyamqp typed dict (``{"TYPE": ..., "VALUE": ...}``) is passed
    through untouched by uamqp and encoded as a nested map, so the service would
    receive a map where it expects a timestamp and two ints. ``skip`` and
    ``top`` travel as AMQP ints; ``last-updated-time`` travels as an AMQP
    timestamp carrying a raw millisecond value (the sentinel is year 10000 and
    cannot be a ``datetime``).

    :param amqp_transport: The pyamqp or uamqp transport providing the value factories.
    :type amqp_transport: ~azure.servicebus._transport._base.AmqpTransport
    :param int last_updated_time_ms: The ``last-updated-time`` wire value.
    :param int skip: The number of sessions to skip (page offset).
    :return: The management request body.
    :rtype: dict
    """
    return {
        "last-updated-time": amqp_transport.AMQP_TIMESTAMP_VALUE(last_updated_time_ms),
        "skip": amqp_transport.AMQP_INT_VALUE(skip),
        "top": amqp_transport.AMQP_INT_VALUE(_PAGE_SIZE),
    }


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

    def _open(self, timeout: Optional[float] = None):
        if self._running:
            return
        if self._handler:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        try:
            self._handler.open(connection=self._connection)
            deadline = get_link_ready_deadline(timeout)
            while not self._handler.client_ready():
                check_link_ready_deadline(deadline)
                time.sleep(0.05)
            self._running = True
        except:
            self._close_handler()
            raise

    def list_sessions(
        self,
        *,
        state_updated_after: Optional[datetime] = None,
        timeout: Optional[float] = None,
        _now: Callable[[], float] = time.monotonic,
    ) -> ItemPaged[str]:
        """List session IDs for this entity.

        :keyword ~datetime.datetime state_updated_after: If specified, only sessions whose
            session state was set or updated after this time are returned. If not specified,
            returns sessions with active messages or stored session state in the entity. Sessions
            with neither are excluded.
        :keyword float timeout: The total operation timeout in seconds, spent across
            every page of the enumeration.
        :keyword _now: Monotonic clock function, injectable for tests. Internal.
        :paramtype _now: callable
        :returns: A paged iterable of session ID strings.
        :rtype: ~azure.core.paging.ItemPaged[str]

        .. note::

            Pagination uses skip-based indexing over a server-side snapshot. If sessions
            are added or removed between page requests, the iterator may yield duplicate
            session IDs or skip some. Callers should not assume uniqueness.
        """
        last_updated_time_ms = _to_last_updated_ms(state_updated_after)
        # `timeout` is the total budget across every page. ItemPaged is lazy, so
        # establish the deadline on the first page fetch and share it, so a
        # multi-page enumeration cannot run for `timeout` seconds per page.
        deadline_state: list = [None]

        def _get_next(continuation_token):
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
            result = self._mgmt_request_response_with_retry(
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op,
                keep_alive_associated_link=False,
                timeout=page_timeout,
            )
            return skip, (result or [])

        def _extract_data(page_response):
            skip, page = page_response
            if not page or len(page) < _PAGE_SIZE:
                # Terminal page: eagerly release the connection for the common
                # full-enumeration case. A caller that abandons the iterator
                # early leaves cleanup to the owning client (which holds the
                # shared connection) and to garbage collection - the client's
                # handler set holds only a weak reference.
                self.close()
                return None, iter(page)
            return str(skip + len(page)), iter(page)

        return ItemPaged(_get_next, _extract_data)
