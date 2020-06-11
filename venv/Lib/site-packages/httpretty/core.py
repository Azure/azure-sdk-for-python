# <HTTPretty - HTTP client mock for Python>
# Copyright (C) <2011-2020> Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import io
import codecs
import contextlib
import functools
import hashlib
import inspect
import logging
import itertools
import json
import types
import re
import socket
import tempfile
import threading
import traceback
import warnings

from functools import partial
from typing import Callable

from .compat import (
    BaseClass,
    BaseHTTPRequestHandler,
    quote,
    quote_plus,
    urlencode,
    encode_obj,
    urlunsplit,
    urlsplit,
    parse_qs,
    unquote_utf8,
)
from .http import (
    STATUSES,
    HttpBaseClass,
    parse_requestline,
    last_requestline,
)

from .utils import (
    utf8,
    decode_utf8,
)

from .errors import HTTPrettyError, UnmockedError

from datetime import datetime
from datetime import timedelta
from errno import EAGAIN

old_socket = socket.socket
old_SocketType = socket.SocketType
old_create_connection = socket.create_connection
old_gethostbyname = socket.gethostbyname
old_gethostname = socket.gethostname
old_getaddrinfo = socket.getaddrinfo
old_socksocket = None
old_ssl_wrap_socket = None
old_sslwrap_simple = None
old_sslsocket = None
old_sslcontext_wrap_socket = None
old_sslcontext = None

MULTILINE_ANY_REGEX = re.compile(r'.*', re.M)
hostname_re = re.compile(r'\^?(?:https?://)?[^:/]*[:/]?')


logger = logging.getLogger(__name__)

try:  # pragma: no cover
    import socks
    old_socksocket = socks.socksocket
except ImportError:
    socks = None

try:  # pragma: no cover
    import ssl
    old_sslcontext_class = ssl.SSLContext
    old_sslcontext = ssl.create_default_context()
    old_ssl_wrap_socket = old_sslcontext.wrap_socket
    try:
        old_sslcontext_wrap_socket = ssl.SSLContext.wrap_socket
    except AttributeError:
        pass
    old_sslsocket = ssl.SSLSocket
except ImportError:  # pragma: no cover
    ssl = None

try:
    import _ssl
except ImportError:
    _ssl = None
# used to handle error caused by ndg-httpsclient
try:
    from requests.packages.urllib3.contrib.pyopenssl import inject_into_urllib3, extract_from_urllib3
    pyopenssl_override = True
except Exception:
    pyopenssl_override = False


try:
    import requests.packages.urllib3.connection as requests_urllib3_connection
    old_requests_ssl_wrap_socket = requests_urllib3_connection.ssl_wrap_socket
except ImportError:
    requests_urllib3_connection = None
    old_requests_ssl_wrap_socket = None

try:
    import eventlet
    import eventlet.green
except ImportError:
    eventlet = None

DEFAULT_HTTP_PORTS = frozenset([80])
POTENTIAL_HTTP_PORTS = set(DEFAULT_HTTP_PORTS)
DEFAULT_HTTPS_PORTS = frozenset([443])
POTENTIAL_HTTPS_PORTS = set(DEFAULT_HTTPS_PORTS)


def FALLBACK_FUNCTION(x):
    return x


class HTTPrettyRequest(BaseHTTPRequestHandler, BaseClass):
    r"""
    Represents a HTTP request. It takes a valid multi-line,
    ``\r\n`` separated string with HTTP headers and parse them out using
    the internal `parse_request` method.

    It also replaces the `rfile` and `wfile` attributes with :py:class:`io.BytesIO`
    instances so that we guarantee that it won't make any I/O, neither
    for writing nor reading.

    It has some convenience attributes:

    ``headers`` -> a mimetype object that can be cast into a dictionary,
    contains all the request headers

    ``method`` -> the HTTP method used in this request

    ``querystring`` -> a dictionary containing lists with the
    attributes. Please notice that if you need a single value from a
    query string you will need to get it manually like:

    ``body`` -> the request body as a string

    ``parsed_body`` -> the request body parsed by ``parse_request_body``

    .. testcode::

      >>> request.querystring
      {'name': ['Gabriel Falcao']}
      >>> print request.querystring['name'][0]



    """
    def __init__(self, headers, body=''):
        # first of all, lets make sure that if headers or body are
        # unicode strings, it must be converted into a utf-8 encoded
        # byte string
        self.raw_headers = utf8(headers.strip())
        self._body = utf8(body)

        # Now let's concatenate the headers with the body, and create
        # `rfile` based on it
        self.rfile = io.BytesIO(b'\r\n\r\n'.join([self.raw_headers, self.body]))

        # Creating `wfile` as an empty BytesIO, just to avoid any
        # real I/O calls
        self.wfile = io.BytesIO()

        # parsing the request line preemptively
        self.raw_requestline = self.rfile.readline()

        # initiating the error attributes with None
        self.error_code = None
        self.error_message = None

        # Parse the request based on the attributes above
        if not self.parse_request():
            return

        # making the HTTP method string available as the command
        self.method = self.command

        # Now 2 convenient attributes for the HTTPretty API:

        # `querystring` holds a dictionary with the parsed query string
        try:
            self.path = self.path.encode('iso-8859-1')
        except UnicodeDecodeError:
            pass

        self.path = decode_utf8(self.path)

        qstring = self.path.split("?", 1)[-1]
        self.querystring = self.parse_querystring(qstring)

        # And the body will be attempted to be parsed as
        # `application/json` or `application/x-www-form-urlencoded`
        """a dictionary containing parsed request body or None if
        HTTPrettyRequest doesn't know how to parse it.  It currently
        supports parsing body data that was sent under the
        ``content`-type` headers values: ``application/json`` or
        ``application/x-www-form-urlencoded``
        """
        self.parsed_body = self.parse_request_body(self._body)

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = utf8(value)

        # And the body will be attempted to be parsed as
        # `application/json` or `application/x-www-form-urlencoded`
        self.parsed_body = self.parse_request_body(self._body)

    def __nonzero__(self):
        return bool(self.body) or bool(self.raw_headers)

    def __str__(self):
        tmpl = '<HTTPrettyRequest("{}", total_headers={}, body_length={})>'
        return tmpl.format(
            self.headers.get('content-type', ''),
            len(self.headers),
            len(self.body),
        )

    def parse_querystring(self, qs):
        """parses an UTF-8 encoded query string into a dict of string lists

        :param qs: a querystring
        :returns: a dict of lists

        """
        expanded = unquote_utf8(qs)
        parsed = parse_qs(expanded)
        result = {}
        for k in parsed:
            result[k] = list(map(decode_utf8, parsed[k]))

        return result

    def parse_request_body(self, body):
        """Attempt to parse the post based on the content-type passed.
        Return the regular body if not

        :param body: string
        :returns: a python object such as dict or list in case the deserialization suceeded. Else returns the given param ``body``
        """

        PARSING_FUNCTIONS = {
            'application/json': json.loads,
            'text/json': json.loads,
            'application/x-www-form-urlencoded': self.parse_querystring,
        }

        content_type = self.headers.get('content-type', '')

        do_parse = PARSING_FUNCTIONS.get(content_type, FALLBACK_FUNCTION)
        try:
            body = decode_utf8(body)
            return do_parse(body)
        except Exception:
            return body


class EmptyRequestHeaders(dict):
    """A dict subclass used as internal representation of empty request
    headers
    """


class HTTPrettyRequestEmpty(object):
    """Represents an empty :py:class:`~httpretty.core.HTTPrettyRequest`
    where all its properties are somehow empty or ``None``
    """

    method = None
    url = None
    body = ''
    headers = EmptyRequestHeaders()


class FakeSockFile(object):
    """Fake socket file descriptor. Under the hood all data is written in
    a temporary file, giving it a real file descriptor number.

    """
    def __init__(self):
        self.file = tempfile.TemporaryFile()
        self._fileno = self.file.fileno()

    def getvalue(self):
        if hasattr(self.file, 'getvalue'):
            return self.file.getvalue()
        else:
            return self.file.read()

    def close(self):
        self.socket.close()
        self.file.close()

    def fileno(self):
        return self._fileno

    def __getattr__(self, name):
        return getattr(self.file, name)

    def __del__(self):
        try:
            self.close()
        except (ValueError, AttributeError):
            pass


class FakeSSLSocket(object):
    """Shorthand for :py:class:`~httpretty.core.fakesock`
    """
    def __init__(self, sock, *args, **kw):
        self._httpretty_sock = sock

    def __getattr__(self, attr):
        return getattr(self._httpretty_sock, attr)


class FakeAddressTuple(object):
    def __init__(self, fakesocket):
        self.fakesocket = fakesocket

    def __getitem__(self, *args, **kw):
        raise AssertionError('socket {} is not connected'.format(self.fakesocket.truesock))


class fakesock(object):
    """
    fake :py:mod:`socket`
    """
    class socket(object):
        """drop-in replacement for :py:class:`socket.socket`
        """
        _entry = None
        debuglevel = 0
        _sent_data = []

        def __init__(
            self,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=0,
            fileno=None
        ):
            self.socket_family = family
            self.socket_type = type
            self.socket_proto = proto
            if httpretty.allow_net_connect:
                self.truesock = self.create_socket()
            else:
                self.truesock = None

            self._address = FakeAddressTuple(self)
            self.__truesock_is_connected__ = False
            self.fd = FakeSockFile()
            self.fd.socket = fileno or self
            self.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
            self._sock = fileno or self
            self.is_http = False
            self._bufsize = 32 * 1024

        def create_socket(self):
            return old_socket(self.socket_family, self.socket_type, self.socket_proto)

        def getpeercert(self, *a, **kw):
            now = datetime.now()
            shift = now + timedelta(days=30 * 12)
            return {
                'notAfter': shift.strftime('%b %d %H:%M:%S GMT'),
                'subjectAltName': (
                    ('DNS', '*.%s' % self._host),
                    ('DNS', self._host),
                    ('DNS', '*'),
                ),
                'subject': (
                    (
                        ('organizationName', '*.%s' % self._host),
                    ),
                    (
                        ('organizationalUnitName',
                         'Domain Control Validated'),
                    ),
                    (
                        ('commonName', '*.%s' % self._host),
                    ),
                ),
            }

        def ssl(self, sock, *args, **kw):
            return sock

        def setsockopt(self, level, optname, value):
            if httpretty.allow_net_connect and not self.truesock:
                self.truesock = self.create_socket()
            elif not self.truesock:
                logger.debug('setsockopt(%s, %s, %s) failed', level, optname, value)
                return

            return self.truesock.setsockopt(level, optname, value)

        def connect(self, address):
            try:
                self._address = (self._host, self._port) = address
            except ValueError:
                # We get here when the address is just a string pointing to a
                # unix socket path/file
                #
                # See issue #206
                self.is_http = False
            else:
                ports_to_check = (
                    POTENTIAL_HTTP_PORTS.union(POTENTIAL_HTTPS_PORTS))
                self.is_http = self._port in ports_to_check

            if not self.is_http:
                self.connect_truesock()
            elif self.truesock and not self.__truesock_is_connected__:
                # TODO: remove nested if
                matcher = httpretty.match_http_address(self._host, self._port)
                if matcher is None:
                    self.connect_truesock()

        def bind(self, address):
            self._address = (self._host, self._port) = address
            if self.truesock:
                self.bind_truesock(address)

        def bind_truesock(self, address):
            if httpretty.allow_net_connect and not self.truesock:
                self.truesock = self.create_socket()
            elif not self.truesock:
                raise UnmockedError()

            return self.truesock.bind(address)

        def connect_truesock(self):
            if httpretty.allow_net_connect and not self.truesock:
                self.truesock = self.create_socket()
            elif not self.truesock:
                raise UnmockedError()

            if self.__truesock_is_connected__:
                return self.truesock
            with restored_libs():
                hostname = self._address[0]
                port = 80
                if len(self._address) == 2:
                    port = self._address[1]
                if port ==  443 and old_sslsocket:
                    self.truesock = old_ssl_wrap_socket(self.truesock, server_hostname=hostname)

                sock = self.truesock

                sock.connect(self._address)
                self.__truesock_is_connected__ = True
                self.truesock = sock
            return self.truesock

        def real_socket_is_connected(self):
            return self.__truesock_is_connected__

        def fileno(self):
            if self.truesock:
                return self.truesock.fileno()
            return self.fd.fileno()

        def close(self):
            if self.truesock:
                self.truesock.close()
                self.truesock = None
                self.__truesock_is_connected__ = False

        def makefile(self, mode='r', bufsize=-1):
            """Returns this fake socket's own tempfile buffer.

            If there is an entry associated with the socket, the file
            descriptor gets filled in with the entry data before being
            returned.
            """
            self._mode = mode
            self._bufsize = bufsize

            if self._entry:
                t = threading.Thread(
                    target=self._entry.fill_filekind, args=(self.fd,)
                )
                t.start()
                if self.timeout == socket._GLOBAL_DEFAULT_TIMEOUT:
                    timeout = None
                else:
                    timeout = self.timeout
                t.join(timeout)
                if t.is_alive():
                    raise socket.timeout

            return self.fd

        def real_sendall(self, data, *args, **kw):
            """Sends data to the remote server. This method is called
            when HTTPretty identifies that someone is trying to send
            non-http data.

            The received bytes are written in this socket's tempfile
            buffer so that HTTPretty can return it accordingly when
            necessary.
            """

            if httpretty.allow_net_connect and not self.truesock:
                self.connect_truesock()
            elif not self.truesock:
                raise UnmockedError()

            if not self.is_http:
                self.truesock.setblocking(1)
                return self.truesock.sendall(data, *args, **kw)

            sock = self.connect_truesock()

            sock.setblocking(1)
            sock.sendall(data, *args, **kw)

            should_continue = True
            while should_continue:
                try:
                    received = sock.recv(self._bufsize)
                    self.fd.write(received)
                    should_continue = bool(received.strip())

                except socket.error as e:
                    if e.errno == EAGAIN:
                        continue
                    break

            self.fd.seek(0)

        def sendall(self, data, *args, **kw):
            # if self.__truesock_is_connected__:
            #     return self.truesock.sendall(data, *args, **kw)

            self._sent_data.append(data)
            self.fd = FakeSockFile()
            self.fd.socket = self
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif not isinstance(data, bytes):
                logger.debug('cannot sendall({data!r})')
                data = bytes(data)

            try:
                requestline, _ = data.split(b'\r\n', 1)
                method, path, version = parse_requestline(
                    decode_utf8(requestline))
                is_parsing_headers = True
            except ValueError:
                path = ''
                is_parsing_headers = False

                if self._entry is None:
                    # If the previous request wasn't mocked, don't
                    # mock the subsequent sending of data
                    return self.real_sendall(data, *args, **kw)
                else:
                    method = self._entry.method
                    path = self._entry.info.path

            self.fd.seek(0)

            if not is_parsing_headers:
                if len(self._sent_data) > 1:
                    headers = utf8(last_requestline(self._sent_data))
                    meta = self._entry.request.headers
                    body = utf8(self._sent_data[-1])
                    if meta.get('transfer-encoding', '') == 'chunked':
                        if not body.isdigit() and (body != b'\r\n') and (body != b'0\r\n\r\n'):
                            self._entry.request.body += body
                    else:
                        self._entry.request.body += body

                    httpretty.historify_request(headers, body, False)
                    return

            if path[:2] == '//':
                path = '//' + path
            # path might come with
            s = urlsplit(path)
            POTENTIAL_HTTP_PORTS.add(int(s.port or 80))
            parts = list(map(utf8, data.split(b'\r\n\r\n', 1)))
            if len(parts) == 2:
                headers, body = parts
            else:
                headers = ''
                body = data

            request = httpretty.historify_request(headers, body)

            info = URIInfo(
                hostname=self._host,
                port=self._port,
                path=s.path,
                query=s.query,
                last_request=request
            )

            matcher, entries = httpretty.match_uriinfo(info)

            if not entries:
                self._entry = None
                self.real_sendall(data)
                return

            self._entry = matcher.get_next_entry(method, info, request)

        def forward_and_trace(self, function_name, *a, **kw):
            if self.truesock and not self.__truesock_is_connected__:
                self.truesock = self.create_socket()
                ### self.connect_truesock()

            if self.__truesock_is_connected__:
                function = getattr(self.truesock, function_name)

            if self.is_http:
                if self.truesock and not self.__truesock_is_connected__:
                    self.truesock = self.create_socket()
                    ### self.connect_truesock()

            if not self.truesock:
                raise UnmockedError()

            callback = getattr(self.truesock, function_name)
            return callback(*a, **kw)

        def settimeout(self, new_timeout):
            self.timeout = new_timeout
            if not self.is_http:
                if self.truesock:
                    self.truesock.settimeout(new_timeout)

        def send(self, *args, **kwargs):
            return self.forward_and_trace('send', *args, **kwargs)

        def sendto(self, *args, **kwargs):
            return self.forward_and_trace('sendto', *args, **kwargs)

        def recvfrom_into(self, *args, **kwargs):
            return self.forward_and_trace('recvfrom_into', *args, **kwargs)

        def recv_into(self, *args, **kwargs):
            if self.truesock and not self.__truesock_is_connected__:
                self.connect_truesock()
            return self.forward_and_trace('recv_into', *args, **kwargs)

        def recvfrom(self, *args, **kwargs):
            if self.truesock and not self.__truesock_is_connected__:
                self.connect_truesock()
            return self.forward_and_trace('recvfrom', *args, **kwargs)

        def recv(self, buffersize=None, *args, **kwargs):
            if self.truesock and not self.__truesock_is_connected__:
                self.connect_truesock()
            buffersize = buffersize or self._bufsize
            return self.forward_and_trace('recv', buffersize, *args, **kwargs)

        def __getattr__(self, name):
            if httpretty.allow_net_connect and not self.truesock:
                # can't call self.connect_truesock() here because we
                # don't know if user wants to execute server of client
                # calls (or can they?)
                self.truesock = self.create_socket()
            elif not self.truesock:
                raise UnmockedError()
            return getattr(self.truesock, name)


def fake_wrap_socket(orig_wrap_socket_fn, *args, **kw):
    """drop-in replacement for py:func:`ssl.wrap_socket`
    """
    server_hostname = kw.get('server_hostname')
    if server_hostname is not None:
        matcher = httpretty.match_https_hostname(server_hostname)
        if matcher is None:
            return orig_wrap_socket_fn(*args, **kw)
    if 'sock' in kw:
        return kw['sock']
    else:
        return args[0]


def create_fake_connection(
        address,
        timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
        source_address=None):
    """drop-in replacement for :py:func:`socket.create_connection`"""
    s = fakesock.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
        s.settimeout(timeout)

    if isinstance(source_address, tuple) and len(source_address) == 2:
        source_address[1] = int(source_address[1])

    if source_address:
        s.bind(source_address)
    s.connect(address)
    return s


def fake_gethostbyname(host):
    """drop-in replacement for :py:func:`socket.gethostbyname`"""
    return '127.0.0.1'


def fake_gethostname():
    """drop-in replacement for :py:func:`socket.gethostname`"""
    return 'localhost'


def fake_getaddrinfo(
        host, port, family=None, socktype=None, proto=None, flags=None):
    """drop-in replacement for :py:func:`socket.getaddrinfo`"""
    return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP,
             '', (host, port)),
            (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP,
             '', (host, port))]


class Entry(BaseClass):
    """Created by :py:meth:`~httpretty.core.httpretty.register_uri` and
    stored in memory as internal representation of a HTTP
    request/response definition.

    Args:
        method (str): One of ``httpretty.GET``, ``httpretty.PUT``, ``httpretty.POST``, ``httpretty.DELETE``, ``httpretty.HEAD``, ``httpretty.PATCH``, ``httpretty.OPTIONS``, ``httpretty.CONNECT``.
        uri (str|re.Pattern): The URL to match
        adding_headers (dict): Extra headers to be added to the response
        forcing_headers (dict): Overwrite response headers.
        status (int): The status code for the response, defaults to ``200``.
        streaming (bool): Whether should stream the response into chunks via generator.
        headers: Headers to inject in the faked response.

    Returns:
        httpretty.Entry: containing the request-matching metadata.


    .. warning:: When using the ``forcing_headers`` option make sure to add the header ``Content-Length`` to match at most the total body length, otherwise some HTTP clients can hang indefinitely.
    """
    def __init__(self, method, uri, body,
                 adding_headers=None,
                 forcing_headers=None,
                 status=200,
                 streaming=False,
                 **headers):

        self.method = method
        self.uri = uri
        self.info = None
        self.request = None

        self.body_is_callable = False
        if hasattr(body, "__call__"):
            self.callable_body = body
            self.body = None
            self.body_is_callable = True
        elif isinstance(body, str):
            self.body = utf8(body)
        else:
            self.body = body

        self.streaming = streaming
        if not streaming and not self.body_is_callable:
            self.body_length = len(self.body or '')
        else:
            self.body_length = 0

        self.adding_headers = adding_headers or {}
        self.forcing_headers = forcing_headers or {}
        self.status = int(status)

        for k, v in headers.items():
            name = "-".join(k.split("_")).title()
            self.adding_headers[name] = v

        self.validate()

    def validate(self):
        """validates the body size with the value of the ``Content-Length``
        header
        """
        content_length_keys = 'Content-Length', 'content-length'
        for key in content_length_keys:
            got = self.adding_headers.get(
                key, self.forcing_headers.get(key, None))

            if got is None:
                continue

            igot = None
            try:
                igot = int(got)
            except (ValueError, TypeError):
                warnings.warn(
                    'HTTPretty got to register the Content-Length header '
                    'with "%r" which is not a number' % got)
                return

            if igot and igot > self.body_length:
                raise HTTPrettyError(
                    'HTTPretty got inconsistent parameters. The header '
                    'Content-Length you registered expects size "%d" but '
                    'the body you registered for that has actually length '
                    '"%d".' % (
                        igot, self.body_length,
                    )
                )

    def __str__(self):
        return r'<Entry {} {} getting {}>'.format(
            self.method,
            self.uri,
            self.status
        )

    def normalize_headers(self, headers):
        """Normalize keys in header names so that ``COntent-tyPe`` becomes ``content-type``

        :param headers: dict

        :returns: dict
        """
        new = {}
        for k in headers:
            new_k = '-'.join([s.lower() for s in k.split('-')])
            new[new_k] = headers[k]

        return new

    def fill_filekind(self, fk):
        """writes HTTP Response data to a file descriptor

        :parm fk: a file-like object

        .. warning:: **side-effect:** this method moves the cursor of the given file object to zero
        """
        now = datetime.utcnow()

        headers = {
            'status': self.status,
            'date': now.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'server': 'Python/HTTPretty',
            'connection': 'close',
        }

        if self.forcing_headers:
            headers = self.forcing_headers

        if self.adding_headers:
            headers.update(
                self.normalize_headers(
                    self.adding_headers))

        headers = self.normalize_headers(headers)
        status = headers.get('status', self.status)
        if self.body_is_callable:
            status, headers, self.body = self.callable_body(self.request, self.info.full_url(), headers)
            headers = self.normalize_headers(headers)
            # TODO: document this behavior:
            if 'content-length' not in headers:
                headers.update({
                    'content-length': len(self.body)
                })

        string_list = [
            'HTTP/1.1 %d %s' % (status, STATUSES[status]),
        ]

        if 'date' in headers:
            string_list.append('date: %s' % headers.pop('date'))

        if not self.forcing_headers:
            content_type = headers.pop('content-type',
                                       'text/plain; charset=utf-8')

            content_length = headers.pop('content-length',
                                         self.body_length)

            string_list.append('content-type: %s' % content_type)
            if not self.streaming:
                string_list.append('content-length: %s' % content_length)

            server = headers.pop('server', None)
            if server:
                string_list.append('server: %s' % server)

        for k, v in headers.items():
            string_list.append(
                '{}: {}'.format(k, v),
            )

        for item in string_list:
            fk.write(utf8(item) + b'\n')

        fk.write(b'\r\n')

        if self.streaming:
            self.body, body = itertools.tee(self.body)
            for chunk in body:
                fk.write(utf8(chunk))
        else:
            fk.write(utf8(self.body))

        fk.seek(0)


def url_fix(s, charset=None):
    """escapes special characters
    """
    if charset:
        warnings.warn("{}.url_fix() charset argument is deprecated".format(__name__), DeprecationWarning)

    scheme, netloc, path, querystring, fragment = urlsplit(s)
    path = quote(path, b'/%')
    querystring = quote_plus(querystring, b':&=')
    return urlunsplit((scheme, netloc, path, querystring, fragment))


class URIInfo(BaseClass):
    """Internal representation of `URIs <https://en.wikipedia.org/wiki/Uniform_Resource_Identifier>`_

    .. tip:: all arguments are optional

    :param username:
    :param password:
    :param hostname:
    :param port:
    :param path:
    :param query:
    :param fragment:
    :param scheme:
    :param last_request:
    """
    default_str_attrs = (
        'username',
        'password',
        'hostname',
        'port',
        'path',
    )

    def __init__(self,
                 username='',
                 password='',
                 hostname='',
                 port=80,
                 path='/',
                 query='',
                 fragment='',
                 scheme='',
                 last_request=None):

        self.username = username or ''
        self.password = password or ''
        self.hostname = hostname or ''

        if port:
            port = int(port)

        elif scheme == 'https':
            port = 443

        self.port = port or 80
        self.path = path or ''
        if query:
            query_items = sorted(parse_qs(query).items())
            self.query = urlencode(
                encode_obj(query_items),
                doseq=True,
            )
        else:
            self.query = ''
        if scheme:
            self.scheme = scheme
        elif self.port in POTENTIAL_HTTPS_PORTS:
            self.scheme = 'https'
        else:
            self.scheme = 'http'
        self.fragment = fragment or ''
        self.last_request = last_request

    def to_str(self, attrs):
        fmt = ", ".join(['%s="%s"' % (k, getattr(self, k, '')) for k in attrs])
        return r'<httpretty.URIInfo(%s)>' % fmt

    def __str__(self):
        return self.to_str(self.default_str_attrs)

    def str_with_query(self):
        attrs = self.default_str_attrs + ('query',)
        return self.to_str(attrs)

    def __hash__(self):
        return int(hashlib.sha1(bytes(self, 'ascii')).hexdigest(), 16)

    def __eq__(self, other):
        self_tuple = (
            self.port,
            decode_utf8(self.hostname.lower()),
            url_fix(decode_utf8(self.path)),
        )
        other_tuple = (
            other.port,
            decode_utf8(other.hostname.lower()),
            url_fix(decode_utf8(other.path)),
        )
        return self_tuple == other_tuple

    def full_url(self, use_querystring=True):
        """
        :param use_querystring: bool
        :returns: a string with the full url with the format ``{scheme}://{credentials}{domain}{path}{query}``
        """
        credentials = ""
        if self.password:
            credentials = "{}:{}@".format(
                self.username, self.password)

        query = ""
        if use_querystring and self.query:
            query = "?{}".format(decode_utf8(self.query))

        result = "{scheme}://{credentials}{domain}{path}{query}".format(
            scheme=self.scheme,
            credentials=credentials,
            domain=self.get_full_domain(),
            path=decode_utf8(self.path),
            query=query
        )
        return result

    def get_full_domain(self):
        """
        :returns: a string in the form ``{domain}:{port}`` or just the domain if the port is 80 or 443
        """
        hostname = decode_utf8(self.hostname)
        # Port 80/443 should not be appended to the url
        if self.port not in DEFAULT_HTTP_PORTS | DEFAULT_HTTPS_PORTS:
            return ":".join([hostname, str(self.port)])

        return hostname

    @classmethod
    def from_uri(cls, uri, entry):
        """
        :param uri: string
        :param entry: an instance of :py:class:`~httpretty.core.Entry`
        """
        result = urlsplit(uri)
        if result.scheme == 'https':
            POTENTIAL_HTTPS_PORTS.add(int(result.port or 443))
        else:
            POTENTIAL_HTTP_PORTS.add(int(result.port or 80))
        return cls(result.username,
                   result.password,
                   result.hostname,
                   result.port,
                   result.path,
                   result.query,
                   result.fragment,
                   result.scheme,
                   entry)


class URIMatcher(object):
    regex = None
    info = None

    def __init__(self, uri, entries, match_querystring=False, priority=0):
        self._match_querystring = match_querystring
        # CPython, Jython
        regex_types = ('SRE_Pattern', 'org.python.modules.sre.PatternObject',
                       'Pattern')
        is_regex = type(uri).__name__ in regex_types
        if is_regex:
            self.regex = uri
            result = urlsplit(uri.pattern)
            if result.scheme == 'https':
                POTENTIAL_HTTPS_PORTS.add(int(result.port or 443))
            else:
                POTENTIAL_HTTP_PORTS.add(int(result.port or 80))
        else:
            self.info = URIInfo.from_uri(uri, entries)

        self.entries = entries
        self.priority = priority
        self.uri = uri
        # hash of current_entry pointers, per method.
        self.current_entries = {}

    def matches(self, info):
        if self.info:
            # Query string is not considered when comparing info objects, compare separately
            return self.info == info and (not self._match_querystring or self.info.query == info.query)
        else:
            return self.regex.search(info.full_url(
                use_querystring=self._match_querystring))

    def __str__(self):
        wrap = 'URLMatcher({})'
        if self.info:
            if self._match_querystring:
                return wrap.format(str(self.info.str_with_query()))
            else:
                return wrap.format(str(self.info))
        else:
            return wrap.format(self.regex.pattern)

    def get_next_entry(self, method, info, request):
        """Cycle through available responses, but only once.
        Any subsequent requests will receive the last response"""

        if method not in self.current_entries:
            self.current_entries[method] = 0

        # restrict selection to entries that match the requested
        # method
        entries_for_method = [e for e in self.entries if e.method == method]

        if self.current_entries[method] >= len(entries_for_method):
            self.current_entries[method] = -1

        if not self.entries or not entries_for_method:
            raise ValueError('I have no entries for method %s: %s'
                             % (method, self))

        entry = entries_for_method[self.current_entries[method]]
        if self.current_entries[method] != -1:
            self.current_entries[method] += 1

        # Create a copy of the original entry to make it thread-safe
        body = entry.callable_body if entry.body_is_callable else entry.body
        new_entry = Entry(entry.method, entry.uri, body,
                          status=entry.status,
                          streaming=entry.streaming,
                          adding_headers=entry.adding_headers,
                          forcing_headers=entry.forcing_headers)

        # Attach more info to the entry
        # So the callback can be more clever about what to do
        # This does also fix the case where the callback
        # would be handed a compiled regex as uri instead of the
        # real uri
        new_entry.info = info
        new_entry.request = request
        return new_entry

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class httpretty(HttpBaseClass):
    """manages HTTPretty's internal request/response registry and request matching.
    """
    _entries = {}
    latest_requests = []

    last_request = HTTPrettyRequestEmpty()
    _is_enabled = False
    allow_net_connect = True

    @classmethod
    def match_uriinfo(cls, info):
        """
        :param info: an :py:class:`~httpretty.core.URIInfo`
        :returns: a 2-item tuple: (:py:class:`~httpretty.core.URLMatcher`, :py:class:`~httpretty.core.URIInfo`) or ``(None, [])``
        """
        items = sorted(
            cls._entries.items(),
            key=lambda matcher_entries: matcher_entries[0].priority,
            reverse=True,
        )
        for matcher, value in items:
            if matcher.matches(info):
                return (matcher, info)

        return (None, [])

    @classmethod
    def match_https_hostname(cls, hostname):
        """
        :param hostname: a string
        :returns: an :py:class:`~httpretty.core.URLMatcher` or ``None``
        """
        items = sorted(
            cls._entries.items(),
            key=lambda matcher_entries: matcher_entries[0].priority,
            reverse=True,
        )
        for matcher, value in items:
            if matcher.info is None:
                pattern_with_port = "https://{0}:".format(hostname)
                pattern_without_port = "https://{0}/".format(hostname)
                hostname_pattern = (
                    hostname_re
                    .match(matcher.regex.pattern)
                    .group(0)
                )
                for pattern in [pattern_with_port, pattern_without_port]:
                    if re.match(hostname_pattern, pattern):
                        return matcher

            elif matcher.info.hostname == hostname:
                return matcher
        return None

    @classmethod
    def match_http_address(cls, hostname, port):
        """
        :param hostname: a string
        :param port: an integer
        :returns: an :py:class:`~httpretty.core.URLMatcher` or ``None``
        """
        items = sorted(
            cls._entries.items(),
            key=lambda matcher_entries: matcher_entries[0].priority,
            reverse=True,
        )
        for matcher, value in items:
            if matcher.info is None:
                if port in POTENTIAL_HTTPS_PORTS:
                    scheme = 'https://'
                else:
                    scheme = 'http://'

                pattern_without_port = "{0}{1}/".format(scheme, hostname)
                pattern_with_port = "{0}{1}:{2}/".format(scheme, hostname, port)
                hostname_pattern = (
                    hostname_re
                    .match(matcher.regex.pattern)
                    .group(0)
                )
                for pattern in [pattern_with_port, pattern_without_port]:
                    if re.match(hostname_pattern, pattern):
                        return matcher

            elif matcher.info.hostname == hostname \
                    and matcher.info.port == port:
                return matcher

        return None

    @classmethod
    @contextlib.contextmanager
    def record(cls, filename, indentation=4, encoding='utf-8'):
        """
        .. testcode::

           import io
           import json
           import requests
           import httpretty

           with httpretty.record('/tmp/ip.json'):
               data = requests.get('https://httpbin.org/ip').json()

           with io.open('/tmp/ip.json') as fd:
               assert data == json.load(fd)

        :param filename: a string
        :param indentation: an integer, defaults to **4**
        :param encoding: a string, defaults to **"utf-8"**

        :returns: a `context-manager <https://docs.python.org/3/reference/datamodel.html#context-managers>`_
        """
        try:
            import urllib3
        except ImportError:
            msg = (
                'HTTPretty requires urllib3 installed '
                'for recording actual requests.'
            )
            raise RuntimeError(msg)

        http = urllib3.PoolManager()

        cls.enable()
        calls = []

        def record_request(request, uri, headers):
            cls.disable()

            kw = {}
            kw.setdefault('body', request.body)
            kw.setdefault('headers', dict(request.headers))
            response = http.request(request.method, uri, **kw)
            calls.append({
                'request': {
                    'uri': uri,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'body': decode_utf8(request.body),
                    'querystring': request.querystring
                },
                'response': {
                    'status': response.status,
                    'body': decode_utf8(response.data),
                    # urllib3 1.10 had a bug if you just did:
                    # dict(response.headers)
                    # which would cause all the values to become lists
                    # with the header name as the first item and the
                    # true value as the second item. Workaround that
                    'headers': dict(response.headers.items())
                }
            })
            cls.enable()
            return response.status, response.headers, response.data

        for method in cls.METHODS:
            cls.register_uri(method, MULTILINE_ANY_REGEX, body=record_request)

        yield
        cls.disable()
        with codecs.open(filename, 'w', encoding) as f:
            f.write(json.dumps(calls, indent=indentation))

    @classmethod
    @contextlib.contextmanager
    def playback(cls, filename):
        """
        .. testcode::

           import io
           import json
           import requests
           import httpretty

           with httpretty.record('/tmp/ip.json'):
               data = requests.get('https://httpbin.org/ip').json()

           with io.open('/tmp/ip.json') as fd:
               assert data == json.load(fd)

        :param filename: a string
        :returns: a `context-manager <https://docs.python.org/3/reference/datamodel.html#context-managers>`_
        """
        cls.enable()

        data = json.loads(open(filename).read())
        for item in data:
            uri = item['request']['uri']
            method = item['request']['method']
            body = item['response']['body']
            headers = item['response']['headers']
            cls.register_uri(method, uri, body=body, forcing_headers=headers)

        yield
        cls.disable()

    @classmethod
    def reset(cls):
        """resets the internal state of HTTPretty, unregistering all URLs
        """
        POTENTIAL_HTTP_PORTS.intersection_update(DEFAULT_HTTP_PORTS)
        POTENTIAL_HTTPS_PORTS.intersection_update(DEFAULT_HTTPS_PORTS)
        cls._entries.clear()
        cls.latest_requests = []
        cls.last_request = HTTPrettyRequestEmpty()

    @classmethod
    def historify_request(cls, headers, body='', append=True):
        """appends request to a list for later retrieval

        .. testcode::

           import httpretty

           httpretty.register_uri(httpretty.GET, 'https://httpbin.org/ip', body='')
           with httpretty.enabled():
               requests.get('https://httpbin.org/ip')

           assert httpretty.latest_requests[-1].url == 'https://httpbin.org/ip'
        """
        request = HTTPrettyRequest(headers, body)
        cls.last_request = request
        if append or not cls.latest_requests:
            cls.latest_requests.append(request)
        else:
            cls.latest_requests[-1] = request
        return request

    @classmethod
    def register_uri(cls, method, uri, body='{"message": "HTTPretty :)"}',
                     adding_headers=None,
                     forcing_headers=None,
                     status=200,
                     responses=None,
                     match_querystring=False,
                     priority=0,
                     **headers):
        """
        .. testcode::

           import httpretty


           def request_callback(request, uri, response_headers):
               content_type = request.headers.get('Content-Type')
               assert request.body == '{"nothing": "here"}', 'unexpected body: {}'.format(request.body)
               assert content_type == 'application/json', 'expected application/json but received Content-Type: {}'.format(content_type)
               return [200, response_headers, json.dumps({"hello": "world"})]

           httpretty.register_uri(
               HTTPretty.POST, "https://httpretty.example.com/api",
               body=request_callback)


           with httpretty.enabled():
               requests.post('https://httpretty.example.com/api', data='{"nothing": "here"}', headers={'Content-Type': 'application/json'})

           assert httpretty.latest_requests[-1].url == 'https://httpbin.org/ip'

        :param method: one of ``httpretty.GET``, ``httpretty.PUT``, ``httpretty.POST``, ``httpretty.DELETE``, ``httpretty.HEAD``, ``httpretty.PATCH``, ``httpretty.OPTIONS``, ``httpretty.CONNECT``
        :param uri: a string or regex pattern (e.g.: **"https://httpbin.org/ip"**)
        :param body: a string, defaults to ``{"message": "HTTPretty :)"}``
        :param adding_headers: dict - headers to be added to the response
        :param forcing_headers: dict - headers to be forcefully set in the response
        :param status: an integer, defaults to **200**
        :param responses: a list of entries, ideally each created with :py:meth:`~httpretty.core.httpretty.Response`
        :param priority: an integer, useful for setting higher priority over previously registered urls. defaults to zero
        :param match_querystring: bool - whether to take the querystring into account when matching an URL
        :param headers: headers to be added to the response

        .. warning:: When using a port in the request, add a trailing slash if no path is provided otherwise Httpretty will not catch the request.  Ex: ``httpretty.register_uri(httpretty.GET, 'http://fakeuri.com:8080/', body='{"hello":"world"}')``
        """
        uri_is_string = isinstance(uri, str)

        if uri_is_string and re.search(r'^\w+://[^/]+[.]\w{2,}$', uri):
            uri += '/'

        if isinstance(responses, list) and len(responses) > 0:
            for response in responses:
                response.uri = uri
                response.method = method
            entries_for_this_uri = responses
        else:
            headers['body'] = body
            headers['adding_headers'] = adding_headers
            headers['forcing_headers'] = forcing_headers
            headers['status'] = status

            entries_for_this_uri = [
                cls.Response(method=method, uri=uri, **headers),
            ]

        matcher = URIMatcher(uri, entries_for_this_uri,
                             match_querystring, priority)
        if matcher in cls._entries:
            matcher.entries.extend(cls._entries[matcher])
            del cls._entries[matcher]

        cls._entries[matcher] = entries_for_this_uri

    def __str__(self):
        return '<HTTPretty with %d URI entries>' % len(self._entries)

    @classmethod
    def Response(
            cls, body,
            method=None,
            uri=None,
            adding_headers=None,
            forcing_headers=None,
            status=200,
            streaming=False,
            **kw):
        """Shortcut to create an :py:class:`~httpretty.core.Entry` that takes
        the body as first positional argument.

        .. seealso:: the parameters of this function match those of
                     the :py:class:`~httpretty.core.Entry` constructor.

        Args:
            body (str): The body to return as response..
            method (str): One of ``httpretty.GET``, ``httpretty.PUT``, ``httpretty.POST``, ``httpretty.DELETE``, ``httpretty.HEAD``, ``httpretty.PATCH``, ``httpretty.OPTIONS``, ``httpretty.CONNECT``.
            uri (str|re.Pattern): The URL to match
            adding_headers (dict): Extra headers to be added to the response
            forcing_headers (dict): Overwrite **any** response headers, even "Content-Length".
            status (int): The status code for the response, defaults to ``200``.
            streaming (bool): Whether should stream the response into chunks via generator.
            kwargs: Keyword-arguments are forwarded to :py:class:`~httpretty.core.Entry`

        Returns:
            httpretty.Entry: containing the request-matching metadata.
        """
        kw['body'] = body
        kw['adding_headers'] = adding_headers
        kw['forcing_headers'] = forcing_headers
        kw['status'] = int(status)
        kw['streaming'] = streaming
        return Entry(method, uri, **kw)

    @classmethod
    def disable(cls):
        """Disables HTTPretty entirely, putting the original :py:mod:`socket`
        module back in its place.


        .. code::

           import re, json
           import httpretty

           httpretty.enable()
           # request passes through fake socket
           response = requests.get('https://httpbin.org')

           httpretty.disable()
           # request uses real python socket module
           response = requests.get('https://httpbin.org')

        .. note:: This method does not call :py:meth:`httpretty.core.reset` automatically.
        """
        undo_patch_socket()
        cls._is_enabled = False


    @classmethod
    def is_enabled(cls):
        """Check if HTTPretty is enabled

        :returns: bool

        .. testcode::

           import httpretty

           httpretty.enable()
           assert httpretty.is_enabled() == True

           httpretty.disable()
           assert httpretty.is_enabled() == False
        """
        return cls._is_enabled

    @classmethod
    def enable(cls, allow_net_connect=True):
        """Enables HTTPretty.
        When ``allow_net_connect`` is ``False`` any connection to an unregistered uri will throw :py:class:`httpretty.errors.UnmockedError`.

        .. testcode::

           import re, json
           import httpretty

           httpretty.enable()

           httpretty.register_uri(
               httpretty.GET,
               re.compile(r'http://.*'),
               body=json.dumps({'man': 'in', 'the': 'middle'})
           )

           response = requests.get('https://foo.bar/foo/bar')

           response.json().should.equal({
               "man": "in",
               "the": "middle",
           })

        .. warning:: after calling this method the original :py:mod:`socket` is replaced with :py:class:`httpretty.core.fakesock`. Make sure to call :py:meth:`~httpretty.disable` after done with your tests or use the :py:class:`httpretty.enabled` as decorator or `context-manager <https://docs.python.org/3/reference/datamodel.html#context-managers>`_
        """
        cls.allow_net_connect = allow_net_connect
        apply_patch_socket()
        cls._is_enabled = True


def apply_patch_socket():
    # Some versions of python internally shadowed the
    # SocketType variable incorrectly https://bugs.python.org/issue20386
    bad_socket_shadow = (socket.socket != socket.SocketType)

    new_wrap = None
    socket.socket = fakesock.socket
    socket._socketobject = fakesock.socket
    if not bad_socket_shadow:
        socket.SocketType = fakesock.socket

    socket.create_connection = create_fake_connection
    socket.gethostname = fake_gethostname
    socket.gethostbyname = fake_gethostbyname
    socket.getaddrinfo = fake_getaddrinfo

    socket.__dict__['socket'] = fakesock.socket
    socket.__dict__['_socketobject'] = fakesock.socket
    if not bad_socket_shadow:
        socket.__dict__['SocketType'] = fakesock.socket

    socket.__dict__['create_connection'] = create_fake_connection
    socket.__dict__['gethostname'] = fake_gethostname
    socket.__dict__['gethostbyname'] = fake_gethostbyname
    socket.__dict__['getaddrinfo'] = fake_getaddrinfo


    if pyopenssl_override:
        # Take out the pyopenssl version - use the default implementation
        extract_from_urllib3()

    if requests_urllib3_connection is not None:
        urllib3_wrap = partial(fake_wrap_socket, old_requests_ssl_wrap_socket)
        requests_urllib3_connection.ssl_wrap_socket = urllib3_wrap
        requests_urllib3_connection.__dict__['ssl_wrap_socket'] = urllib3_wrap

    if eventlet:
        eventlet.green.ssl.GreenSSLContext = old_sslcontext_class
        eventlet.green.ssl.__dict__['GreenSSLContext'] = old_sslcontext_class
        eventlet.green.ssl.SSLContext = old_sslcontext_class
        eventlet.green.ssl.__dict__['SSLContext'] = old_sslcontext_class

    if socks:
        socks.socksocket = fakesock.socket
        socks.__dict__['socksocket'] = fakesock.socket

    if ssl:
        new_wrap = partial(fake_wrap_socket, old_ssl_wrap_socket)
        ssl.wrap_socket = new_wrap
        ssl.SSLSocket = FakeSSLSocket
        ssl.SSLContext = old_sslcontext_class
        try:
            ssl.SSLContext.wrap_socket = partial(fake_wrap_socket, old_ssl_wrap_socket)
        except AttributeError:
            pass

        ssl.__dict__['wrap_socket'] = new_wrap
        ssl.__dict__['SSLSocket'] = FakeSSLSocket
        ssl.__dict__['SSLContext'] = old_sslcontext_class


def undo_patch_socket():
    socket.socket = old_socket
    socket.SocketType = old_SocketType
    socket._socketobject = old_socket

    socket.create_connection = old_create_connection
    socket.gethostname = old_gethostname
    socket.gethostbyname = old_gethostbyname
    socket.getaddrinfo = old_getaddrinfo

    socket.__dict__['socket'] = old_socket
    socket.__dict__['_socketobject'] = old_socket
    socket.__dict__['SocketType'] = old_SocketType

    socket.__dict__['create_connection'] = old_create_connection
    socket.__dict__['gethostname'] = old_gethostname
    socket.__dict__['gethostbyname'] = old_gethostbyname
    socket.__dict__['getaddrinfo'] = old_getaddrinfo

    if socks:
        socks.socksocket = old_socksocket
        socks.__dict__['socksocket'] = old_socksocket

    if ssl:
        ssl.wrap_socket = old_ssl_wrap_socket
        ssl.SSLSocket = old_sslsocket
        try:
            ssl.SSLContext.wrap_socket = old_sslcontext_wrap_socket
        except AttributeError:
            pass
        ssl.__dict__['wrap_socket'] = old_ssl_wrap_socket
        ssl.__dict__['SSLSocket'] = old_sslsocket

    if requests_urllib3_connection is not None:
        requests_urllib3_connection.ssl_wrap_socket = \
            old_requests_ssl_wrap_socket
        requests_urllib3_connection.__dict__['ssl_wrap_socket'] = \
            old_requests_ssl_wrap_socket

    if pyopenssl_override:
        # Put the pyopenssl version back in place
        inject_into_urllib3()


@contextlib.contextmanager
def restored_libs():
    undo_patch_socket()
    yield
    apply_patch_socket()


class httprettized(object):
    """`context-manager <https://docs.python.org/3/reference/datamodel.html#context-managers>`_ for enabling HTTPretty.

    .. tip:: Also available under the alias :py:func:`httpretty.enabled`

    .. testcode::

       import json
       import httpretty

       httpretty.register_uri(httpretty.GET, 'https://httpbin.org/ip', body=json.dumps({'origin': '42.42.42.42'}))
       with httpretty.enabled():
           response = requests.get('https://httpbin.org/ip')

       assert httpretty.latest_requests[-1].url == 'https://httpbin.org/ip'
       assert response.json() == {'origin': '42.42.42.42'}
    """
    def __init__(self, allow_net_connect=True):
        self.allow_net_connect = allow_net_connect

    def __enter__(self):
        httpretty.reset()
        httpretty.enable(allow_net_connect=self.allow_net_connect)

    def __exit__(self, exc_type, exc_value, db):
        httpretty.disable()
        httpretty.reset()


def httprettified(test=None, allow_net_connect=True):
    """decorator for test functions

    .. tip:: Also available under the alias :py:func:`httpretty.activate`

    :param test: a callable


    example usage with `nosetests <https://nose.readthedocs.io/en/latest/>`_

    .. testcode::

       import sure
       from httpretty import httprettified

       @httprettified
       def test_using_nosetests():
           httpretty.register_uri(
               httpretty.GET,
               'https://httpbin.org/ip'
           )

           response = requests.get('https://httpbin.org/ip')

           response.json().should.equal({
               "message": "HTTPretty :)"
           })

    example usage with `unittest module <https://docs.python.org/3/library/unittest.html>`_

    .. testcode::

       import unittest
       from sure import expect
       from httpretty import httprettified

       @httprettified
       class TestWithPyUnit(unittest.TestCase):
           def test_httpbin(self):
               httpretty.register_uri(httpretty.GET, 'https://httpbin.org/ip')
               response = requests.get('https://httpbin.org/ip')
               expect(response.json()).to.equal({
                   "message": "HTTPretty :)"
               })

    """
    def decorate_unittest_TestCase_setUp(klass):

        # Prefer addCleanup (added in python 2.7), but fall back
        # to using tearDown if it isn't available
        use_addCleanup = hasattr(klass, 'addCleanup')

        original_setUp = (klass.setUp
                          if hasattr(klass, 'setUp')
                          else None)

        def new_setUp(self):
            httpretty.reset()
            httpretty.enable(allow_net_connect)
            if use_addCleanup:
                self.addCleanup(httpretty.disable)
            if original_setUp:
                original_setUp(self)
        klass.setUp = new_setUp

        if not use_addCleanup:
            original_tearDown = (klass.setUp
                                 if hasattr(klass, 'tearDown')
                                 else None)

            def new_tearDown(self):
                httpretty.disable()
                httpretty.reset()
                if original_tearDown:
                    original_tearDown(self)
            klass.tearDown = new_tearDown

        return klass

    def decorate_test_methods(klass):
        for attr in dir(klass):
            if not attr.startswith('test_'):
                continue

            attr_value = getattr(klass, attr)
            if not hasattr(attr_value, "__call__"):
                continue

            setattr(klass, attr, decorate_callable(attr_value))
        return klass

    def is_unittest_TestCase(klass):
        try:
            import unittest
            return issubclass(klass, unittest.TestCase)
        except ImportError:
            return False

    "A decorator for tests that use HTTPretty"
    def decorate_class(klass):
        if is_unittest_TestCase(klass):
            return decorate_unittest_TestCase_setUp(klass)
        return decorate_test_methods(klass)

    def decorate_callable(test):
        @functools.wraps(test)
        def wrapper(*args, **kw):
            with httprettized(allow_net_connect):
                return test(*args, **kw)
        return wrapper

    if isinstance(test, type):
        return decorate_class(test)
    elif callable(test):
        return decorate_callable(test)
    return decorate_callable
