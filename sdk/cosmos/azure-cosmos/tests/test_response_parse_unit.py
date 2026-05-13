# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_response_parse.py`` —— no network, no Cosmos emulator.

Covers all four success-path tasks (D1 build CosmosDict, D2 stash
last_response_headers, D3 no-body 204 path, D4 response_hook) and
the failure-path raise-via-typed-exception contract. The function under test is
pure modulo a single documented side effect (writing to
``client_connection.last_response_headers``); both branches are
covered.
"""
import unittest

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos._helpers._response_parse import parse_backend_response
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)


def _make_response(*, status_code=200, sub_status=0, headers=None, body=b""):
    """Tiny BackendResponse factory."""
    return BackendResponse(
        status_code=status_code,
        sub_status=sub_status,
        headers=CaseInsensitiveDict(headers or {}),
        body=body,
    )


class _FakeClientConnection:
    """Tiny stand-in for CosmosClientConnection.

    The parser writes to ``last_response_headers``; nothing else on
    the real connection is touched. Using a bare class instead of a
    MagicMock makes the assertions read more cleanly.
    """

    def __init__(self):
        self.last_response_headers = None


# ---------------------------------------------------------------------------
# Success path: 2xx with a JSON body (D1, D2, D4)
# ---------------------------------------------------------------------------


class TestSuccessWithBody(unittest.TestCase):
    """D1 + D2 + D4 —— common case."""

    def test_returns_cosmos_dict_with_parsed_body(self):
        body = b'{"id":"order-42","total":99.5}'
        result = parse_backend_response(
            _make_response(status_code=201, body=body),
        )
        self.assertIsInstance(result, CosmosDict)
        # CosmosDict subclasses dict; equality compares the dict
        # content.
        self.assertEqual(dict(result), {"id": "order-42", "total": 99.5})

    def test_response_headers_attached_to_cosmos_dict(self):
        body = b'{"id":"x"}'
        result = parse_backend_response(
            _make_response(
                status_code=201,
                body=body,
                headers={"etag": "\"00000\"", "x-ms-request-charge": "1.0"},
            ),
        )
        # CosmosDict has a ``response_headers`` attribute that
        # carries the per-call headers map.
        self.assertEqual(result.get_response_headers()["etag"], "\"00000\"")
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.0")

    def test_last_response_headers_updated_on_client_connection(self):
        # D2: the legacy code stamps ``last_response_headers`` on the
        # client_connection so customers reading
        # ``client.client_connection.last_response_headers`` after a
        # call keep working. The parser does the same.
        cc = _FakeClientConnection()
        parse_backend_response(
            _make_response(
                status_code=201,
                body=b'{"id":"x"}',
                headers={"x-ms-request-charge": "2.43"},
            ),
            client_connection=cc,
        )
        self.assertEqual(cc.last_response_headers["x-ms-request-charge"], "2.43")

    def test_response_hook_invoked_once_on_success(self):
        # D4: response_hook(headers, parsed) fires exactly once on
        # success.
        captured = []

        def hook(headers, parsed):
            captured.append((dict(headers), parsed))

        parse_backend_response(
            _make_response(
                status_code=201,
                body=b'{"id":"x","v":1}',
                headers={"etag": "\"00000\""},
            ),
            response_hook=hook,
        )
        self.assertEqual(len(captured), 1)
        # Hook received the headers map and the parsed body.
        captured_headers, captured_body = captured[0]
        self.assertEqual(captured_headers["etag"], "\"00000\"")
        self.assertEqual(captured_body, {"id": "x", "v": 1})

    def test_no_response_hook_supplied_does_not_raise(self):
        # The hook param is optional; the parser must not require it.
        parse_backend_response(_make_response(status_code=201, body=b'{"id":"x"}'))


# ---------------------------------------------------------------------------
# Success path: no_response=True -> 204 with empty body (D3)
# ---------------------------------------------------------------------------


class TestSuccessWithEmptyBody(unittest.TestCase):
    """D3 —— the ``no_response=True`` path."""

    def test_204_with_empty_body_returns_empty_cosmos_dict(self):
        # The legacy code returns an empty CosmosDict({}), NOT None
        # and NOT raising. ``json.loads(b"")`` would raise
        # JSONDecodeError; the parser explicitly bypasses that.
        result = parse_backend_response(_make_response(status_code=204, body=b""))
        self.assertIsInstance(result, CosmosDict)
        self.assertEqual(dict(result), {})

    def test_200_with_empty_body_also_returns_empty_dict(self):
        # Some operations return 200 with no body (rare but possible).
        # Treat them the same as 204 —— empty CosmosDict, no parse.
        result = parse_backend_response(_make_response(status_code=200, body=b""))
        self.assertEqual(dict(result), {})

    def test_response_hook_receives_empty_dict_for_no_body_path(self):
        # The hook still fires for 204; it just sees an empty body.
        # Customers who use the hook for telemetry expect the
        # invocation count to match the request count, regardless of
        # whether the request asked for a response payload.
        captured = []
        parse_backend_response(
            _make_response(status_code=204, body=b""),
            response_hook=lambda headers, parsed: captured.append(parsed),
        )
        self.assertEqual(captured, [{}])

    def test_2xx_with_malformed_body_raises_jsondecodeerror(self):
        # 2xx with a non-JSON body is surfaced as JSONDecodeError, the
        # same failure mode the legacy CreateItem path produced. The
        # response_hook is never invoked in this case (the parser
        # raises before reaching the hook).
        import json as _json
        captured = []
        with self.assertRaises(_json.JSONDecodeError):
            parse_backend_response(
                _make_response(status_code=200, body=b"not-valid-json{"),
                response_hook=lambda headers, parsed: captured.append(parsed),
            )
        self.assertEqual(captured, [])


# ---------------------------------------------------------------------------
# Failure path: non-2xx -> raise via the exception-mapping helper
# ---------------------------------------------------------------------------


class TestFailurePath(unittest.TestCase):
    """Non-2xx raises the right typed exception; hook is not called."""

    def test_409_raises_resource_exists_error(self):
        with self.assertRaises(CosmosResourceExistsError):
            parse_backend_response(
                _make_response(
                    status_code=409,
                    body=b'{"code":"Conflict","message":"already exists"}',
                ),
            )

    def test_404_raises_resource_not_found(self):
        with self.assertRaises(CosmosResourceNotFoundError):
            parse_backend_response(_make_response(status_code=404))

    def test_500_raises_base_cosmos_http_response_error(self):
        with self.assertRaises(CosmosHttpResponseError):
            parse_backend_response(_make_response(status_code=500))

    def test_exception_carries_status_and_response_shim(self):
        # The exception's response attribute exposes status_code and
        # headers, and the create-item exception contract.
        try:
            parse_backend_response(
                _make_response(
                    status_code=409,
                    headers={"x-ms-x": "1"},
                    body=b'{"message":"dup"}',
                ),
            )
        except CosmosResourceExistsError as exc:
            self.assertEqual(exc.response.status_code, 409)
            self.assertEqual(exc.response.headers["x-ms-x"], "1")
        else:
            self.fail("expected CosmosResourceExistsError")

    def test_response_hook_not_invoked_on_failure(self):
        captured = []

        def hook(*_):
            captured.append(True)

        with self.assertRaises(CosmosResourceExistsError):
            parse_backend_response(
                _make_response(status_code=409, body=b'{"message":"dup"}'),
                response_hook=hook,
            )
        # Hook never ran because the failure path raised before
        # invocation.
        self.assertEqual(captured, [])

    def test_last_response_headers_updated_even_on_failure(self):
        # The legacy code path stamps last_response_headers BEFORE it
        # raises so the customer's ``except`` block can still read
        # the headers off the client. Match that.
        cc = _FakeClientConnection()
        with self.assertRaises(CosmosResourceExistsError):
            parse_backend_response(
                _make_response(status_code=409, headers={"x-ms-x": "1"}, body=b""),
                client_connection=cc,
            )
        self.assertIsNotNone(cc.last_response_headers)
        self.assertEqual(cc.last_response_headers["x-ms-x"], "1")


# ---------------------------------------------------------------------------
# Header normalization
# ---------------------------------------------------------------------------


class TestHeaderNormalization(unittest.TestCase):
    """Headers come back as CaseInsensitiveDict regardless of input shape."""

    def test_plain_dict_input_becomes_case_insensitive_in_output(self):
        # A backend that hands back a plain dict (not yet wrapped in
        # CaseInsensitiveDict) should still produce a parser output
        # whose response_headers responds to mixed-case lookups.
        backend_response = BackendResponse(
            status_code=201,
            headers={"X-MS-Request-Charge": "1.0"},  # plain dict, mixed case
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        # Mixed-case lookup against the output should work.
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.0")

    def test_none_headers_input_does_not_crash(self):
        # A backend that did not populate headers at all (test
        # fixture) should still produce a CosmosDict with an empty
        # but valid headers map.
        backend_response = BackendResponse(status_code=201, headers=None, body=b"{}")
        result = parse_backend_response(backend_response)
        self.assertEqual(dict(result.get_response_headers()), {})

    def test_numeric_request_charge_is_stringified(self):
        # The Rust path may surface request charge as a typed numeric
        # in headers. The parser must coerce it to a string so
        # customer code that string-compares the value keeps working.
        backend_response = BackendResponse(
            status_code=201,
            headers={"x-ms-request-charge": 1.43},  # numeric, not string
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.43")

    def test_string_request_charge_is_left_alone(self):
        # The core-python path always provides a string. No
        # round-tripping that introduces drift.
        backend_response = BackendResponse(
            status_code=201,
            headers={"x-ms-request-charge": "2.50"},
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        # Note: kept exactly as the wire string —— including the
        # trailing zero the server might have sent.
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "2.50")


if __name__ == "__main__":
    unittest.main()
