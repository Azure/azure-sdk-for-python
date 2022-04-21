"""Stubs for patching HTTP and HTTPS requests"""

import logging
import six
from six.moves.http_client import HTTPConnection, HTTPSConnection, HTTPResponse
from six import BytesIO
from vcr.request import Request
from vcr.errors import CannotOverwriteExistingCassetteException
from . import compat

log = logging.getLogger(__name__)


class VCRFakeSocket(object):
    """
    A socket that doesn't do anything!
    Used when playing back cassettes, when there
    is no actual open socket.
    """

    def close(self):
        pass

    def settimeout(self, *args, **kwargs):
        pass

    def fileno(self):
        """
        This is not very good.  requests will watch
        this descriptor and make sure it's not closed.
        Return file descriptor 0 since that's stdin.
        """
        return 0  # wonder how bad this is....


def parse_headers(header_list):
    """
    Convert headers from our serialized dict with lists for keys to a
    HTTPMessage
    """
    header_string = b""
    for key, values in header_list.items():
        for v in values:
            header_string += key.encode("utf-8") + b":" + v.encode("utf-8") + b"\r\n"
    return compat.get_httpmessage(header_string)


def serialize_headers(response):
    out = {}
    for key, values in compat.get_headers(response.msg):
        out.setdefault(key, [])
        out[key].extend(values)
    return out


class VCRHTTPResponse(HTTPResponse):
    """
    Stub response class that gets returned instead of a HTTPResponse
    """

    def __init__(self, recorded_response):
        self.fp = None
        self.recorded_response = recorded_response
        self.reason = recorded_response["status"]["message"]
        self.status = self.code = recorded_response["status"]["code"]
        self.version = None
        self._content = BytesIO(self.recorded_response["body"]["string"])
        self._closed = False

        headers = self.recorded_response["headers"]
        # Since we are loading a response that has already been serialized, our
        # response is no longer chunked.  That means we don't want any
        # libraries trying to process a chunked response.  By removing the
        # transfer-encoding: chunked header, this should cause the downstream
        # libraries to process this as a non-chunked response.
        te_key = [h for h in headers.keys() if h.upper() == "TRANSFER-ENCODING"]
        if te_key:
            del headers[te_key[0]]
        self.headers = self.msg = parse_headers(headers)

        self.length = compat.get_header(self.msg, "content-length") or None

    @property
    def closed(self):
        # in python3, I can't change the value of self.closed.  So I'
        # twiddling self._closed and using this property to shadow the real
        # self.closed from the superclas
        return self._closed

    def read(self, *args, **kwargs):
        return self._content.read(*args, **kwargs)

    def readall(self):
        return self._content.readall()

    def readinto(self, *args, **kwargs):
        return self._content.readinto(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self._content.readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        return self._content.readlines(*args, **kwargs)

    def seekable(self):
        return self._content.seekable()

    def tell(self):
        return self._content.tell()

    def isatty(self):
        return self._content.isatty()

    def seek(self, *args, **kwargs):
        return self._content.seek(*args, **kwargs)

    def close(self):
        self._closed = True
        return True

    def getcode(self):
        return self.status

    def isclosed(self):
        return self.closed

    def info(self):
        return parse_headers(self.recorded_response["headers"])

    def getheaders(self):
        message = parse_headers(self.recorded_response["headers"])
        return list(compat.get_header_items(message))

    def getheader(self, header, default=None):
        values = [v for (k, v) in self.getheaders() if k.lower() == header.lower()]

        if values:
            return ", ".join(values)
        else:
            return default

    def readable(self):
        return self._content.readable()


class VCRConnection(object):
    # A reference to the cassette that's currently being patched in
    cassette = None

    def _port_postfix(self):
        """
        Returns empty string for the default port and ':port' otherwise
        """
        port = self.real_connection.port
        default_port = {"https": 443, "http": 80}[self._protocol]
        return ":{}".format(port) if port != default_port else ""

    def _uri(self, url):
        """Returns request absolute URI"""
        if url and not url.startswith("/"):
            # Then this must be a proxy request.
            return url
        uri = "{}://{}{}{}".format(self._protocol, self.real_connection.host, self._port_postfix(), url)
        log.debug("Absolute URI: %s", uri)
        return uri

    def _url(self, uri):
        """Returns request selector url from absolute URI"""
        prefix = "{}://{}{}".format(self._protocol, self.real_connection.host, self._port_postfix())
        return uri.replace(prefix, "", 1)

    def request(self, method, url, body=None, headers=None, *args, **kwargs):
        """Persist the request metadata in self._vcr_request"""
        self._vcr_request = Request(method=method, uri=self._uri(url), body=body, headers=headers or {})
        log.debug("Got {}".format(self._vcr_request))

        # Note: The request may not actually be finished at this point, so
        # I'm not sending the actual request until getresponse().  This
        # allows me to compare the entire length of the response to see if it
        # exists in the cassette.

        self._sock = VCRFakeSocket()

    def putrequest(self, method, url, *args, **kwargs):
        """
        httplib gives you more than one way to do it.  This is a way
        to start building up a request.  Usually followed by a bunch
        of putheader() calls.
        """
        self._vcr_request = Request(method=method, uri=self._uri(url), body="", headers={})
        log.debug("Got {}".format(self._vcr_request))

    def putheader(self, header, *values):
        self._vcr_request.headers[header] = values

    def send(self, data):
        """
        This method is called after request(), to add additional data to the
        body of the request.  So if that happens, let's just append the data
        onto the most recent request in the cassette.
        """
        self._vcr_request.body = self._vcr_request.body + data if self._vcr_request.body else data

    def close(self):
        # Note: the real connection will only close if it's open, so
        # no need to check that here.
        self.real_connection.close()

    def endheaders(self, message_body=None):
        """
        Normally, this would actually send the request to the server.
        We are not sending the request until getting the response,
        so bypass this part and just append the message body, if any.
        """
        if message_body is not None:
            self._vcr_request.body = message_body

    def getresponse(self, _=False, **kwargs):
        """Retrieve the response"""
        # Check to see if the cassette has a response for this request. If so,
        # then return it
        if self.cassette.can_play_response_for(self._vcr_request):
            log.info("Playing response for {} from cassette".format(self._vcr_request))
            response = self.cassette.play_response(self._vcr_request)
            return VCRHTTPResponse(response)
        else:
            if self.cassette.write_protected and self.cassette.filter_request(self._vcr_request):
                raise CannotOverwriteExistingCassetteException(
                    cassette=self.cassette, failed_request=self._vcr_request
                )

            # Otherwise, we should send the request, then get the response
            # and return it.

            log.info("{} not in cassette, sending to real server".format(self._vcr_request))
            # This is imported here to avoid circular import.
            # TODO(@IvanMalison): Refactor to allow normal import.
            from vcr.patch import force_reset

            with force_reset():
                self.real_connection.request(
                    method=self._vcr_request.method,
                    url=self._url(self._vcr_request.uri),
                    body=self._vcr_request.body,
                    headers=self._vcr_request.headers,
                )

            # get the response
            response = self.real_connection.getresponse()

            # put the response into the cassette
            response = {
                "status": {"code": response.status, "message": response.reason},
                "headers": serialize_headers(response),
                "body": {"string": response.read()},
            }
            self.cassette.append(self._vcr_request, response)
        return VCRHTTPResponse(response)

    def set_debuglevel(self, *args, **kwargs):
        self.real_connection.set_debuglevel(*args, **kwargs)

    def connect(self, *args, **kwargs):
        """
        httplib2 uses this.  Connects to the server I'm assuming.

        Only pass to the baseclass if we don't have a recorded response
        and are not write-protected.
        """

        if hasattr(self, "_vcr_request") and self.cassette.can_play_response_for(self._vcr_request):
            # We already have a response we are going to play, don't
            # actually connect
            return

        if self.cassette.write_protected:
            # Cassette is write-protected, don't actually connect
            return

        from vcr.patch import force_reset

        with force_reset():
            return self.real_connection.connect(*args, **kwargs)

        self._sock = VCRFakeSocket()

    @property
    def sock(self):
        if self.real_connection.sock:
            return self.real_connection.sock
        return self._sock

    @sock.setter
    def sock(self, value):
        if self.real_connection.sock:
            self.real_connection.sock = value

    def __init__(self, *args, **kwargs):
        if six.PY3:
            kwargs.pop("strict", None)  # apparently this is gone in py3

        # need to temporarily reset here because the real connection
        # inherits from the thing that we are mocking out.  Take out
        # the reset if you want to see what I mean :)
        from vcr.patch import force_reset

        with force_reset():
            self.real_connection = self._baseclass(*args, **kwargs)

        self._sock = None

    def __setattr__(self, name, value):
        """
        We need to define this because any attributes that are set on the
        VCRConnection need to be propogated to the real connection.

        For example, urllib3 will set certain attributes on the connection,
        such as 'ssl_version'. These attributes need to get set on the real
        connection to have the correct and expected behavior.

        TODO: Separately setting the attribute on the two instances is not
        ideal. We should switch to a proxying implementation.
        """
        try:
            setattr(self.real_connection, name, value)
        except AttributeError:
            # raised if real_connection has not been set yet, such as when
            # we're setting the real_connection itself for the first time
            pass

        super(VCRConnection, self).__setattr__(name, value)

    def __getattr__(self, name):
        """
        Send requests for weird attributes up to the real connection
        (counterpart to __setattr above)
        """
        if self.__dict__.get("real_connection"):
            # check in case real_connection has not been set yet, such as when
            # we're setting the real_connection itself for the first time
            return getattr(self.real_connection, name)

        return super(VCRConnection, self).__getattr__(name)


for k, v in HTTPConnection.__dict__.items():
    if isinstance(v, staticmethod):
        setattr(VCRConnection, k, v)


class VCRHTTPConnection(VCRConnection):
    """A Mocked class for HTTP requests"""

    _baseclass = HTTPConnection
    _protocol = "http"


class VCRHTTPSConnection(VCRConnection):
    """A Mocked class for HTTPS requests"""

    _baseclass = HTTPSConnection
    _protocol = "https"
    is_verified = True
