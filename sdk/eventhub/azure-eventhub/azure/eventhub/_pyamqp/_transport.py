#-------------------------------------------------------------------------
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
#-------------------------------------------------------------------------


from __future__ import absolute_import, unicode_literals

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

import certifi

from ._platform import KNOWN_TCP_OPTS, SOL_TCP, pack, unpack
from ._encode import encode_frame
from ._decode import decode_frame, decode_empty_frame
from .constants import TLS_HEADER_FRAME, WEBSOCKET_PORT, TransportType, AMQP_WS_SUBPROTOCOL


try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None   # noqa
try:
    from os import set_cloexec  # Python 3.4?
except ImportError:  # pragma: no cover
    # TODO: Drop this once we drop Python 2.7 support
    def set_cloexec(fd, cloexec):  # noqa
        """Set flag to close fd after exec."""
        if fcntl is None:
            return
        try:
            FD_CLOEXEC = fcntl.FD_CLOEXEC
        except AttributeError:
            raise NotImplementedError(
                'close-on-exec flag not supported on this platform',
            )
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
AMQP_FRAME = memoryview(b'AMQP')
EMPTY_BUFFER = bytes()
SIGNED_INT_MAX = 0x7FFFFFFF
TIMEOUT_INTERVAL = 1

# Match things like: [fe80::1]:5432, from RFC 2732
IPV6_LITERAL = re.compile(r'\[([\.0-9a-f:]+)\](?::(\d+))?')

DEFAULT_SOCKET_SETTINGS = {
    'TCP_NODELAY': 1,
    'TCP_USER_TIMEOUT': 1000,
    'TCP_KEEPIDLE': 60,
    'TCP_KEEPINTVL': 10,
    'TCP_KEEPCNT': 9,
}


def get_errno(exc):
    """Get exception errno (if set).

    Notes:
        :exc:`socket.error` and :exc:`IOError` first got
        the ``.errno`` attribute in Py2.7.
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


def to_host_port(host, port=AMQP_PORT):
    """Convert hostname:port string to host, port tuple."""
    m = IPV6_LITERAL.match(host)
    if m:
        host = m.group(1)
        if m.group(2):
            port = int(m.group(2))
    else:
        if ':' in host:
            host, port = host.rsplit(':', 1)
            port = int(port)
    return host, port


class UnexpectedFrame(Exception):
    pass


class _AbstractTransport(object):
    """Common superclass for TCP and SSL transports."""

    def __init__(self, host, port=AMQP_PORT, connect_timeout=None,
                 read_timeout=None, write_timeout=None,
                 socket_settings=None, raise_on_initial_eintr=True, **kwargs):
        self.connected = False
        self.sock = None
        self.raise_on_initial_eintr = raise_on_initial_eintr
        self._read_buffer = BytesIO()
        self.host, self.port = to_host_port(host, port)
        self.connect_timeout = connect_timeout or TIMEOUT_INTERVAL
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.socket_settings = socket_settings
        self.socket_lock = Lock()

    def connect(self):
        try:
            # are we already connected?
            if self.connected:
                return
            self._connect(self.host, self.port, self.connect_timeout)
            self._init_socket(
                self.socket_settings, self.read_timeout, self.write_timeout,
            )
            # we've sent the banner; signal connect
            # EINTR, EAGAIN, EWOULDBLOCK would signal that the banner
            # has _not_ been sent
            self.connected = True
        except (OSError, IOError, SSLError):
            # if not fully connected, close socket, and reraise error
            if self.sock and not self.connected:
                self.sock.close()
                self.sock = None
            raise

    @contextmanager
    def block_with_timeout(self, timeout):
        if timeout is None:
            yield self.sock
        else:
            sock = self.sock
            prev = sock.gettimeout()
            if prev != timeout:
                sock.settimeout(timeout)
            try:
                yield self.sock
            except SSLError as exc:
                if 'timed out' in str(exc):
                    # http://bugs.python.org/issue10272
                    raise socket.timeout()
                elif 'The operation did not complete' in str(exc):
                    # Non-blocking SSL sockets can throw SSLError
                    raise socket.timeout()
                raise
            except socket.error as exc:
                if get_errno(exc) == errno.EWOULDBLOCK:
                    raise socket.timeout()
                raise
            finally:
                if timeout != prev:
                    sock.settimeout(prev)

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
            if 'timed out' in str(exc):
                # http://bugs.python.org/issue10272
                raise socket.timeout()
            elif 'The operation did not complete' in str(exc):
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
            if 'timed out' in str(exc):
                # http://bugs.python.org/issue10272
                raise socket.timeout()
            elif 'The operation did not complete' in str(exc):
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

    def _connect(self, host, port, timeout):
        e = None

        # Below we are trying to avoid additional DNS requests for AAAA if A
        # succeeds. This helps a lot in case when a hostname has an IPv4 entry
        # in /etc/hosts but not IPv6. Without the (arguably somewhat twisted)
        # logic below, getaddrinfo would attempt to resolve the hostname for
        # both IP versions, which would make the resolver talk to configured
        # DNS servers. If those servers are for some reason not available
        # during resolution attempt (either because of system misconfiguration,
        # or network connectivity problem), resolution process locks the
        # _connect call for extended time.
        addr_types = (socket.AF_INET, socket.AF_INET6)
        addr_types_num = len(addr_types)
        for n, family in enumerate(addr_types):
            # first, resolve the address for a single address family
            try:
                entries = socket.getaddrinfo(
                    host, port, family, socket.SOCK_STREAM, SOL_TCP)
                entries_num = len(entries)
            except socket.gaierror:
                # we may have depleted all our options
                if n + 1 >= addr_types_num:
                    # if getaddrinfo succeeded before for another address
                    # family, reraise the previous socket.error since it's more
                    # relevant to users
                    raise (e
                           if e is not None
                           else socket.error(
                               "failed to resolve broker hostname"))
                continue  # pragma: no cover

            # now that we have address(es) for the hostname, connect to broker
            for i, res in enumerate(entries):
                af, socktype, proto, _, sa = res
                try:
                    self.sock = socket.socket(af, socktype, proto)
                    try:
                        set_cloexec(self.sock, True)
                    except NotImplementedError:
                        pass
                    self.sock.settimeout(timeout)
                    self.sock.connect(sa)
                except socket.error as ex:
                    e = ex
                    if self.sock is not None:
                        self.sock.close()
                        self.sock = None
                    # we may have depleted all our options
                    if i + 1 >= entries_num and n + 1 >= addr_types_num:
                        raise
                else:
                    # hurray, we established connection
                    return

    def _init_socket(self, socket_settings, read_timeout, write_timeout):
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
        # TODO: a greater timeout value is needed in long distance communication
        #  we should either figure out a reasonable value error/dynamically adjust the timeout
        #  1 second is enough for perf analysis
        self.sock.settimeout(1)  # set socket back to non-blocking mode

    def _get_tcp_socket_defaults(self, sock):
        tcp_opts = {}
        for opt in KNOWN_TCP_OPTS:
            enum = None
            if opt == 'TCP_USER_TIMEOUT':
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
                    tcp_opts[enum] = sock.getsockopt(
                        SOL_TCP, getattr(socket, opt))
        return tcp_opts

    def _set_socket_options(self, socket_settings):
        tcp_opts = self._get_tcp_socket_defaults(self.sock)
        if socket_settings:
            tcp_opts.update(socket_settings)
        for opt, val in tcp_opts.items():
            self.sock.setsockopt(SOL_TCP, opt, val)

    def _read(self, n, initial=False):
        """Read exactly n bytes from the peer."""
        raise NotImplementedError('Must be overriden in subclass')

    def _setup_transport(self):
        """Do any additional initialization of the class."""
        pass

    def _shutdown_transport(self):
        """Do any preliminary work in shutting down the connection."""
        pass

    def _write(self, s):
        """Completely write a string to the peer."""
        raise NotImplementedError('Must be overriden in subclass')

    def close(self):
        if self.sock is not None:
            self._shutdown_transport()
            # Call shutdown first to make sure that pending messages
            # reach the AMQP broker if the program exits after
            # calling this method.
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception as exc:
                # TODO: shutdown could raise OSError, Transport endpoint is not connected if the endpoint is already
                #  disconnected. can we safely ignore the errors since the close operation is initiated by us.
                _LOGGER.info("An error occurred when shutting down the socket: %r", exc)
            self.sock.close()
            self.sock = None
        self.connected = False

    def read(self, verify_frame_type=0, **kwargs):  # TODO: verify frame type?
        read = self._read
        read_frame_buffer = BytesIO()
        try:
            frame_header = memoryview(bytearray(8))
            read_frame_buffer.write(read(8, buffer=frame_header, initial=True))

            channel = struct.unpack('>H', frame_header[6:])[0]
            size = frame_header[0:4]
            if size == AMQP_FRAME:  # Empty frame or AMQP header negotiation TODO
                return frame_header, channel, None
            size = struct.unpack('>I', size)[0]
            offset = frame_header[4]
            frame_type = frame_header[5]

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
            if isinstance(exc, SSLError) and 'timed out' in str(exc):
                raise socket.timeout()
            if get_errno(exc) not in _UNAVAIL:
                self.connected = False
            raise
        offset -= 2
        return frame_header, channel, payload[offset:]

    def write(self, s):
        try:
            self._write(s)
        except socket.timeout:
            raise
        except (OSError, IOError, socket.error) as exc:
            if get_errno(exc) not in _UNAVAIL:
                self.connected = False
            raise

    def receive_frame(self, *args, **kwargs):
        try:
            header, channel, payload = self.read(**kwargs)
            if not payload:
                decoded = decode_empty_frame(header)
            else:
                decoded = decode_frame(payload)
            # TODO: Catch decode error and return amqp:decode-error
            return channel, decoded
        except (socket.timeout, TimeoutError):
            return None, None

    def send_frame(self, channel, frame, **kwargs):
        header, performative = encode_frame(frame, **kwargs)
        if performative is None:
            data = header
        else:
            encoded_channel = struct.pack('>H', channel)
            data = header + encoded_channel + performative
        self.write(data)

    def negotiate(self, encode, decode):
        pass


class SSLTransport(_AbstractTransport):
    """Transport that works over SSL."""

    def __init__(self, host, port=AMQPS_PORT, connect_timeout=None, ssl=None, **kwargs):
        self.sslopts = ssl if isinstance(ssl, dict) else {}
        self._read_buffer = BytesIO()
        super(SSLTransport, self).__init__(
            host,
            port=port,
            connect_timeout=connect_timeout,
            **kwargs
        )

    def _setup_transport(self):
        """Wrap the socket in an SSL object."""
        self.sock = self._wrap_socket(self.sock, **self.sslopts)
        a = self.sock.do_handshake()
        self._quick_recv = self.sock.recv

    def _wrap_socket(self, sock, context=None, **sslopts):
        if context:
            return self._wrap_context(sock, sslopts, **context)
        return self._wrap_socket_sni(sock, **sslopts)

    def _wrap_context(self, sock, sslopts, check_hostname=None, **ctx_options):
        ctx = ssl.create_default_context(**ctx_options)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile=certifi.where())
        ctx.check_hostname = check_hostname
        return ctx.wrap_socket(sock, **sslopts)

    def _wrap_socket_sni(self, sock, keyfile=None, certfile=None,
                         server_side=False, cert_reqs=ssl.CERT_REQUIRED,
                         ca_certs=None, do_handshake_on_connect=False,
                         suppress_ragged_eofs=True, server_hostname=None,
                         ciphers=None, ssl_version=None):
        """Socket wrap with SNI headers.

        Default `ssl.wrap_socket` method augmented with support for
        setting the server_hostname field required for SNI hostname header
        """
        # Setup the right SSL version; default to optimal versions across
        # ssl implementations
        if ssl_version is None:
            # older versions of python 2.7 and python 2.6 do not have the
            # ssl.PROTOCOL_TLS defined the equivalent is ssl.PROTOCOL_SSLv23
            # we default to PROTOCOL_TLS and fallback to PROTOCOL_SSLv23
            # TODO: Drop this once we drop Python 2.7 support
            if hasattr(ssl, 'PROTOCOL_TLS'):
                ssl_version = ssl.PROTOCOL_TLS
            else:
                ssl_version = ssl.PROTOCOL_SSLv23

        opts = {
            'sock': sock,
            'keyfile': keyfile,
            'certfile': certfile,
            'server_side': server_side,
            'cert_reqs': cert_reqs,
            'ca_certs': ca_certs,
            'do_handshake_on_connect': do_handshake_on_connect,
            'suppress_ragged_eofs': suppress_ragged_eofs,
            'ciphers': ciphers,
            #'ssl_version': ssl_version
        }

        sock = ssl.wrap_socket(**opts)
        # Set SNI headers if supported
        if (server_hostname is not None) and (
                hasattr(ssl, 'HAS_SNI') and ssl.HAS_SNI) and (
                hasattr(ssl, 'SSLContext')):
            context = ssl.SSLContext(opts['ssl_version'])
            context.verify_mode = cert_reqs
            if cert_reqs != ssl.CERT_NONE:
                context.check_hostname = True
            if (certfile is not None) and (keyfile is not None):
                context.load_cert_chain(certfile, keyfile)
            sock = context.wrap_socket(sock, server_hostname=server_hostname)
        return sock

    def _shutdown_transport(self):
        """Unwrap a SSL socket, so we can call shutdown()."""
        if self.sock is not None:
            try:
                self.sock = self.sock.unwrap()
            except OSError:
                pass

    def _read(self, toread, initial=False, buffer=None,
              _errnos=(errno.ENOENT, errno.EAGAIN, errno.EINTR)):
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
                    nbytes = self.sock.recv_into(view[length:])
                except socket.error as exc:
                    # ssl.sock.read may cause a SSLerror without errno
                    # http://bugs.python.org/issue10272
                    if isinstance(exc, SSLError) and 'timed out' in str(exc):
                        raise socket.timeout()
                    # ssl.sock.read may cause ENOENT if the
                    # operation couldn't be performed (Issue celery#1414).
                    if exc.errno in _errnos:
                        if initial and self.raise_on_initial_eintr:
                            raise socket.timeout()
                        continue
                    raise
                if not nbytes:
                    raise IOError('Server unexpectedly closed connection')

                length += nbytes
                toread -= nbytes
        except:  # noqa
            self._read_buffer = BytesIO(view[:length])
            raise
        return view

    def _write(self, s):
        """Write a string out to the SSL socket fully."""
        write = self.sock.send
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
                raise IOError('Socket closed')
            s = s[n:]

    def negotiate(self):
        with self.block():
            self.write(TLS_HEADER_FRAME)
            channel, returned_header = self.receive_frame(verify_frame_type=None)
            if returned_header[1] == TLS_HEADER_FRAME:
                raise ValueError("Mismatching TLS header protocol. Excpected: {}, received: {}".format(
                    TLS_HEADER_FRAME, returned_header[1]))


class TCPTransport(_AbstractTransport):
    """Transport that deals directly with TCP socket."""

    def _setup_transport(self):
        # Setup to _write() directly to the socket, and
        # do our own buffered reads.
        self._write = self.sock.sendall
        self._read_buffer = EMPTY_BUFFER
        self._quick_recv = self.sock.recv

    def _read(self, n, initial=False, _errnos=(errno.EAGAIN, errno.EINTR)):
        """Read exactly n bytes from the socket."""
        recv = self._quick_recv
        rbuf = self._read_buffer
        try:
            while len(rbuf) < n:
                try:
                    s = self.sock.read(n - len(rbuf))
                except socket.error as exc:
                    if exc.errno in _errnos:
                        if initial and self.raise_on_initial_eintr:
                            raise socket.timeout()
                        continue
                    raise
                if not s:
                    raise IOError('Server unexpectedly closed connection')
                rbuf += s
        except:  # noqa
            self._read_buffer = rbuf
            raise

        result, self._read_buffer = rbuf[:n], rbuf[n:]
        return result

def Transport(host, transport_type, connect_timeout=None, ssl=False, **kwargs):
    """Create transport.

    Given a few parameters from the Connection constructor,
    select and create a subclass of _AbstractTransport.
    """
    if transport_type == TransportType.AmqpOverWebsocket:
        transport = WebSocketTransport
    else:
        transport = SSLTransport if ssl else TCPTransport
    return transport(host, connect_timeout=connect_timeout, ssl=ssl, **kwargs)

class WebSocketTransport(_AbstractTransport):
    def __init__(self, host, port=WEBSOCKET_PORT, connect_timeout=None, ssl=None, **kwargs):
        self.sslopts = ssl if isinstance(ssl, dict) else {}
        self._connect_timeout = connect_timeout or TIMEOUT_INTERVAL
        self._host = host
        self._custom_endpoint = kwargs.get("custom_endpoint")
        super().__init__(
            host, port, connect_timeout, **kwargs
            )
        self.ws = None
        self._http_proxy = kwargs.get('http_proxy', None)

    def connect(self):
        http_proxy_host, http_proxy_port, http_proxy_auth = None, None, None
        if self._http_proxy:
            http_proxy_host = self._http_proxy['proxy_hostname']
            http_proxy_port = self._http_proxy['proxy_port']
            username = self._http_proxy.get('username', None)
            password = self._http_proxy.get('password', None)
            if username or password:
                http_proxy_auth = (username, password)
        try:
            from websocket import create_connection
            self.ws = create_connection(
                url="wss://{}".format(self._custom_endpoint or self._host),
                subprotocols=[AMQP_WS_SUBPROTOCOL],
                timeout=self._connect_timeout,
                skip_utf8_validation=True,
                http_proxy_host=http_proxy_host,
                http_proxy_port=http_proxy_port,
                http_proxy_auth=http_proxy_auth
            )

        except ImportError:
            raise ValueError("Please install websocket-client library to use websocket transport.")

    def _read(self, n, initial=False, buffer=None, **kwargs):  # pylint: disable=unused-arguments
        """Read exactly n bytes from the peer."""
        from websocket import WebSocketTimeoutException

        length = 0
        view = buffer or memoryview(bytearray(n))
        nbytes = self._read_buffer.readinto(view)
        length += nbytes
        n -= nbytes
        try:
            while n:
                data = self.ws.recv()

                if len(data) <= n:
                    view[length: length + len(data)] = data
                    n -= len(data)
                else:
                    view[length: length + n] = data[0:n]
                    self._read_buffer = BytesIO(data[n:])
                    n = 0
            return view
        except WebSocketTimeoutException:
            raise TimeoutError()

    def _shutdown_transport(self):
        """Do any preliminary work in shutting down the connection."""
        self.ws.close()

    def _write(self, s):
        """Completely write a string to the peer.
        ABNF, OPCODE_BINARY = 0x2
        See http://tools.ietf.org/html/rfc5234
        http://tools.ietf.org/html/rfc6455#section-5.2
        """
        self.ws.send_binary(s)
