# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for opt-in compact UTF-8 serialization of item write bodies."""
# cspell:ignore d83d de00 udfff

import json
import unittest
from unittest import mock

import pytest

from azure.cosmos import (
    _base,
    _global_endpoint_manager,
    _synchronized_request,
    cosmos_client,
    documents,
    http_constants,
)

from azure.cosmos.aio import _asynchronous_request, _cosmos_client
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders


class _DummyRequestParams:
    """Stand-in for RequestObject carrying only the fields the body
    serialization decision reads: resource type and operation type."""

    def __init__(
        self,
        resource_type=http_constants.ResourceType.Document,
        operation_type=_OperationType.Create,
    ):
        self.availability_strategy = None
        self.is_hedging_request = False
        self.resource_type = resource_type
        self.operation_type = operation_type
        self.retry_write = 0


class _DummyGlobalEndpointManager:
    """Endpoint manager stub that reports hedging as disabled, so requests
    take the plain (non-hedged) path through to the mocked executor."""

    @staticmethod
    def is_per_partition_automatic_failover_enabled():
        return False


class _DummyRequest:
    """Minimal HttpRequest stand-in capturing just the body and headers."""

    def __init__(self):
        self.headers = {}
        self.data = None


class _DummyClient:
    """Client stub exposing only the opt-in flag the serializer checks."""

    def __init__(self, enable_compact_utf8_item_writes):
        self._enable_compact_utf8_item_writes = enable_compact_utf8_item_writes


class _DummyHeaderClient:
    """Client stub with the attributes GetHeaders needs to build headers
    without a real connection."""

    UseMultipleWriteLocations = False
    master_key = None
    resource_tokens = None
    client_id = None

    class connection_policy:
        ResponsePayloadOnWriteDisabled = False


class _EncodingCountingStr(str):
    """A str that counts how many times .encode() is called on it.

    Used to prove the body is encoded to UTF-8 exactly once per request:
    the serializer keeps the bytes it already produced and reuses their
    length for Content-Length, rather than encoding the body a second time.
    """

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance.encode_calls = 0
        return instance

    def encode(self, encoding="utf-8", errors="strict"):
        self.encode_calls += 1
        return super().encode(encoding, errors)


def _compact_text(body):
    """Decode a compact request body for text assertions.

    Compact UTF-8 bodies are handed to the transport as ``bytes`` (never
    ``str``) so no transport layer can re-encode them: urllib3 1.x routes
    ``str`` bodies through ``http.client``, which Latin-1 encodes them. Asserting
    the type here means a regression back to ``str`` fails loudly rather than
    silently reintroducing that bug.
    """
    assert isinstance(body, bytes), f"compact body must be bytes, got {type(body).__name__}"
    return body.decode("utf-8")


def _capture_sync_body(
    request_data,
    *,
    enable_compact_utf8_item_writes,
    resource_type,
    operation_type,
):
    """Run one request through the sync path with the retry executor mocked
    out, and return the body and Content-Length that would have been sent."""
    request = _DummyRequest()
    captured = {}

    def _fake_execute(*args, **kwargs):
        request_arg = args[6]
        captured["body"] = request_arg.data
        captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
        return {}, {}

    with mock.patch.object(
        _synchronized_request._retry_utility,
        "Execute",
        side_effect=_fake_execute,
    ):
        _synchronized_request.SynchronizedRequest(
            client=_DummyClient(enable_compact_utf8_item_writes),
            request_params=_DummyRequestParams(resource_type, operation_type),
            global_endpoint_manager=_DummyGlobalEndpointManager(),
            connection_policy=object(),
            pipeline_client=object(),
            request=request,
            request_data=request_data,
        )
    return captured


async def _capture_async_body(
    request_data,
    *,
    enable_compact_utf8_item_writes,
    resource_type,
    operation_type,
):
    """Async twin of _capture_sync_body. Same capture, async pipeline."""
    request = _DummyRequest()
    captured = {}

    async def _fake_execute(*args, **kwargs):
        request_arg = args[6]
        captured["body"] = request_arg.data
        captured["content_length"] = request_arg.headers.get(HttpHeaders.ContentLength)
        return {}, {}

    with mock.patch.object(
        _asynchronous_request._retry_utility_async,
        "ExecuteAsync",
        side_effect=_fake_execute,
    ):
        await _asynchronous_request.AsynchronousRequest(
            client=_DummyClient(enable_compact_utf8_item_writes),
            request_params=_DummyRequestParams(resource_type, operation_type),
            global_endpoint_manager=_DummyGlobalEndpointManager(),
            connection_policy=object(),
            pipeline_client=object(),
            request=request,
            request_data=request_data,
        )
    return captured


def _capture_sync_query_builder(query):
    """Build a real sync QueryFeed request and capture its serialized body."""
    # Bypass __init__ because it builds the full connection infrastructure and
    # performs account discovery. These assignments are the minimal QueryFeed
    # fixture; add an attribute here if QueryFeed gains another dependency.
    connection = object.__new__(cosmos_client.CosmosClientConnection)
    connection.default_headers = {}
    connection.last_response_headers = {}
    connection._query_compatibility_mode = (
        cosmos_client.CosmosClientConnection._QueryCompatibilityMode.Default
    )
    connection.availability_strategy = None
    connection.availability_strategy_executor = None
    connection._global_endpoint_manager = _DummyGlobalEndpointManager()
    connection.connection_policy = object()
    connection.pipeline_client = mock.Mock()
    connection.pipeline_client.post.return_value = _DummyRequest()
    connection._enable_compact_utf8_item_writes = True
    connection._UpdateSessionIfRequired = mock.Mock()
    captured = {}

    def _fake_execute(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        _client,
        _global_endpoint_manager,
        _request_function,
        request_params,
        _connection_policy,
        _pipeline_client,
        request,
        **_kwargs,
    ):
        captured["resource_type"] = request_params.resource_type
        captured["operation_type"] = request_params.operation_type
        captured["body"] = request.data
        captured["content_length"] = request.headers.get(HttpHeaders.ContentLength)
        return {"Documents": []}, {}

    with (
        mock.patch.object(_base, "GetHeaders", return_value={}),
        mock.patch.object(_base, "set_session_token_header"),
        mock.patch.object(
            _synchronized_request._retry_utility,
            "Execute",
            side_effect=_fake_execute,
        ),
    ):
        connection.QueryFeed(
            "dbs/db/colls/container/docs",
            "container-rid",
            query,
            {},
        )
    return captured


async def _capture_async_query_builder(query):
    """Build a real async QueryFeed request and capture its serialized body."""
    # Bypass __init__ because it builds the full async connection infrastructure.
    # These assignments are the minimal QueryFeed fixture; add an attribute here
    # if QueryFeed gains another dependency.
    connection = object.__new__(_cosmos_client.CosmosClientConnection)
    connection.default_headers = {}
    connection.last_response_headers = {}
    connection._query_compatibility_mode = (
        _cosmos_client.CosmosClientConnection._QueryCompatibilityMode.Default
    )
    connection.availability_strategy = None
    connection.availability_strategy_max_concurrency = None
    connection._global_endpoint_manager = _DummyGlobalEndpointManager()
    connection.connection_policy = object()
    connection.pipeline_client = mock.Mock()
    connection.pipeline_client.post.return_value = _DummyRequest()
    connection._enable_compact_utf8_item_writes = True
    connection._UpdateSessionIfRequired = mock.Mock()
    captured = {}

    async def _fake_execute(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        _client,
        _global_endpoint_manager,
        _request_function,
        request_params,
        _connection_policy,
        _pipeline_client,
        request,
        **_kwargs,
    ):
        captured["resource_type"] = request_params.resource_type
        captured["operation_type"] = request_params.operation_type
        captured["body"] = request.data
        captured["content_length"] = request.headers.get(HttpHeaders.ContentLength)
        return {"Documents": []}, {}

    with (
        mock.patch.object(_base, "GetHeaders", return_value={}),
        mock.patch.object(_base, "set_session_token_header_async"),
        mock.patch.object(
            _asynchronous_request._retry_utility_async,
            "ExecuteAsync",
            side_effect=_fake_execute,
        ),
    ):
        await connection.QueryFeed(
            "dbs/db/colls/container/docs",
            "container-rid",
            query,
            {},
        )
    return captured


# These tests need no emulator, but the Cosmos CI lane selects tests with
# "-m cosmosEmulator" (see eng/pipelines/templates/stages/cosmos-sdk-client.yml),
# so an unmarked test is silently deselected and would never run.
@pytest.mark.cosmosEmulator
class TestItemBodySerialization(unittest.TestCase):
    """Sync path: how item write bodies are serialized on and off the option."""

    def test_default_serialization_remains_ascii_escaped(self):
        """With the option off (the default), bodies keep the historical
        \\uXXXX-escaped form, so existing customers see no change on the wire."""
        data = {"text": "café 日本 🎉"}

        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=False,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )

        self.assertEqual(captured["body"], json.dumps(data, separators=(",", ":")))
        self.assertNotIn("日本", captured["body"])

    def test_enabled_item_write_operations_use_compact_utf8(self):
        """With the option on, every operation the feature is scoped to
        (create, upsert, replace, patch) sends unescaped UTF-8, and
        Content-Length matches the body's real byte count."""
        data = {"text": "café 日本 🎉"}
        expected = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        for operation_type in (
            _OperationType.Create,
            _OperationType.Upsert,
            _OperationType.Replace,
            _OperationType.Patch,
        ):
            with self.subTest(operation_type=operation_type):
                captured = _capture_sync_body(
                    data,
                    enable_compact_utf8_item_writes=True,
                    resource_type=http_constants.ResourceType.Document,
                    operation_type=operation_type,
                )
                self.assertEqual(captured["body"], expected.encode("utf-8"))
                self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    def test_batch_wire_shape_is_what_the_detector_keys_off(self):
        """Pin the service's batch wire contract independently of the SDK.

        _batch_contains_item_body decides on the presence of a resourceBody
        key. The formatter-driven tests below would still pass if the
        formatter and the detector were renamed together, so hard-code the
        shape the service actually expects here: write operations carry a
        resourceBody, read and delete carry only an id."""
        item = {"id": "item-日本", "text": "ไทย 🎉"}
        with_body = _base._format_batch_operations([
            ("create", (item,)),
            ("upsert", (item,)),
            ("replace", ("item-日本", item)),
            ("patch", ("item-日本", [{"op": "add", "path": "/text", "value": "ไทย"}])),
        ])
        without_body = _base._format_batch_operations([
            ("read", ("item-日本",)),
            ("delete", ("item-日本",)),
        ])

        for operation in with_body:
            with self.subTest(operation=operation["operationType"]):
                self.assertIn("resourceBody", operation)
        for operation in without_body:
            with self.subTest(operation=operation["operationType"]):
                self.assertNotIn("resourceBody", operation)
                self.assertIn("id", operation)

    def test_body_free_batches_remain_ascii_escaped(self):
        """Read and delete operations both carry only an id, so any batch made
        up solely of them has no item body and must keep the escaped form."""
        body_free_batches = (
            [("read", ("item-日本",)), ("read", ("item-ไทย",))],
            [("delete", ("item-日本",)), ("delete", ("item-ไทย",))],
            [("read", ("item-日本",)), ("delete", ("item-ไทย",))],
            [],
        )

        for batch in body_free_batches:
            with self.subTest(batch=batch):
                data = _base._format_batch_operations(batch)
                captured = _capture_sync_body(
                    data,
                    enable_compact_utf8_item_writes=True,
                    resource_type=http_constants.ResourceType.Document,
                    operation_type=_OperationType.Batch,
                )
                self.assertEqual(captured["body"], json.dumps(data, separators=(",", ":")))
                self.assertNotIn("日本", captured["body"])

    def test_batches_built_by_the_sdk_are_detected_as_item_writes(self):
        """Drive the real batch formatter rather than a hand-written payload,
        so renaming the resourceBody key can never silently disable compact
        UTF-8 while these tests still pass. Patch is included because its body
        is nested one level deeper than the others."""
        item = {"id": "item-日本", "text": "ไทย 🎉"}
        write_batches = (
            [("create", (item,))],
            [("upsert", (item,))],
            [("replace", ("item-日本", item))],
            [("patch", ("item-日本", [{"op": "add", "path": "/text", "value": "ไทย"}]))],
            [("read", ("item-日本",)), ("create", (item,))],
        )

        for batch in write_batches:
            with self.subTest(batch=batch[0][0]):
                data = _base._format_batch_operations(batch)
                self.assertTrue(_synchronized_request._batch_contains_item_body(data))

                captured = _capture_sync_body(
                    data,
                    enable_compact_utf8_item_writes=True,
                    resource_type=http_constants.ResourceType.Document,
                    operation_type=_OperationType.Batch,
                )
                expected = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
                self.assertEqual(captured["body"], expected.encode("utf-8"))
                self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    def test_compact_body_reuses_encoded_byte_length(self):
        """The body is encoded to UTF-8 exactly once. Guards the memory fix:
        the Content-Length header reuses the bytes already produced during
        serialization instead of re-encoding the whole body a second time."""
        serialized = _EncodingCountingStr('{"text":"日本"}')

        with mock.patch.object(_synchronized_request.json, "dumps", return_value=serialized):
            captured = _capture_sync_body(
                {"text": "日本"},
                enable_compact_utf8_item_writes=True,
                resource_type=http_constants.ResourceType.Document,
                operation_type=_OperationType.Create,
            )

        self.assertEqual(serialized.encode_calls, 1)
        self.assertEqual(captured["content_length"], len('{"text":"日本"}'.encode("utf-8")))

    def test_enabled_option_does_not_change_other_request_bodies(self):
        """The option is scoped to item writes only. Control-plane bodies
        (databases, containers, users, permissions, sprocs, triggers, UDFs)
        and document queries all stay ASCII-escaped even when it is on."""
        data = {"text": "日本"}
        expected = json.dumps(data, separators=(",", ":"))
        unaffected_requests = (
            (http_constants.ResourceType.Database, _OperationType.Create),
            (http_constants.ResourceType.Collection, _OperationType.Replace),
            (http_constants.ResourceType.User, _OperationType.Upsert),
            (http_constants.ResourceType.Permission, _OperationType.Create),
            (http_constants.ResourceType.StoredProcedure, _OperationType.Create),
            (http_constants.ResourceType.StoredProcedure, _OperationType.ExecuteJavaScript),
            (http_constants.ResourceType.Trigger, _OperationType.Create),
            (http_constants.ResourceType.UserDefinedFunction, _OperationType.Create),
            (http_constants.ResourceType.Document, _OperationType.SqlQuery),
        )

        for resource_type, operation_type in unaffected_requests:
            with self.subTest(resource_type=resource_type, operation_type=operation_type):
                captured = _capture_sync_body(
                    data,
                    enable_compact_utf8_item_writes=True,
                    resource_type=resource_type,
                    operation_type=operation_type,
                )
                self.assertEqual(captured["body"], expected)

    def test_query_builder_keeps_non_ascii_parameters_escaped(self):
        """The real QueryFeed builder uses SqlQuery metadata and keeps query
        parameters on the historical escaped-string serialization path."""
        data = {
            "query": "SELECT * FROM c WHERE c.name = @name",
            "parameters": [{"name": "@name", "value": "日本"}],
        }
        expected = json.dumps(data, separators=(",", ":"))

        captured = _capture_sync_query_builder(data)

        self.assertEqual(captured["resource_type"], http_constants.ResourceType.Document)
        self.assertEqual(captured["operation_type"], _OperationType.SqlQuery)
        self.assertEqual(captured["body"], expected)
        self.assertNotIn("日本", captured["body"])
        self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    def test_pre_serialized_string_is_unchanged(self):
        """A body the caller already serialized to a str is passed through
        untouched. The SDK never re-parses or rewrites it."""
        data = '{"text":"\\u65e5\\u672c"}'

        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )

        self.assertEqual(captured["body"], data)

    def test_surrogate_pairs_are_compact_and_lone_surrogates_are_escaped(self):
        """Adjacent surrogate pairs become compact scalars while unpaired
        surrogates remain valid JSON escapes."""
        data = {
            "paired": "\ud83d\ude00",
            "lone_high": "\ud800",
            "lone_low": "\udfff",
            "mixed": "before\ud800\ud83d\ude00\udfffafter",
            "reverse_lone": "\udfff\ud800",
            "literal_escape": "\\ud83d\\ude00",
            "key\ud800": "value",
            "key\ud83d\ude00": "paired key",
            "emoji": "🎉",
        }
        expected = {
            "paired": "😀",
            "lone_high": "\ud800",
            "lone_low": "\udfff",
            "mixed": "before\ud800😀\udfffafter",
            "reverse_lone": "\udfff\ud800",
            "literal_escape": "\\ud83d\\ude00",
            "key\ud800": "value",
            "key😀": "paired key",
            "emoji": "🎉",
        }
        expected_body = json.dumps(
            expected,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8", "backslashreplace")

        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )
        body = _compact_text(captured["body"])

        self.assertIn("\\ud800", body)
        self.assertIn("\\udfff", body)
        self.assertIn("😀", body)
        self.assertIn("🎉", body)
        self.assertEqual(captured["body"], expected_body)
        self.assertEqual(json.loads(body), expected)
        self.assertEqual(captured["content_length"], len(captured["body"]))

    def test_json_required_escapes_are_preserved(self):
        """Turning off ASCII escaping must not turn off JSON escaping. Quotes,
        backslashes, newlines, tabs, and NUL stay escaped; U+2028/U+2029 are
        emitted literally, which is valid JSON."""
        data = {"text": "\"\\\n\t\x00", "line_separators": "\u2028\u2029"}

        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )
        body = _compact_text(captured["body"])

        self.assertIn('\\"', body)
        self.assertIn("\\\\", body)
        self.assertIn("\\n", body)
        self.assertIn("\\t", body)
        self.assertIn("\\u0000", body)
        self.assertIn("\u2028\u2029", body)
        self.assertEqual(json.loads(body), data)

    def test_large_cjk_item_stays_below_two_mib(self):
        """The point of the feature: a CJK document that exceeds the 2 MB item
        limit when \\uXXXX-escaped fits under it as compact UTF-8."""
        data = {"text": "日" * 400000}

        escaped = json.dumps(data, separators=(",", ":")).encode("utf-8")
        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )
        compact = captured["body"]
        self.assertIsInstance(compact, bytes)

        self.assertGreater(len(escaped), 2 * 1024 * 1024)
        self.assertLess(len(compact), 2 * 1024 * 1024)
        self.assertEqual(captured["content_length"], len(compact))

    def test_large_surrogate_pair_item_stays_below_two_mib(self):
        """UTF-16-derived supplementary characters are compacted rather than
        remaining as 12-byte surrogate-pair escapes."""
        data = {"text": "\ud83d\ude00" * 175000}
        escaped = json.dumps(data, separators=(",", ":")).encode("utf-8")
        expected = json.dumps(
            {"text": "😀" * 175000},
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        captured = _capture_sync_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )

        self.assertGreater(len(escaped), 2 * 1024 * 1024)
        self.assertLess(len(captured["body"]), 2 * 1024 * 1024)
        self.assertEqual(captured["body"], expected)
        self.assertEqual(captured["content_length"], len(expected))

    def test_partition_key_header_remains_ascii_escaped(self):
        """The partition key header is unaffected by the option and stays
        ASCII-escaped, since headers are not UTF-8 safe in transit."""
        headers = _base.GetHeaders(
            _DummyHeaderClient(),
            {},
            "post",
            "dbs/db/colls/container/docs",
            "item",
            http_constants.ResourceType.Document,
            _OperationType.Create,
            {"partitionKey": "日本"},
        )

        self.assertEqual(headers[HttpHeaders.PartitionKey], '["\\u65e5\\u672c"]')


@pytest.mark.cosmosEmulator
class TestItemBodySerializationAsync(unittest.IsolatedAsyncioTestCase):
    """Async path: mirrors the sync coverage so both stacks stay in step."""

    async def test_default_item_write_remains_ascii_escaped(self):
        """Async default is escaped, same as sync, with a byte-accurate
        Content-Length."""
        data = {"text": "café 日本 🎉"}
        expected = json.dumps(data, separators=(",", ":"))

        captured = await _capture_async_body(
            data,
            enable_compact_utf8_item_writes=False,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )

        self.assertEqual(captured["body"], expected)
        self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    async def test_enabled_item_write_uses_compact_utf8(self):
        """Async opt-in sends compact UTF-8 with a byte-accurate
        Content-Length."""
        data = {"text": "café 日本 🎉"}
        expected = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        captured = await _capture_async_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Upsert,
        )

        self.assertEqual(captured["body"], expected.encode("utf-8"))
        self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    async def test_write_containing_batch_uses_compact_utf8(self):
        """Async mixed batches use compact UTF-8 when one operation contains
        an item body. The read operation's id is compact too, since the whole
        batch body is serialized in one pass."""
        data = _base._format_batch_operations([
            ("read", ("existing-日本",)),
            ("create", ({"id": "new-日本", "text": "ไทย 🎉"},)),
        ])
        expected = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        captured = await _capture_async_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Batch,
        )

        self.assertEqual(captured["body"], expected.encode("utf-8"))
        self.assertIn("existing-日本", _compact_text(captured["body"]))
        self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))

    async def test_body_free_batches_remain_ascii_escaped(self):
        """Async twin: read-only, delete-only, and mixed read/delete batches
        all lack an item body and stay escaped."""
        body_free_batches = (
            [("read", ("item-日本",)), ("read", ("item-ไทย",))],
            [("delete", ("item-日本",)), ("delete", ("item-ไทย",))],
            [("read", ("item-日本",)), ("delete", ("item-ไทย",))],
            [],
        )

        for batch in body_free_batches:
            with self.subTest(batch=batch):
                data = _base._format_batch_operations(batch)
                captured = await _capture_async_body(
                    data,
                    enable_compact_utf8_item_writes=True,
                    resource_type=http_constants.ResourceType.Document,
                    operation_type=_OperationType.Batch,
                )
                self.assertEqual(captured["body"], json.dumps(data, separators=(",", ":")))
                self.assertNotIn("日本", captured["body"])

    async def test_compact_body_reuses_encoded_byte_length(self):
        """Async twin of the single-encode check, so the memory fix is
        pinned on both stacks."""
        serialized = _EncodingCountingStr('{"text":"日本"}')

        with mock.patch.object(_synchronized_request.json, "dumps", return_value=serialized):
            captured = await _capture_async_body(
                {"text": "日本"},
                enable_compact_utf8_item_writes=True,
                resource_type=http_constants.ResourceType.Document,
                operation_type=_OperationType.Create,
            )

        self.assertEqual(serialized.encode_calls, 1)
        self.assertEqual(captured["content_length"], len('{"text":"日本"}'.encode("utf-8")))

    async def test_surrogate_pairs_are_compact_and_lone_surrogates_are_escaped(self):
        """Async twin of the mixed paired and unpaired surrogate check."""
        data = {
            "paired": "\ud83d\ude00",
            "lone_high": "\ud800",
            "lone_low": "\udfff",
            "mixed": "before\ud800\ud83d\ude00\udfffafter",
            "reverse_lone": "\udfff\ud800",
            "literal_escape": "\\ud83d\\ude00",
            "key\ud800": "value",
            "key\ud83d\ude00": "paired key",
            "emoji": "🎉",
        }
        expected = {
            "paired": "😀",
            "lone_high": "\ud800",
            "lone_low": "\udfff",
            "mixed": "before\ud800😀\udfffafter",
            "reverse_lone": "\udfff\ud800",
            "literal_escape": "\\ud83d\\ude00",
            "key\ud800": "value",
            "key😀": "paired key",
            "emoji": "🎉",
        }
        expected_body = json.dumps(
            expected,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8", "backslashreplace")

        captured = await _capture_async_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.Create,
        )
        body = _compact_text(captured["body"])

        self.assertIn("\\ud800", body)
        self.assertIn("\\udfff", body)
        self.assertIn("😀", body)
        self.assertIn("🎉", body)
        self.assertEqual(captured["body"], expected_body)
        self.assertEqual(json.loads(body), expected)
        self.assertEqual(captured["content_length"], len(captured["body"]))

    async def test_query_body_remains_ascii_escaped(self):
        """Query bodies stay escaped on the async path even with the option
        on, since queries are not item writes."""
        data = {"query": "SELECT * FROM c WHERE c.name = @name", "parameters": [{"value": "日本"}]}

        captured = await _capture_async_body(
            data,
            enable_compact_utf8_item_writes=True,
            resource_type=http_constants.ResourceType.Document,
            operation_type=_OperationType.SqlQuery,
        )

        self.assertEqual(captured["body"], json.dumps(data, separators=(",", ":")))

    async def test_query_builder_keeps_non_ascii_parameters_escaped(self):
        """The real async QueryFeed builder uses SqlQuery metadata and keeps
        query parameters on the historical escaped-string serialization path."""
        data = {
            "query": "SELECT * FROM c WHERE c.name = @name",
            "parameters": [{"name": "@name", "value": "日本"}],
        }
        expected = json.dumps(data, separators=(",", ":"))

        captured = await _capture_async_query_builder(data)

        self.assertEqual(captured["resource_type"], http_constants.ResourceType.Document)
        self.assertEqual(captured["operation_type"], _OperationType.SqlQuery)
        self.assertEqual(captured["body"], expected)
        self.assertNotIn("日本", captured["body"])
        self.assertEqual(captured["content_length"], len(expected.encode("utf-8")))


@pytest.mark.cosmosEmulator
class TestClientOptionWiring(unittest.IsolatedAsyncioTestCase):
    """How the keyword travels from the client constructor to the serializer,
    and how bad values are rejected."""

    def test_sync_client_consumes_and_forwards_option(self):
        """The keyword is forwarded to the client connection and is not leaked
        into the connection policy kwargs, where it would be an unknown option."""
        with (
            mock.patch.object(
                cosmos_client,
                "_build_connection_policy",
                return_value=object(),
            ) as build_policy,
            mock.patch.object(cosmos_client, "CosmosClientConnection") as connection,
        ):
            cosmos_client.CosmosClient(
                "https://example.test",
                "credential",
                enable_compact_utf8_item_writes=True,
            )

        self.assertNotIn(
            "enable_compact_utf8_item_writes",
            build_policy.call_args.args[0],
        )
        self.assertTrue(connection.call_args.kwargs["enable_compact_utf8_item_writes"])

    def test_sync_client_rejects_non_boolean_option(self):
        """A string such as "true" is rejected with a TypeError at client
        construction rather than being silently coerced. Guards against a
        config-sourced "false" evaluating truthy and enabling the feature."""
        with self.assertRaisesRegex(
            TypeError,
            "enable_compact_utf8_item_writes must be a bool",
        ):
            cosmos_client.CosmosClient(
                "https://example.test",
                "credential",
                enable_compact_utf8_item_writes="true",
            )

    def test_sync_connection_rejects_non_boolean_option(self):
        """The same strict bool check applies at the connection layer, for
        ints, strings, and None."""
        for invalid_value in (0, "false", None):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    TypeError,
                    "enable_compact_utf8_item_writes must be a bool",
                ):
                    cosmos_client.CosmosClientConnection(
                        "https://example.test",
                        {"masterKey": "credential"},
                        enable_compact_utf8_item_writes=invalid_value,
                    )

    def test_sync_connection_string_forwards_option(self):
        """The option survives the from_connection_string entry point."""
        with mock.patch.object(cosmos_client.CosmosClient, "__init__", return_value=None) as init:
            cosmos_client.CosmosClient.from_connection_string(
                "AccountEndpoint=https://example.test;AccountKey=credential;",
                enable_compact_utf8_item_writes=True,
            )

        self.assertTrue(init.call_args.kwargs["enable_compact_utf8_item_writes"])

    def test_sync_real_client_stores_and_honors_option(self):
        """End to end on a real client object: the flag is stored and actually
        flips the serializer's decision for an item write."""
        with (
            mock.patch.object(
                _global_endpoint_manager._GlobalEndpointManager,
                "_GetDatabaseAccount",
                return_value=documents.DatabaseAccount(),
            ),
            mock.patch.object(
                _global_endpoint_manager._GlobalEndpointManager,
                "force_refresh_on_startup",
            ),
        ):
            client = cosmos_client.CosmosClient(
                "https://example.test",
                "credential",
                enable_compact_utf8_item_writes=True,
            )

        try:
            self.assertTrue(
                client.client_connection._enable_compact_utf8_item_writes
            )
            self.assertFalse(
                _synchronized_request._should_escape_non_ascii_in_request_body(
                    client.client_connection,
                    _DummyRequestParams(),
                    {"text": "日本"},
                )
            )
        finally:
            client.close()

    def test_async_client_consumes_and_forwards_option(self):
        """Async twin of the forwarding check."""
        with (
            mock.patch.object(
                _cosmos_client,
                "_build_connection_policy",
                return_value=object(),
            ) as build_policy,
            mock.patch.object(_cosmos_client, "CosmosClientConnection") as connection,
        ):
            _cosmos_client.CosmosClient(
                "https://example.test",
                "credential",
                enable_compact_utf8_item_writes=True,
            )

        self.assertNotIn(
            "enable_compact_utf8_item_writes",
            build_policy.call_args.args[0],
        )
        self.assertTrue(connection.call_args.kwargs["enable_compact_utf8_item_writes"])

    def test_async_client_rejects_non_boolean_option(self):
        """Async twin of the string-rejection check."""
        with self.assertRaisesRegex(
            TypeError,
            "enable_compact_utf8_item_writes must be a bool",
        ):
            _cosmos_client.CosmosClient(
                "https://example.test",
                "credential",
                enable_compact_utf8_item_writes="true",
            )

    def test_async_connection_rejects_non_boolean_option(self):
        """Async twin of the connection-layer validation check."""
        for invalid_value in (0, "false", None):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesRegex(
                    TypeError,
                    "enable_compact_utf8_item_writes must be a bool",
                ):
                    _cosmos_client.CosmosClientConnection(
                        "https://example.test",
                        {"masterKey": "credential"},
                        enable_compact_utf8_item_writes=invalid_value,
                    )

    def test_async_connection_string_forwards_option(self):
        """Async twin of the from_connection_string check."""
        with mock.patch.object(_cosmos_client.CosmosClient, "__init__", return_value=None) as init:
            _cosmos_client.CosmosClient.from_connection_string(
                "AccountEndpoint=https://example.test;AccountKey=credential;",
                enable_compact_utf8_item_writes=True,
            )

        self.assertTrue(init.call_args.kwargs["enable_compact_utf8_item_writes"])

    async def test_async_real_client_stores_and_honors_option(self):
        """Async twin of the end-to-end stored-and-honored check."""
        client = _cosmos_client.CosmosClient(
            "https://example.test",
            "credential",
            enable_compact_utf8_item_writes=True,
        )

        try:
            self.assertTrue(
                client.client_connection._enable_compact_utf8_item_writes
            )
            self.assertFalse(
                _synchronized_request._should_escape_non_ascii_in_request_body(
                    client.client_connection,
                    _DummyRequestParams(),
                    {"text": "日本"},
                )
            )
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()
