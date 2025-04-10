# -------------------------------------------------------------------------  # pylint: disable=file-needs-copyright-header,useless-suppression
# This is a fork of the transport.py which was originally written by Barry Pederson and
# maintained by the Celery project: https://github.com/celery/py-amqp.
#
# Copyright (C) 2009 Barry Pederson <bp@barryp.org>
#
# The license text can also be found here:
# http://www.opensource.org/licenses/BSD-3-Clause
#
# License
# =======
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------

import asyncio
import errno
import socket
import ssl
import struct
from ssl import SSLError
from io import BytesIO
import logging


from .._platform import KNOWN_TCP_OPTS, SOL_TCP
from .._encode import encode_frame
from .._decode import decode_frame, decode_empty_frame
from ..constants import (
    DEFAULT_WEBSOCKET_HEARTBEAT_SECONDS,
    TLS_HEADER_FRAME,
    WEBSOCKET_PORT,
    AMQP_WS_SUBPROTOCOL,
    CONNECT_TIMEOUT,
)
from .._transport import (
    AMQP_FRAME,
    get_errno,
    to_host_port,
    DEFAULT_SOCKET_SETTINGS,
    SIGNED_INT_MAX,
    _UNAVAIL,
    AMQP_PORT,
)
from ..error import AuthenticationException, ErrorCondition


_LOGGER = logging.getLogger(__name__)


class AsyncTransportMixin:
    async def receive_frame(self, timeout=None, **kwargs):
        try:
            header, channel, payload = await asyncio.wait_for(self.read(**kwargs), timeout=timeout)
            if not payload:
                decoded = decode_empty_frame(header)
            else:
                decoded = decode_frame(payload)
            return channel, decoded
        except (
            TimeoutError,
            socket.timeout,
            asyncio.IncompleteReadError,
            asyncio.TimeoutError,
        ):
            return None, None

    async def read(self, verify_frame_type=0):
        async with self.socket_lock:
            read_frame_buffer = BytesIO()
            try:
                frame_header = memoryview(bytearray(8))
                read_frame_buffer.write(await self._read(8, buffer=frame_header, initial=True))

                channel = struct.unpack(">H", frame_header[6:])[0]
                size = frame_header[0:4]
                if size == AMQP_FRAME:  # Empty frame or AMQP header negotiation
                    return frame_header, channel, None
                size = struct.unpack(">I", size)[0]
                offset = frame_header[4]
                frame_type = frame_header[5]
                if verify_frame_type is not None and frame_type != verify_frame_type:
                    _LOGGER.debug(
                        "Received invalid frame type: %r, expected: %r",
                        frame_type,
                        verify_frame_type,
                        extra=self.network_trace_params,
                    )
                    raise ValueError(f"Received invalid frame type: {frame_type}, expected: {verify_frame_type}")
                # >I is an unsigned int, but the argument to sock.recv is signed,
                # so we know the size can be at most 2 * SIGNED_INT_MAX
                payload_size = size - len(frame_header)
                payload = memoryview(bytearray(payload_size))
                if size > SIGNED_INT_MAX:
                    read_frame_buffer.write(await self._read(SIGNED_INT_MAX, buffer=payload))
                    read_frame_buffer.write(await self._read(size - SIGNED_INT_MAX, buffer=payload[SIGNED_INT_MAX:]))
                else:
                    read_frame_buffer.write(await self._read(payload_size, buffer=payload))
            except (
                asyncio.CancelledError,
                asyncio.TimeoutError,
                TimeoutError,
                socket.timeout,
                asyncio.IncompleteReadError,
            ):
                read_frame_buffer.write(self._read_buffer.getvalue())
                self._read_buffer = read_frame_buffer
                self._read_buffer.seek(0)
                raise
            except (OSError, IOError, SSLError, socket.error) as exc:
                # Don't disconnect for ssl read time outs
                # http://bugs.python.org/issue10272
                if isinstance(exc, SSLError) and "timed out" in str(exc):
                    raise socket.timeout()
                if get_errno(exc) not in _UNAVAIL:
                    self.connected = False
                _LOGGER.debug("Transport read failed: %r", exc, extra=self.network_trace_params)
                raise
            offset -= 2
        return frame_header, channel, payload[offset:]

    async def write(self, s):
        async with self.socket_lock:
            try:
                await self._write(s)
            except socket.timeout:
                raise
            except (OSError, IOError, socket.error) as exc:
                _LOGGER.debug("Transport write failed: %r", exc, extra=self.network_trace_params)
                if get_errno(exc) not in _UNAVAIL:
                    self.connected = False
                raise

    async def send_frame(self, channel, frame, **kwargs):
        header, performative = encode_frame(frame, **kwargs)
        if performative is None:
            data = header
        else:
            encoded_channel = struct.pack(">H", channel)
            data = header + encoded_channel + performative

        await self.write(data)

    def _build_ssl_opts(self, sslopts):
        if sslopts in [True, False, None, {}]:
            return sslopts
        try:
            if "context" in sslopts:
                return sslopts["context"]
            ssl_version = sslopts.get("ssl_version")
            if ssl_version is None:
                ssl_version = ssl.PROTOCOL_TLS_CLIENT

            context = ssl.SSLContext(ssl_version)

            purpose = ssl.Purpose.SERVER_AUTH

            ca_certs = sslopts.get("ca_certs")

            if ca_certs is not None:
                try:
                    context.load_verify_locations(ca_certs)
                except FileNotFoundError as exc:
                    # FileNotFoundError does not have missing filename info, so adding it below.
                    # since this is the only file path that users can pass in
                    # (`connection_verify` in the EH/SB clients) through opts above.
                    exc.filename = {"ca_certs": ca_certs}
                    raise exc from None
            elif context.verify_mode != ssl.CERT_NONE:
                # load the default system root CA certs.
                context.load_default_certs(purpose=purpose)

            certfile = sslopts.get("certfile")
            keyfile = sslopts.get("keyfile")
            if certfile is not None:
                context.load_cert_chain(certfile, keyfile)

            server_hostname = sslopts.get("server_hostname")
            cert_reqs = sslopts.get("cert_reqs", ssl.CERT_REQUIRED)
            if cert_reqs == ssl.CERT_NONE and server_hostname is None:
                context.check_hostname = False
                context.verify_mode = cert_reqs

            return context
        except TypeError:
            raise TypeError("SSL configuration must be a dictionary, or the value True.") from None


class AsyncTransport(AsyncTransportMixin):  # pylint: disable=too-many-instance-attributes
    """Common superclass for TCP and SSL transports."""

    def __init__(
        self,
        host,
        *,
        port=AMQP_PORT,
        ssl_opts=False,
        socket_settings=None,
        raise_on_initial_eintr=True,
        use_tls: bool = True,
        **kwargs,
    ):
        self.connected = False
        self.sock = None
        self.reader = None
        self.writer = None
        self.raise_on_initial_eintr = raise_on_initial_eintr
        self._read_buffer = BytesIO()
        self.host, self.port = to_host_port(host, port)
        self.host = kwargs.get("custom_endpoint") or self.host
        self.port = kwargs.get("custom_port") or self.port
        self.socket_settings = socket_settings
        self.socket_lock = asyncio.Lock()
        self.sslopts = ssl_opts
        self.network_trace_params = kwargs.get("network_trace_params")
        self._use_tls = use_tls

    async def connect(self):
        try:
            # are we already connected?
            if self.connected:
                return
            try:
                # Building ssl opts here instead of constructor, so that invalid cert error is raised
                # when client is connecting, rather then during creation. For uamqp exception parity.
                self.sslopts = self._build_ssl_opts(self.sslopts)
            except FileNotFoundError as exc:
                # FileNotFoundError does not have missing filename info, so adding it below.
                # Assuming that this must be ca_certs, since this is the only file path that
                # users can pass in (`connection_verify` in the EH/SB clients) through sslopts above.
                # For uamqp exception parity. Remove later when resolving issue #27128.
                exc.filename = self.sslopts
                raise exc
            self.reader, self.writer = await asyncio.open_connection(
                host=self.host,
                port=self.port,
                ssl=self.sslopts if self._use_tls else None,
                family=socket.AF_UNSPEC,
                proto=SOL_TCP,
                server_hostname=self.host if self._use_tls else None,
            )
            self.connected = True
            sock = self.writer.transport.get_extra_info("socket")
            if sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self._set_socket_options(sock, self.socket_settings)

        except (OSError, IOError, SSLError) as e:
            _LOGGER.info("Transport connect failed: %r", e, extra=self.network_trace_params)
            # if not fully connected, close socket, and reraise error
            if self.writer and not self.connected:
                self.writer.close()
                await self.writer.wait_closed()
                self.connected = False
            raise

    def _get_tcp_socket_defaults(self, sock):
        tcp_opts = {}
        for opt in KNOWN_TCP_OPTS:
            enum = None
            if opt == "TCP_USER_TIMEOUT":
                try:
                    from socket import TCP_USER_TIMEOUT as enum
                except ImportError:
                    # should be in Python 3.6+ on Linux.
                    enum = 18
            elif hasattr(socket, opt):
                enum = getattr(socket, opt)

            if enum:
                if opt in DEFAULT_SOCKET_SETTINGS:
                    tcp_opts[enum] = DEFAULT_SOCKET_SETTINGS[opt]
                elif hasattr(socket, opt):
                    tcp_opts[enum] = sock.getsockopt(SOL_TCP, getattr(socket, opt))
        return tcp_opts

    def _set_socket_options(self, sock, socket_settings):
        tcp_opts = self._get_tcp_socket_defaults(sock)
        if socket_settings:
            tcp_opts.update(socket_settings)
        for opt, val in tcp_opts.items():
            sock.setsockopt(SOL_TCP, opt, val)

    async def _read(
        self,
        toread,
        initial=False,
        buffer=None,
        _errnos=(errno.ENOENT, errno.EAGAIN, errno.EINTR),
    ):
        # According to SSL_read(3), it can at most return 16kb of data.
        # Thus, we use an internal read buffer like TCPTransport._read
        # to get the exact number of bytes wanted.
        length = 0
        view = buffer or memoryview(bytearray(toread))
        nbytes = self._read_buffer.readinto(view)
        toread -= nbytes
        length += nbytes
        try:
            while toread:
                try:
                    view[nbytes : nbytes + toread] = await self.reader.readexactly(toread)
                    nbytes = toread
                except AttributeError:
                    # This means that close() was called concurrently
                    # self.reader has been set to None.
                    raise IOError("Connection has already been closed") from None
                except asyncio.IncompleteReadError as exc:
                    pbytes = len(exc.partial)
                    view[nbytes : nbytes + pbytes] = exc.partial
                    nbytes = pbytes
                except socket.error as exc:
                    # ssl.sock.read may cause a SSLerror without errno
                    # http://bugs.python.org/issue10272
                    if isinstance(exc, SSLError) and "timed out" in str(exc):
                        raise socket.timeout()
                    # errno 110 is equivalent to ETIMEDOUT on linux non blocking sockets, when a keep alive is set,
                    # and is set when the connection to the server doesnt succeed
                    # https://man7.org/linux/man-pages/man7/tcp.7.html.
                    # This behavior is linux specific and only on async. sync Linux & async/sync Windows & Mac raised
                    # ConnectionAborted or ConnectionReset errors which properly end up in a retry loop.
                    if exc.errno in [110]:
                        raise ConnectionAbortedError("The connection was closed abruptly.") from exc
                    # ssl.sock.read may cause ENOENT if the
                    # operation couldn't be performed (Issue celery#1414).
                    if exc.errno in _errnos:
                        if initial and self.raise_on_initial_eintr:
                            raise socket.timeout()
                        continue
                    raise
                if not nbytes:
                    raise IOError("Server unexpectedly closed connection")

                length += nbytes
                toread -= nbytes
        except:  # noqa
            self._read_buffer = BytesIO(view[:length])
            raise
        return view

    async def _write(self, s):
        """Write a string out to the SSL socket fully.
        :param str s: The string to write.
        """
        try:
            self.writer.write(s)
            await self.writer.drain()
        except AttributeError:
            raise IOError("Connection has already been closed") from None

    async def close(self):
        async with self.socket_lock:
            try:
                if self.writer is not None:
                    # Closing the writer closes the underlying socket.
                    self.writer.close()
                    if self.sslopts:
                        # see issue: https://github.com/encode/httpx/issues/914
                        await asyncio.sleep(0)
                        self.writer.transport.abort()
                    await self.writer.wait_closed()
            except Exception as e:  # pylint: disable=broad-except
                # Sometimes SSL raises APPLICATION_DATA_AFTER_CLOSE_NOTIFY here on close.
                _LOGGER.debug("Error shutting down socket: %r", e, extra=self.network_trace_params)
            self.writer, self.reader = None, None
        self.connected = False

    async def negotiate(self):
        if not self.sslopts:
            return
        await self.write(TLS_HEADER_FRAME)
        _, returned_header = await self.receive_frame(verify_frame_type=None)
        if returned_header[1] == TLS_HEADER_FRAME:
            raise ValueError(
                f"""Mismatching TLS header protocol. Expected: {TLS_HEADER_FRAME!r},"""
                """received: {returned_header[1]!r}"""
            )


class WebSocketTransportAsync(AsyncTransportMixin):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        host,
        *,
        port=WEBSOCKET_PORT,
        socket_timeout=CONNECT_TIMEOUT,
        ssl_opts=None,
        use_tls: bool = True,
        **kwargs,
    ):
        self._read_buffer = BytesIO()
        self.socket_lock = asyncio.Lock()
        self.sslopts = ssl_opts if isinstance(ssl_opts, dict) else None
        self.socket_timeout = socket_timeout
        self._custom_endpoint = kwargs.get("custom_endpoint")
        self.host, self.port = to_host_port(host, port)
        self.sock = None
        self.session = None
        self._http_proxy = kwargs.get("http_proxy", None)
        self.connected = False
        self.network_trace_params = kwargs.get("network_trace_params")
        self._use_tls = use_tls

    async def connect(self):
        self.sslopts = self._build_ssl_opts(self.sslopts)
        username, password = None, None
        http_proxy_host, http_proxy_port = None, None
        http_proxy_auth = None

        if self._http_proxy:
            http_proxy_host = self._http_proxy["proxy_hostname"]
            http_proxy_port = self._http_proxy["proxy_port"]
            if http_proxy_host and http_proxy_port:
                http_proxy_host = f"{http_proxy_host}:{http_proxy_port}"
            username = self._http_proxy.get("username", None)
            password = self._http_proxy.get("password", None)

        try:
            from aiohttp import (  # pylint: disable=networking-import-outside-azure-core-transport
                ClientSession,
                ClientConnectorError,
                ClientWSTimeout,
            )
            from urllib.parse import urlsplit
        except ImportError:
            raise ImportError("Please install aiohttp library to use async websocket transport.") from None
        if username or password:
            from aiohttp import BasicAuth  # pylint: disable=networking-import-outside-azure-core-transport

            http_proxy_auth = BasicAuth(login=username, password=password)

        self.session = ClientSession()
        if self._custom_endpoint:
            url = f"wss://{self._custom_endpoint}" if self._use_tls else f"ws://{self._custom_endpoint}"
        else:
            url = f"wss://{self.host}" if self._use_tls else f"ws://{self.host}"
            parsed_url = urlsplit(url)
            url = f"{parsed_url.scheme}://{parsed_url.netloc}:{self.port}{parsed_url.path}"

        try:
            # Enabling heartbeat that sends a ping message every n seconds and waits for pong response.
            # if pong response is not received then close connection. This raises an error when trying
            # to communicate with the websocket which is no longer active.
            # We are waiting a bug fix in aiohttp for these 2 bugs where aiohttp ws might hang on network disconnect
            # and the heartbeat mechanism helps mitigate these two.
            # https://github.com/aio-libs/aiohttp/pull/5860
            # https://github.com/aio-libs/aiohttp/issues/2309

            self.sock = await self.session.ws_connect(
                url=url,
                timeout=ClientWSTimeout(ws_close=self.socket_timeout),
                protocols=[AMQP_WS_SUBPROTOCOL],
                autoclose=False,
                proxy=http_proxy_host,
                proxy_auth=http_proxy_auth,
                ssl=self.sslopts if self._use_tls else None,
                heartbeat=DEFAULT_WEBSOCKET_HEARTBEAT_SECONDS,
            )
        except ClientConnectorError as exc:
            _LOGGER.info("Websocket connect failed: %r", exc, extra=self.network_trace_params)
            if self._custom_endpoint:
                raise AuthenticationException(
                    ErrorCondition.ClientError,
                    description="Failed to authenticate the connection due to exception: " + str(exc),
                    error=exc,
                ) from exc
            raise ConnectionError("Failed to establish websocket connection: " + str(exc)) from exc
        self.connected = True

    async def _read(self, toread, buffer=None, **kwargs):  # pylint: disable=unused-argument
        """Read exactly n bytes from the peer.

        :param int toread: The number of bytes to read.
        :param bytearray or None buffer: The buffer to read into. If not specified, a new buffer is allocated.
        :return: The buffer of bytes read.
        :rtype: bytearray
        """
        length = 0
        view = buffer or memoryview(bytearray(toread))
        nbytes = self._read_buffer.readinto(view)
        length += nbytes
        toread -= nbytes
        try:
            try:
                while toread:
                    data = await self.sock.receive_bytes()
                    read_length = len(data)
                    if read_length <= toread:
                        view[length : length + read_length] = data
                        toread -= read_length
                        length += read_length
                    else:
                        view[length : length + toread] = data[0:toread]
                        self._read_buffer = BytesIO(data[toread:])
                        toread = 0
                return view
            except TypeError as te:
                # aiohttp websocket raises TypeError when a websocket disconnects, as it ends up
                # reading None over the wire and cant convert to bytes.
                raise ConnectionError("Websocket disconnected: %r" % te) from None
        except:
            self._read_buffer = BytesIO(view[:length])
            raise

    async def close(self):
        """Do any preliminary work in shutting down the connection."""
        async with self.socket_lock:
            await self.sock.close()
            await self.session.close()
            self.connected = False

    async def _write(self, s):
        """Completely write a string (byte array) to the peer.
        ABNF, OPCODE_BINARY = 0x2
        See http://tools.ietf.org/html/rfc5234
        http://tools.ietf.org/html/rfc6455#section-5.2

        :param str s: The string to write.
        """
        await self.sock.send_bytes(s)
