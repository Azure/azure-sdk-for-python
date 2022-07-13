# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import threading
import struct
import uuid
import logging
import time
from urllib.parse import urlparse
import socket
from ssl import SSLError
from enum import Enum
import asyncio

from ._transport_async import AsyncTransport
from ._sasl_async import SASLTransport, SASLWithWebSocket
from ._session_async import Session
from ..performatives import OpenFrame, CloseFrame
from .._connection import get_local_timeout
from ..constants import (
    PORT,
    SECURE_PORT,
    MAX_FRAME_SIZE_BYTES,
    MAX_CHANNELS,
    HEADER_FRAME,
    WEBSOCKET_PORT,
    ConnectionState,
    EMPTY_FRAME,
    TransportType
)

from ..error import (
    ErrorCondition,
    AMQPConnectionError,
    AMQPError
)

_LOGGER = logging.getLogger(__name__)
_CLOSING_STATES = (
    ConnectionState.OC_PIPE,
    ConnectionState.CLOSE_PIPE,
    ConnectionState.DISCARDING,
    ConnectionState.CLOSE_SENT,
    ConnectionState.END
)


class Connection(object):
    """
    :param str container_id: The ID of the source container.
    :param str hostname: The name of the target host.
    :param int max_frame_size: Proposed maximum frame size in bytes.
    :param int channel_max: The maximum channel number that may be used on the Connection.
    :param timedelta idle_timeout: Idle time-out in milliseconds.
    :param list(str) outgoing_locales: Locales available for outgoing text.
    :param list(str) incoming_locales: Desired locales for incoming text in decreasing level of preference.
    :param list(str) offered_capabilities: The extension capabilities the sender supports.
    :param list(str) desired_capabilities: The extension capabilities the sender may use if the receiver supports
    :param dict properties: Connection properties.
    :keyword str transport_type: Determines if the transport type is Amqp or AmqpOverWebSocket.
     Defaults to TransportType.Amqp. It will be AmqpOverWebSocket if using http_proxy.
    :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value). When using these settings,
     the transport_type would be AmqpOverWebSocket.
     Additionally the following keys may also be present: `'username', 'password'`.
    """

    def __init__(self, endpoint, **kwargs):
        parsed_url = urlparse(endpoint)
        self.hostname = parsed_url.hostname
        endpoint = self.hostname
        self._transport_type = kwargs.pop('transport_type', TransportType.Amqp)
        if parsed_url.port:
            self.port = parsed_url.port
        elif parsed_url.scheme == 'amqps':
            self.port = SECURE_PORT
        else:
            self.port = PORT
        self.state = None

        # Custom Endpoint
        custom_endpoint_address = kwargs.get("custom_endpoint_address")
        custom_endpoint = None
        if custom_endpoint_address:
            custom_parsed_url = urlparse(custom_endpoint_address)
            custom_port = custom_parsed_url.port or WEBSOCKET_PORT
            custom_endpoint = "{}:{}{}".format(custom_parsed_url.hostname, custom_port, custom_parsed_url.path)

        transport = kwargs.get('transport')
        if transport:
            self.transport = transport
        elif 'sasl_credential' in kwargs:
            sasl_transport = SASLTransport
            if self._transport_type.name == "AmqpOverWebsocket" or kwargs.get("http_proxy"):
                sasl_transport = SASLWithWebSocket
                endpoint = parsed_url.hostname + parsed_url.path
            self.transport = sasl_transport(
                host=endpoint,
                credential=kwargs['sasl_credential'],
                custom_endpoint=custom_endpoint,
                **kwargs
            )
        else:
            self.transport = AsyncTransport(parsed_url.netloc, **kwargs)
        self._container_id = kwargs.get('container_id') or str(uuid.uuid4())
        self.max_frame_size = kwargs.get('max_frame_size', MAX_FRAME_SIZE_BYTES)
        self._remote_max_frame_size = None
        self.channel_max = kwargs.get('channel_max', MAX_CHANNELS)
        self.idle_timeout = kwargs.get('idle_timeout')
        self.outgoing_locales = kwargs.get('outgoing_locales')
        self.incoming_locales = kwargs.get('incoming_locales')
        self.offered_capabilities = None
        self.desired_capabilities = kwargs.get('desired_capabilities')
        self.properties = kwargs.pop('properties', None)

        self.allow_pipelined_open = kwargs.get('allow_pipelined_open', True)
        self.remote_idle_timeout = None
        self.remote_idle_timeout_send_frame = None
        self.idle_timeout_empty_frame_send_ratio = kwargs.get('idle_timeout_empty_frame_send_ratio', 0.5)
        self.last_frame_received_time = None
        self.last_frame_sent_time = None
        self.idle_wait_time = kwargs.get('idle_wait_time', 0.1)
        self.network_trace = kwargs.get('network_trace', False)
        self.network_trace_params = {
            'connection': self._container_id,
            'session': None,
            'link': None
        }
        self._error = None
        self.outgoing_endpoints = {}
        self.incoming_endpoints = {}
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _set_state(self, new_state):
        # type: (ConnectionState) -> None
        """Update the connection state."""
        with self._lock:
            if new_state is None:
                return
            previous_state = self.state
            self.state = new_state
            _LOGGER.info("Connection '%s' state changed: %r -> %r", self._container_id, previous_state, new_state)

            for session in self.outgoing_endpoints.values():
                await session._on_connection_state_change()

    async def _connect(self):
        with self._lock:
            try:
                if not self.state:
                    await self.transport.connect()
                    await self._set_state(ConnectionState.START)
                await self.transport.negotiate()
                await self._outgoing_header()
                await self._set_state(ConnectionState.HDR_SENT)
                if not self.allow_pipelined_open:
                    await self._process_incoming_frame(*(await self._read_frame(wait=True)))
                    if self.state != ConnectionState.HDR_EXCH:
                        await self._disconnect()
                        raise ValueError("Did not receive reciprocal protocol header. Disconnecting.")
                else:
                    await self._set_state(ConnectionState.HDR_SENT)
            except (OSError, IOError, SSLError, socket.error) as exc:
                raise AMQPConnectionError(
                    ErrorCondition.SocketError,
                    description="Failed to initiate the connection due to exception: " + str(exc),
                    error=exc
                )

    async def _disconnect(self, *args):
        with self._lock:
            if self.state == ConnectionState.END:
                return
            await self._set_state(ConnectionState.END)
            self.transport.close()

    def _can_read(self):
        # type: () -> bool
        """Whether the connection is in a state where it is legal to read for incoming frames."""
        with self._lock:
            return self.state not in (ConnectionState.CLOSE_RCVD, ConnectionState.END)

    async def _read_frame(self, **kwargs):
        with self._lock:
            if self._can_read():
                return await self.transport.receive_frame(**kwargs)
            _LOGGER.warning("Cannot read frame in current state: %r", self.state)

    def _can_write(self):
        # type: () -> bool
        """Whether the connection is in a state where it is legal to write outgoing frames."""
        with self._lock:
            return self.state not in _CLOSING_STATES

    async def _send_frame(self, channel, frame, timeout=None, **kwargs):
        with self._lock:
            try:
                raise self._error
            except TypeError:
                pass

            if self._can_write():
                try:
                    self.last_frame_sent_time = time.time()
                    await self.transport.send_frame(channel, frame, **kwargs)
                except (OSError, IOError, SSLError, socket.error) as exc:
                    self._error = AMQPConnectionError(
                        ErrorCondition.SocketError,
                        description="Can not send frame out due to exception: " + str(exc),
                        error=exc
                    )
            else:
                _LOGGER.warning("Cannot write frame in current state: %r", self.state)

    def _get_next_outgoing_channel(self):
        # type: () -> int
        """Get the next available outgoing channel number within the max channel limit.

        :raises ValueError: If maximum channels has been reached.
        :returns: The next available outgoing channel number.
        :rtype: int
        """
        with self._lock:
            if (len(self.incoming_endpoints) + len(self.outgoing_endpoints)) >= self.channel_max:
                raise ValueError("Maximum number of channels ({}) has been reached.".format(self.channel_max))
            next_channel = next(i for i in range(1, self.channel_max) if i not in self.outgoing_endpoints)
            return next_channel

    async def _outgoing_empty(self):
        with self._lock:
            if self.network_trace:
                _LOGGER.info("-> empty()", extra=self.network_trace_params)
            try:
                if self._can_write():
                    await self.transport.write(EMPTY_FRAME)
                    self.last_frame_sent_time = time.time()
            except (OSError, IOError, SSLError, socket.error) as exc:
                self._error = AMQPConnectionError(
                    ErrorCondition.SocketError,
                    description="Can not send empty frame due to exception: " + str(exc),
                    error=exc
                )

    async def _outgoing_header(self):
        with self._lock:
            self.last_frame_sent_time = time.time()
            if self.network_trace:
                _LOGGER.info("-> header(%r)", HEADER_FRAME, extra=self.network_trace_params)
            await self.transport.write(HEADER_FRAME)

    async def _incoming_header(self, channel, frame):
        with self._lock:
            if self.network_trace:
                _LOGGER.info("<- header(%r)", frame, extra=self.network_trace_params)
            if self.state == ConnectionState.START:
                await self._set_state(ConnectionState.HDR_RCVD)
            elif self.state == ConnectionState.HDR_SENT:
                await self._set_state(ConnectionState.HDR_EXCH)
            elif self.state == ConnectionState.OPEN_PIPE:
                await self._set_state(ConnectionState.OPEN_SENT)

    async def _outgoing_open(self):
        with self._lock:
            open_frame = OpenFrame(
                container_id=self._container_id,
                hostname=self.hostname,
                max_frame_size=self.max_frame_size,
                channel_max=self.channel_max,
                idle_timeout=self.idle_timeout * 1000 if self.idle_timeout else None,  # Convert to milliseconds
                outgoing_locales=self.outgoing_locales,
                incoming_locales=self.incoming_locales,
                offered_capabilities=self.offered_capabilities if self.state == ConnectionState.OPEN_RCVD else None,
                desired_capabilities=self.desired_capabilities if self.state == ConnectionState.HDR_EXCH else None,
                properties=self.properties,
            )
            if self.network_trace:
                _LOGGER.info("-> %r", open_frame, extra=self.network_trace_params)
            await self._send_frame(0, open_frame)

    async def _incoming_open(self, channel, frame):
        with self._lock:
            if self.network_trace:
                _LOGGER.info("<- %r", OpenFrame(*frame), extra=self.network_trace_params)
            if channel != 0:
                _LOGGER.error("OPEN frame received on a channel that is not 0.")
                await self.close(error=None)  # TODO: not allowed
                await self._set_state(ConnectionState.END)
            if self.state == ConnectionState.OPENED:
                _LOGGER.error("OPEN frame received in the OPENED state.")
                await self.close()
            if frame[4]:
                self.remote_idle_timeout = frame[4] / 1000  # Convert to seconds
                self.remote_idle_timeout_send_frame = self.idle_timeout_empty_frame_send_ratio * self.remote_idle_timeout

            if frame[2] < 512:
                pass  # TODO: error
            self._remote_max_frame_size = frame[2]
            if self.state == ConnectionState.OPEN_SENT:
                await self._set_state(ConnectionState.OPENED)
            elif self.state == ConnectionState.HDR_EXCH:
                await self._set_state(ConnectionState.OPEN_RCVD)
                await self._outgoing_open()
                await self._set_state(ConnectionState.OPENED)
            else:
                pass  # TODO what now...?

    async def _outgoing_close(self, error=None):
        with self._lock:
            close_frame = CloseFrame(error=error)
            if self.network_trace:
                _LOGGER.info("-> %r", close_frame, extra=self.network_trace_params)
            await self._send_frame(0, close_frame)

    async def _incoming_close(self, channel, frame):
        with self._lock:
            if self.network_trace:
                _LOGGER.info("<- %r", CloseFrame(*frame), extra=self.network_trace_params)
            disconnect_states = [
                ConnectionState.HDR_RCVD,
                ConnectionState.HDR_EXCH,
                ConnectionState.OPEN_RCVD,
                ConnectionState.CLOSE_SENT,
                ConnectionState.DISCARDING
            ]
            if self.state in disconnect_states:
                await self._disconnect()
                await self._set_state(ConnectionState.END)
                return
            if channel > self.channel_max:
                _LOGGER.error("Invalid channel")

            await self._set_state(ConnectionState.CLOSE_RCVD)
            await self._outgoing_close()
            await self._disconnect()
            await self._set_state(ConnectionState.END)

            if frame[0]:
                self._error = AMQPConnectionError(
                    condition=frame[0][0],
                    description=frame[0][1],
                    info=frame[0][2]
                )
                _LOGGER.error("Connection error: {}".format(frame[0]))

    async def _incoming_begin(self, channel, frame):
        with self._lock:
            try:
                existing_session = self.outgoing_endpoints[frame[0]]
                self.incoming_endpoints[channel] = existing_session
                await self.incoming_endpoints[channel]._incoming_begin(frame)
            except KeyError:
                new_session = Session.from_incoming_frame(self, channel, frame)
                self.incoming_endpoints[channel] = new_session
                await new_session._incoming_begin(frame)

    async def _incoming_end(self, channel, frame):
        with self._lock:
            try:
                await self.incoming_endpoints[channel]._incoming_end(frame)
            except KeyError:
                pass  # TODO: channel error
            # self.incoming_endpoints.pop(channel)  # TODO
            # self.outgoing_endpoints.pop(channel)  # TODO

    async def _process_incoming_frame(self, channel, frame):
        with self._lock:
            try:
                performative, fields = frame
            except TypeError:
                return True  # Empty Frame or socket timeout
            try:
                self.last_frame_received_time = time.time()
                if performative == 20:
                    await self.incoming_endpoints[channel]._incoming_transfer(fields)
                    return False
                if performative == 21:
                    await self.incoming_endpoints[channel]._incoming_disposition(fields)
                    return False
                if performative == 19:
                    await self.incoming_endpoints[channel]._incoming_flow(fields)
                    return False
                if performative == 18:
                    await self.incoming_endpoints[channel]._incoming_attach(fields)
                    return False
                if performative == 22:
                    await self.incoming_endpoints[channel]._incoming_detach(fields)
                    return True
                if performative == 17:
                    await self._incoming_begin(channel, fields)
                    return True
                if performative == 23:
                    await self._incoming_end(channel, fields)
                    return True
                if performative == 16:
                    await self._incoming_open(channel, fields)
                    return True
                if performative == 24:
                    await self._incoming_close(channel, fields)
                    return True
                if performative == 0:
                    await self._incoming_header(channel, fields)
                    return True
                if performative == 1:
                    return False  # TODO: incoming EMPTY
                else:
                    _LOGGER.error("Unrecognized incoming frame: {}".format(frame))
                    return True
            except KeyError:
                return True  # TODO: channel error

    async def _process_outgoing_frame(self, channel, frame):
        with self._lock:
            if self.network_trace:
                _LOGGER.info("-> %r", frame, extra=self.network_trace_params)
            if not self.allow_pipelined_open and self.state in [ConnectionState.OPEN_PIPE, ConnectionState.OPEN_SENT]:
                raise ValueError("Connection not configured to allow pipeline send.")
            if self.state not in [ConnectionState.OPEN_PIPE, ConnectionState.OPEN_SENT, ConnectionState.OPENED]:
                raise ValueError("Connection not open.")
            now = time.time()
            if get_local_timeout(now, self.idle_timeout, self.last_frame_received_time) or (
            await self._get_remote_timeout(now)):
                await self.close(
                    # TODO: check error condition
                    error=AMQPError(
                        condition=ErrorCondition.ConnectionCloseForced,
                        description="No frame received for the idle timeout."
                    ),
                    wait=False
                )
                return
            await self._send_frame(channel, frame)

    async def _get_remote_timeout(self, now):
        with self._lock:
            if self.remote_idle_timeout and self.last_frame_sent_time:
                time_since_last_sent = now - self.last_frame_sent_time
                if time_since_last_sent > self.remote_idle_timeout_send_frame:
                    await self._outgoing_empty()
            return False

    async def _wait_for_response(self, wait, end_state):
        # type: (Union[bool, float], ConnectionState) -> None
        with self._lock:
            if wait == True:
                await self.listen(wait=False)
                while self.state != end_state:
                    await asyncio.sleep(self.idle_wait_time)
                    await self.listen(wait=False)
            elif wait:
                await self.listen(wait=False)
                timeout = time.time() + wait
                while self.state != end_state:
                    if time.time() >= timeout:
                        break
                    await asyncio.sleep(self.idle_wait_time)
                    await self.listen(wait=False)

    async def _listen_one_frame(self, **kwargs):
        with self._lock:
            new_frame = await self._read_frame(**kwargs)
            return await self._process_incoming_frame(*new_frame)

    async def listen(self, wait=False, batch=1, **kwargs):
        with self._lock:
            try:
                raise self._error
            except TypeError:
                pass
            try:
                if self.state not in _CLOSING_STATES:
                    now = time.time()
                    if get_local_timeout(now, self.idle_timeout, self.last_frame_received_time) or (
                    await self._get_remote_timeout(now)):
                        # TODO: check error condition
                        await self.close(
                            error=AMQPError(
                                condition=ErrorCondition.ConnectionCloseForced,
                                description="No frame received for the idle timeout."
                            ),
                            wait=False
                        )
                        return
                if self.state == ConnectionState.END:
                    # TODO: check error condition
                    self._error = AMQPConnectionError(
                        condition=ErrorCondition.ConnectionCloseForced,
                        description="Connection was already closed."
                    )
                    return
                for _ in range(batch):
                    if await asyncio.ensure_future(self._listen_one_frame(**kwargs)):
                        # TODO: compare the perf difference between ensure_future and direct await
                        break
            except (OSError, IOError, SSLError, socket.error) as exc:
                self._error = AMQPConnectionError(
                    ErrorCondition.SocketError,
                    description="Can not send frame out due to exception: " + str(exc),
                    error=exc
                )

    def create_session(self, **kwargs):
        with self._lock:
            assigned_channel = self._get_next_outgoing_channel()
            kwargs['allow_pipelined_open'] = self.allow_pipelined_open
            kwargs['idle_wait_time'] = self.idle_wait_time
            session = Session(
                self,
                assigned_channel,
                network_trace=kwargs.pop('network_trace', self.network_trace),
                network_trace_params=dict(self.network_trace_params),
                **kwargs)
            self.outgoing_endpoints[assigned_channel] = session
            return session

    async def open(self, wait=False):
        with self._lock:
            await self._connect()
            await self._outgoing_open()
            if self.state == ConnectionState.HDR_EXCH:
                await self._set_state(ConnectionState.OPEN_SENT)
            elif self.state == ConnectionState.HDR_SENT:
                await self._set_state(ConnectionState.OPEN_PIPE)
            if wait:
                await self._wait_for_response(wait, ConnectionState.OPENED)
            elif not self.allow_pipelined_open:
                raise ValueError("Connection has been configured to not allow piplined-open. Please set 'wait' parameter.")

    async def close(self, error=None, wait=False):
        with self._lock:
            if self.state in [ConnectionState.END, ConnectionState.CLOSE_SENT]:
                return
            try:
                await self._outgoing_close(error=error)
                if error:
                    self._error = AMQPConnectionError(
                        condition=error.condition,
                        description=error.description,
                        info=error.info
                    )
                if self.state == ConnectionState.OPEN_PIPE:
                    await self._set_state(ConnectionState.OC_PIPE)
                elif self.state == ConnectionState.OPEN_SENT:
                    await self._set_state(ConnectionState.CLOSE_PIPE)
                elif error:
                    await self._set_state(ConnectionState.DISCARDING)
                else:
                    await self._set_state(ConnectionState.CLOSE_SENT)
                await self._wait_for_response(wait, ConnectionState.END)
            except Exception as exc:
                # If error happened during closing, ignore the error and set state to END
                _LOGGER.info("An error occurred when closing the connection: %r", exc)
                await self._set_state(ConnectionState.END)
            finally:
                await self._disconnect()
