# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Transport-level checks for compact UTF-8 item write bodies.

These tests send requests through the real ``azure-core`` sync and async
transports to a local HTTP server and assert on the bytes that server receives.
Assertions made on ``request.data`` before it reaches a transport cannot
observe re-encoding performed by the transport itself, so the checks here are
made against the wire bytes.

Three properties are covered:

* A compact body is handed to the transport as ``bytes``, not ``str``. The
  supported dependency range still permits urllib3 1.x (``requests`` declares
  ``urllib3<3,>=1.26``), where a ``str`` body is encoded as Latin-1 by
  ``http.client`` (RFC 2616 3.7.1). Passing ``bytes`` leaves no re-encoding
  step for any transport to get wrong.
* The server receives the exact UTF-8 encoding of the body, with a
  ``Content-Length`` matching those bytes. Two payloads are used: CJK text,
  which has no Latin-1 representation, and ``é``, which has one and so would be
  sent as the single byte 0xE9 instead of the UTF-8 pair 0xC3 0xA9 without
  raising anything.
* A PATCH request carries the explicit Cosmos media type, so the body type
  cannot change the ``Content-Type`` a transport infers for it.
"""
# pylint: disable=invalid-name,missing-class-docstring,too-few-public-methods

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

# azure-core exposes the transports lazily through a module __getattr__, so
# static analysis cannot see them even though they are public API.
from azure.core.pipeline.transport import (  # pylint: disable=no-name-in-module
    AioHttpTransport,
    HttpRequest,
    RequestsTransport,
)

from azure.cosmos import _base, http_constants
from azure.cosmos._synchronized_request import _request_body_from_data
from azure.cosmos.documents import _OperationType

# One payload that cannot be represented in Latin-1 at all, and one that can be
# but encodes to different bytes than UTF-8. Written as escapes so the intent
# survives any tooling that rewrites this file with the wrong encoding.
_CJK = {"x": "\u65e5\u672c"}
_LATIN1_REPRESENTABLE = {"x": "\u00e9"}

# The exact bytes each payload must produce on the wire.
_CJK_UTF8 = b'{"x":"\xe6\x97\xa5\xe6\x9c\xac"}'
_LATIN1_REPRESENTABLE_UTF8 = b'{"x":"\xc3\xa9"}'
# What a str body would produce instead on urllib3 1.x: the same character
# written as one Latin-1 byte rather than the required UTF-8 pair.
_LATIN1_REPRESENTABLE_LATIN1 = b'{"x":"\xe9"}'


def _make_echo_handler(captured):
    """Build a request handler that records one request into ``captured``.

    :param dict captured: Mapping the handler writes the body and headers into.
    :returns: A handler class bound to the supplied mapping.
    :rtype: type
    """

    class _EchoHandler(BaseHTTPRequestHandler):
        """Records the exact request body bytes and Content-Length header."""

        def do_POST(self):  # pylint: disable=invalid-name
            """Record the request body, then answer with an empty 200."""
            length = int(self.headers.get("Content-Length") or 0)
            captured["body"] = self.rfile.read(length)
            captured["content_length"] = self.headers.get("Content-Length")
            captured["content_type"] = self.headers.get("Content-Type")
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()

        do_PATCH = do_POST  # pylint: disable=invalid-name

        def log_message(self, *args):
            """Silence the default stderr request logging."""

    return _EchoHandler


def _latin1_encode_like_http_client(text):
    """Reproduce what ``http.client._send_request`` does to a ``str`` body.

    The stdlib comment there cites RFC 2616 3.7.1 ("text default has a default
    charset of iso-8859-1") and calls ``data.encode('latin-1')``. Spelled out
    here rather than calling the private helper so this test does not depend on
    a private stdlib API.

    :param str text: The body text a transport would encode.
    :returns: The Latin-1 encoding of the text.
    :rtype: bytes
    """
    return text.encode("latin-1")


def _compact_body(document):
    """Serialize exactly the way the SDK does for a compact item write.

    :param dict document: The item body to serialize.
    :returns: The serialized body and its UTF-8 byte length.
    :rtype: tuple
    """
    return _request_body_from_data(document, ensure_ascii=False)


class _DummyHeaderClient:
    """Minimal connection object for generating Cosmos request headers."""

    UseMultipleWriteLocations = False
    master_key = None
    resource_tokens = None
    client_id = None

    class connection_policy:
        ResponsePayloadOnWriteDisabled = False


def _patch_headers(content_type=None):
    """Generate the headers used by a Cosmos item PATCH request."""
    options = {"partitionKey": "pk"}
    if content_type:
        options["contentType"] = content_type
    return _base.GetHeaders(
        _DummyHeaderClient(),
        {},
        "patch",
        "dbs/db/colls/container/docs",
        "item",
        http_constants.ResourceType.Document,
        _OperationType.Patch,
        options,
    )


class _LocalServer:
    """A localhost HTTP server that captures one request."""

    def __init__(self):
        self.captured = {}
        self._server = None
        self._thread = None

    def __enter__(self):
        """Start the server on an ephemeral port.

        :returns: This server, ready to receive one request.
        :rtype: _LocalServer
        """
        self._server = HTTPServer(("127.0.0.1", 0), _make_echo_handler(self.captured))
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc_info):
        """Shut the server down and join its thread."""
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

    @property
    def url(self):
        """Return the base URL the server is listening on.

        :returns: The server's URL.
        :rtype: str
        """
        host, port = self._server.server_address
        return f"http://{host}:{port}/"


# These tests use a local HTTP server and do not require the Cosmos emulator.
# The standard Cosmos PR CI jobs run pytest with "-m cosmosEmulator", so this
# marker is required for these transport regressions to run in PR validation.
@pytest.mark.cosmosEmulator
class TestCompactBodyReachesTransportIntact(unittest.TestCase):
    """The bytes the server receives must be the UTF-8 encoding of the body."""

    def _round_trip_sync(self, document):
        """Send one compact body through the real sync transport.

        :param dict document: The item body to send.
        :returns: The serialized body, its byte length, and what the server saw.
        :rtype: tuple
        """
        body, byte_length = _compact_body(document)
        with _LocalServer() as server:
            request = HttpRequest("POST", server.url)
            request.data = body
            request.headers["Content-Length"] = str(byte_length)
            with RequestsTransport() as transport:
                transport.send(request)
            return body, byte_length, server.captured

    def _round_trip_patch_sync(self, document, compact):
        """Send a PATCH body through the real sync transport."""
        if compact:
            body, byte_length = _compact_body(document)
        else:
            body = json.dumps(document, separators=(",", ":"))
            byte_length = len(body.encode("utf-8"))
        with _LocalServer() as server:
            request = HttpRequest("PATCH", server.url, headers=_patch_headers())
            request.data = body
            request.headers["Content-Length"] = str(byte_length)
            with RequestsTransport() as transport:
                transport.send(request)
            return server.captured

    def test_payload_constants_are_the_intended_characters(self):
        """Guard against this file being rewritten with the wrong encoding,
        which would leave the tests passing against mojibake instead of the
        characters they are meant to cover."""
        self.assertEqual(_CJK["x"].encode("utf-8"), b"\xe6\x97\xa5\xe6\x9c\xac")
        self.assertEqual(_LATIN1_REPRESENTABLE["x"].encode("utf-8"), b"\xc3\xa9")
        self.assertEqual(len(_LATIN1_REPRESENTABLE_UTF8), 10)
        self.assertEqual(len(_LATIN1_REPRESENTABLE_LATIN1), 9)

    def test_compact_body_is_bytes_not_str(self):
        """The serializer returns ``bytes`` for a compact body, for both a
        payload with no Latin-1 representation and one that has one."""
        for label, document in (("cjk", _CJK), ("latin1", _LATIN1_REPRESENTABLE)):
            with self.subTest(payload=label):
                body, _ = _compact_body(document)
                self.assertIsInstance(body, bytes)
                self.assertNotIsInstance(body, str)

    def test_str_body_would_be_latin1_encoded_by_http_client(self):
        """Latin-1 encoding of a ``str`` body either rejects the text outright
        or produces bytes that are not its UTF-8 encoding. Asserts on stdlib
        behavior rather than SDK behavior, to document what passing ``bytes``
        avoids."""
        cjk_text = json.dumps(_CJK, separators=(",", ":"), ensure_ascii=False)
        with self.assertRaises(UnicodeEncodeError):
            # CJK has no Latin-1 representation, so nothing would be sent.
            _latin1_encode_like_http_client(cjk_text)

        latin_text = json.dumps(_LATIN1_REPRESENTABLE, separators=(",", ":"), ensure_ascii=False)
        latin1_bytes = _latin1_encode_like_http_client(latin_text)

        # The character is representable in Latin-1, so this case would be sent
        # silently with the wrong encoding: 0xE9 where the service requires the
        # UTF-8 pair 0xC3 0xA9.
        self.assertEqual(latin1_bytes, _LATIN1_REPRESENTABLE_LATIN1)
        self.assertNotEqual(latin1_bytes, _LATIN1_REPRESENTABLE_UTF8)
        self.assertEqual(latin_text.encode("utf-8"), _LATIN1_REPRESENTABLE_UTF8)

    def test_cjk_body_arrives_as_utf8_over_sync_transport(self):
        """A CJK body reaches the server as UTF-8 with a matching length."""
        body, byte_length, captured = self._round_trip_sync(_CJK)

        self.assertEqual(captured["body"], body)
        self.assertEqual(captured["body"], _CJK_UTF8)
        self.assertEqual(json.loads(captured["body"].decode("utf-8")), _CJK)
        self.assertEqual(int(captured["content_length"]), len(captured["body"]))
        self.assertEqual(int(captured["content_length"]), byte_length)

    def test_latin1_representable_body_arrives_as_utf8_over_sync_transport(self):
        """This character is representable in Latin-1, so a regression to a str
        body would be sent without error but with the wrong bytes. Assert the
        exact UTF-8 encoding rather than only the length, because a Latin-1 body
        is self-consistent with its own Content-Length."""
        body, byte_length, captured = self._round_trip_sync(_LATIN1_REPRESENTABLE)

        self.assertEqual(captured["body"], body)
        self.assertEqual(captured["body"], _LATIN1_REPRESENTABLE_UTF8)
        self.assertNotEqual(captured["body"], _LATIN1_REPRESENTABLE_LATIN1)
        self.assertEqual(int(captured["content_length"]), len(captured["body"]))
        self.assertEqual(int(captured["content_length"]), byte_length)

    def test_patch_content_type_is_json_patch_for_str_and_bytes(self):
        """The explicit Cosmos media type prevents transport auto-detection
        from changing PATCH semantics when compact mode changes the body type."""
        for compact in (False, True):
            with self.subTest(compact=compact):
                captured = self._round_trip_patch_sync(_CJK, compact)
                self.assertEqual(
                    captured["content_type"],
                    "application/json-patch+json",
                )

    def test_patch_content_type_override_is_preserved(self):
        """Caller-supplied content types remain authoritative."""
        custom_content_type = "application/vnd.contoso.patch+json"
        self.assertEqual(
            _patch_headers(custom_content_type)[http_constants.HttpHeaders.ContentType],
            custom_content_type,
        )


@pytest.mark.cosmosEmulator
class TestCompactBodyReachesTransportIntactAsync(unittest.IsolatedAsyncioTestCase):
    """Async twin of the sync checks. aiohttp encodes a ``str`` body as UTF-8
    rather than Latin-1, so these assert the same wire contract to keep the two
    stacks from drifting apart."""

    async def _round_trip_async(self, document):
        """Send one compact body through the real async transport.

        :param dict document: The item body to send.
        :returns: The serialized body, its byte length, and what the server saw.
        :rtype: tuple
        """
        body, byte_length = _compact_body(document)
        with _LocalServer() as server:
            request = HttpRequest("POST", server.url)
            request.data = body
            request.headers["Content-Length"] = str(byte_length)
            async with AioHttpTransport() as transport:
                await transport.send(request)
            # The handler records the body before it answers, so the capture is
            # complete once the response has been received.
            return body, byte_length, server.captured

    async def _round_trip_patch_async(self, document, compact):
        """Send a PATCH body through the real async transport."""
        if compact:
            body, byte_length = _compact_body(document)
        else:
            body = json.dumps(document, separators=(",", ":"))
            byte_length = len(body.encode("utf-8"))
        with _LocalServer() as server:
            request = HttpRequest("PATCH", server.url, headers=_patch_headers())
            request.data = body
            request.headers["Content-Length"] = str(byte_length)
            async with AioHttpTransport() as transport:
                await transport.send(request)
            return server.captured

    async def test_cjk_body_arrives_as_utf8_over_async_transport(self):
        """Async twin of the CJK check."""
        body, byte_length, captured = await self._round_trip_async(_CJK)

        self.assertEqual(captured["body"], body)
        self.assertEqual(captured["body"], _CJK_UTF8)
        self.assertEqual(int(captured["content_length"]), len(captured["body"]))
        self.assertEqual(int(captured["content_length"]), byte_length)

    async def test_latin1_representable_body_arrives_as_utf8_over_async_transport(self):
        """Async twin of the Latin-1-representable check, asserting exact UTF-8."""
        body, byte_length, captured = await self._round_trip_async(_LATIN1_REPRESENTABLE)

        self.assertEqual(captured["body"], body)
        self.assertEqual(captured["body"], _LATIN1_REPRESENTABLE_UTF8)
        self.assertNotEqual(captured["body"], _LATIN1_REPRESENTABLE_LATIN1)
        self.assertEqual(int(captured["content_length"]), len(captured["body"]))
        self.assertEqual(int(captured["content_length"]), byte_length)

    async def test_patch_content_type_is_json_patch_for_str_and_bytes(self):
        """Async transport sees the same explicit media type in both modes."""
        for compact in (False, True):
            with self.subTest(compact=compact):
                captured = await self._round_trip_patch_async(_CJK, compact)
                self.assertEqual(
                    captured["content_type"],
                    "application/json-patch+json",
                )


if __name__ == "__main__":
    unittest.main()
