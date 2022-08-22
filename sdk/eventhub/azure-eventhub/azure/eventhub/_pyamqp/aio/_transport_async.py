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

import asyncio
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

from .._platform import KNOWN_TCP_OPTS, SOL_TCP, pack, unpack
from .._encode import encode_frame
from .._decode import decode_frame, decode_empty_frame
from ..constants import TLS_HEADER_FRAME, WEBSOCKET_PORT, AMQP_WS_SUBPROTOCOL
from .._transport import (
    AMQP_FRAME,
    get_errno,
    to_host_port,
    DEFAULT_SOCKET_SETTINGS,
    IPV6_LITERAL,
    SIGNED_INT_MAX,
    _UNAVAIL,
    set_cloexec,
    AMQP_PORT,
    TIMEOUT_INTERVAL,
    WebSocketTransport
)


_LOGGER = logging.getLogger(__name__)


def get_running_loop():
    try:
        import asyncio  # pylint: disable=import-error
        return asyncio.get_running_loop()
    except AttributeError:  # 3.6
        loop = None
        try:
            loop = asyncio._get_running_loop()  # pylint: disable=protected-access
        except AttributeError:
            _LOGGER.warning('This version of Python is deprecated, please upgrade to >= v3.6')
        if loop is None:
            _LOGGER.warning('No running event loop')
            loop = asyncio.get_event_loop()
        return loop


class AsyncTransportMixin():
    async def receive_frame(self, timeout=None, *args, **kwargs):
        try:
            header, channel, payload = await asyncio.wait_for(self.read(**kwargs), timeout=timeout)
            if not payload:
                decoded = decode_empty_frame(header)
            else:
                decoded = decode_frame(payload)
            # TODO: Catch decode error and return amqp:decode-error
            #_LOGGER.info("ICH%d <- %r", channel, decoded)
            return channel, decoded
        except (TimeoutError, socket.timeout, asyncio.IncompleteReadError, asyncio.TimeoutError):
            return None, None

    async def read(self, verify_frame_type=0, **kwargs):  # TODO: verify frame type?
        async with self.socket_lock:
            read_frame_buffer = BytesIO()
            try:
                frame_header = memoryview(bytearray(8))
                read_frame_buffer.write(await self._read(8, buffer=frame_header, initial=True))

                channel = struct.unpack('>H', frame_header[6:])[0]
                size = frame_header[0:4]
                if size == AMQP_FRAME:  # Empty frame or AMQP header negotiation
                    return frame_header, channel, None
                size = struct.unpack('>I', size)[0]
                offset = frame_header[4]
                frame_type = frame_header[5]

                # >I is an unsigned int, but the argument to sock.recv is signed,
                # so we know the size can be at most 2 * SIGNED_INT_MAX
                payload_size = size - len(frame_header)
                payload = memoryview(bytearray(payload_size))
                if size > SIGNED_INT_MAX:
                    read_frame_buffer.write(await self._read(SIGNED_INT_MAX, buffer=payload))
                    read_frame_buffer.write(await self._read(size - SIGNED_INT_MAX, buffer=payload[SIGNED_INT_MAX:]))
                else:
                    read_frame_buffer.write(await self._read(payload_size, buffer=payload))
            except (TimeoutError, socket.timeout,  asyncio.IncompleteReadError):
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

    async def send_frame(self, channel, frame, **kwargs):
        header, performative = encode_frame(frame, **kwargs)
        if performative is None:
            data = header
        else:
            encoded_channel = struct.pack('>H', channel)
            data = header + encoded_channel + performative

        await self.write(data)
        #_LOGGER.info("OCH%d -> %r", channel, frame)

class AsyncTransport(AsyncTransportMixin):
    """Common superclass for TCP and SSL transports."""

    def __init__(self, host, port=AMQP_PORT, connect_timeout=None,
                 read_timeout=None, write_timeout=None, ssl=False,
                 socket_settings=None, raise_on_initial_eintr=True, **kwargs):
        self.connected = False
        self.sock = None
        self.reader = None
        self.writer = None
        self.raise_on_initial_eintr = raise_on_initial_eintr
        self._read_buffer = BytesIO()
        self.host, self.port = to_host_port(host, port)
        
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.socket_settings = socket_settings
        self.loop = get_running_loop()
        self.socket_lock = asyncio.Lock()
        self.sslopts = self._build_ssl_opts(ssl)

    def _build_ssl_opts(self, sslopts):
        if sslopts in [True, False, None, {}]:
            return sslopts
        try:
            if 'context' in sslopts:
                return self._build_ssl_context(sslopts, **sslopts.pop('context'))
            ssl_version = sslopts.get('ssl_version')
            if ssl_version is None:
                ssl_version = ssl.PROTOCOL_TLS

            # Set SNI headers if supported
            server_hostname = sslopts.get('server_hostname')
            if (server_hostname is not None) and (hasattr(ssl, 'HAS_SNI') and ssl.HAS_SNI) and (hasattr(ssl, 'SSLContext')):
                context = ssl.SSLContext(ssl_version)
                cert_reqs = sslopts.get('cert_reqs', ssl.CERT_REQUIRED)
                certfile = sslopts.get('certfile')
                keyfile = sslopts.get('keyfile')
                context.verify_mode = cert_reqs
                if cert_reqs != ssl.CERT_NONE:
                    context.check_hostname = True
                if (certfile is not None) and (keyfile is not None):
                    context.load_cert_chain(certfile, keyfile)
                return context
            return True
        except TypeError:
            raise TypeError('SSL configuration must be a dictionary, or the value True.')

    def _build_ssl_context(self, sslopts, check_hostname=None, **ctx_options):
        ctx = ssl.create_default_context(**ctx_options)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile=certifi.where())
        ctx.check_hostname = check_hostname
        return ctx

    async def connect(self):
        try:
            # are we already connected?
            if self.connected:
                return
            await self._connect(self.host, self.port, self.connect_timeout)
            self._init_socket(
                self.socket_settings, self.read_timeout, self.write_timeout,
            )
            self.reader, self.writer = await asyncio.open_connection(
                sock=self.sock,
                ssl=self.sslopts,
                server_hostname=self.host if self.sslopts else None
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

    async def _connect(self, host, port, timeout):
        # Below we are trying to avoid additional DNS requests for AAAA if A
        # succeeds. This helps a lot in case when a hostname has an IPv4 entry
        # in /etc/hosts but not IPv6. Without the (arguably somewhat twisted)
        # logic below, getaddrinfo would attempt to resolve the hostname for
        # both IP versions, which would make the resolver talk to configured
        # DNS servers. If those servers are for some reason not available
        # during resolution attempt (either because of system misconfiguration,
        # or network connectivity problem), resolution process locks the
        # _connect call for extended time.
        e = None
        addr_types = (socket.AF_INET, socket.AF_INET6)
        addr_types_num = len(addr_types)
        for n, family in enumerate(addr_types):
            # first, resolve the address for a single address family
            try:
                entries = await self.loop.getaddrinfo(
                    host, port, family=family, type=socket.SOCK_STREAM, proto=SOL_TCP)
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
                    await self.loop.sock_connect(self.sock, sa)
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

    async def _read(self, toread, initial=False, buffer=None,
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
                    view[nbytes:nbytes + toread] = await self.reader.readexactly(toread)
                    nbytes = toread
                except asyncio.IncompleteReadError as exc:
                    pbytes = len(exc.partial)
                    view[nbytes:nbytes + pbytes] = exc.partial
                    nbytes = pbytes
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

    async def _write(self, s):
        """Write a string out to the SSL socket fully."""
        self.writer.write(s)

    def close(self):
        if self.writer is not None:
            if self.sslopts:
                # see issue: https://github.com/encode/httpx/issues/914
                self.writer.transport.abort()
            self.writer.close()
            self.writer, self.reader = None, None
        self.sock = None
        self.connected = False

    async def write(self, s):
        try:
            await self._write(s)
        except socket.timeout:
            raise
        except (OSError, IOError, socket.error) as exc:
            if get_errno(exc) not in _UNAVAIL:
                self.connected = False
            raise

    async def receive_frame_with_lock(self, *args, **kwargs):
        try:
            async with self.socket_lock:
                header, channel, payload = await self.read(**kwargs)
            if not payload:
                decoded = decode_empty_frame(header)
            else:
                decoded = decode_frame(payload)
            return channel, decoded
        except (socket.timeout, TimeoutError):
            return None, None

    async def negotiate(self):
        if not self.sslopts:
            return
        await self.write(TLS_HEADER_FRAME)
        channel, returned_header = await self.receive_frame(verify_frame_type=None)
        if returned_header[1] == TLS_HEADER_FRAME:
            raise ValueError("Mismatching TLS header protocol. Excpected: {}, received: {}".format(
                TLS_HEADER_FRAME, returned_header[1]))


class WebSocketTransportAsync(AsyncTransportMixin):
    def __init__(self, host, port=WEBSOCKET_PORT, connect_timeout=None, ssl=None, **kwargs
        ):
        self._read_buffer = BytesIO()
        self.loop = get_running_loop()
        self.socket_lock = asyncio.Lock()
        self.sslopts = ssl if isinstance(ssl, dict) else {}
        self._connect_timeout = connect_timeout or TIMEOUT_INTERVAL
        self._custom_endpoint = kwargs.get("custom_endpoint")
        self.host = host
        self.ws = None
        self._http_proxy = kwargs.get('http_proxy', None)

    async def connect(self):
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
                url="wss://{}".format(self._custom_endpoint or self.host),
                subprotocols=[AMQP_WS_SUBPROTOCOL],
                timeout=self._connect_timeout,
                skip_utf8_validation=True,
                sslopt=self.sslopts,
                http_proxy_host=http_proxy_host,
                http_proxy_port=http_proxy_port,
                http_proxy_auth=http_proxy_auth
            )
        except ImportError:
            raise ValueError("Please install websocket-client library to use websocket transport.")

    async def _read(self, n, buffer=None, **kwargs): # pylint: disable=unused-arguments
        """Read exactly n bytes from the peer."""
        from websocket import WebSocketTimeoutException

        length = 0
        view = buffer or memoryview(bytearray(n))
        nbytes = self._read_buffer.readinto(view)
        length += nbytes
        n -= nbytes
        try:
            while n:
                data = await self.loop.run_in_executor(
                    None, self.ws.recv
                )

                if len(data) <= n:
                    view[length: length + len(data)] = data
                    n -= len(data)
                else:
                    view[length: length + n] = data[0:n]
                    self._read_buffer = BytesIO(data[n:])
                    n = 0

            return view 
        except WebSocketTimeoutException as wex:
            raise TimeoutError()

    def close(self):
        """Do any preliminary work in shutting down the connection."""
        # TODO: async close doesn't:
        # 1) shutdown socket and close. --> self.sock.shutdown(socket.SHUT_RDWR) and self.sock.close()
        # 2) set self.connected = False
        # I think we need to do this, like in sync
        self.ws.close()

    async def write(self, s):
        """Completely write a string to the peer.
        ABNF, OPCODE_BINARY = 0x2
        See http://tools.ietf.org/html/rfc5234
        http://tools.ietf.org/html/rfc6455#section-5.2
        """
        await self.loop.run_in_executor(
                None, self.ws.send_binary, s
                )
