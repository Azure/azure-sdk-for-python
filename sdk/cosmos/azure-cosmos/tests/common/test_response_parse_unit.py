# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_response_parse.py`` — no network, no Cosmos emulator.

``parse_backend_response`` is the mirror image of the request-prep
helpers: where prep turns a customer call into a request-byte request, parse
turns the backend's request-byte response into the ``CosmosDict`` (or typed
exception) that the customer sees.

Every successful 2xx call has to do four things, and they're spread
across the four "D-tasks" fixed by these tests:

* **D1 build CosmosDict** — JSON-decode the body bytes and wrap them
  in a ``CosmosDict`` (which subclasses ``dict`` so customer code
  can index it like a normal dict).
* **D2 stash last_response_headers** — write the response headers to
  ``client_connection.last_response_headers`` so existing customer
  code that reads ``client.client_connection.last_response_headers``
  after a call keeps working.
* **D3 no-body 204 path** — ``no_response=True`` calls return 204
  with an empty body. ``json.loads(b"")`` would raise; the parser
  must explicitly return an empty ``CosmosDict`` instead.
* **D4 response_hook** — fire the optional ``response_hook(headers,
  parsed)`` exactly once on success, never on failure.

On the failure path (any non-2xx), the parser must raise the right
typed ``CosmosHttpResponseError`` subclass via the exception-mapping
helper, populate ``last_response_headers`` *before* raising (so the
customer's ``except`` block can still read them), and **never**
invoke the response hook.

The function is pure modulo the one documented side effect (writing
to ``client_connection.last_response_headers``). Both branches —
with and without that side effect — are covered.
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
    """Tiny ``BackendResponse`` factory so the test bodies stay readable."""
    return BackendResponse(
        status_code=status_code,
        sub_status=sub_status,
        headers=CaseInsensitiveDict(headers or {}),
        body=body,
    )


class _FakeClientConnection:
    """Tiny stand-in for ``CosmosClientConnection``.

    The parser writes to ``last_response_headers``; nothing else on
    the real connection is touched. Using a bare class instead of a
    ``MagicMock`` makes the assertions read more cleanly.
    """

    def __init__(self):
        self.last_response_headers = None


# ---------------------------------------------------------------------------
# Success path: 2xx with a JSON body (D1, D2, D4)
# ---------------------------------------------------------------------------


class TestSuccessWithBody(unittest.TestCase):
    """Success path covering D1 (build CosmosDict), D2 (stash headers), D4 (response_hook).

    These tests cover the common case: a 2xx response with a JSON
    body. Together they cover the parsed-body shape, the headers
    surfaced on the result, the legacy ``last_response_headers``
    side effect on the connection, and the hook invocation contract.
    """

    def test_returns_cosmos_dict_with_parsed_body(self):
        """2xx + JSON body → ``CosmosDict`` whose dict content is the parsed body."""
        body = b'{"id":"order-42","total":99.5}'
        result = parse_backend_response(
            _make_response(status_code=201, body=body),
        )
        self.assertIsInstance(result, CosmosDict)
        self.assertEqual(dict(result), {"id": "order-42", "total": 99.5})

    def test_response_headers_attached_to_cosmos_dict(self):
        """The per-call response headers are accessible via ``result.get_response_headers()``."""
        body = b'{"id":"x"}'
        result = parse_backend_response(
            _make_response(
                status_code=201,
                body=body,
                headers={"etag": "\"00000\"", "x-ms-request-charge": "1.0"},
            ),
        )
        self.assertEqual(result.get_response_headers()["etag"], "\"00000\"")
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.0")

    def test_last_response_headers_updated_on_client_connection(self):
        """D2: response headers are stashed on ``client_connection.last_response_headers`` (legacy compat)."""
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
        """D4: ``response_hook(headers, parsed)`` fires exactly once on success with the right arguments."""
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
        captured_headers, captured_body = captured[0]
        self.assertEqual(captured_headers["etag"], "\"00000\"")
        self.assertEqual(captured_body, {"id": "x", "v": 1})

    def test_no_response_hook_supplied_does_not_raise(self):
        """The ``response_hook`` parameter is optional; omitting it must not raise."""
        parse_backend_response(_make_response(status_code=201, body=b'{"id":"x"}'))


# ---------------------------------------------------------------------------
# Success path: no_response=True -> 204 with empty body (D3)
# ---------------------------------------------------------------------------


class TestSuccessWithEmptyBody(unittest.TestCase):
    """D3: the ``no_response=True`` path returns 204 with an empty body.

    ``json.loads(b"")`` would raise ``JSONDecodeError``; the parser
    must explicitly bypass the parse and return an empty
    ``CosmosDict``. The hook still fires (callers using the hook for
    telemetry expect the invocation count to match the request
    count). 2xx with a *malformed* body is a different case — that
    one does raise, matching legacy behaviour.
    """

    def test_204_with_empty_body_returns_empty_cosmos_dict(self):
        """204 + empty body → empty ``CosmosDict`` (never raises ``JSONDecodeError``, never returns ``None``)."""
        result = parse_backend_response(_make_response(status_code=204, body=b""))
        self.assertIsInstance(result, CosmosDict)
        self.assertEqual(dict(result), {})

    def test_200_with_empty_body_also_returns_empty_dict(self):
        """200 + empty body is treated the same as 204 — empty ``CosmosDict``, no parse attempted."""
        result = parse_backend_response(_make_response(status_code=200, body=b""))
        self.assertEqual(dict(result), {})

    def test_response_hook_receives_empty_dict_for_no_body_path(self):
        """Hook still fires on the 204 path; it sees an empty parsed body."""
        captured = []
        parse_backend_response(
            _make_response(status_code=204, body=b""),
            response_hook=lambda headers, parsed: captured.append(parsed),
        )
        self.assertEqual(captured, [{}])

    def test_2xx_with_malformed_body_raises_jsondecodeerror(self):
        """2xx + non-JSON body → raises ``JSONDecodeError`` (legacy parity); the hook is not invoked."""
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
    """Non-2xx raises the right typed exception; hook is not called; headers are still stashed.

    The status-code → exception-class mapping itself is exhaustively
    covered in ``test_exceptions_unit.py``; these tests cover only
    the wiring through ``parse_backend_response`` (the right
    subclass is raised, the response shim carries the metadata,
    ``response_hook`` is suppressed, and ``last_response_headers``
    is populated *before* the raise).
    """

    def test_409_raises_resource_exists_error(self):
        """409 → ``CosmosResourceExistsError`` propagated by the parser."""
        with self.assertRaises(CosmosResourceExistsError):
            parse_backend_response(
                _make_response(
                    status_code=409,
                    body=b'{"code":"Conflict","message":"already exists"}',
                ),
            )

    def test_404_raises_resource_not_found(self):
        """404 → ``CosmosResourceNotFoundError`` propagated by the parser."""
        with self.assertRaises(CosmosResourceNotFoundError):
            parse_backend_response(_make_response(status_code=404))

    def test_500_raises_base_cosmos_http_response_error(self):
        """500 (unmapped status) → base ``CosmosHttpResponseError`` propagated by the parser."""
        with self.assertRaises(CosmosHttpResponseError):
            parse_backend_response(_make_response(status_code=500))

    def test_exception_carries_status_and_response_shim(self):
        """The raised exception's ``response`` exposes ``status_code`` and ``headers`` from the underlying response."""
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
        """The response hook is *not* called when the parser raises (it runs only on success)."""
        captured = []

        def hook(*_):
            captured.append(True)

        with self.assertRaises(CosmosResourceExistsError):
            parse_backend_response(
                _make_response(status_code=409, body=b'{"message":"dup"}'),
                response_hook=hook,
            )
        self.assertEqual(captured, [])

    def test_last_response_headers_updated_even_on_failure(self):
        """``last_response_headers`` is stashed on the connection *before* the raise, so ``except`` blocks can read it."""
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
    """The parser normalises headers regardless of the shape the backend handed back.

    Different backends / test fixtures hand headers in different
    shapes (``CaseInsensitiveDict``, plain ``dict``, ``None``,
    numeric-typed values for things like RU charges). The parser
    must produce a stable, customer-facing surface from any of
    them: case-insensitive lookups always work, missing headers
    give an empty map (not a crash), and numeric values are
    coerced to strings so customer code that string-compares stays
    stable.
    """

    def test_plain_dict_input_becomes_case_insensitive_in_output(self):
        """A plain-dict (mixed-case) input → output supports case-insensitive header lookups."""
        backend_response = BackendResponse(
            status_code=201,
            headers={"X-MS-Request-Charge": "1.0"},
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.0")

    def test_none_headers_input_does_not_crash(self):
        """A ``headers=None`` response (test fixture) → empty headers map, no crash."""
        backend_response = BackendResponse(status_code=201, headers=None, body=b"{}")
        result = parse_backend_response(backend_response)
        self.assertEqual(dict(result.get_response_headers()), {})

    def test_numeric_request_charge_is_stringified(self):
        """A numeric-typed RU charge from the Rust path is coerced to a string for customer compatibility."""
        backend_response = BackendResponse(
            status_code=201,
            headers={"x-ms-request-charge": 1.43},
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "1.43")

    def test_string_request_charge_is_left_alone(self):
        """A string RU charge from the core-python path is preserved verbatim — no round-trip drift."""
        backend_response = BackendResponse(
            status_code=201,
            headers={"x-ms-request-charge": "2.50"},
            body=b"{}",
        )
        result = parse_backend_response(backend_response)
        # Kept exactly as the request-byte string — including any trailing zero.
        self.assertEqual(result.get_response_headers()["x-ms-request-charge"], "2.50")


if __name__ == "__main__":
    unittest.main()
