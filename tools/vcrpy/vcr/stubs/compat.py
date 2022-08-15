import six
from six import BytesIO
from six.moves.http_client import HTTPMessage

try:
    import http.client
except ImportError:
    pass


"""
The python3 http.client api moved some stuff around, so this is an abstraction
layer that tries to cope with this move.
"""


def get_header(message, name):
    if six.PY3:
        return message.getallmatchingheaders(name)
    else:
        return message.getheader(name)


def get_header_items(message):
    for (key, values) in get_headers(message):
        for value in values:
            yield key, value


def get_headers(message):
    for key in set(message.keys()):
        if six.PY3:
            yield key, message.get_all(key)
        else:
            yield key, message.getheaders(key)


def get_httpmessage(headers):
    if six.PY3:
        return http.client.parse_headers(BytesIO(headers))
    msg = HTTPMessage(BytesIO(headers))
    msg.fp.seek(0)
    msg.readheaders()
    return msg
