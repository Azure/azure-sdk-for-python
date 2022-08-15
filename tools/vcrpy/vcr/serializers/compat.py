import six


def convert_to_bytes(resp):
    resp = convert_body_to_bytes(resp)
    return resp


def convert_to_unicode(resp):
    resp = convert_body_to_unicode(resp)
    return resp


def convert_body_to_bytes(resp):
    """
    If the request body is a string, encode it to bytes (for python3 support)

    By default yaml serializes to utf-8 encoded bytestrings.
    When this cassette is loaded by python3, it's automatically decoded
    into unicode strings. This makes sure that it stays a bytestring, since
    that's what all the internal httplib machinery is expecting.

    For more info on py3 yaml:
    http://pyyaml.org/wiki/PyYAMLDocumentation#Python3support
    """
    try:
        if resp["body"]["string"] is not None and not isinstance(resp["body"]["string"], six.binary_type):
            resp["body"]["string"] = resp["body"]["string"].encode("utf-8")
    except (KeyError, TypeError, UnicodeEncodeError):
        # The thing we were converting either wasn't a dictionary or didn't
        # have the keys we were expecting.  Some of the tests just serialize
        # and deserialize a string.

        # Also, sometimes the thing actually is binary, so if you can't encode
        # it, just give up.
        pass
    return resp


def _convert_string_to_unicode(string):
    """
    If the string is bytes, decode it to a string (for python3 support)
    """
    result = string

    try:
        if string is not None and not isinstance(string, six.text_type):
            result = string.decode("utf-8")
    except (TypeError, UnicodeDecodeError, AttributeError):
        # Sometimes the string actually is binary or StringIO object,
        # so if you can't decode it, just give up.
        pass

    return result


def convert_body_to_unicode(resp):
    """
    If the request or responses body is bytes, decode it to a string
    (for python3 support)
    """
    if type(resp) is not dict:
        # Some of the tests just serialize and deserialize a string.
        return _convert_string_to_unicode(resp)
    else:
        body = resp.get("body")

        if body is not None:
            try:
                body["string"] = _convert_string_to_unicode(body["string"])
            except (KeyError, TypeError, AttributeError):
                # The thing we were converting either wasn't a dictionary or
                # didn't have the keys we were expecting.
                # For example request object has no 'string' key.
                resp["body"] = _convert_string_to_unicode(body)

    return resp
