from six import BytesIO, text_type
from six.moves.urllib.parse import urlparse, urlencode, urlunparse
import copy
import json
import zlib

from .util import CaseInsensitiveDict


def replace_headers(request, replacements):
    """
    Replace headers in request according to replacements. The replacements
    should be a list of (key, value) pairs where the value can be any of:
      1. A simple replacement string value.
      2. None to remove the given header.
      3. A callable which accepts (key, value, request) and returns a string
         value or None.
    """
    new_headers = request.headers.copy()
    for k, rv in replacements:
        if k in new_headers:
            ov = new_headers.pop(k)
            if callable(rv):
                rv = rv(key=k, value=ov, request=request)
            if rv is not None:
                new_headers[k] = rv
    request.headers = new_headers
    return request


def remove_headers(request, headers_to_remove):
    """
    Wrap replace_headers() for API backward compatibility.
    """
    replacements = [(k, None) for k in headers_to_remove]
    return replace_headers(request, replacements)


def replace_query_parameters(request, replacements):
    """
    Replace query parameters in request according to replacements. The
    replacements should be a list of (key, value) pairs where the value can be
    any of:
      1. A simple replacement string value.
      2. None to remove the given header.
      3. A callable which accepts (key, value, request) and returns a string
         value or None.
    """
    query = request.query
    new_query = []
    replacements = dict(replacements)
    for k, ov in query:
        if k not in replacements:
            new_query.append((k, ov))
        else:
            rv = replacements[k]
            if callable(rv):
                rv = rv(key=k, value=ov, request=request)
            if rv is not None:
                new_query.append((k, rv))
    uri_parts = list(urlparse(request.uri))
    uri_parts[4] = urlencode(new_query)
    request.uri = urlunparse(uri_parts)
    return request


def remove_query_parameters(request, query_parameters_to_remove):
    """
    Wrap replace_query_parameters() for API backward compatibility.
    """
    replacements = [(k, None) for k in query_parameters_to_remove]
    return replace_query_parameters(request, replacements)


def replace_post_data_parameters(request, replacements):
    """
    Replace post data in request--either form data or json--according to
    replacements. The replacements should be a list of (key, value) pairs where
    the value can be any of:
      1. A simple replacement string value.
      2. None to remove the given header.
      3. A callable which accepts (key, value, request) and returns a string
         value or None.
    """
    if not request.body:
        # Nothing to replace
        return request

    replacements = dict(replacements)
    if request.method == "POST" and not isinstance(request.body, BytesIO):
        if request.headers.get("Content-Type") == "application/json":
            json_data = json.loads(request.body.decode("utf-8"))
            for k, rv in replacements.items():
                if k in json_data:
                    ov = json_data.pop(k)
                    if callable(rv):
                        rv = rv(key=k, value=ov, request=request)
                    if rv is not None:
                        json_data[k] = rv
            request.body = json.dumps(json_data).encode("utf-8")
        else:
            if isinstance(request.body, text_type):
                request.body = request.body.encode("utf-8")
            splits = [p.partition(b"=") for p in request.body.split(b"&")]
            new_splits = []
            for k, sep, ov in splits:
                if sep is None:
                    new_splits.append((k, sep, ov))
                else:
                    rk = k.decode("utf-8")
                    if rk not in replacements:
                        new_splits.append((k, sep, ov))
                    else:
                        rv = replacements[rk]
                        if callable(rv):
                            rv = rv(key=rk, value=ov.decode("utf-8"), request=request)
                        if rv is not None:
                            new_splits.append((k, sep, rv.encode("utf-8")))
            request.body = b"&".join(k if sep is None else b"".join([k, sep, v]) for k, sep, v in new_splits)
    return request


def remove_post_data_parameters(request, post_data_parameters_to_remove):
    """
    Wrap replace_post_data_parameters() for API backward compatibility.
    """
    replacements = [(k, None) for k in post_data_parameters_to_remove]
    return replace_post_data_parameters(request, replacements)


def decode_response(response):
    """
    If the response is compressed with gzip or deflate:
      1. decompress the response body
      2. delete the content-encoding header
      3. update content-length header to decompressed length
    """

    def is_compressed(headers):
        encoding = headers.get("content-encoding", [])
        return encoding and encoding[0] in ("gzip", "deflate")

    def decompress_body(body, encoding):
        """Returns decompressed body according to encoding using zlib.
        to (de-)compress gzip format, use wbits = zlib.MAX_WBITS | 16
        """
        if encoding == "gzip":
            return zlib.decompress(body, zlib.MAX_WBITS | 16)
        else:  # encoding == 'deflate'
            return zlib.decompress(body)

    # Deepcopy here in case `headers` contain objects that could
    # be mutated by a shallow copy and corrupt the real response.
    response = copy.deepcopy(response)
    headers = CaseInsensitiveDict(response["headers"])
    if is_compressed(headers):
        encoding = headers["content-encoding"][0]
        headers["content-encoding"].remove(encoding)
        if not headers["content-encoding"]:
            del headers["content-encoding"]

        new_body = decompress_body(response["body"]["string"], encoding)
        response["body"]["string"] = new_body
        headers["content-length"] = [str(len(new_body))]
        response["headers"] = dict(headers)
    return response
