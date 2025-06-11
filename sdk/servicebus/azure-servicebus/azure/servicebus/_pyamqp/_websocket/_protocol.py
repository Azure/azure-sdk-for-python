# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import errno
import socket
import ssl
import struct
from typing import Union
from ._url import parse_url, WebSocketURL

from ._headers import (
    build_request_headers,
    parse_response_headers,
    build_key,
    match_key,
    parse_proxy_response
)
from ._constants import EOF, ConnectionStatus
from ._frame import Frame, Opcode, CloseReason
from ._exceptions import WebSocketConnectionError, WebSocketPayloadError, WebSocketProtocolError


class WebSocketMixin:
    def validate_handshake(self, code: bytes, status: bytes, headers: dict) -> None:
        self._key: bytes
        if code != b'101':
            raise ConnectionError(f'Handshake failed: {status.decode()}')

        if b'upgrade' in headers and headers[b'upgrade'] != b'websocket':
            raise ConnectionError('Server did not upgrade to websocket')

        if b'connection' in headers and headers[b'connection'] != b'upgrade':
            raise ConnectionError('Connection was not upgraded to websocket')

        if b'sec-websocket-accept' in headers:
            if not match_key(self._key, headers[b'sec-websocket-accept']):
                raise ConnectionError('Server did not accept the key')
    
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


class WebSocketProtocol(WebSocketMixin):
    def __init__(self,
                 url: str,
                 *,
                 headers = None,
                 http_proxy = None,
                 subprotocols = None,
                 ssl_ctx=None,
                 timeout=None
        ) -> None:
        self._socket: socket.socket
        self._url: str = url
        self._key = build_key()
        self._conn_status = ConnectionStatus.CLOSED
        self._headers = headers if headers else {}
        self._http_proxy = http_proxy
        self._subprotocols = subprotocols
        self._ws_url: WebSocketURL = parse_url(self._url)
        self._timeout = timeout
        self._ssl_ctx = ssl_ctx


    def open_connection(self) -> None:

        # create a socket connection
        try:
            # TODO: handle proxy support
            if self._http_proxy:
                self._socket = socket.create_connection(
                    (self._http_proxy['host'], self._http_proxy['port']),
                    timeout=self._timeout
                )
                self._socket.sendall(f'CONNECT {self._ws_url.hostname}:{self._ws_url.port} HTTP/1.1\r\n'.encode())
                self._socket.sendall(b'Host: ' + f'{self._ws_url.hostname}:{self._ws_url.port}'.encode() + b'\r\n')
                if self._http_proxy['auth']:
                    import base64
                    credentials = f"{self._http_proxy['username']}:{self._http_proxy['password']}"
                    encoded_credentials = base64.b64encode(credentials.encode()).decode()
                    self._socket.sendall(f'Proxy-Authorization: Basic {encoded_credentials}\r\n'.encode())
                self._socket.sendall(b'\r\n')
                proxy_response = parse_proxy_response(self._socket.recv(1024))
                if not proxy_response[0].startswith(b'HTTP/'):
                    self._socket.close()
                    raise ConnectionError('Received invalid response from the proxy')

                if int(proxy_response[1]) < 100 or int(proxy_response[1]) > 999:
                    self._socket.close()
                    raise ConnectionError('Received invalid status code from the proxy')

                if proxy_response[1] != b'200':
                    self._socket.close()
                    raise ConnectionError('Could not connect to the proxy')

                if proxy_response[2] != b'Connection established':
                    raise ConnectionError('Could not connect to the proxy')
            else:
                self._socket = socket.create_connection(
                    (self._ws_url.hostname, self._ws_url.port),
                    timeout=self._timeout
                )
            if self._ws_url.is_secure:
                if 'context' not in self._ssl_ctx:
                    self._socket = self._wrap_socket_sni(
                        self._socket,
                        keyfile=self._ssl_ctx.get('keyfile', None),
                        certfile=self._ssl_ctx.get('certfile', None),
                        ca_certs=self._ssl_ctx.get('ca_certs', None),
                        ciphers=self._ssl_ctx.get('ciphers', None),
                        ssl_version=self._ssl_ctx.get('ssl_version', None),
                        server_hostname = self._ws_url.hostname
                    )
                else:
                    self._socket = self._ssl_ctx['context'].wrap_socket(
                        self._socket, server_hostname=self._ws_url.hostname
                    )
            # TODO: add logging
            self._socket.setblocking(True)
            self._socket.settimeout(self._timeout)

            # build the headers
            self._headers = build_request_headers(
                self._ws_url.path if not self._ws_url.query else f'{self._ws_url.path}?{self._ws_url.query}',
                self._ws_url.hostname,
                self._ws_url.port,
                self._ws_url.is_secure,
                self._key,
                subprotocols=self._subprotocols
                )
            # start the handshake
            self._socket.sendall(self._headers)
            self._conn_status = ConnectionStatus.CONNECTING

            self._receive_handshake()
        except ssl.SSLError as sslex:
            raise sslex from None
        except socket.error as e:
            raise WebSocketConnectionError('Could not send the handshake') from e

    def _receive_handshake(self) -> None:
        if not self._socket:
            raise ConnectionError('Socket is not connected')

        response_headers = []
        while True:
            # a response header ends with a double CRLF
            # we want to process a line at a time
            line = []
            data = self._socket.recv(1)
            while data != b'\n':
                line.append(data)
                data = self._socket.recv(1)
            line.append(data)

            header_line = b''.join(line)
            if header_line == b'\r\n':
                break
            response_headers.append(header_line)

        code, status, headers = parse_response_headers(b"".join(response_headers))

        self.validate_handshake(code, status, headers)

        self._conn_status = ConnectionStatus.OPEN

    

    def receive_frame(self) -> Frame:
        last_frame = None

        while True:
            if not self._socket or self._conn_status == ConnectionStatus.CLOSED:
                raise ConnectionError('Socket is not connected')

            # read the first two bytes to get the header of the frame
            header = self._read_socket(2)

            # parse the header
            fin = bool(header[0] >> 7 & 1)
            rsv1 = header[0] >> 6 & 1
            rsv2 = header[0] >> 5 & 1
            rsv3 = header[0] >> 4 & 1
            opcode = header[0] & 0b00001111
            mask = bool(header[1] >> 7 & 1)
            payload_len = header[1] & 0b01111111

            if payload_len == 126:
                payload_len = struct.unpack('!H', self._read_socket(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack('!Q', self._read_socket(8))[0]
            elif payload_len > 127:
                raise WebSocketPayloadError('Payload length is too large')

            masking_key = None # pylint: disable=unused-variable
            if mask:
                masking_key = self._read_socket(4)

            payload = self._read_socket(payload_len)

            frame = Frame(payload, opcode, fin, mask, rsv1, rsv2, rsv3)

            if frame.opcode == Opcode.CONTINUATION and not last_frame:
                if frame.fin:
                    raise WebSocketProtocolError("Fragements must not have FIN bit set")

            if last_frame and not last_frame.fin and frame.opcode in (Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY):
                if frame.opcode != Opcode.CONTINUATION:
                    raise WebSocketProtocolError("Expected continuation frame")
                frame.data = last_frame.data + frame.data
                frame.opcode = last_frame.opcode

            frame.validate()

            if frame.opcode == Opcode.PING:
                self.send_frame(frame.data, Opcode.PONG)
                continue

            if frame.fin:
                break

            last_frame = frame

        if frame.opcode == Opcode.CLOSE:
            self.close()

        return frame

    def _read_socket(self, n: int) -> bytes:
        data = []

        to_receive = n

        while to_receive:
            try:
                chunk = self._socket.recv(min(4096,to_receive))
                if not chunk:
                    raise WebSocketConnectionError("Connection to the server was closed")
                data.append(chunk)
                to_receive -= len(chunk)
            except socket.error as exc:
                if isinstance(exc, ssl.SSLError) and "timed out" in str(exc):
                    raise WebSocketConnectionError("Connection timed out") from exc
                raise
        return b''.join(data)

    def send_frame(self, data: Union[bytes, str], opcode: int = 1) -> None:
        if not self._socket or self._conn_status != ConnectionStatus.OPEN:
            raise ConnectionError('Socket is not connected')

        if isinstance(data, str):
            data = data.encode("utf-8")

        frame = Frame(data,opcode)

        payload = frame.encode()

        while payload:
            try:
                sent = self._socket.send(payload)
            except ValueError:
                sent = 0
            except socket.error as exc:
                error_code = exc.args[0]
                if error_code not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                    raise

            if not sent:
                raise WebSocketConnectionError("Could not send the frame")
            payload = payload[sent:]

    def close(self, code: int = CloseReason.NORMAL, reason: bytes = b"") -> None:
        if self._conn_status != ConnectionStatus.OPEN:
            return

        if not self._socket:
            raise WebSocketConnectionError('Websocket is not connected')

        if code not in CloseReason:
            raise ValueError("Invalid close code")

        close_frame = Frame(struct.pack('!H', code) + reason, Opcode.CLOSE)
        self.send_frame(close_frame.data, close_frame.opcode)
        self._conn_status = ConnectionStatus.CLOSING

        while True:
            try:
                frame = self.receive_frame()
                if frame.opcode == Opcode.CLOSE:
                    break
            except: # pylint: disable=bare-except
                break

        self._conn_status = ConnectionStatus.CLOSED
        # shut down the socket
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except OSError as e:
            # on macOS this can result in the following error:
            # OSError: [Errno 57] Socket is not connected
            # this can be ignored and is due to not handling SIGINT properly.
            if e.errno != errno.ENOTCONN:
                raise


class AsyncWebSocketProtocol(WebSocketMixin):
    def __init__(self, url: str, *, headers = None, http_proxy = None, subprotocols = None, ssl_ctx=None) -> None:
        self._stream_reader: asyncio.StreamReader
        self._stream_writer: asyncio.StreamWriter
        self._url = url
        self._key = build_key()
        self._conn_status = ConnectionStatus.CLOSED
        self._headers = headers
        self._http_proxy = http_proxy
        self._subprotocols = subprotocols
        self._ws_url: WebSocketURL = parse_url(self._url)
        self._ssl = ssl_ctx
        self._socket: socket.socket

    async def open_connection(self) -> None:
        try:
            # TODO: handle proxy support
            ssl_ctx = None
            if self._ws_url.is_secure:
                if not self._ssl:
                    ssl_ctx = self._wrap_socket_sni(server_hostname=self._ws_url.hostname)
                else:
                    ssl_ctx = self._ssl

            if self._http_proxy:
                self._socket = socket.create_connection(
                    (self._http_proxy['host'], self._http_proxy['port']),
                    #timeout=self._timeout
                )
                self._socket.sendall(f'CONNECT {self._ws_url.hostname}:{self._ws_url.port} HTTP/1.1\r\n'.encode())
                self._socket.sendall(b'Host: ' + f'{self._ws_url.hostname}:{self._ws_url.port}'.encode() + b'\r\n')
                if self._http_proxy['auth'] and self._http_proxy['auth'][0]:
                    import base64
                    credentials = f"{self._http_proxy['username']}:{self._http_proxy['password'] if self._http_proxy['password'] else ''}"
                    encoded_credentials = base64.b64encode(credentials.encode()).decode()
                    self._socket.sendall(f'Proxy-Authorization: Basic {encoded_credentials}\r\n'.encode())
                self._socket.sendall(b'\r\n')
                proxy_response = parse_proxy_response(self._socket.recv(1024))
                if not proxy_response[0].startswith(b'HTTP/'):
                    self._socket.close()
                    raise ConnectionError('Received invalid response from the proxy')

                if int(proxy_response[1]) < 100 or int(proxy_response[1]) > 999:
                    self._socket.close()
                    raise ConnectionError('Received invalid status code from the proxy')

                if proxy_response[1] != b'200':
                    self._socket.close()
                    raise ConnectionError('Could not connect to the proxy')

                if proxy_response[2] != b'Connection established':
                    raise ConnectionError('Could not connect to the proxy')
            else:
                self._socket = socket.create_connection(
                    (self._ws_url.hostname, self._ws_url.port),
                    #timeout=self._timeout
                )
            if self._ws_url.is_secure:
                self._stream_reader, self._stream_writer = await asyncio.open_connection(
                    sock = self._socket,
                    ssl = self._ssl,
                    server_hostname = self._ws_url.hostname if ssl_ctx else None
                )
                
            else:
                self._stream_reader, self._stream_writer = await asyncio.open_connection(
                    self._ws_url.hostname,
                    self._ws_url.port,
                    ssl = ssl_ctx,
                    server_hostname = self._ws_url.hostname if ssl_ctx else None
                    )

            # build the headers
            self._headers = build_request_headers(
                self._ws_url.path if not self._ws_url.query else f'{self._ws_url.path}?{self._ws_url.query}',
                self._ws_url.hostname,
                self._ws_url.port,
                self._ws_url.is_secure,
                self._key,
                subprotocols=self._subprotocols
                )
            # start the handshake
            self._stream_writer.write(self._headers)
            await self._stream_writer.drain()
            self._conn_status = ConnectionStatus.CONNECTING

            await self._receive_handshake()
        except socket.error as exc:
            raise WebSocketConnectionError('Could not send the handshake') from exc

    async def _receive_handshake(self) -> None:
        if not self._stream_reader:
            raise ConnectionError('Socket is not connected')

        response_headers = b''
        try:
            response_headers = await self._stream_reader.readuntil(EOF)
        except Exception as exc:
            print(exc)
        code, status, headers = parse_response_headers(response_headers)

        self.validate_handshake(code, status, headers)
        self._conn_status = ConnectionStatus.OPEN

    def _wrap_socket_sni(
        self,
        keyfile=None,
        certfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        ca_certs=None,
        server_hostname=None,
        ciphers=None,
        ssl_version=None,
    ):
        """Socket wrap with SNI headers.

        Default `ssl.wrap_socket` method augmented with support for
        setting the server_hostname field required for SNI hostname header

        :param str or None keyfile: key file path
        :param str or None certfile: cert file path
        :param int cert_reqs: cert requirements
        :param str or None ca_certs: ca certs file path
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

        return context

    async def receive_frame(self) -> Frame:
        last_frame = None

        while True:
            if not self._stream_reader or self._conn_status == ConnectionStatus.CLOSED:
                raise ConnectionError('Socket is not connected')

            # read the first two bytes to get the header of the frame
            header = await self._stream_reader.readexactly(2)
            # parse the header
            fin = bool(header[0] >> 7 & 1)
            rsv1 = header[0] >> 6 & 1
            rsv2 = header[0] >> 5 & 1
            rsv3 = header[0] >> 4 & 1
            opcode = header[0] & 0b00001111
            mask = bool(header[1] >> 7 & 1)
            payload_len = header[1] & 0b01111111
            if payload_len == 126:
                payload_len = struct.unpack('!H', await self._stream_reader.readexactly(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack('!Q', await self._stream_reader.readexactly(8))[0]
            elif payload_len > 127:
                raise WebSocketPayloadError('Payload length is too large')
            if rsv1 or rsv2 or rsv3:
                raise WebSocketProtocolError("Reserved bits are set")
            if opcode == Opcode.PING and payload_len > 125:
                raise WebSocketProtocolError("PING frame too large")

            masking_key = None # pylint: disable=unused-variable
            if mask:
                masking_key = await self._stream_reader.readexactly(4)
            payload = await self._stream_reader.readexactly(payload_len)
            frame = Frame(payload, opcode, fin, mask, rsv1, rsv2, rsv3)

            if frame.opcode == Opcode.CONTINUATION and not last_frame:
                if frame.fin:
                    raise WebSocketProtocolError("Fragements must not have FIN bit set")
            if last_frame and not last_frame.fin and frame.opcode in (Opcode.CONTINUATION, Opcode.TEXT, Opcode.BINARY):
                if frame.opcode != Opcode.CONTINUATION:
                    raise WebSocketProtocolError("Expected continuation frame")
                frame.data = last_frame.data + frame.data
                frame.opcode = last_frame.opcode

            frame.validate()

            if frame.opcode == Opcode.PING:
                await self.send_frame(frame.data, Opcode.PONG)
                continue

            if frame.fin:
                break
            last_frame = frame

        if frame.opcode == Opcode.CLOSE and self._conn_status == ConnectionStatus.OPEN:
            await self.close()

        return frame

    async def send_frame(self, data: Union[bytes, str], opcode: int = 1) -> None:
        if not self._stream_writer or self._conn_status != ConnectionStatus.OPEN:
            raise ConnectionError('Socket is not connected')

        if isinstance(data, str):
            data = data.encode("utf-8")

        frame = Frame(data,opcode)

        payload = frame.encode()

        try:
            self._stream_writer.write(payload)
            await self._stream_writer.drain()
        except AttributeError as exc:
            raise WebSocketConnectionError("Could not send the frame") from exc

    async def close(self, code: int = CloseReason.NORMAL, reason: bytes = b"") -> None:
        if self._conn_status != ConnectionStatus.OPEN:
            return

        if not self._stream_writer or not self._stream_reader:
            raise WebSocketConnectionError('Websocket is not connected')

        if code not in CloseReason:
            raise ValueError("Invalid close code")

        close_frame = Frame(struct.pack('!H', code) + reason, Opcode.CLOSE)
        await self.send_frame(close_frame.data, close_frame.opcode)
        self._conn_status = ConnectionStatus.CLOSING

        while True:
            try:
                frame = await self.receive_frame()
                if frame.opcode == Opcode.CLOSE:
                    break
            except: # pylint: disable=bare-except
                break

        self._conn_status = ConnectionStatus.CLOSED
        # shut down the socket
        self._stream_writer.close()
        await asyncio.sleep(0)
        if hasattr(self._stream_writer, 'abort'):
            self._stream_writer.abort()
        await self._stream_writer.wait_closed()