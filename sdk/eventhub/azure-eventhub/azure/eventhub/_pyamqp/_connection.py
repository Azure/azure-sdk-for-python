# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
import logging
import time
from urllib.parse import urlparse
import socket
from ssl import SSLError
from typing import Any, Dict, List, Tuple, Optional, NamedTuple, Type, Union, cast

from ._transport import Transport
from .sasl import SASLTransport, SASLWithWebSocket
from .session import Session
from .performatives import OpenFrame, CloseFrame
from .constants import (
    PORT,
    SECURE_PORT,
    SOCKET_TIMEOUT,
    WEBSOCKET_PORT,
    MAX_CHANNELS,
    MAX_FRAME_SIZE_BYTES,
    HEADER_FRAME,
    WS_TIMEOUT_INTERVAL,
    ConnectionState,
    EMPTY_FRAME,
    TransportType,
)

from .error import ErrorCondition, AMQPConnectionError, AMQPError

_LOGGER = logging.getLogger(__name__)
_CLOSING_STATES = (
    ConnectionState.OC_PIPE,
    ConnectionState.CLOSE_PIPE,
    ConnectionState.DISCARDING,
    ConnectionState.CLOSE_SENT,
    ConnectionState.END,
)


def get_local_timeout(now: float, idle_timeout: float, last_frame_received_time: float) -> bool:
    """Check whether the local timeout has been reached since a new incoming frame was received.

    :param float now: The current time to check against.
    :param float idle_timeout: The idle timeout value.
    :param float last_frame_received_time: The time the last frame was received.
    :returns: Whether to shutdown the connection due to timeout.
    :rtype: bool
    """
    if idle_timeout and last_frame_received_time:
        time_since_last_received = now - last_frame_received_time
        return time_since_last_received > idle_timeout
    return False


class Connection:  # pylint:disable=too-many-instance-attributes
    """An AMQP Connection.

    :ivar str state: The connection state.
    :param str endpoint: The endpoint to connect to. Must be fully qualified with scheme and port number.
    :keyword str container_id: The ID of the source container. If not set a GUID will be generated.
    :keyword int max_frame_size: Proposed maximum frame size in bytes. Default value is 64kb.
    :keyword int channel_max: The maximum channel number that may be used on the Connection. Default value is 65535.
    :keyword float idle_timeout: Connection idle time-out in seconds.
    :keyword list(str) outgoing_locales: Locales available for outgoing text.
    :keyword list(str) incoming_locales: Desired locales for incoming text in decreasing level of preference.
    :keyword list(str) offered_capabilities: The extension capabilities the sender supports.
    :keyword list(str) desired_capabilities: The extension capabilities the sender may use if the receiver supports
    :keyword dict properties: Connection properties.
    :keyword bool allow_pipelined_open: Allow frames to be sent on the connection before a response Open frame
     has been received. Default value is `True`.
    :keyword float idle_timeout_empty_frame_send_ratio: Portion of the idle timeout time to wait before sending an
     empty frame. The default portion is 50% of the idle timeout value (i.e. `0.5`).
    :keyword float idle_wait_time: The time in seconds to sleep while waiting for a response from the endpoint.
     Default value is `0.1`.
    :keyword bool network_trace: Whether to log the network traffic. Default value is `False`. If enabled, frames
     will be logged at the logging.INFO level.
    :keyword str transport_type: Determines if the transport type is Amqp or AmqpOverWebSocket.
     Defaults to TransportType.Amqp. It will be AmqpOverWebSocket if using http_proxy.
    :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value). When using these settings,
     the transport_type would be AmqpOverWebSocket.
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword float socket_timeout: The maximum time in seconds that the underlying socket in the transport should
     wait when reading or writing data before timing out. The default value is 0.2 (for transport type Amqp),
     and 1 for transport type AmqpOverWebsocket.
    """

    def __init__(  # pylint:disable=too-many-locals
        self,
        endpoint: str,
        *,
        container_id: Optional[str] = None,
        max_frame_size: int = MAX_FRAME_SIZE_BYTES,
        channel_max: int = MAX_CHANNELS,
        idle_timeout: Optional[float] = None,
        outgoing_locales: Optional[List[str]] = None,
        incoming_locales: Optional[List[str]] = None,
        offered_capabilities: Optional[List[str]] = None,
        desired_capabilities: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        allow_pipelined_open: bool = True,
        idle_timeout_empty_frame_send_ratio: float = 0.5,
        idle_wait_time: float = 0.1,
        network_trace: bool = False,
        transport_type: TransportType = TransportType.Amqp,
        http_proxy: Optional[Dict[str, Any]] = None,
        socket_timeout: Optional[float] = None,
        **kwargs: Any,
    ):  # pylint:disable=too-many-statements
        parsed_url = urlparse(endpoint)

        if parsed_url.hostname is None:
            raise ValueError(f"Invalid endpoint: {endpoint}")
        self._hostname = parsed_url.hostname
        kwargs["http_proxy"] = http_proxy
        endpoint = self._hostname
        if parsed_url.port and not kwargs.get("use_tls", True):
            self._port = parsed_url.port
        elif parsed_url.scheme == "amqps":
            self._port = SECURE_PORT
        else:
            self._port = PORT
        self.state: Optional[ConnectionState] = None

        # Set the port for AmqpOverWebsocket
        if transport_type.value == TransportType.AmqpOverWebsocket.value:
            self._port = WEBSOCKET_PORT

        # Custom Endpoint
        custom_endpoint_address = kwargs.get("custom_endpoint_address")
        custom_endpoint = None
        custom_port = None
        if custom_endpoint_address:
            custom_parsed_url = urlparse(custom_endpoint_address)
            if transport_type.value == TransportType.Amqp.value:
                custom_port = custom_parsed_url.port or SECURE_PORT
                custom_endpoint = f"{custom_parsed_url.hostname}"
            else:
                custom_port = custom_parsed_url.port or WEBSOCKET_PORT
                custom_endpoint = f"{custom_parsed_url.hostname}:{custom_port}{custom_parsed_url.path}"
        self._container_id = container_id or str(uuid.uuid4())
        self._network_trace = network_trace
        self._network_trace_params = {"amqpConnection": self._container_id, "amqpSession": "", "amqpLink": ""}

        transport = kwargs.get("transport")
        self._transport_type = transport_type
        self._socket_timeout = socket_timeout

        if self._transport_type.value == TransportType.Amqp.value and self._socket_timeout is None:
            self._socket_timeout = SOCKET_TIMEOUT
        elif self._transport_type.value == TransportType.AmqpOverWebsocket.value and self._socket_timeout is None:
            self._socket_timeout = WS_TIMEOUT_INTERVAL

        if transport:
            self._transport = transport
        elif "sasl_credential" in kwargs:
            sasl_transport: Union[Type[SASLTransport], Type[SASLWithWebSocket]] = SASLTransport
            if self._transport_type.name == "AmqpOverWebsocket" or kwargs.get("http_proxy"):
                sasl_transport = SASLWithWebSocket
                endpoint = parsed_url.hostname + parsed_url.path
            self._transport = sasl_transport(
                host=endpoint,
                credential=kwargs["sasl_credential"],
                port=self._port,
                custom_endpoint=custom_endpoint,
                custom_port=custom_port,
                socket_timeout=self._socket_timeout,
                network_trace_params=self._network_trace_params,
                **kwargs,
            )
        else:
            self._transport = Transport(
                parsed_url.netloc,
                transport_type=self._transport_type,
                socket_timeout=self._socket_timeout,
                network_trace_params=self._network_trace_params,
                **kwargs,
            )
        self._max_frame_size: int = max_frame_size
        self._remote_max_frame_size: Optional[int] = None
        self._channel_max: int = channel_max
        self._idle_timeout: Optional[float] = idle_timeout
        self._outgoing_locales: Optional[List[str]] = outgoing_locales
        self._incoming_locales: Optional[List[str]] = incoming_locales
        self._offered_capabilities: Optional[List[str]] = offered_capabilities
        self._desired_capabilities: Optional[List[str]] = desired_capabilities
        self._properties: Optional[Dict[str, Any]] = properties
        self._remote_properties: Optional[Dict[str, str]] = None

        self._allow_pipelined_open: bool = allow_pipelined_open
        self._remote_idle_timeout: Optional[float] = None
        self._remote_idle_timeout_send_frame: Optional[float] = None
        self._idle_timeout_empty_frame_send_ratio: float = idle_timeout_empty_frame_send_ratio
        self._last_frame_received_time: Optional[float] = None
        self._last_frame_sent_time: Optional[float] = None
        self._idle_wait_time: float = idle_wait_time
        self._error: Optional[AMQPConnectionError] = None
        self._outgoing_endpoints: Dict[int, Session] = {}
        self._incoming_endpoints: Dict[int, Session] = {}

    def __enter__(self) -> "Connection":
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _set_state(self, new_state: ConnectionState) -> None:
        """Update the connection state.
        :param ~pyamqp.constants.ConnectionState new_state: The new state of the connection.
        """
        if new_state is None:
            return
        previous_state = self.state
        self.state = new_state
        _LOGGER.info("Connection state changed: %r -> %r", previous_state, new_state, extra=self._network_trace_params)
        for session in self._outgoing_endpoints.values():
            session._on_connection_state_change()  # pylint:disable=protected-access

    def _connect(self) -> None:
        """Initiate the connection.

        If `allow_pipelined_open` is enabled, the incoming response header will be processed immediately
        and the state on exiting will be HDR_EXCH. Otherwise, the function will return before waiting for
        the response header and the final state will be HDR_SENT.

        :raises ValueError: If a reciprocating protocol header is not received during negotiation.
        """
        try:
            if not self.state:
                self._transport.connect()
                self._set_state(ConnectionState.START)
            self._transport.negotiate()
            self._outgoing_header()
            self._set_state(ConnectionState.HDR_SENT)
            if not self._allow_pipelined_open:
                # TODO: List/tuple expected as variable args
                self._read_frame(wait=True)
                if self.state != ConnectionState.HDR_EXCH:
                    self._disconnect()
                    raise ValueError("Did not receive reciprocal protocol header. Disconnecting.")
            else:
                self._set_state(ConnectionState.HDR_SENT)
        except (OSError, IOError, SSLError, socket.error) as exc:
            # FileNotFoundError is being raised for exception parity with uamqp when invalid
            # `connection_verify` file path is passed in. Remove later when resolving issue #27128.
            if isinstance(exc, FileNotFoundError) and exc.filename and "ca_certs" in exc.filename:
                raise
            raise AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Failed to initiate the connection due to exception: " + str(exc),
                error=exc,
            ) from exc

    def _disconnect(self) -> None:
        """Disconnect the transport and set state to END."""
        if self.state == ConnectionState.END:
            return
        self._set_state(ConnectionState.END)
        self._transport.close()

    def _can_read(self) -> bool:
        """Whether the connection is in a state where it is legal to read for incoming frames.
        :return: True if the connection is in a state where it is legal to read for incoming frames.
        :rtype: bool
        """
        return self.state not in (ConnectionState.CLOSE_RCVD, ConnectionState.END)

    def _read_frame(self, wait: Union[bool, float] = True, **kwargs: Any) -> bool:
        """Read an incoming frame from the transport.

        :param Union[bool, float] wait: Whether to block on the socket while waiting for an incoming frame.
         The default value is `False`, where the frame will block for the configured timeout only (0.1 seconds).
         If set to `True`, socket will block indefinitely. If set to a timeout value in seconds, the socket will
         block for at most that value.
        :rtype: Tuple[int, Optional[Tuple[int, NamedTuple]]]
        :returns: A tuple with the incoming channel number, and the frame in the form or a tuple of performative
         descriptor and field values.
        """
        # Since we use `sock.settimeout()` in the transport for reading/writing, that acts as a
        # "block with timeout" when we pass in a timeout value. If `wait` is float value, then
        # timeout was set during socket init.
        if wait is not True:  # wait is float/int/False
            new_frame = self._transport.receive_frame(**kwargs)
        else:
            with self._transport.block():
                new_frame = self._transport.receive_frame(**kwargs)
        return self._process_incoming_frame(*new_frame)

    def _can_write(self) -> bool:
        """Whether the connection is in a state where it is legal to write outgoing frames.
        :return: Whether the connection is in a state where it is legal to write outgoing frames.
        :rtype: bool
        """
        return self.state not in _CLOSING_STATES

    def _send_frame(self, channel: int, frame: NamedTuple, **kwargs: Any) -> None:
        """Send a frame over the connection.

        :param int channel: The outgoing channel number.
        :param NamedTuple frame: The outgoing frame.
        :rtype: None
        """
        if self._error:
            raise self._error

        if self._can_write():
            try:
                self._last_frame_sent_time = time.time()
                # Since we use `sock.settimeout()` in the transport for reading/writing,
                # that acts as a "block with timeout" when we pass in a timeout value.
                self._transport.send_frame(channel, frame, **kwargs)
            except (OSError, IOError, SSLError, socket.error) as exc:
                self._error = AMQPConnectionError(
                    ErrorCondition.SocketError,
                    description="Can not send frame out due to exception: " + str(exc),
                    error=exc,
                )
            except Exception:  # pylint:disable=try-except-raise
                raise
        else:
            _LOGGER.info("Cannot write frame in current state: %r", self.state, extra=self._network_trace_params)

    def _get_next_outgoing_channel(self) -> int:
        """Get the next available outgoing channel number within the max channel limit.

        :raises ValueError: If maximum channels has been reached.
        :returns: The next available outgoing channel number.
        :rtype: int
        """
        if (len(self._incoming_endpoints) + len(self._outgoing_endpoints)) >= self._channel_max:
            raise ValueError("Maximum number of channels ({}) has been reached.".format(self._channel_max))
        next_channel = next(i for i in range(1, self._channel_max) if i not in self._outgoing_endpoints)
        return next_channel

    def _outgoing_empty(self) -> None:
        """Send an empty frame to prevent the connection from reaching an idle timeout."""
        if self._error:
            raise self._error

        try:
            if self._can_write():
                if self._network_trace:
                    _LOGGER.debug("-> EmptyFrame()", extra=self._network_trace_params)
                self._transport.write(EMPTY_FRAME)
                self._last_frame_sent_time = time.time()
        except (OSError, IOError, SSLError, socket.error) as exc:
            self._error = AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Can not send empty frame due to exception: " + str(exc),
                error=exc,
            )
        except Exception:  # pylint:disable=try-except-raise
            raise

    def _outgoing_header(self) -> None:
        """Send the AMQP protocol header to initiate the connection."""
        self._last_frame_sent_time = time.time()
        if self._network_trace:
            _LOGGER.debug("-> Header(%r)", HEADER_FRAME, extra=self._network_trace_params)
        self._transport.write(HEADER_FRAME)

    def _incoming_header(self, _, frame: bytes) -> None:
        """Process an incoming AMQP protocol header and update the connection state.

        :param int _: Ignored.
        :param bytes frame: The incoming frame.
        """
        if self._network_trace:
            _LOGGER.debug("<- Header(%r)", frame, extra=self._network_trace_params)
        if self.state == ConnectionState.START:
            self._set_state(ConnectionState.HDR_RCVD)
        elif self.state == ConnectionState.HDR_SENT:
            self._set_state(ConnectionState.HDR_EXCH)
        elif self.state == ConnectionState.OPEN_PIPE:
            self._set_state(ConnectionState.OPEN_SENT)

    def _outgoing_open(self) -> None:
        """Send an Open frame to negotiate the AMQP connection functionality."""
        open_frame = OpenFrame(
            container_id=self._container_id,
            hostname=self._hostname,
            max_frame_size=self._max_frame_size,
            channel_max=self._channel_max,
            idle_timeout=self._idle_timeout * 1000 if self._idle_timeout else None,  # Convert to milliseconds
            outgoing_locales=self._outgoing_locales,
            incoming_locales=self._incoming_locales,
            offered_capabilities=self._offered_capabilities if self.state == ConnectionState.OPEN_RCVD else None,
            desired_capabilities=self._desired_capabilities if self.state == ConnectionState.HDR_EXCH else None,
            properties=self._properties,
        )
        if self._network_trace:
            _LOGGER.debug("-> %r", open_frame, extra=self._network_trace_params)
        self._send_frame(0, open_frame)

    def _incoming_open(self, channel: int, frame) -> None:
        """Process incoming Open frame to finish the connection negotiation.

        The incoming frame format is::

            - frame[0]: container_id (str)
            - frame[1]: hostname (str)
            - frame[2]: max_frame_size (int)
            - frame[3]: channel_max (int)
            - frame[4]: idle_timeout (Optional[int])
            - frame[5]: outgoing_locales (Optional[List[bytes]])
            - frame[6]: incoming_locales (Optional[List[bytes]])
            - frame[7]: offered_capabilities (Optional[List[bytes]])
            - frame[8]: desired_capabilities (Optional[List[bytes]])
            - frame[9]: properties (Optional[Dict[bytes, bytes]])

        :param int channel: The incoming channel number.
        :param frame: The incoming Open frame.
        :type frame: Tuple[Any, ...]
        :rtype: None
        """
        # TODO: Add type hints for full frame tuple contents.
        if self._network_trace:
            _LOGGER.debug("<- %r", OpenFrame(*frame), extra=self._network_trace_params)
        if channel != 0:
            _LOGGER.error("OPEN frame received on a channel that is not 0.", extra=self._network_trace_params)
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.NotAllowed, description="OPEN frame received on a channel that is not 0."
                )
            )
            self._set_state(ConnectionState.END)
        if self.state == ConnectionState.OPENED:
            _LOGGER.error("OPEN frame received in the OPENED state.", extra=self._network_trace_params)
            self.close()
        if frame[4]:
            self._remote_idle_timeout = cast(float, frame[4] / 1000)  # Convert to seconds
            self._remote_idle_timeout_send_frame = self._idle_timeout_empty_frame_send_ratio * self._remote_idle_timeout

        if frame[2] < 512:
            # Max frame size is less than supported minimum.
            # If any of the values in the received open frame are invalid then the connection shall be closed.
            # The error amqp:invalid-field shall be set in the error.condition field of the CLOSE frame.
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.InvalidField,
                    description="Failed parsing OPEN frame: Max frame size is less than supported minimum.",
                )
            )
            _LOGGER.error(
                "Failed parsing OPEN frame: Max frame size is less than supported minimum.",
                extra=self._network_trace_params,
            )
            return
        self._remote_max_frame_size = frame[2]
        self._remote_properties = frame[9]
        if self.state == ConnectionState.OPEN_SENT:
            self._set_state(ConnectionState.OPENED)
        elif self.state == ConnectionState.HDR_EXCH:
            self._set_state(ConnectionState.OPEN_RCVD)
            self._outgoing_open()
            self._set_state(ConnectionState.OPENED)
        else:
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.IllegalState,
                    description=f"connection is an illegal state: {self.state}",
                )
            )
            _LOGGER.error("Connection is an illegal state: %r", self.state, extra=self._network_trace_params)

    def _outgoing_close(self, error: Optional[AMQPError] = None) -> None:
        """Send a Close frame to shutdown connection with optional error information.
        :param ~pyamqp.error.AMQPError or None error: Optional error information.
        """
        close_frame = CloseFrame(error=error)
        if self._network_trace:
            _LOGGER.debug("-> %r", close_frame, extra=self._network_trace_params)
        self._send_frame(0, close_frame)

    def _incoming_close(self, channel: int, frame: Tuple[Any, ...]) -> None:
        """Process incoming Open frame to finish the connection negotiation.

        The incoming frame format is::

            - frame[0]: error (Optional[AMQPError])

        :param int channel: The incoming channel number.
        :param tuple frame: The incoming Close frame.
        """
        if self._network_trace:
            _LOGGER.debug("<- %r", CloseFrame(*frame), extra=self._network_trace_params)
        disconnect_states = [
            ConnectionState.HDR_RCVD,
            ConnectionState.HDR_EXCH,
            ConnectionState.OPEN_RCVD,
            ConnectionState.CLOSE_SENT,
            ConnectionState.DISCARDING,
        ]
        if self.state in disconnect_states:
            self._disconnect()
            return

        close_error = None
        if channel > self._channel_max:
            _LOGGER.error(
                "CLOSE frame received on a channel greated than support max.", extra=self._network_trace_params
            )
            close_error = AMQPError(condition=ErrorCondition.InvalidField, description="Invalid channel", info=None)

        self._set_state(ConnectionState.CLOSE_RCVD)
        self._outgoing_close(error=close_error)
        self._disconnect()

        if frame[0]:
            self._error = AMQPConnectionError(condition=frame[0][0], description=frame[0][1], info=frame[0][2])
            _LOGGER.warning("Connection closed with error: %r", frame[0], extra=self._network_trace_params)

    def _incoming_begin(self, channel: int, frame: Tuple[Any, ...]) -> None:
        """Process incoming Begin frame to finish negotiating a new session.

        The incoming frame format is::

            - frame[0]: remote_channel (int)
            - frame[1]: next_outgoing_id (int)
            - frame[2]: incoming_window (int)
            - frame[3]: outgoing_window (int)
            - frame[4]: handle_max (int)
            - frame[5]: offered_capabilities (Optional[List[bytes]])
            - frame[6]: desired_capabilities (Optional[List[bytes]])
            - frame[7]: properties (Optional[Dict[bytes, bytes]])

        :param int channel: The incoming channel number.
        :param frame: The incoming Begin frame.
        :type frame: Tuple[Any, ...]
        :rtype: None
        """
        try:
            existing_session = self._outgoing_endpoints[frame[0]]
            self._incoming_endpoints[channel] = existing_session
            self._incoming_endpoints[channel]._incoming_begin(frame)  # pylint:disable=protected-access
        except KeyError:
            new_session = Session.from_incoming_frame(self, channel)
            self._incoming_endpoints[channel] = new_session
            new_session._incoming_begin(frame)  # pylint:disable=protected-access

    def _incoming_end(self, channel: int, frame: Tuple[Any, ...]) -> None:
        """Process incoming End frame to close a session.

        The incoming frame format is::

            - frame[0]: error (Optional[AMQPError])

        :param int channel: The incoming channel number.
        :param frame: The incoming End frame.
        :type frame: Tuple[Any, ...]
        :rtype: None
        """
        try:
            self._incoming_endpoints[channel]._incoming_end(frame)  # pylint:disable=protected-access
            outgoing_channel = self._incoming_endpoints[channel].channel
            self._incoming_endpoints.pop(channel)
            self._outgoing_endpoints.pop(outgoing_channel)
        except KeyError:
            # close the connection
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.ConnectionCloseForced, description="Invalid channel number received"
                )
            )
            _LOGGER.error(
                "END frame received on invalid channel. Closing connection.", extra=self._network_trace_params
            )

    def _process_incoming_frame(  # pylint:disable=too-many-return-statements
        self, channel: int, frame: Optional[Union[bytes, Tuple[Any, ...]]]
    ) -> bool:
        """Process an incoming frame, either directly or by passing to the necessary Session.

        :param int channel: The channel the frame arrived on.
        :param frame: A tuple containing the performative descriptor and the field values of the frame.
         This parameter can be None in the case of an empty frame or a socket timeout.
        :type frame: Optional[Tuple[int, NamedTuple]]
        :rtype: bool
        :returns: A boolean to indicate whether more frames in a batch can be processed or whether the
         incoming frame has altered the state. If `True` is returned, the state has changed and the batch
         should be interrupted.
        """
        try:
            performative, fields = cast(Union[bytes, Tuple], frame)
        except TypeError:
            return True  # Empty Frame or socket timeout
        fields = cast(Tuple[Any, ...], fields)
        try:
            self._last_frame_received_time = time.time()
            if performative == 20:
                self._incoming_endpoints[channel]._incoming_transfer(fields)  # pylint:disable=protected-access
                return False
            if performative == 21:
                self._incoming_endpoints[channel]._incoming_disposition(fields)  # pylint:disable=protected-access
                return False
            if performative == 19:
                self._incoming_endpoints[channel]._incoming_flow(fields)  # pylint:disable=protected-access
                return False
            if performative == 18:
                self._incoming_endpoints[channel]._incoming_attach(fields)  # pylint:disable=protected-access
                return False
            if performative == 22:
                self._incoming_endpoints[channel]._incoming_detach(fields)  # pylint:disable=protected-access
                return True
            if performative == 17:
                self._incoming_begin(channel, fields)
                return True
            if performative == 23:
                self._incoming_end(channel, fields)
                return True
            if performative == 16:
                self._incoming_open(channel, fields)
                return True
            if performative == 24:
                self._incoming_close(channel, fields)
                return True
            if performative == 0:
                self._incoming_header(channel, cast(bytes, fields))
                return True
            if performative == 1:
                return False
            _LOGGER.error("Unrecognized incoming frame: %r", frame, extra=self._network_trace_params)
            return True
        except KeyError:
            return True  # TODO: channel error

    def _process_outgoing_frame(self, channel: int, frame) -> None:
        """Send an outgoing frame if the connection is in a legal state.

        :param int channel: The channel to send the frame on.
        :param NamedTuple frame: The frame to send.
        :return: None
        :rtype: None
        :raises ValueError: If the connection is not open or not in a valid state.
        """
        if not self._allow_pipelined_open and self.state in [
            ConnectionState.OPEN_PIPE,
            ConnectionState.OPEN_SENT,
        ]:
            raise ValueError("Connection not configured to allow pipeline send.")
        if self.state not in [
            ConnectionState.OPEN_PIPE,
            ConnectionState.OPEN_SENT,
            ConnectionState.OPENED,
        ]:
            raise AMQPConnectionError(ErrorCondition.SocketError, description="Connection not open.")
        now = time.time()
        if get_local_timeout(
            now,
            cast(float, self._idle_timeout),
            cast(float, self._last_frame_received_time),
        ) or self._get_remote_timeout(now):
            _LOGGER.info(
                "No frame received for the idle timeout. Closing connection.", extra=self._network_trace_params
            )
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.ConnectionCloseForced,
                    description="No frame received for the idle timeout.",
                ),
                wait=False,
            )
            return
        self._send_frame(channel, frame)

    def _get_remote_timeout(self, now: float) -> bool:
        """Check whether the local connection has reached the remote endpoints idle timeout since
        the last outgoing frame was sent.

        If the time since the last since frame is greater than the allowed idle interval, an Empty
        frame will be sent to maintain the connection.

        :param float now: The current time to check against.
        :rtype: bool
        :returns: Whether the local connection should be shutdown due to timeout.
        """
        if self._remote_idle_timeout and self._last_frame_sent_time:
            time_since_last_sent = now - self._last_frame_sent_time
            if time_since_last_sent > cast(int, self._remote_idle_timeout_send_frame):
                self._outgoing_empty()
        return False

    def _wait_for_response(self, wait: Union[bool, float], end_state: ConnectionState) -> None:
        """Wait for an incoming frame to be processed that will result in a desired state change.

        :param wait: Whether to wait for an incoming frame to be processed. Can be set to `True` to wait
         indefinitely, or an int to wait for a specified amount of time (in seconds). To not wait, set to `False`.
        :type wait: bool or float
        :param ConnectionState end_state: The desired end state to wait until.
        :rtype: None
        """
        if wait is True:
            self.listen(wait=False)
            while self.state != end_state:
                time.sleep(self._idle_wait_time)
                self.listen(wait=False)
        elif wait:
            self.listen(wait=False)
            timeout = time.time() + wait
            while self.state != end_state:
                if time.time() >= timeout:
                    break
                time.sleep(self._idle_wait_time)
                self.listen(wait=False)

    def listen(self, wait: Union[float, bool] = False, batch: int = 1, **kwargs: Any) -> None:
        """Listen on the socket for incoming frames and process them.

        :param wait: Whether to block on the socket until a frame arrives. If set to `True`, socket will
         block indefinitely. Alternatively, if set to a time in seconds, the socket will block for at most
         the specified timeout. Default value is `False`, where the socket will block for its configured read
         timeout (by default 0.2 seconds).
        :type wait: float or bool
        :param int batch: The number of frames to attempt to read and process before returning. The default value
         is 1, i.e. process frames one-at-a-time. A higher value should only be used when a receiver is established
         and is processing incoming Transfer frames.
        :rtype: None
        """
        if self._error:
            raise self._error

        try:
            if self.state not in _CLOSING_STATES:
                now = time.time()
                if get_local_timeout(
                    now,
                    cast(float, self._idle_timeout),
                    cast(float, self._last_frame_received_time),
                ) or self._get_remote_timeout(now):
                    _LOGGER.info(
                        "No frame received for the idle timeout. Closing connection.", extra=self._network_trace_params
                    )
                    self.close(
                        error=AMQPError(
                            condition=ErrorCondition.ConnectionCloseForced,
                            description="No frame received for the idle timeout.",
                        ),
                        wait=False,
                    )
                    return
            if self.state == ConnectionState.END:
                self._error = AMQPConnectionError(
                    condition=ErrorCondition.ConnectionCloseForced, description="Connection was already closed."
                )
                return
            for _ in range(batch):
                if self._can_read():
                    if self._read_frame(wait=wait, **kwargs):
                        break
                else:
                    _LOGGER.info(
                        "Connection cannot read frames in this state: %r", self.state, extra=self._network_trace_params
                    )
                    break
        except (OSError, IOError, SSLError, socket.error) as exc:
            self._error = AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Can not read frame due to exception: " + str(exc),
                error=exc,
            )
        except Exception:  # pylint:disable=try-except-raise
            raise

    def create_session(
        self,
        *,
        name: Optional[str] = None,
        next_outgoing_id: int = 0,
        incoming_window: int = 1,
        outgoing_window: int = 1,
        handle_max: int = 4294967295,
        offered_capabilities: Optional[List[str]] = None,
        desired_capabilities: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        allow_pipelined_open: Optional[bool] = None,
        idle_wait_time: Optional[float] = None,
        network_trace: Optional[bool] = None,
        **kwargs: Any,
    ) -> Session:
        """Create a new session within this connection.

        :keyword str name: The name of the connection. If not set a GUID will be generated.
        :keyword int next_outgoing_id: The transfer-id of the first transfer id the sender will send.
         Default value is 0.
        :keyword int incoming_window: The initial incoming-window of the Session. Default value is 1.
        :keyword int outgoing_window: The initial outgoing-window of the Session. Default value is 1.
        :keyword int handle_max: The maximum handle value that may be used on the session. Default value is 4294967295.
        :keyword list(str) offered_capabilities: The extension capabilities the session supports.
        :keyword list(str) desired_capabilities: The extension capabilities the session may use if
         the endpoint supports it.
        :keyword dict properties: Session properties.
        :keyword bool allow_pipelined_open: Allow frames to be sent on the connection before a response Open frame
         has been received. Default value is that configured for the connection.
        :keyword float idle_wait_time: The time in seconds to sleep while waiting for a response from the endpoint.
         Default value is that configured for the connection.
        :keyword bool network_trace: Whether to log the network traffic of this session. If enabled, frames
         will be logged at the logging.INFO level. Default value is that configured for the connection.

        :return: A new Session.
        :rtype: ~pyamqp._session.Session
        """
        assigned_channel = self._get_next_outgoing_channel()
        kwargs["offered_capabilities"] = offered_capabilities
        session = Session(
            self,
            assigned_channel,
            name=name,
            handle_max=handle_max,
            properties=properties,
            next_outgoing_id=next_outgoing_id,
            incoming_window=incoming_window,
            outgoing_window=outgoing_window,
            desired_capabilities=desired_capabilities,
            allow_pipelined_open=allow_pipelined_open or self._allow_pipelined_open,
            idle_wait_time=idle_wait_time or self._idle_wait_time,
            network_trace=network_trace or self._network_trace,
            network_trace_params=dict(self._network_trace_params),
            **kwargs,
        )
        self._outgoing_endpoints[assigned_channel] = session
        return session

    def open(self, wait: bool = False) -> None:
        """Send an Open frame to start the connection.

        Alternatively, this will be called on entering a Connection context manager.

        :param bool wait: Whether to wait to receive an Open response from the endpoint. Default is `False`.
        :raises ValueError: If `wait` is set to `False` and `allow_pipelined_open` is disabled.
        :rtype: None
        """
        self._connect()
        self._outgoing_open()
        if self.state == ConnectionState.HDR_EXCH:
            self._set_state(ConnectionState.OPEN_SENT)
        elif self.state == ConnectionState.HDR_SENT:
            self._set_state(ConnectionState.OPEN_PIPE)
        if wait:
            self._wait_for_response(wait, ConnectionState.OPENED)
        elif not self._allow_pipelined_open:
            raise ValueError("Connection has been configured to not allow piplined-open. Please set 'wait' parameter.")

    def close(self, error: Optional[AMQPError] = None, wait: bool = False) -> None:
        """Close the connection and disconnect the transport.

        Alternatively this method will be called on exiting a Connection context manager.

        :param ~uamqp.AMQPError error: Optional error information to include in the close request.
        :param bool wait: Whether to wait for a service Close response. Default is `False`.
        :rtype: None
        """
        try:
            if self.state in [
                ConnectionState.END,
                ConnectionState.CLOSE_SENT,
                ConnectionState.DISCARDING,
            ]:
                return
            self._outgoing_close(error=error)
            if error:
                self._error = AMQPConnectionError(
                    condition=error.condition,
                    description=error.description,
                    info=error.info,
                )
            if self.state == ConnectionState.OPEN_PIPE:
                self._set_state(ConnectionState.OC_PIPE)
            elif self.state == ConnectionState.OPEN_SENT:
                self._set_state(ConnectionState.CLOSE_PIPE)
            elif error:
                self._set_state(ConnectionState.DISCARDING)
            else:
                self._set_state(ConnectionState.CLOSE_SENT)
            self._wait_for_response(wait, ConnectionState.END)
        except Exception as exc:  # pylint:disable=broad-except
            # If error happened during closing, ignore the error and set state to END
            _LOGGER.info("An error occurred when closing the connection: %r", exc, extra=self._network_trace_params)
            self._set_state(ConnectionState.END)
        finally:
            self._disconnect()
