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

import errno
import re
import socket
import ssl
import struct
from ssl import SSLError
from contextlib import contextmanager
from io import BytesIO
import logging
from threading import Lock

from ._platform import KNOWN_TCP_OPTS, SOL_TCP
from ._encode import encode_frame
from ._decode import decode_frame, decode_empty_frame
from .constants import (
    TLS_HEADER_FRAME,
    WEBSOCKET_PORT,
    TransportType,
    AMQP_WS_SUBPROTOCOL,
    WS_TIMEOUT_INTERVAL,
    SOCKET_TIMEOUT,
    CONNECT_TIMEOUT,
)
from .error import AuthenticationException, ErrorCondition


try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore  # noqa


def set_cloexec(fd, cloexec):  # noqa # pylint: disable=inconsistent-return-statements
    """Set flag to close fd after exec.
    :param int fd: File descriptor.
    :param bool cloexec: Close on exec.
    :return: Returns 0 on success, raises an OSError exception on failure.
    :rtype: int
    """
    if fcntl is None:
        return
    try:
        FD_CLOEXEC = fcntl.FD_CLOEXEC
    except AttributeError:
        raise NotImplementedError(
            "close-on-exec flag not supported on this platform",
        ) from None
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    if cloexec:
        flags |= FD_CLOEXEC
    else:
        flags &= ~FD_CLOEXEC
    return fcntl.fcntl(fd, fcntl.F_SETFD, flags)


_LOGGER = logging.getLogger(__name__)
_UNAVAIL = {errno.EAGAIN, errno.EINTR, errno.ENOENT, errno.EWOULDBLOCK}

AMQP_PORT = 5672
AMQPS_PORT = 5671
AMQP_FRAME = memoryview(b"AMQP")
EMPTY_BUFFER = b""
SIGNED_INT_MAX = 0x7FFFFFFF

# Match things like: [fe80::1]:5432, from RFC 2732
IPV6_LITERAL = re.compile(r"\[([\.0-9a-f:]+)\](?::(\d+))?")

DEFAULT_SOCKET_SETTINGS = {
    "TCP_NODELAY": 1,
    "TCP_USER_TIMEOUT": 1000,
    "TCP_KEEPIDLE": 60,
    "TCP_KEEPINTVL": 10,
    "TCP_KEEPCNT": 9,
}


def get_errno(exc):
    """Get exception errno (if set).

    Notes:
        :exc:`socket.error` and :exc:`IOError` first got
        the ``.errno`` attribute in Py2.7.

    :param Exception exc: Exception instance.
    :return: Exception errno.
    :rtype: int
    """
    try:
        return exc.errno
    except AttributeError:
        try:
            # e.args = (errno, reason)
            if isinstance(exc.args, tuple) and len(exc.args) == 2:
                return exc.args[0]
        except AttributeError:
            pass
    return 0


# TODO: fails when host = hostname:port/path. fix
def to_host_port(host, port=AMQP_PORT):
    """Convert hostname:port string to host, port tuple.
    :param str host: Hostname.
    :param int port: Port number.
    :return: Tuple of (host, port).
    :rtype: tuple
    """
    m = IPV6_LITERAL.match(host)
    if m:
        host = m.group(1)
        if m.group(2):
            port = int(m.group(2))
    else:
        if ":" in host:
            host, port = host.rsplit(":", 1)
            port = int(port)
    return host, port


class UnexpectedFrame(Exception):
    pass


class _AbstractTransport(object):  # pylint: disable=too-many-instance-attributes
    """Common superclass for TCP and SSL transports."""

    def __init__(
        self,
        host,
        *,
        port=AMQP_PORT,
        connect_timeout=CONNECT_TIMEOUT,
        socket_timeout=SOCKET_TIMEOUT,
        socket_settings=None,
        raise_on_initial_eintr=True,
        use_tls: bool = True,
        **kwargs,
    ):
        self._quick_recv = None
        self.connected = False
        self.sock = None
        self.raise_on_initial_eintr = raise_on_initial_eintr
        self._read_buffer = BytesIO()
        self.host, self.port = to_host_port(host, port)
        self.network_trace_params = kwargs.get("network_trace_params")

        self.connect_timeout = connect_timeout
        self.socket_timeout = socket_timeout
        self.socket_settings = socket_settings
        self.socket_lock = Lock()

        self._use_tls = use_tls

    def connect(self):
        try:
            # are we already connected?
            if self.connected:
                return
            self.sock = socket.create_connection((self.host, self.port), self.connect_timeout)
            try:
                set_cloexec(self.sock, True)
            except NotImplementedError:
                pass
            self._init_socket(
                self.socket_settings,
                self.socket_timeout,
            )
            # we've sent the banner; signal connect
            # EINTR, EAGAIN, EWOULDBLOCK would signal that the banner
            # has _not_ been sent
            self.connected = True
        except (OSError, IOError, SSLError) as e:
            _LOGGER.info("Transport connection failed: %r", e, extra=self.network_trace_params)
            # if not fully connected, close socket, and reraise error
            if self.sock and not self.connected:
                self.sock.close()
                self.sock = None
            raise

    @contextmanager
    def block(self):
        bocking_timeout = None
        sock = self.sock
        prev = sock.gettimeout()
        if prev != bocking_timeout:
            sock.settimeout(bocking_timeout)
        try:
            yield self.sock
        except SSLError as exc:
            if "timed out" in str(exc):
                # http://bugs.python.org/issue10272
                raise socket.timeout()
            if "The operation did not complete" in str(exc):
                # Non-blocking SSL sockets can throw SSLError
                raise socket.timeout()
            raise
        except socket.error as exc:
            if get_errno(exc) == errno.EWOULDBLOCK:
                raise socket.timeout()
            raise
        finally:
            if bocking_timeout != prev:
                sock.settimeout(prev)

    @contextmanager
    def non_blocking(self):
        non_bocking_timeout = 0.0
        sock = self.sock
        prev = sock.gettimeout()
        if prev != non_bocking_timeout:
            sock.settimeout(non_bocking_timeout)
        try:
            yield self.sock
        except SSLError as exc:
            if "timed out" in str(exc):
                # http://bugs.python.org/issue10272
                raise socket.timeout()
            if "The operation did not complete" in str(exc):
                # Non-blocking SSL sockets can throw SSLError
                raise socket.timeout()
            raise
        except socket.error as exc:
            if get_errno(exc) == errno.EWOULDBLOCK:
                raise socket.timeout()
            raise
        finally:
            if non_bocking_timeout != prev:
                sock.settimeout(prev)


    def _init_socket(self, socket_settings, socket_timeout):
        self.sock.settimeout(None)  # set socket back to blocking mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._set_socket_options(socket_settings)

        # set socket timeouts
        # for timeout, interval in ((socket.SO_SNDTIMEO, write_timeout),
        #                           (socket.SO_RCVTIMEO, read_timeout)):
        #     if interval is not None:
        #         sec = int(interval)
        #         usec = int((interval - sec) * 1000000)
        #         self.sock.setsockopt(
        #             socket.SOL_SOCKET, timeout,
        #             pack('ll', sec, usec),
        #         )
        self._setup_transport()
        self.sock.settimeout(socket_timeout)  # set socket to blocking with timeout

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

    def _set_socket_options(self, socket_settings):
        tcp_opts = self._get_tcp_socket_defaults(self.sock)
        if socket_settings:
            tcp_opts.update(socket_settings)
        for opt, val in tcp_opts.items():
            self.sock.setsockopt(SOL_TCP, opt, val)

    def _read(self, n, initial=False, buffer=None, _errnos=None):
        """Read exactly n bytes from the peer.
        :param int n: The number of bytes to read.
        :param bool initial: Whether this is the initial read of a frame.
        :param bytearray or None buffer: A buffer to read into.
        :param list or None _errnos: A list of socket errors to catch.
        :return: None
        :rtype: None
        """
        raise NotImplementedError("Must be overriden in subclass")

    def _setup_transport(self):
        """Do any additional initialization of the class."""

    def _shutdown_transport(self):
        """Do any preliminary work in shutting down the connection."""

    def _write(self, s):
        """Completely write a string to the peer.
        :param str s: The string to write.
        :return: None
        :rtype: None
        """
        raise NotImplementedError("Must be overriden in subclass")

    def close(self):
        with self.socket_lock:
            if self.sock is not None:
                self._shutdown_transport()
                # Call shutdown first to make sure that pending messages
                # reach the AMQP broker if the program exits after
                # calling this method.
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception as exc:  # pylint: disable=broad-except
                    # TODO: shutdown could raise OSError, Transport endpoint is not connected if the endpoint is already
                    #  disconnected. can we safely ignore the errors since the close operation is initiated by us.
                    _LOGGER.debug(
                        "Transport endpoint is already disconnected: %r", exc, extra=self.network_trace_params
                    )
                self.sock.close()
                self.sock = None
            self.connected = False

    def read(self, verify_frame_type=0):
        with self.socket_lock:
            read = self._read
            read_frame_buffer = BytesIO()
            try:
                frame_header = memoryview(bytearray(8))
                read_frame_buffer.write(read(8, buffer=frame_header, initial=True))

                channel = struct.unpack(">H", frame_header[6:])[0]
                size = frame_header[0:4]
                if size == AMQP_FRAME:  # Empty frame or AMQP header negotiation TODO
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
                    read_frame_buffer.write(read(SIGNED_INT_MAX, buffer=payload))
                    read_frame_buffer.write(read(size - SIGNED_INT_MAX, buffer=payload[SIGNED_INT_MAX:]))
                else:
                    read_frame_buffer.write(read(payload_size, buffer=payload))
            except (socket.timeout, TimeoutError):
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

    def write(self, s):
        with self.socket_lock:
            try:
                self._write(s)
            except socket.timeout:
                raise
            except (OSError, IOError, socket.error) as exc:
                _LOGGER.debug("Transport write failed: %r", exc, extra=self.network_trace_params)
                if get_errno(exc) not in _UNAVAIL:
                    self.connected = False
                raise

    def receive_frame(self, **kwargs):
        try:
            header, channel, payload = self.read(**kwargs)
            if not payload:
                decoded = decode_empty_frame(header)
            else:
                decoded = decode_frame(payload)
            return channel, decoded
        except (socket.timeout, TimeoutError):
            return None, None

    def send_frame(self, channel, frame, **kwargs):
        header, performative = encode_frame(frame, **kwargs)
        if performative is None:
            data = header
        else:
            encoded_channel = struct.pack(">H", channel)
            data = header + encoded_channel + performative
        self.write(data)

    def negotiate(self):
        pass


class SSLTransport(_AbstractTransport):
    """Transport that works over SSL."""

    def __init__(self, host, *, port=AMQPS_PORT, socket_timeout=None, ssl_opts=None, **kwargs):
        self.sslopts = ssl_opts if isinstance(ssl_opts, dict) else {}
        self._custom_endpoint = kwargs.get("custom_endpoint")
        self._custom_port = kwargs.get("custom_port")
        self.sslopts["server_hostname"] = self._custom_endpoint or host
        self._read_buffer = BytesIO()
        super(SSLTransport, self).__init__(
            self._custom_endpoint or host, port=self._custom_port or port, socket_timeout=socket_timeout, **kwargs
        )

    def _setup_transport(self):
        """Wrap the socket in an SSL object."""
        if self._use_tls:
            self.sock = self._wrap_socket(self.sock, **self.sslopts)
        self._quick_recv = self.sock.recv

    def _wrap_socket(self, sock, **sslopts):
        if "context" in sslopts:
            context = sslopts.pop("context")
            return context.wrap_socket(sock, **sslopts)
        return self._wrap_socket_sni(sock, **sslopts)

    def _wrap_socket_sni(
        self,
        sock,
        keyfile=None,
        certfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        ca_certs=None,
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
        server_hostname=None,
        ciphers=None,
        ssl_version=None,
    ):
        """Socket wrap with SNI headers.

        Default `ssl.wrap_socket` method augmented with support for
        setting the server_hostname field required for SNI hostname header

        :param socket.socket sock: socket to wrap
        :param str or None keyfile: key file path
        :param str or None certfile: cert file path
        :param int cert_reqs: cert requirements
        :param str or None ca_certs: ca certs file path
        :param bool do_handshake_on_connect: do handshake on connect
        :param bool suppress_ragged_eofs: suppress ragged EOFs
        :param str or None server_hostname: server hostname
        :param str or None ciphers: ciphers to use
        :param int or None ssl_version: ssl version to use
        :return: wrapped socket
        :rtype: SSLSocket
        """
        # Setup the right SSL version; default to optimal versions across
        # ssl implementations
        if ssl_version is None:
            ssl_version = ssl.PROTOCOL_TLS_CLIENT
        purpose = ssl.Purpose.SERVER_AUTH

        opts = {
            "sock": sock,
            "do_handshake_on_connect": do_handshake_on_connect,
            "suppress_ragged_eofs": suppress_ragged_eofs,
            "server_hostname": server_hostname,
        }

        context = ssl.SSLContext(ssl_version)

        if ca_certs is not None:
            try:
                context.load_verify_locations(ca_certs)
            except FileNotFoundError as exc:
                exc.filename = {"ca_certs": ca_certs}
                raise exc from None
        elif context.verify_mode != ssl.CERT_NONE:
            # load the default system root CA certs.
            context.load_default_certs(purpose=purpose)

        if certfile is not None:
            context.load_cert_chain(certfile, keyfile)

        if ciphers is not None:
            context.set_ciphers(ciphers)

        if cert_reqs == ssl.CERT_NONE and server_hostname is None:
            context.check_hostname = False
            context.verify_mode = cert_reqs

        sock = context.wrap_socket(**opts)
        return sock

    def _shutdown_transport(self):
        """Unwrap a SSL socket, so we can call shutdown()."""
        if self.sock is not None:
            try:
                if self._use_tls:
                    self.sock = self.sock.unwrap()
            except OSError:
                pass

    def _read(
        self,
        n,
        initial=False,
        buffer=None,
        _errnos=(errno.ENOENT, errno.EAGAIN, errno.EINTR),
    ):
        # According to SSL_read(3), it can at most return 16kb of data.
        # Thus, we use an internal read buffer like TCPTransport._read
        # to get the exact number of bytes wanted.
        length = 0
        view = buffer or memoryview(bytearray(n))
        nbytes = self._read_buffer.readinto(view)
        toread = n - nbytes
        length += nbytes
        try:
            while toread:
                try:
                    nbytes = self.sock.recv_into(view[length:])
                except socket.error as exc:
                    # ssl.sock.read may cause a SSLerror without errno
                    # http://bugs.python.org/issue10272
                    if isinstance(exc, SSLError) and "timed out" in str(exc):
                        raise socket.timeout()
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

    def _write(self, s):
        """Write a string out to the SSL socket fully.
        :param str s: The string to write.
        """
        try:
            write = self.sock.send
        except AttributeError:
            raise IOError("Socket has already been closed.") from None

        while s:
            try:
                n = write(s)
            except ValueError:
                # AG: sock._sslobj might become null in the meantime if the
                # remote connection has hung up.
                # In python 3.4, a ValueError is raised is self._sslobj is
                # None.
                n = 0
            if not n:
                raise IOError("Socket closed.")
            s = s[n:]

    def negotiate(self):
        with self.block():
            self.write(TLS_HEADER_FRAME)
            _, returned_header = self.receive_frame(verify_frame_type=None)
            if returned_header[1] == TLS_HEADER_FRAME:
                raise ValueError(
                    f"""Mismatching TLS header protocol. Expected: {TLS_HEADER_FRAME!r},"""
                    """received: {returned_header[1]!r}"""
                )


def Transport(host, transport_type, socket_timeout=None, ssl_opts=True, **kwargs):
    """Create transport.

    Given a few parameters from the Connection constructor,
    select and create a subclass of _AbstractTransport.

    :param str host: The host to connect to.
    :param ~pyamqp.TransportType transport_type: The transport type.
    :param int or None socket_timeout: The socket timeout.
    :param bool ssl_opts: SSL options.
    :return: Transport instance.
    :rtype: ~pyamqp.transport._AbstractTransport
    """
    if transport_type == TransportType.AmqpOverWebsocket:
        transport = WebSocketTransport
    else:
        transport = SSLTransport
    return transport(host, socket_timeout=socket_timeout, ssl_opts=ssl_opts, **kwargs)


class WebSocketTransport(_AbstractTransport):
    def __init__(
        self,
        host,
        *,
        port=WEBSOCKET_PORT,
        socket_timeout=None,
        ssl_opts=None,
        **kwargs,
    ):
        self.sslopts = ssl_opts if isinstance(ssl_opts, dict) else {}
        self.socket_timeout = socket_timeout or WS_TIMEOUT_INTERVAL
        self._host = host
        self._custom_endpoint = kwargs.get("custom_endpoint")
        super().__init__(host, port=port, socket_timeout=socket_timeout, **kwargs)
        self.sock = None
        self._http_proxy = kwargs.get("http_proxy", None)

    def connect(self):
        http_proxy_host, http_proxy_port, http_proxy_auth = None, None, None
        if self._http_proxy:
            http_proxy_host = self._http_proxy["proxy_hostname"]
            http_proxy_port = self._http_proxy["proxy_port"]
            username = self._http_proxy.get("username", None)
            password = self._http_proxy.get("password", None)
            if username or password:
                http_proxy_auth = (username, password)
        try:
            from websocket import (
                create_connection,
                WebSocketAddressException,
                WebSocketTimeoutException,
                WebSocketConnectionClosedException,
            )
        except ImportError:
            raise ImportError("Please install websocket-client library to use sync websocket transport.") from None
        try:
            self.sock = create_connection(
                url=(
                    "wss://{}".format(self._custom_endpoint or self._host)
                    if self._use_tls
                    else "ws://{}".format(self._custom_endpoint or self._host)
                ),
                subprotocols=[AMQP_WS_SUBPROTOCOL],
                timeout=self.socket_timeout,  # timeout for read/write operations
                skip_utf8_validation=True,
                sslopt=self.sslopts if self._use_tls else None,
                http_proxy_host=http_proxy_host,
                http_proxy_port=http_proxy_port,
                http_proxy_auth=http_proxy_auth,
            )
        except WebSocketAddressException as exc:
            raise AuthenticationException(
                ErrorCondition.ClientError,
                description="Failed to authenticate the connection due to exception: " + str(exc),
                error=exc,
            ) from exc
        # TODO: resolve pylance error when type: ignore is removed below, issue #22051
        except (WebSocketTimeoutException, SSLError, WebSocketConnectionClosedException) as exc:  # type: ignore
            self.close()
            raise ConnectionError("Websocket failed to establish connection: %r" % exc) from exc
        except (OSError, IOError, SSLError) as e:
            _LOGGER.info("Websocket connection failed: %r", e, extra=self.network_trace_params)
            self.close()
            raise

    def _read(self, n, initial=False, buffer=None, _errnos=None):
        """Read exactly n bytes from the peer.

        :param int n: The number of bytes to read.
        :param bool initial: Whether this is the first read in a sequence.
        :param bytearray or None buffer: The buffer to read into.
        :param list or None _errnos: A list of errno values to catch and retry on.
        :return: The data read.
        :rtype: bytearray
        """
        from websocket import WebSocketTimeoutException, WebSocketConnectionClosedException

        try:
            length = 0
            view = buffer or memoryview(bytearray(n))
            nbytes = self._read_buffer.readinto(view)
            length += nbytes
            n -= nbytes
            try:
                while n:
                    data = self.sock.recv()
                    if len(data) <= n:
                        view[length : length + len(data)] = data
                        n -= len(data)
                        length += len(data)
                    else:
                        view[length : length + n] = data[0:n]
                        self._read_buffer = BytesIO(data[n:])
                        n = 0
                return view
            except AttributeError:
                raise IOError("Websocket connection has already been closed.") from None
            except WebSocketTimeoutException as wte:
                raise TimeoutError("Websocket receive timed out (%s)" % wte) from wte
            except (WebSocketConnectionClosedException, SSLError) as e:
                raise ConnectionError("Websocket disconnected: %r" % e) from e
        except:
            self._read_buffer = BytesIO(view[:length])
            raise

    def close(self):
        with self.socket_lock:
            if self.sock:
                self._shutdown_transport()
                self.sock = None

    def _shutdown_transport(self):
        # TODO Sync and Async close functions named differently
        """Do any preliminary work in shutting down the connection."""
        if self.sock:
            self.sock.close()

    def _write(self, s):
        """Completely write a string to the peer.
        ABNF, OPCODE_BINARY = 0x2
        See http://tools.ietf.org/html/rfc5234
        http://tools.ietf.org/html/rfc6455#section-5.2

        :param str s: The string to write.
        """
        from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException

        try:
            self.sock.send_binary(s)
        except AttributeError:
            raise IOError("Websocket connection has already been closed.") from None
        except WebSocketTimeoutException as e:
            raise socket.timeout("Websocket send timed out (%s)" % e) from e
        except (WebSocketConnectionClosedException, SSLError) as e:
            raise ConnectionError("Websocket disconnected: %r" % e) from e
