# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests for the response-body UTF-8 decode helper and its env-var-driven
fallback behavior. Covers the healthy path (strict decode succeeds), the
default behavior when the env var is unset (strict decode fails with an
actionable hint), and the opt-in REPLACE / IGNORE modes.
"""
import os
import unittest
from unittest import mock

from azure.cosmos import _response_decoding


# A small payload containing one valid 2-byte UTF-8 sequence followed by a
# byte (0xC3 followed by 0x28) that is not a valid UTF-8 continuation byte.
# `\xC3\x28` is the textbook example of an invalid UTF-8 sequence.
_INVALID_UTF8 = b'{"note":"hello \xc3\x28 world"}'
_VALID_UTF8 = b'{"note":"hello world"}'

_MALFORMED_INPUT_ENV_VAR = "COSMOS.CHARSET_DECODER_ERROR_ACTION_ON_MALFORMED_INPUT"


class _DecoderEnvIsolatedTestCase(unittest.TestCase):
    """Base class that isolates each test from the surrounding process
    environment and from sibling tests by restoring both the recognized
    env var and the module-level fallback-mode cache after every test."""

    def setUp(self):
        # Snapshot the cache value and start an env patch that will
        # roll back any mutations the test makes.
        self._original_fallback_mode = _response_decoding._fallback_errors_mode
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        # Strip the env var for the duration of the test so the helper's
        # default behavior (no env -> strict) is the explicit baseline.
        # Tests that need a specific env value set it themselves and call
        # `_reset_for_tests()`.
        os.environ.pop(_MALFORMED_INPUT_ENV_VAR, None)
        _response_decoding._reset_for_tests()

    def tearDown(self):
        # `mock.patch.dict` rolls back any env mutations the test made,
        # including the pop in setUp.
        self._env_patch.stop()
        # Restore the cache last, so the next test's setUp sees the
        # same module state the suite started with.
        _response_decoding._fallback_errors_mode = self._original_fallback_mode


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
        # setUp already cleared the env var and reset the cache; the
        # assertion below makes that contract explicit for the reader.
        self.assertIsNone(_response_decoding._fallback_errors_mode)

        with self.assertRaises(UnicodeDecodeError) as ctx:
            _response_decoding.decode_response_body(_INVALID_UTF8, operation_context="read_item")

        self.assertIn(_MALFORMED_INPUT_ENV_VAR, ctx.exception.reason)
        # Original exception must be chained so callers and log readers
        # can still see the underlying decoder error.
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)


class TestPermissiveFallback(_DecoderEnvIsolatedTestCase):
    """Exercises the decode behavior in each fallback mode by writing the
    cache directly. """

    def test_replace_mode_substitutes_replacement_character(self):
        _response_decoding._fallback_errors_mode = "replace"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # The bad byte is replaced by U+FFFD; the surrounding text is preserved.
        self.assertIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)

    def test_ignore_mode_drops_bad_bytes(self):
        _response_decoding._fallback_errors_mode = "ignore"
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        # No replacement character; the bad byte is silently dropped.
        self.assertNotIn("\ufffd", result)
        self.assertIn("hello", result)
        self.assertIn("world", result)



class TestEnvVarSnapshot(_DecoderEnvIsolatedTestCase):
    """Tests for the env-var parser in isolation. Each test sets the
    env var, calls ``_reset_for_tests()``, and asserts the cached
    fallback mode matches the documented mapping."""

    def test_replace_env_value_resolves_to_replace_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        _response_decoding._reset_for_tests()
        self.assertEqual(_response_decoding._fallback_errors_mode, "replace")

    def test_ignore_env_value_resolves_to_ignore_mode(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "IGNORE"
        _response_decoding._reset_for_tests()
        self.assertEqual(_response_decoding._fallback_errors_mode, "ignore")

    def test_unknown_env_value_resolves_to_strict(self):
        """Anything other than REPLACE / IGNORE (case-insensitive) must
        leave strict decoding in effect."""
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "BOGUS"
        _response_decoding._reset_for_tests()
        self.assertIsNone(_response_decoding._fallback_errors_mode)

    def test_env_value_is_case_insensitive_and_trims_whitespace(self):
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "  replace  "
        _response_decoding._reset_for_tests()
        self.assertEqual(_response_decoding._fallback_errors_mode, "replace")

    def test_unset_env_resolves_to_strict(self):
        # setUp already pops the var; this makes the contract explicit.
        self.assertNotIn(_MALFORMED_INPUT_ENV_VAR, os.environ)
        _response_decoding._reset_for_tests()
        self.assertIsNone(_response_decoding._fallback_errors_mode)


class TestEnvVarToBehaviorEndToEnd(_DecoderEnvIsolatedTestCase):
    """Verifies the full contract: setting the env var and calling
    ``_reset_for_tests()`` actually changes what ``decode_response_body``
    does. Catches regressions where the env parser and the per-call
    read drift apart."""

    def test_setting_replace_env_var_makes_invalid_utf8_decode_succeed(self):
        # Baseline: with no env var, the same input raises.
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)

        # Opt in via the env var, refresh, and prove the same input now
        # decodes to a replacement-character-bearing string instead of raising.
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        _response_decoding._reset_for_tests()
        result = _response_decoding.decode_response_body(_INVALID_UTF8)
        self.assertIn("\ufffd", result)

    def test_clearing_env_var_after_reset_returns_to_strict(self):
        # Opt in.
        os.environ[_MALFORMED_INPUT_ENV_VAR] = "REPLACE"
        _response_decoding._reset_for_tests()
        self.assertEqual(_response_decoding._fallback_errors_mode, "replace")

        # Opt out by removing the var and re-snapshotting.
        del os.environ[_MALFORMED_INPUT_ENV_VAR]
        _response_decoding._reset_for_tests()
        with self.assertRaises(UnicodeDecodeError):
            _response_decoding.decode_response_body(_INVALID_UTF8)


if __name__ == "__main__":
    unittest.main()

