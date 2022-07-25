#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import logging
import time
from urllib.parse import urlparse
import socket
from ssl import SSLError

from ._transport import Transport
from .sasl import SASLTransport, SASLWithWebSocket
from .session import Session
from .performatives import OpenFrame, CloseFrame
from .constants import (
    PORT,
    SECURE_PORT,
    WEBSOCKET_PORT,
    MAX_CHANNELS,
    MAX_FRAME_SIZE_BYTES,
    HEADER_FRAME,
    ConnectionState,
    EMPTY_FRAME,
    TransportType
)

from .error import (
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


def get_local_timeout(now, idle_timeout, last_frame_received_time):
    # type: (float, float, float) -> bool
    """Check whether the local timeout has been reached since a new incoming frame was received.

    :param float now: The current time to check against.
    :rtype: bool
    :returns: Whether to shutdown the connection due to timeout.
    """
    if idle_timeout and last_frame_received_time:
        time_since_last_received = now - last_frame_received_time
        return time_since_last_received > idle_timeout
    return False


class Connection(object): # pylint:disable=too-many-instance-attributes
    """An AMQP Connection.

    :ivar str state: The connection state.
    :param str endpoint: The endpoint to connect to. Must be fully qualified with scheme and port number.
    :keyword str container_id: The ID of the source container. If not set a GUID will be generated.
    :keyword int max_frame_size: Proposed maximum frame size in bytes. Default value is 64kb.
    :keyword int channel_max: The maximum channel number that may be used on the Connection. Default value is 65535.
    :keyword int idle_timeout: Connection idle time-out in seconds.
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
    """

    def __init__(self, endpoint, **kwargs): # pylint:disable=too-many-statements
        # type(str, Any) -> None
        parsed_url = urlparse(endpoint)
        self._hostname = parsed_url.hostname
        endpoint = self._hostname
        if parsed_url.port:
            self._port = parsed_url.port
        elif parsed_url.scheme == 'amqps':
            self._port = SECURE_PORT
        else:
            self._port = PORT
        self.state = None  # type: Optional[ConnectionState]

        # Custom Endpoint
        custom_endpoint_address = kwargs.get("custom_endpoint_address")
        custom_endpoint = None
        if custom_endpoint_address:
            custom_parsed_url = urlparse(custom_endpoint_address)
            custom_port = custom_parsed_url.port or WEBSOCKET_PORT
            custom_endpoint = "{}:{}{}".format(custom_parsed_url.hostname, custom_port, custom_parsed_url.path)

        transport = kwargs.get('transport')
        self._transport_type = kwargs.pop('transport_type', TransportType.Amqp)
        if transport:
            self._transport = transport
        elif 'sasl_credential' in kwargs:
            sasl_transport = SASLTransport
            if self._transport_type.name == 'AmqpOverWebsocket' or kwargs.get("http_proxy"):
                sasl_transport = SASLWithWebSocket
                endpoint = parsed_url.hostname + parsed_url.path
            self._transport = sasl_transport(
                host=endpoint,
                credential=kwargs['sasl_credential'],
                custom_endpoint=custom_endpoint,
                **kwargs
            )
        else:
            self._transport = Transport(parsed_url.netloc, transport_type=self._transport_type, **kwargs)

        self._container_id = kwargs.pop('container_id', None) or str(uuid.uuid4())  # type: str
        self._max_frame_size = kwargs.pop('max_frame_size', MAX_FRAME_SIZE_BYTES)  # type: int
        self._remote_max_frame_size = None  # type: Optional[int]
        self._channel_max = kwargs.pop('channel_max', MAX_CHANNELS)  # type: int
        self._idle_timeout = kwargs.pop('idle_timeout', None)  # type: Optional[int]
        self._outgoing_locales = kwargs.pop('outgoing_locales', None)  # type: Optional[List[str]]
        self._incoming_locales = kwargs.pop('incoming_locales', None)  # type: Optional[List[str]]
        self._offered_capabilities = None  # type: Optional[str]
        self._desired_capabilities = kwargs.pop('desired_capabilities', None)  # type: Optional[str]
        self._properties = kwargs.pop('properties', None)  # type: Optional[Dict[str, str]]

        self._allow_pipelined_open = kwargs.pop('allow_pipelined_open', True)  # type: bool
        self._remote_idle_timeout = None  # type: Optional[int]
        self._remote_idle_timeout_send_frame = None  # type: Optional[int]
        self._idle_timeout_empty_frame_send_ratio = kwargs.get('idle_timeout_empty_frame_send_ratio', 0.5)  # type: float, line-too-long
        self._last_frame_received_time = None  # type: Optional[float]
        self._last_frame_sent_time = None  # type: Optional[float]
        self._idle_wait_time = kwargs.get('idle_wait_time', 0.1)  # type: float
        self._network_trace = kwargs.get('network_trace', False)
        self._network_trace_params = {
            'connection': self._container_id,
            'session': None,
            'link': None
        }
        self._error = None
        self._outgoing_endpoints = {}  # type: Dict[int, Session]
        self._incoming_endpoints = {}  # type: Dict[int, Session]

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def _set_state(self, new_state):
        # type: (ConnectionState) -> None
        """Update the connection state."""
        if new_state is None:
            return
        previous_state = self.state
        self.state = new_state
        _LOGGER.info("Connection '%s' state changed: %r -> %r", self._container_id, previous_state, new_state)
        for session in self._outgoing_endpoints.values():
            session._on_connection_state_change()  # pylint:disable=protected-access

    def _connect(self):
        # type: () -> None
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
                self._process_incoming_frame(*self._read_frame(wait=True))
                if self.state != ConnectionState.HDR_EXCH:
                    self._disconnect()
                    raise ValueError("Did not receive reciprocal protocol header. Disconnecting.")
            else:
                self._set_state(ConnectionState.HDR_SENT)
        except (OSError, IOError, SSLError, socket.error) as exc:
            raise AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Failed to initiate the connection due to exception: " + str(exc),
                error=exc
            )
        except Exception: # pylint:disable=try-except-raise
            raise 

    def _disconnect(self):
        # type: () -> None
        """Disconnect the transport and set state to END."""
        if self.state == ConnectionState.END:
            return
        self._set_state(ConnectionState.END)
        self._transport.close()

    def _can_read(self):
        # type: () -> bool
        """Whether the connection is in a state where it is legal to read for incoming frames."""
        return self.state not in (ConnectionState.CLOSE_RCVD, ConnectionState.END)

    def _read_frame(self, wait=True, **kwargs):
        # type: (bool, Any) -> Tuple[int, Optional[Tuple[int, NamedTuple]]]
        """Read an incoming frame from the transport.

        :param Union[bool, float] wait: Whether to block on the socket while waiting for an incoming frame.
         The default value is `False`, where the frame will block for the configured timeout only (0.1 seconds).
         If set to `True`, socket will block indefinitely. If set to a timeout value in seconds, the socket will
         block for at most that value.
        :rtype: Tuple[int, Optional[Tuple[int, NamedTuple]]]
        :returns: A tuple with the incoming channel number, and the frame in the form or a tuple of performative
         descriptor and field values.
        """
        if self._can_read():
            if wait is False: # pylint:disable=no-else-return
                return self._transport.receive_frame(**kwargs)
            elif wait is True:
                with self._transport.block():
                    return self._transport.receive_frame(**kwargs)
            else:
                with self._transport.block_with_timeout(timeout=wait):
                    return self._transport.receive_frame(**kwargs)
        _LOGGER.warning("Cannot read frame in current state: %r", self.state)

    def _can_write(self):
        # type: () -> bool
        """Whether the connection is in a state where it is legal to write outgoing frames."""
        return self.state not in _CLOSING_STATES

    def _send_frame(self, channel, frame, timeout=None, **kwargs):
        # type: (int, NamedTuple, Optional[int], Any) -> None
        """Send a frame over the connection.

        :param int channel: The outgoing channel number.
        :param NamedTuple: The outgoing frame.
        :param int timeout: An optional timeout value to wait until the socket is ready to send the frame.
        :rtype: None
        """
        try:
            raise self._error
        except TypeError:
            pass

        if self._can_write():
            try:
                self._last_frame_sent_time = time.time()
                if timeout:
                    with self._transport.block_with_timeout(timeout):
                        self._transport.send_frame(channel, frame, **kwargs)
                else:
                    self._transport.send_frame(channel, frame, **kwargs)
            except (OSError, IOError, SSLError, socket.error) as exc:
                self._error = AMQPConnectionError(
                    ErrorCondition.SocketError,
                    description="Can not send frame out due to exception: " + str(exc),
                    error=exc
                )
            except Exception: # pylint:disable=try-except-raise
                raise
        else:
            _LOGGER.warning("Cannot write frame in current state: %r", self.state)

    def _get_next_outgoing_channel(self):
        # type: () -> int
        """Get the next available outgoing channel number within the max channel limit.

        :raises ValueError: If maximum channels has been reached.
        :returns: The next available outgoing channel number.
        :rtype: int
        """
        if (len(self._incoming_endpoints) + len(self._outgoing_endpoints)) >= self._channel_max:
            raise ValueError("Maximum number of channels ({}) has been reached.".format(self._channel_max))
        next_channel = next(i for i in range(1, self._channel_max) if i not in self._outgoing_endpoints)
        return next_channel

    def _outgoing_empty(self):
        # type: () -> None
        """Send an empty frame to prevent the connection from reaching an idle timeout."""
        if self._network_trace:
            _LOGGER.info("-> empty()", extra=self._network_trace_params)
        try:
            raise self._error
        except TypeError:
            pass
        try:
            if self._can_write():
                self._transport.write(EMPTY_FRAME)
                self._last_frame_sent_time = time.time()
        except (OSError, IOError, SSLError, socket.error) as exc:
            self._error = AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Can not send empty frame due to exception: " + str(exc),
                error=exc
            )
        except Exception: # pylint:disable=try-except-raise
            raise

    def _outgoing_header(self):
        # type: () -> None
        """Send the AMQP protocol header to initiate the connection."""
        self._last_frame_sent_time = time.time()
        if self._network_trace:
            _LOGGER.info("-> header(%r)", HEADER_FRAME, extra=self._network_trace_params)
        self._transport.write(HEADER_FRAME)

    def _incoming_header(self, _, frame):
        # type: (int, bytes) -> None
        """Process an incoming AMQP protocol header and update the connection state."""
        if self._network_trace:
            _LOGGER.info("<- header(%r)", frame, extra=self._network_trace_params)
        if self.state == ConnectionState.START:
            self._set_state(ConnectionState.HDR_RCVD)
        elif self.state == ConnectionState.HDR_SENT:
            self._set_state(ConnectionState.HDR_EXCH)
        elif self.state == ConnectionState.OPEN_PIPE:
            self._set_state(ConnectionState.OPEN_SENT)

    def _outgoing_open(self):
        # type: () -> None
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
            _LOGGER.info("-> %r", open_frame, extra=self._network_trace_params)
        self._send_frame(0, open_frame)

    def _incoming_open(self, channel, frame):
        # type: (int, Tuple[Any, ...]) -> None
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
            _LOGGER.info("<- %r", OpenFrame(*frame), extra=self._network_trace_params)
        if channel != 0:
            _LOGGER.error("OPEN frame received on a channel that is not 0.")
            self.close(
                error=AMQPError(
                    condition=ErrorCondition.NotAllowed,
                    description="OPEN frame received on a channel that is not 0."
                )
            )
            self._set_state(ConnectionState.END)
        if self.state == ConnectionState.OPENED:
            _LOGGER.error("OPEN frame received in the OPENED state.")
            self.close()
        if frame[4]:
            self._remote_idle_timeout = frame[4]/1000  # Convert to seconds
            self._remote_idle_timeout_send_frame = self._idle_timeout_empty_frame_send_ratio * self._remote_idle_timeout

        if frame[2] < 512:  # Ensure minimum max frame size.
            pass  # TODO: error
        self._remote_max_frame_size = frame[2]
        if self.state == ConnectionState.OPEN_SENT:
            self._set_state(ConnectionState.OPENED)
        elif self.state == ConnectionState.HDR_EXCH:
            self._set_state(ConnectionState.OPEN_RCVD)
            self._outgoing_open()
            self._set_state(ConnectionState.OPENED)
        else:
            pass # TODO what now...?

    def _outgoing_close(self, error=None):
        # type: (Optional[AMQPError]) -> None
        """Send a Close frame to shutdown connection with optional error information."""
        close_frame = CloseFrame(error=error)
        if self._network_trace:
            _LOGGER.info("-> %r", close_frame, extra=self._network_trace_params)
        self._send_frame(0, close_frame)

    def _incoming_close(self, channel, frame):
        # type: (int, Tuple[Any, ...]) -> None
        """Process incoming Open frame to finish the connection negotiation.

        The incoming frame format is::

            - frame[0]: error (Optional[AMQPError])

        """
        if self._network_trace:
            _LOGGER.info("<- %r", CloseFrame(*frame), extra=self._network_trace_params)
        disconnect_states = [
            ConnectionState.HDR_RCVD,
            ConnectionState.HDR_EXCH,
            ConnectionState.OPEN_RCVD,
            ConnectionState.CLOSE_SENT,
            ConnectionState.DISCARDING
        ]
        if self.state in disconnect_states:
            self._disconnect()
            self._set_state(ConnectionState.END)
            return

        close_error = None
        if channel > self._channel_max:
            _LOGGER.error("Invalid channel")
            close_error = AMQPError(condition=ErrorCondition.InvalidField, description="Invalid channel", info=None)

        self._set_state(ConnectionState.CLOSE_RCVD)
        self._outgoing_close(error=close_error)
        self._disconnect()
        self._set_state(ConnectionState.END)

        if frame[0]:
            self._error = AMQPConnectionError(
                condition=frame[0][0],
                description=frame[0][1],
                info=frame[0][2]
            )
            _LOGGER.error("Connection error: {}".format(frame[0])) # pylint:disable=logging-format-interpolation

    def _incoming_begin(self, channel, frame):
        # type: (int, Tuple[Any, ...]) -> None
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
            new_session = Session.from_incoming_frame(self, channel, frame)
            self._incoming_endpoints[channel] = new_session
            new_session._incoming_begin(frame)  # pylint:disable=protected-access

    def _incoming_end(self, channel, frame):
        # type: (int, Tuple[Any, ...]) -> None
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
        except KeyError:
            pass  # TODO: channel error
        #self._incoming_endpoints.pop(channel)  # TODO
        #self._outgoing_endpoints.pop(channel)  # TODO

    def _process_incoming_frame(self, channel, frame): # pylint:disable=too-many-return-statements
        # type: (int, Optional[Union[bytes, Tuple[int, Tuple[Any, ...]]]]) -> bool
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
            performative, fields = frame
        except TypeError:
            return True  # Empty Frame or socket timeout
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
                self._incoming_header(channel, fields)
                return True
            if performative == 1: # pylint:disable=no-else-return
                return False  # TODO: incoming EMPTY
            else:
                _LOGGER.error("Unrecognized incoming frame: {}".format(frame)) # pylint:disable=logging-format-interpolation
                return True
        except KeyError:
            return True  #TODO: channel error

    def _process_outgoing_frame(self, channel, frame):
        # type: (int, NamedTuple) -> None
        """Send an outgoing frame if the connection is in a legal state.

        :raises ValueError: If the connection is not open or not in a valid state.
        """
        if self._network_trace:
            _LOGGER.info("-> %r", frame, extra=self._network_trace_params)
        if not self._allow_pipelined_open and self.state in [ConnectionState.OPEN_PIPE, ConnectionState.OPEN_SENT]:
            raise ValueError("Connection not configured to allow pipeline send.")
        if self.state not in [ConnectionState.OPEN_PIPE, ConnectionState.OPEN_SENT, ConnectionState.OPENED]:
            raise ValueError("Connection not open.")
        now = time.time()
        if get_local_timeout(now, self._idle_timeout, self._last_frame_received_time) or self._get_remote_timeout(now):
            self.close(
                # TODO: check error condition
                error=AMQPError(
                    condition=ErrorCondition.ConnectionCloseForced,
                    description="No frame received for the idle timeout."
                ),
                wait=False
            )
            return
        self._send_frame(channel, frame)

    def _get_remote_timeout(self, now):
        # type: (float) -> bool
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
            if time_since_last_sent > self._remote_idle_timeout_send_frame:
                self._outgoing_empty()
        return False

    def _wait_for_response(self, wait, end_state):
        # type: (Union[bool, float], ConnectionState) -> None
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

    def listen(self, wait=False, batch=1, **kwargs):
        # type: (Union[float, int, bool], int, Any) -> None
        """Listen on the socket for incoming frames and process them.

        :param wait: Whether to block on the socket until a frame arrives. If set to `True`, socket will
         block indefinitely. Alternatively, if set to a time in seconds, the socket will block for at most
         the specified timeout. Default value is `False`, where the socket will block for its configured read
         timeout (by default 0.1 seconds).
        :type wait: int or float or bool
        :param int batch: The number of frames to attempt to read and process before returning. The default value
         is 1, i.e. process frames one-at-a-time. A higher value should only be used when a receiver is established
         and is processing incoming Transfer frames.
        :rtype: None
        """
        try:
            raise self._error
        except TypeError:
            pass
        try:
            if self.state not in _CLOSING_STATES:
                now = time.time()
                if get_local_timeout(now, self._idle_timeout, self._last_frame_received_time) or self._get_remote_timeout(now): # pylint:disable=line-too-long
                    # TODO: check error condition
                    self.close(
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
                new_frame = self._read_frame(wait=wait, **kwargs)
                if self._process_incoming_frame(*new_frame):
                    break
        except (OSError, IOError, SSLError, socket.error) as exc:
            self._error = AMQPConnectionError(
                ErrorCondition.SocketError,
                description="Can not send frame out due to exception: " + str(exc),
                error=exc
            )
        except Exception: # pylint:disable=try-except-raise
            raise

    def create_session(self, **kwargs):
        # type: (Any) -> Session
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
        """
        assigned_channel = self._get_next_outgoing_channel()
        kwargs['allow_pipelined_open'] = self._allow_pipelined_open
        kwargs['idle_wait_time'] = self._idle_wait_time
        session = Session(
            self,
            assigned_channel,
            network_trace=kwargs.pop('network_trace', self._network_trace),
            network_trace_params=dict(self._network_trace_params),
            **kwargs)
        self._outgoing_endpoints[assigned_channel] = session
        return session

    def open(self, wait=False):
        # type: (bool) -> None
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

    def close(self, error=None, wait=False):
        # type: (Optional[AMQPError], bool) -> None
        """Close the connection and disconnect the transport.

        Alternatively this method will be called on exiting a Connection context manager.

        :param ~uamqp.AMQPError error: Optional error information to include in the close request.
        :param bool wait: Whether to wait for a service Close response. Default is `False`.
        :rtype: None
        """
        if self.state in [ConnectionState.END, ConnectionState.CLOSE_SENT, ConnectionState.DISCARDING]:
            return
        try:
            self._outgoing_close(error=error)
            if error:
                self._error = AMQPConnectionError(
                    condition=error.condition,
                    description=error.descrption,
                    info=error.info
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
        except Exception as exc: # pylint:disable=broad-except
            # If error happened during closing, ignore the error and set state to END
            _LOGGER.info("An error occurred when closing the connection: %r", exc)
            self._set_state(ConnectionState.END)
        finally:
            self._disconnect()
