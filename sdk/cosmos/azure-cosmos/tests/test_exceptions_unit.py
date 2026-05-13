# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_exceptions.py`` â—” no network, no Cosmos emulator.

These tests pin the (status, sub_status) â→ exception class mapping
that the helper-layer parser uses on a non-2xx ``BackendResponse``.
The duplicate-id 409 â→ ``CosmosResourceExistsError`` mapping in
particular is the one customer code most relies on (``except
CosmosResourceExistsError`` as a cheap idempotency check); keeping
it pinned here makes that contract impossible to break silently.
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
    """Tiny BackendResponse factory so the test bodies stay readable."""
    return BackendResponse(
        status_code=status_code,
        sub_status=sub_status,
        headers=CaseInsensitiveDict(headers or {}),
        body=body,
    )


class TestStatusToExceptionMapping(unittest.TestCase):
    """The status-code â→ typed-exception table is the contract."""

    def test_409_maps_to_resource_exists(self):
        # The signature error of create_item. Customer code does
        # ``except CosmosResourceExistsError:`` to detect "already
        # created"; if 409 ever stops mapping to this class, that
        # branch silently breaks and duplicate orders show up.
        exc = map_backend_response_to_exception(_make_response(status_code=409))
        self.assertIsInstance(exc, CosmosResourceExistsError)

    def test_404_maps_to_resource_not_found(self):
        exc = map_backend_response_to_exception(_make_response(status_code=404))
        self.assertIsInstance(exc, CosmosResourceNotFoundError)

    def test_412_maps_to_access_condition_failed(self):
        exc = map_backend_response_to_exception(_make_response(status_code=412))
        self.assertIsInstance(exc, CosmosAccessConditionFailedError)

    def test_429_falls_back_to_base_class(self):
        # 429 has no dedicated subclass in the public exceptions
        # module today â—” the SDK reports it via the generic
        # CosmosHttpResponseError plus the substatus header. Catch a
        # future addition by treating this as a deliberate decision.
        exc = map_backend_response_to_exception(_make_response(status_code=429))
        self.assertIsInstance(exc, CosmosHttpResponseError)
        # And specifically NOT one of the typed subclasses above.
        self.assertNotIsInstance(exc, CosmosResourceExistsError)
        self.assertNotIsInstance(exc, CosmosResourceNotFoundError)

    def test_500_falls_back_to_base_class(self):
        exc = map_backend_response_to_exception(_make_response(status_code=500))
        self.assertIsInstance(exc, CosmosHttpResponseError)


class TestExceptionMetadataIsCopiedAcross(unittest.TestCase):
    """The exception carries status, sub_status, headers, and a response shim."""

    def test_status_code_is_propagated(self):
        exc = map_backend_response_to_exception(_make_response(status_code=409))
        self.assertEqual(exc.status_code, 409)

    def test_sub_status_from_typed_field_is_propagated(self):
        # The Rust path will fill the typed BackendResponse.sub_status
        # field; we honour it even when the headers map does not
        # carry the same value.
        exc = map_backend_response_to_exception(
            _make_response(status_code=429, sub_status=3200)
        )
        self.assertEqual(exc.sub_status, 3200)

    def test_response_shim_exposes_status_code_and_headers(self):
        # Customer code does ``e.response.status_code`` and
        # ``e.response.headers`` â—” preserve that surface.
        exc = map_backend_response_to_exception(
            _make_response(status_code=409, headers={"x-ms-x": "1"})
        )
        self.assertEqual(exc.response.status_code, 409)
        self.assertEqual(exc.response.headers["x-ms-x"], "1")

    def test_response_shim_text_decodes_body_as_utf8(self):
        # ``e.response.text()`` is a documented HttpResponse-like
        # surface customer code uses to read the error body.
        exc = map_backend_response_to_exception(
            _make_response(status_code=400, body=b'{"message":"bad"}')
        )
        self.assertEqual(exc.response.text(), '{"message":"bad"}')

    def test_response_shim_body_returns_raw_bytes(self):
        exc = map_backend_response_to_exception(
            _make_response(status_code=400, body=b"raw")
        )
        self.assertEqual(exc.response.body(), b"raw")

    def test_message_is_used_in_exception_text(self):
        exc = map_backend_response_to_exception(
            _make_response(status_code=409),
            message="duplicate id detected",
        )
        # CosmosHttpResponseError formats messages as
        # "Status code: NNN\n<message>". The message text we passed
        # in must appear somewhere in the str repr.
        self.assertIn("duplicate id detected", str(exc))


class TestExtractMessageFromBody(unittest.TestCase):
    """Best-effort extraction of the server's error message."""

    def test_json_body_with_message_field_returned(self):
        body = b'{"code":"Conflict","message":"Resource with specified id ..."}'
        self.assertEqual(
            extract_message_from_body(body),
            "Resource with specified id ...",
        )

    def test_json_body_with_capital_message_field_returned(self):
        # The Cosmos service has shipped both ``message`` and
        # ``Message`` capitalisations over the years; cover both.
        body = b'{"code":"Conflict","Message":"capital M variant"}'
        self.assertEqual(extract_message_from_body(body), "capital M variant")

    def test_empty_body_returns_empty_string(self):
        self.assertEqual(extract_message_from_body(b""), "")

    def test_non_json_body_falls_back_to_utf8_decoded_string(self):
        # Defensive: malformed error bodies should not mask the
        # underlying error by raising during exception construction.
        self.assertEqual(extract_message_from_body(b"not json"), "not json")

    def test_invalid_utf8_body_returns_repr(self):
        # The function never raises. Even an undecodable body produces
        # a string we can safely include in the exception message.
        result = extract_message_from_body(b"\xff\xfe invalid utf8")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_json_body_without_message_field_falls_back_to_decoded_string(self):
        body = b'{"code":"Conflict"}'
        self.assertEqual(extract_message_from_body(body), '{"code":"Conflict"}')


class TestIsSuccessStatus(unittest.TestCase):
    """Covers the 2xx range; the rest is False."""

    def test_200_is_success(self):
        self.assertTrue(is_success_status(200))

    def test_204_is_success(self):
        # The no_response=True path returns 204; success.
        self.assertTrue(is_success_status(204))

    def test_299_is_success(self):
        self.assertTrue(is_success_status(299))

    def test_300_is_not_success(self):
        # 3xx is not currently treated as success by Cosmos
        # operations â—” pin that.
        self.assertFalse(is_success_status(300))

    def test_404_is_not_success(self):
        self.assertFalse(is_success_status(404))

    def test_500_is_not_success(self):
        self.assertFalse(is_success_status(500))


class TestBackendResponseShimDirectly(unittest.TestCase):
    """The shim is small but the public-surface contract matters."""

    def test_shim_status_code_matches_inner_response(self):
        shim = _BackendResponseShim(_make_response(status_code=200))
        self.assertEqual(shim.status_code, 200)

    def test_shim_headers_default_to_empty_dict_when_none(self):
        # BackendResponse.headers can be None when a backend never
        # populated it (test fixture). The shim must still expose a
        # headers attribute that is at least an empty mapping so
        # customer code doing ``e.response.headers.get(...)`` does
        # not raise AttributeError.
        empty = BackendResponse(status_code=409)
        shim = _BackendResponseShim(empty)
        self.assertEqual(dict(shim.headers), {})

    def test_shim_text_falls_back_on_invalid_utf8_bytes(self):
        # Customer code calls ``e.response.text()`` from inside its
        # ``except CosmosHttpResponseError`` handler. If the body
        # bytes are not valid UTF-8, raising ``UnicodeDecodeError``
        # here would mask the original Cosmos error and crash the
        # customer's exception handler. The shim must always return a
        # string.
        bad_bytes = b"\xff\xfe\xfd not valid utf-8"
        shim = _BackendResponseShim(BackendResponse(status_code=500, body=bad_bytes))
        text = shim.text()
        self.assertIsInstance(text, str)
        # The replacement-character path is what we expect; assert a
        # representative substring round-trips so the body is not lost
        # entirely.
        self.assertIn("not valid utf-8", text)

    def test_shim_text_falls_back_on_invalid_encoding_name(self):
        # An unknown encoding name (e.g. typo'd by a customer) must
        # not raise either.
        shim = _BackendResponseShim(BackendResponse(status_code=500, body=b"hello"))
        text = shim.text(encoding="not-a-real-encoding")
        self.assertIsInstance(text, str)

    def test_shim_text_returns_empty_string_when_body_is_empty(self):
        shim = _BackendResponseShim(BackendResponse(status_code=204))
        self.assertEqual(shim.text(), "")


if __name__ == "__main__":
    unittest.main()
