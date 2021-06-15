# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from email.message import Message
from six.moves.http_client import HTTPConnection

def await_result(func, *args, **kwargs):
    """If func returns an awaitable, raise that this runner can't handle it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        raise TypeError(
            "Policy {} returned awaitable object in non-async pipeline.".format(func)
        )
    return result

class _HTTPSerializer(HTTPConnection, object):
    """Hacking the stdlib HTTPConnection to serialize HTTP request as strings.
    """

    def __init__(self, *args, **kwargs):
        self.buffer = b""
        kwargs.setdefault("host", "fakehost")
        super(_HTTPSerializer, self).__init__(*args, **kwargs)

    def putheader(self, header, *values):
        if header in ["Host", "Accept-Encoding"]:
            return
        super(_HTTPSerializer, self).putheader(header, *values)

    def send(self, data):
        self.buffer += data

def serialize(request):
    serializer = _HTTPSerializer()
    serializer.request(
        method=request.method,
        url=request.url,
        body=request.content,
        headers=request.headers
    )
    return serializer.buffer

def prepare_multipart_body(request, content_index=0):

    # code taken from here https://github.com/Azure/azure-sdk-for-python/blob/4ee53d07a14b8c76af01768ad98068d8a2766f54/sdk/core/azure-core/azure/core/pipeline/transport/_base.py#L406
    if not hasattr(request, "requests"):
        return 0

    requests = request.requests  # type: List[HttpRequest]
    boundary = request.boundary  # type: Optional[str]

    # Update the main request with the body
    main_message = Message()
    main_message.add_header("Content-Type", "multipart/mixed")
    if boundary:
        main_message.set_boundary(boundary)

    for req in requests:
        part_message = Message()
        if hasattr(req, "requests"):
            content_index = prepare_multipart_body(req, content_index=content_index)
            part_message.add_header("Content-Type", req.headers['Content-Type'])
            payload = serialize(req)
            # We need to remove the ~HTTP/1.1 prefix along with the added content-length
            payload = payload[payload.index(b'--'):]
        else:
            part_message.add_header("Content-Type", "application/http")
            part_message.add_header("Content-Transfer-Encoding", "binary")
            part_message.add_header("Content-ID", str(content_index))
            payload = serialize(req)
            content_index += 1
        part_message.set_payload(payload)
        main_message.attach(part_message)

    try:
        from email.policy import HTTP

        full_message = main_message.as_bytes(policy=HTTP)
        eol = b"\r\n"
    except ImportError:  # Python 2.7
        # Right now we decide to not support Python 2.7 on serialization, since
        # it doesn't serialize a valid HTTP request (and our main scenario Storage refuses it)
        raise NotImplementedError(
            "Multipart request are not supported on Python 2.7"
        )
        # full_message = main_message.as_string()
        # eol = b'\n'
    _, _, body = full_message.split(eol, 2)
    request._data = body
    request.headers["Content-Type"] = (
        "multipart/mixed; boundary=" + main_message.get_boundary()
    )
    return content_index
