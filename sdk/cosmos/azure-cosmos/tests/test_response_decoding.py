# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the response-body UTF-8 decode helper. Covers the default
behavior, the opt-in REPLACE / IGNORE modes, and how the env var that
controls them is parsed."""
# cspell:ignore ufffd
import json
import os
import unittest
from unittest import mock

from azure.cosmos import _response_decoding


# Small payload with an invalid byte sequence: 0xC3 marks the start of
# a two-byte UTF-8 character, but the next byte (0x28) is not a valid
# continuation byte, so this can't be decoded as UTF-8.
_INVALID_UTF8 = b'{"note":"hello \xc3\x28 world"}'
_VALID_UTF8 = b'{"note":"hello world"}'

_MALFORMED_INPUT_ENV_VAR = "AZURE_COSMOS_CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"


class _DecoderEnvIsolatedTestCase(unittest.TestCase):
    """Saves and restores the env var so tests don't leak settings."""

    def setUp(self):
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        # Clear the env var so each test starts from the default state.
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)

    def tearDown(self):
        self._env_patch.stop()


class TestStrictDecodingHealthyPath(_DecoderEnvIsolatedTestCase):

    def test_valid_utf8_decodes_unchanged(self):
        """A well-formed payload decodes to the same string as a plain
        UTF-8 decode would."""
        result = _response_decoding.decode_response_body(_VALID_UTF8)
        self.assertEqual(result, '{"note":"hello world"}')

    def test_empty_bytes_decodes_to_empty_string(self):
        self.assertEqual(_response_decoding.decode_response_body(b""), "")


class TestStrictDecodingRaisesActionableError(_DecoderEnvIsolatedTestCase):

    def test_invalid_utf8_without_env_var_raises_with_hint(self):
        """With the env var unset, invalid bytes raise. The error
        message mentions the env var so users know how to opt in."""
        self.assertNotIn(_MALFORMED_INPUT_ENV_VAR, os.environ)

        with self.assertRaises(UnicodeDecodeError) as ctx:
            _response_decoding.decode_response_body(_INVALID_UTF8, operation_context="read_item")

        self.assertIn(_MALFORMED_INPUT_ENV_VAR, ctx.exception.reason)
        # The original error stays chained so callers can still see it.
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)


class TestPermissiveFallback(_DecoderEnvIsolatedTestCase):
    """Checks decode behavior in each fallback mode."""

    def test_replace_mode_substitutes_replacement_character(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # The bad byte becomes the replacement character; the rest stays.
        self.assertIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)

    def test_ignore_mode_drops_bad_bytes(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # The bad byte is dropped instead of replaced.
        self.assertNotIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)


class TestEnvVarParser(_DecoderEnvIsolatedTestCase):
    """Tests for how the env var value is read and interpreted."""

    def test_replace_env_value_resolves_to_replace_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

    def test_ignore_env_value_resolves_to_ignore_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "ignore")

    def test_unknown_env_value_resolves_to_strict(self):
        """Any value other than REPLACE or IGNORE keeps strict decoding."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "BOGUS"
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_env_value_is_case_insensitive_and_trims_whitespace(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "  replace  "
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

    def test_unset_env_resolves_to_strict(self):
        # setUp already pops the var; this makes the contract explicit.
        self.assertNotIn(_MALFORMED_INPUT_ENV_VAR, os.environ)
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    # The cases below pin down what happens for env-var values that
    # are neither REPLACE nor IGNORE. Each one must resolve to strict
    # so accidental or typo'd values don't silently change behavior.

    def test_empty_string_env_value_resolves_to_strict(self):
        """An empty value (common shell typo: VAR= ) must stay strict."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = ""
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_whitespace_only_env_value_resolves_to_strict(self):
        """Values that are only spaces or newlines must stay strict."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "   \t\n"
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_report_env_value_resolves_to_strict(self):
        """REPORT isn't one of the accepted values, so it stays strict."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPORT"
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_comma_separated_env_value_resolves_to_strict(self):
        """The parser does not split on commas. The whole value is
        treated as one token and stays strict if it isn't recognized."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE,IGNORE"
        self.assertIsNone(_response_decoding._resolve_fallback_mode_from_env())

    def test_mixed_case_replace_resolves_to_replace_mode(self):
        """Values are matched case-insensitively."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "Replace"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")


class TestEnvVarToBehaviorEndToEnd(_DecoderEnvIsolatedTestCase):
    """Checks that setting the env var actually changes what the
    decode helper does, and clearing it goes back to the default."""

    def test_setting_replace_env_var_makes_invalid_utf8_decode_succeed(self):
        # With no env var the same input raises.
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)

        # Set REPLACE and the same input now decodes successfully.
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        self.assertIn("\ufffd", result)

    def test_clearing_env_var_returns_to_strict(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        self.assertEqual(_response_decoding._resolve_fallback_mode_from_env(), "replace")

        # Remove the var and the next decode raises again.
        del os.environ[_MALFORMED_INPUT_ENV_VAR]
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)


class TestDecodeForStatus(_DecoderEnvIsolatedTestCase):
    """Tests the wrapper that lets error responses still produce a
    typed exception even when the response body has invalid bytes."""

    def test_valid_utf8_success_passes_through(self):
        """A 200 with a well-formed body decodes normally."""
        result = _response_decoding.decode_response_body_for_status(
            _VALID_UTF8, status_code=200
        )
        self.assertEqual(result, '{"note":"hello world"}')

    def test_invalid_utf8_on_2xx_still_raises(self):
        """A successful response with invalid bytes still raises so
        the caller is informed about the data problem."""
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body_for_status(
                _INVALID_UTF8, status_code=200
            )

    def test_invalid_utf8_on_404_does_not_raise(self):
        """A 404 with invalid bytes decodes best-effort so the
        caller still gets the typed not-found error."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=404
        )
        # The bad byte is replaced; the rest of the text is preserved.
        self.assertIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)

    def test_invalid_utf8_on_throttle_does_not_raise(self):
        """A 429 with invalid bytes still decodes so the throttle
        handler can see it."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=429
        )
        self.assertIn("\ufffd", result)

    def test_invalid_utf8_on_partition_gone_does_not_raise(self):
        """A 410 with invalid bytes still decodes so the partition
        refresh logic can run."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=410
        )
        self.assertIn("\ufffd", result)

    def test_invalid_utf8_on_service_unavailable_does_not_raise(self):
        """A 503 with invalid bytes still decodes so the retry logic
        can run."""
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=503
        )
        self.assertIn("\ufffd", result)

    def test_boundary_399_still_raises(self):
        """Best-effort decode only kicks in at 400 and above. A 399
        status still raises like a successful response would."""
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body_for_status(
                _INVALID_UTF8, status_code=399
            )

    def test_boundary_400_does_not_raise(self):
        """Confirms 400 is included in the best-effort range."""
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
        """When the env var is set, a 200 with invalid bytes decodes
        too because the env-var path runs before the status check."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        result = _response_decoding.decode_response_body_for_status(
            _INVALID_UTF8, status_code=200
        )
        self.assertIn("\ufffd", result)


class TestPermissiveFallbackJsonPipeline(_DecoderEnvIsolatedTestCase):
    """Checks what happens when the decoded string is then parsed as
    JSON. Bad bytes inside a string value parse cleanly; bad bytes
    that land where a JSON structural character was expected do not.
    """

    # Bad bytes inside a JSON string value. After REPLACE the body is
    # well-formed JSON whose string value contains the replacement
    # character.
    _BAD_BYTES_IN_STRING_VALUE = b'{"name":"caf\xc3\x28 dining"}'

    # Bad bytes where the JSON colon should be. After REPLACE the
    # body is not parseable JSON.
    _BAD_BYTES_IN_STRUCTURE = b'{"name"\xc3\x28"value"}'

    def test_replace_mode_corrupts_string_values_silently(self):
        """When the bad bytes were inside a JSON string value, parsing
        succeeds and the replacement character ends up in the value."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        decoded = _response_decoding.decode_response_body(self._BAD_BYTES_IN_STRING_VALUE)
        parsed = json.loads(decoded)

        self.assertIsInstance(parsed, dict)
        self.assertIn("name", parsed)
        self.assertIsInstance(parsed["name"], str)
        # The replacement character is in the parsed value; the rest
        # of the text is preserved.
        self.assertIn("\ufffd", parsed["name"])
        self.assertIn("caf", parsed["name"])
        self.assertIn("dining", parsed["name"])

    def test_replace_mode_structural_corruption_raises_json_decode_error(self):
        """When the bad bytes broke the JSON structure, decode still
        succeeds but JSON parsing fails."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"

        decoded = _response_decoding.decode_response_body(self._BAD_BYTES_IN_STRUCTURE)
        # Decode itself does not raise.
        self.assertIsInstance(decoded, str)
        self.assertIn("\ufffd", decoded)

        with self.assertRaises(json.JSONDecodeError):
            json.loads(decoded)


if __name__ == "__main__":
    unittest.main()
