import json
from six.moves import urllib, xmlrpc_client
from .util import read_body
import logging


log = logging.getLogger(__name__)


def method(r1, r2):
    assert r1.method == r2.method, "{} != {}".format(r1.method, r2.method)


def uri(r1, r2):
    assert r1.uri == r2.uri, "{} != {}".format(r1.uri, r2.uri)


def host(r1, r2):
    assert r1.host == r2.host, "{} != {}".format(r1.host, r2.host)


def scheme(r1, r2):
    assert r1.scheme == r2.scheme, "{} != {}".format(r1.scheme, r2.scheme)


def port(r1, r2):
    assert r1.port == r2.port, "{} != {}".format(r1.port, r2.port)


def path(r1, r2):
    assert r1.path == r2.path, "{} != {}".format(r1.path, r2.path)


def query(r1, r2):
    assert r1.query == r2.query, "{} != {}".format(r1.query, r2.query)


def raw_body(r1, r2):
    assert read_body(r1) == read_body(r2)


def body(r1, r2):
    transformer = _get_transformer(r1)
    r2_transformer = _get_transformer(r2)
    if transformer != r2_transformer:
        transformer = _identity
    assert transformer(read_body(r1)) == transformer(read_body(r2))


def headers(r1, r2):
    assert r1.headers == r2.headers, "{} != {}".format(r1.headers, r2.headers)


def _header_checker(value, header="Content-Type"):
    def checker(headers):
        _header = headers.get(header, "")
        if isinstance(_header, bytes):
            _header = _header.decode("utf-8")
        return value in _header.lower()

    return checker


def _transform_json(body):
    # Request body is always a byte string, but json.loads() wants a text
    # string. RFC 7159 says the default encoding is UTF-8 (although UTF-16
    # and UTF-32 are also allowed: hmmmmm).
    if body:
        return json.loads(body.decode("utf-8"))


_xml_header_checker = _header_checker("text/xml")
_xmlrpc_header_checker = _header_checker("xmlrpc", header="User-Agent")
_checker_transformer_pairs = (
    (
        _header_checker("application/x-www-form-urlencoded"),
        lambda body: urllib.parse.parse_qs(body.decode("ascii")),
    ),
    (_header_checker("application/json"), _transform_json),
    (lambda request: _xml_header_checker(request) and _xmlrpc_header_checker(request), xmlrpc_client.loads),
)


def _identity(x):
    return x


def _get_transformer(request):
    for checker, transformer in _checker_transformer_pairs:
        if checker(request.headers):
            return transformer
    else:
        return _identity


def requests_match(r1, r2, matchers):
    successes, failures = get_matchers_results(r1, r2, matchers)
    if failures:
        log.debug("Requests {} and {} differ.\n" "Failure details:\n" "{}".format(r1, r2, failures))
    return len(failures) == 0


def _evaluate_matcher(matcher_function, *args):
    """
    Evaluate the result of a given matcher as a boolean with an assertion error message if any.
    It handles two types of matcher :
    - a matcher returning a boolean value.
    - a matcher that only makes an assert, returning None or raises an assertion error.
    """
    assertion_message = None
    try:
        match = matcher_function(*args)
        match = True if match is None else match
    except AssertionError as e:
        match = False
        assertion_message = str(e)
    return match, assertion_message


def get_matchers_results(r1, r2, matchers):
    """
    Get the comparison results of two requests as two list.
    The first returned list represents the matchers names that passed.
    The second list is the failed matchers as a string with failed assertion details if any.
    """
    matches_success, matches_fails = [], []
    for m in matchers:
        matcher_name = m.__name__
        match, assertion_message = _evaluate_matcher(m, r1, r2)
        if match:
            matches_success.append(matcher_name)
        else:
            assertion_message = get_assertion_message(assertion_message)
            matches_fails.append((matcher_name, assertion_message))
    return matches_success, matches_fails


def get_assertion_message(assertion_details):
    """
    Get a detailed message about the failing matcher.
    """
    return assertion_details
