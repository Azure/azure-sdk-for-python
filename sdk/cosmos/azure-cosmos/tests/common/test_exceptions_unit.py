# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_exceptions.py`` — no network, no Cosmos emulator.

When a backend (Rust today, eventually only Rust) returns a non-2xx
``BackendResponse``, the helper layer turns that response into the
right ``CosmosHttpResponseError`` subclass and stamps it with the
metadata customer code expects (``status_code``, ``sub_status``,
``response.headers``, ``response.text()``). This file covers every
piece of that translation:

* The status-code → typed-exception mapping (409 must be
  ``CosmosResourceExistsError``, 404 must be
  ``CosmosResourceNotFoundError``, 412 must be
  ``CosmosAccessConditionFailedError``, the rest fall back to
  ``CosmosHttpResponseError``).
* The exception's metadata mirrors the response (status, sub-status,
  headers, decoded body, custom message).
* ``extract_message_from_body`` digs the human-readable message out
  of the JSON error body in the various shapes the service has
  shipped over the years, and never raises on malformed input.
* ``is_success_status`` agrees with the rest of the SDK on what
  counts as a success (the 2xx range, nothing else).
* The ``_BackendResponseShim`` exposes the same surface customer
  code already uses on ``e.response`` (``status_code``, ``headers``,

  ``text()``, ``body()``) and never raises on weird body bytes.

The duplicate-id 409 → ``CosmosResourceExistsError`` mapping is the
one customer code most often relies on (`except
CosmosResourceExistsError` as a cheap idempotency check); locking down it
here makes that contract impossible to break silently.
"""
import unittest

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import BackendResponse
from azure.cosmos._helpers._exceptions import (
    _BackendResponseShim,
    extract_message_from_body,
    is_success_status,
    map_backend_response_to_exception,
)
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError,
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)


def _make_response(*, status_code, sub_status=0, headers=None, body=b""):
    """Tiny ``BackendResponse`` factory so the test bodies stay readable."""
    return BackendResponse(
        status_code=status_code,
        sub_status=sub_status,
        headers=CaseInsensitiveDict(headers or {}),
        body=body,
    )


class TestStatusToExceptionMapping(unittest.TestCase):
    """Cover the status-code → typed-exception table.

    These four mappings are the contract customer code relies on.
    The first three are the "named" failures with dedicated subclass
    handlers; the rest of the 4xx/5xx range falls back to the base
    ``CosmosHttpResponseError`` plus the ``sub_status`` field for
    finer-grained discrimination.
    """

    def test_409_maps_to_resource_exists(self):
        """409 → ``CosmosResourceExistsError`` (the duplicate-id contract customers ``except`` on)."""
        exc = map_backend_response_to_exception(_make_response(status_code=409))
        self.assertIsInstance(exc, CosmosResourceExistsError)

    def test_404_maps_to_resource_not_found(self):
        """404 → ``CosmosResourceNotFoundError``."""
        exc = map_backend_response_to_exception(_make_response(status_code=404))
        self.assertIsInstance(exc, CosmosResourceNotFoundError)

    def test_412_maps_to_access_condition_failed(self):
        """412 → ``CosmosAccessConditionFailedError`` (etag / If-Match precondition)."""
        exc = map_backend_response_to_exception(_make_response(status_code=412))
        self.assertIsInstance(exc, CosmosAccessConditionFailedError)

    def test_429_falls_back_to_base_class(self):
        """429 has no dedicated subclass today; it must be the base ``CosmosHttpResponseError``.

        If someone later adds a ``CosmosThrottlingError`` subclass,
        this test will fail and force a deliberate review of whether
        existing customer ``except`` handlers still catch it.
        """
        exc = map_backend_response_to_exception(_make_response(status_code=429))
        self.assertIsInstance(exc, CosmosHttpResponseError)
        # Belt-and-braces: not silently downgraded to one of the typed subclasses.
        self.assertNotIsInstance(exc, CosmosResourceExistsError)
        self.assertNotIsInstance(exc, CosmosResourceNotFoundError)

    def test_500_falls_back_to_base_class(self):
        """500 (and any other unmapped status) → base ``CosmosHttpResponseError``."""
        exc = map_backend_response_to_exception(_make_response(status_code=500))
        self.assertIsInstance(exc, CosmosHttpResponseError)


class TestExceptionMetadataIsCopiedAcross(unittest.TestCase):
    """The exception carries the response's status, sub-status, headers, body and message.

    Customer code reads these off the exception (``e.status_code``,
    ``e.sub_status``, ``e.response.headers``, ``e.response.text()``,

    ``str(e)``) and the legacy core-python path always populated
    them. The helper layer must do the same so a Rust round-trip
    surfaces an indistinguishable exception object.
    """

    def test_status_code_is_propagated(self):
        """``BackendResponse.status_code`` → ``exc.status_code``."""
        exc = map_backend_response_to_exception(_make_response(status_code=409))
        self.assertEqual(exc.status_code, 409)

    def test_sub_status_from_typed_field_is_propagated(self):
        """``BackendResponse.sub_status`` is honoured even when the headers map omits it.

        The Rust path fills the typed ``sub_status`` field directly
        rather than only via the ``x-ms-substatus`` header, so the
        helper must read the typed field as the source of truth.
        """
        exc = map_backend_response_to_exception(
            _make_response(status_code=429, sub_status=3200)
        )
        self.assertEqual(exc.sub_status, 3200)

    def test_response_shim_exposes_status_code_and_headers(self):
        """``e.response.status_code`` and ``e.response.headers`` mirror the underlying response."""
        exc = map_backend_response_to_exception(
            _make_response(status_code=409, headers={"x-ms-x": "1"})
        )
        self.assertEqual(exc.response.status_code, 409)
        self.assertEqual(exc.response.headers["x-ms-x"], "1")

    def test_response_shim_text_decodes_body_as_utf8(self):
        """``e.response.text()`` returns the body decoded as UTF-8 (the documented surface)."""
        exc = map_backend_response_to_exception(
            _make_response(status_code=400, body=b'{"message":"bad"}')
        )
        self.assertEqual(exc.response.text(), '{"message":"bad"}')

    def test_response_shim_body_returns_raw_bytes(self):
        """``e.response.body()`` returns the raw bytes, undecoded."""
        exc = map_backend_response_to_exception(
            _make_response(status_code=400, body=b"raw")
        )
        self.assertEqual(exc.response.body(), b"raw")

    def test_message_is_used_in_exception_text(self):
        """A ``message=`` argument shows up in ``str(exc)`` (used by logs and tracebacks)."""
        exc = map_backend_response_to_exception(
            _make_response(status_code=409),
            message="duplicate id detected",
        )
        # CosmosHttpResponseError formats as "Status code: NNN\n<message>".
        self.assertIn("duplicate id detected", str(exc))


class TestExtractMessageFromBody(unittest.TestCase):
    """Pull the human-readable error message out of a Cosmos JSON error body.

    The Cosmos service returns errors as JSON with a ``message`` (or
    historically ``Message``) field. ``extract_message_from_body`` is
    the best-effort parser the helper uses to populate the exception's
    message. It must never raise — a malformed body should never mask
    the underlying error.
    """

    def test_json_body_with_message_field_returned(self):
        """Lower-case ``message`` field is extracted."""
        body = b'{"code":"Conflict","message":"Resource with specified id ..."}'
        self.assertEqual(
            extract_message_from_body(body),
            "Resource with specified id ...",
        )

    def test_json_body_with_capital_message_field_returned(self):
        """Upper-case ``Message`` field is also extracted (older service variant)."""
        body = b'{"code":"Conflict","Message":"capital M variant"}'
        self.assertEqual(extract_message_from_body(body), "capital M variant")

    def test_empty_body_returns_empty_string(self):
        """Empty body → empty string (no synthetic placeholder)."""
        self.assertEqual(extract_message_from_body(b""), "")

    def test_non_json_body_falls_back_to_utf8_decoded_string(self):
        """A non-JSON body is returned as its UTF-8 decoded string."""
        self.assertEqual(extract_message_from_body(b"not json"), "not json")

    def test_invalid_utf8_body_returns_repr(self):
        """An undecodable body still produces a non-empty string and never raises."""
        result = extract_message_from_body(b"\xff\xfe invalid utf8")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_json_body_without_message_field_falls_back_to_decoded_string(self):
        """JSON body with no ``message`` / ``Message`` field → the raw decoded body."""
        body = b'{"code":"Conflict"}'
        self.assertEqual(extract_message_from_body(body), '{"code":"Conflict"}')


class TestIsSuccessStatus(unittest.TestCase):
    """Cover the success-status range used by the helper.

    The whole 2xx range counts as success; everything else is a
    failure. 3xx in particular is *not* treated as success today —
    Cosmos operations don't use it as a normal-path response.
    """

    def test_200_is_success(self):
        """200 OK → success."""
        self.assertTrue(is_success_status(200))

    def test_204_is_success(self):
        """204 No Content → success (this is what the ``no_response=True`` path returns)."""
        self.assertTrue(is_success_status(204))

    def test_299_is_success(self):
        """The whole 2xx range is success, including the upper edge."""
        self.assertTrue(is_success_status(299))

    def test_300_is_not_success(self):
        """3xx is not treated as success (Cosmos doesn't use redirects on the data plane)."""
        self.assertFalse(is_success_status(300))

    def test_404_is_not_success(self):
        """404 Not Found → failure."""
        self.assertFalse(is_success_status(404))

    def test_500_is_not_success(self):
        """500 Internal Server Error → failure."""
        self.assertFalse(is_success_status(500))


class TestBackendResponseShimDirectly(unittest.TestCase):
    """The shim is what customer ``except`` handlers see as ``e.response``.

    Customer code reaches into ``e.response`` for ``status_code``,

    ``headers``, ``text()`` and ``body()``. The shim must expose all
    of those, must never crash on weird inputs (missing headers,
    invalid UTF-8 body, bogus encoding name), and must always return
    a string from ``text()`` so it cannot mask the original Cosmos
    error inside the customer's handler.
    """

    def test_shim_status_code_matches_inner_response(self):
        """``shim.status_code`` mirrors the inner ``BackendResponse.status_code``."""
        shim = _BackendResponseShim(_make_response(status_code=200))
        self.assertEqual(shim.status_code, 200)

    def test_shim_headers_default_to_empty_dict_when_none(self):
        """A response with no headers still exposes a usable headers mapping (no ``AttributeError``)."""
        empty = BackendResponse(status_code=409)
        shim = _BackendResponseShim(empty)
        self.assertEqual(dict(shim.headers), {})

    def test_shim_text_falls_back_on_invalid_utf8_bytes(self):
        """``text()`` on invalid UTF-8 bytes returns a string (replacement chars), never raises.

        If this method raised inside a customer's
        ``except CosmosHttpResponseError`` handler, the original
        Cosmos error would be masked by a confusing
        ``UnicodeDecodeError`` and the handler would crash.
        """
        bad_bytes = b"\xff\xfe\xfd not valid utf-8"
        shim = _BackendResponseShim(BackendResponse(status_code=500, body=bad_bytes))
        text = shim.text()
        self.assertIsInstance(text, str)
        # The decodable substring round-trips so the body isn't lost entirely.
        self.assertIn("not valid utf-8", text)

    def test_shim_text_falls_back_on_invalid_encoding_name(self):
        """An unknown ``encoding=`` name still returns a string instead of raising."""
        shim = _BackendResponseShim(BackendResponse(status_code=500, body=b"hello"))
        text = shim.text(encoding="not-a-real-encoding")
        self.assertIsInstance(text, str)

    def test_shim_text_returns_empty_string_when_body_is_empty(self):
        """Empty body → empty string from ``text()``."""
        shim = _BackendResponseShim(BackendResponse(status_code=204))
        self.assertEqual(shim.text(), "")


if __name__ == "__main__":
    unittest.main()
