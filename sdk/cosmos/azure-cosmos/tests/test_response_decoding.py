# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the response-body UTF-8 decode helper and its env-var-driven
fallback behavior. Covers the healthy path (strict decode succeeds), the
default behavior when the env var is unset (strict decode fails with an
actionable hint), and the opt-in REPLACE / IGNORE modes.

The helper reads the env var per-call on the decode-failure path, so
tests just mutate ``os.environ`` (under ``mock.patch.dict``) and call
``decode_response_body`` directly — no cache reset needed.
"""
# cspell:ignore ufffd
import json
import os
import unittest
from unittest import mock

from azure.cosmos import _response_decoding


# A small payload containing one valid 2-byte UTF-8 sequence followed by a
# byte (0xC3 followed by 0x28) that is not a valid UTF-8 continuation byte.
# `\xC3\x28` is the textbook example of an invalid UTF-8 sequence.
_INVALID_UTF8 = b'{"note":"hello \xc3\x28 world"}'
_VALID_UTF8 = b'{"note":"hello world"}'

_MALFORMED_INPUT_ENV_VAR = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"


class _DecoderEnvIsolatedTestCase(unittest.TestCase):
    """Base class that isolates each test from the surrounding process
    environment by rolling back any env mutations the test makes."""

    def setUp(self):
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        # Strip the env var for the duration of the test so the helper's
        # default behavior (no env -> strict) is the explicit baseline.
        # Tests that need a specific env value set it themselves.
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def tearDown(self):
        # `mock.patch.dict` rolls back any env mutations the test made,
        # including the pop in setUp.
        self._env_patch.stop()


class TestStrictDecodingHealthyPath(_DecoderEnvIsolatedTestCase):

    def test_valid_utf8_decodes_unchanged(self):
        """The healthy path must produce exactly the same string as
        ``bytes.decode('utf-8')``. This is the regression guard for
        the 99.99% case where the body is well-formed."""
        result = _response_decoding.decode_response_body(_VALID_UTF8)
        self.assertEqual(result, '{"note":"hello world"}')

    def test_empty_bytes_decodes_to_empty_string(self):
        self.assertEqual(_response_decoding.decode_response_body(b""), "")


class TestStrictDecodingRaisesActionableError(_DecoderEnvIsolatedTestCase):

    def test_invalid_utf8_without_env_var_raises_with_hint(self):
        """When the env var is unset (the historical default) the helper
        must raise ``UnicodeDecodeError`` so existing call sites continue
        to behave the same way. The hint in ``reason`` points the
        operator at the env var name so they can self-serve."""
        # setUp already cleared the env var; assert it for the reader.
        self.assertNotIn(_MALFORMED_INPUT_ENV_VAR, os.environ)

        with self.assertRaises(UnicodeDecodeError) as ctx:
            _response_decoding.decode_response_body(_INVALID_UTF8, operation_context="read_item")

        self.assertIn(_MALFORMED_INPUT_ENV_VAR, ctx.exception.reason)
        # Original exception must be chained so callers and log readers
        # can still see the underlying decoder error.
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)


class TestPermissiveFallback(_DecoderEnvIsolatedTestCase):
    """Exercises the decode behavior in each fallback mode by setting
    the env var and calling ``decode_response_body`` directly."""

    def test_replace_mode_substitutes_replacement_character(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # The bad byte is replaced by U+FFFD; the surrounding text is preserved.
        self.assertIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)

    def test_ignore_mode_drops_bad_bytes(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # No replacement character; the bad byte is silently dropped.
        self.assertNotIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)


class TestEnvVarParser(_DecoderEnvIsolatedTestCase):
    """Unit tests for ``_resolve_fallback_mode_from_env`` in isolation.
    Each test sets the env var and asserts the parsed mode matches the
    documented mapping."""

    def test_replace_env_value_resolves_to_replace_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

    def test_ignore_env_value_resolves_to_ignore_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "ignore")

    def test_unknown_env_value_resolves_to_strict(self):
        """Anything other than REPLACE / IGNORE (case-insensitive) must
        leave strict decoding in effect."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "BOGUS"
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_env_value_is_case_insensitive_and_trims_whitespace(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "  replace  "
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

    def test_unset_env_resolves_to_strict(self):
        # setUp already pops the var; this makes the contract explicit.
        self.assertNotIn(_MALFORMED_INPUT_ENV_VAR, os.environ)
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())


class TestEnvVarToBehaviorEndToEnd(_DecoderEnvIsolatedTestCase):
    """Verifies the full contract: setting the env var actually changes
    what ``decode_response_body`` does, and clearing it returns to
    strict. Catches regressions where the env parser and the per-call
    read drift apart."""

    def test_setting_replace_env_var_makes_invalid_utf8_decode_succeed(self):
        # Baseline: with no env var, the same input raises.
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)

        # Opt in via the env var and prove the same input now decodes to
        # a replacement-character-bearing string instead of raising.
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        self.assertIn("\ufffd", result)

    def test_clearing_env_var_returns_to_strict(self):
        # Opt in.
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

        # Opt out by removing the var; next decode raises again.
        del os.environ[_MALFORMED_INPUT_ENV_VAR]
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)


class TestDecodeForStatus(_DecoderEnvIsolatedTestCase):
    """Tests ``decode_response_body_for_status`` — the wrapper that
    HTTP request paths use so a malformed-UTF-8 error body does not
    mask the real status-code exception. The SDK's retry/refresh logic
    and customer error handlers branch on status code, so a 404, 410
    (partition split), 429 (throttle), or 503 must surface as the
    correct typed exception even when the body has invalid bytes."""

    def test_valid_utf8_success_passes_through(self):
        """Healthy path: 2xx with well-formed body decodes normally."""
        result = _response_decoding.decode_response_body_for_status(
            _VALID_UTF8, status_code=200
        )
        self.assertEqual(result, '{"note":"hello world"}')

    def test_invalid_utf8_on_2xx_still_raises(self):
        """A successful response with malformed bytes is a data-integrity
        problem the caller needs to see — do not silently paper over it."""
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body_for_status(
                _INVALID_UTF8, status_code=200
            )

    def test_invalid_utf8_on_404_does_not_raise(self):
        """404 with malformed body must decode best-effort so callers
        receive ``CosmosResourceNotFoundError`` instead of a confusing
        ``UnicodeDecodeError``."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=404
        )
        # The bad byte is replaced; surrounding text is preserved so the
        # error message remains human-readable.
        self.assertIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)

    def test_invalid_utf8_on_throttle_does_not_raise(self):
        """429 carries the retry-after signal the SDK's throttle handler
        depends on; it must not be masked by a decode error."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=429
        )
        self.assertIn("\ufffd", result)

    def test_invalid_utf8_on_partition_gone_does_not_raise(self):
        """410 is the partition-split signal that triggers partition-map
        refresh; masking it would break split recovery."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=410
        )
        self.assertIn("\ufffd", result)

    def test_invalid_utf8_on_service_unavailable_does_not_raise(self):
        """503 drives cross-region retry; masking it makes the SDK give
        up instead of failing over."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=503
        )
        self.assertIn("\ufffd", result)

    def test_boundary_399_still_raises(self):
        """The wrapper opens up best-effort decode at exactly 400 and
        above. 399 (unused in HTTP today, but covers 3xx redirects)
        must still raise — same reason as 2xx."""
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body_for_status(
                _INVALID_UTF8, status_code=399
            )

    def test_boundary_400_does_not_raise(self):
        """Confirms the threshold is inclusive at 400 (Bad Request)."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=400
        )
        self.assertIn("\ufffd", result)

    def test_empty_body_decodes_to_empty_string_regardless_of_status(self):
        for status in (200, 404, 503):
            self.assertEqual(
                _response_decoding.decode_response_body_for_status(b"", status_code=status),
                "",
            )

    def test_fallback_env_var_handles_2xx_before_status_check_kicks_in(self):
        """When the operator has opted in via the env var, the inner
        ``decode_response_body`` already succeeds (with replacement), so
        a 2xx with malformed bytes also decodes successfully. The
        wrapper's status-code branch never runs in that case."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=200
        )
        self.assertIn("\ufffd", result)


class TestPermissiveFallbackJsonPipeline(_DecoderEnvIsolatedTestCase):
    """End-to-end tests covering the decode-then-``json.loads`` pipeline
    every caller of ``decode_response_body`` runs.

    These tests document an important operator-facing trade-off of
    enabling permissive fallback (``REPLACE``): malformed bytes inside
    a JSON *string value* become silently-corrupted Python str values
    after parsing (``"\\ufffd"`` ends up in the data), while malformed
    bytes that land on JSON *structural* characters cause the parse
    step to fail with ``json.JSONDecodeError`` — which the SDK's
    request path catches and surfaces as a typed ``DecodeError``.

    Assertions are intentionally outcome-shaped (does parse succeed?
    does the value contain U+FFFD?) and avoid asserting exact error
    messages or byte offsets, so CPython upgrades do not break us.
    Mirrors the coverage in the Java SDK's MalformedResponseTests."""

    # Bad bytes (`\xc3\x28`) inside the JSON string value `"caf??"`.
    # After REPLACE decode the body is well-formed JSON whose value
    # happens to contain U+FFFD — json.loads succeeds.
    _BAD_BYTES_IN_STRING_VALUE = b'{"name":"caf\xc3\x28 dining"}'

    # Bad bytes (`\xc3\x28`) placed where the JSON colon delimiter
    # should be. After REPLACE decode the colon position contains
    # U+FFFD instead — json.loads cannot parse this as an object.
    _BAD_BYTES_IN_STRUCTURE = b'{"name"\xc3\x28"value"}'

    def test_replace_mode_corrupts_string_values_silently(self):
        """REPLACE + parse on bad bytes inside a string value: parse
        succeeds, the resulting Python str contains U+FFFD. This is
        the case operators need to be aware of when enabling REPLACE
        — application code receives data with substituted characters
        and no signal that the substitution happened.

        Cross-SDK parity note: matches the Java
        MalformedResponseTests scenario where a corrupted character
        inside a JSON string is silently preserved through parsing."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        decoded = _response_decoding.decode_response_body(self._BAD_BYTES_IN_STRING_VALUE)
        parsed = json.loads(decoded)

        self.assertIsInstance(parsed, dict)
        self.assertIn("name", parsed)
        self.assertIsInstance(parsed["name"], str)
        # The replacement character is present in the parsed value;
        # the rest of the value text is preserved verbatim.
        self.assertIn("\ufffd", parsed["name"])
        self.assertIn("caf", parsed["name"])
        self.assertIn("dining", parsed["name"])

    def test_replace_mode_structural_corruption_raises_json_decode_error(self):
        """REPLACE + parse on bad bytes in JSON structure: decode
        succeeds, parse raises ``json.JSONDecodeError``. The SDK's
        ``_Request`` path catches that and surfaces it as
        ``azure.core.exceptions.DecodeError`` (covered by the
        ``_Request`` wiring tests). Here we just lock in the seam:
        decode produces a string, parse rejects it."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        decoded = _response_decoding.decode_response_body(self._BAD_BYTES_IN_STRUCTURE)
        # Decode itself does not raise — the byte that broke JSON
        # structure has become U+FFFD in the decoded string.
        self.assertIsInstance(decoded, str)
        self.assertIn("\ufffd", decoded)

        with self.assertRaises(json.JSONDecodeError):
            json.loads(decoded)


if __name__ == "__main__":
    unittest.main()
