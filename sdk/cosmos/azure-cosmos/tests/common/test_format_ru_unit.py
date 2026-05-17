# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_format_ru.py`` — no network, no Cosmos emulator.

Every Cosmos response carries an ``x-ms-request-charge`` header that
tells the customer how many RUs (Request Units) the operation cost.
The helper ``format_ru_charge`` is the single place that turns the
numeric RU value into the string that goes back to the customer
(via response headers, diagnostics, logs, exception messages).

The exact string format is part of the SDK's effective public
contract: customer dashboards, billing reconciliation tools, and
test fixtures all string-match on these values. ``"1.0"`` and
``"1"`` are equivalent numbers but different strings, so a quiet
formatting drift would silently break customer parsers.

This file is short on purpose — the helper is one line — but it
covers every behavior that's worth locking down: trailing-zero handling,
no scientific notation on big values, integer coercion, and never
raising on negative input (so a malformed server response never
masks the original error during exception construction).
"""
import unittest

from azure.cosmos._helpers._format_ru import format_ru_charge


class TestFormatRuCharge(unittest.TestCase):
    """Cover the exact string output for every RU-formatting case worth locking down.

    The function is one line today (``str(float(value))``). These
    tests document the cases that string form covers, so any future
    change (e.g. fixed-precision to mirror the service exactly) is a
    deliberate decision recorded as a test diff.
    """

    def test_whole_ru_renders_with_decimal_zero(self):
        """``1.0`` → ``"1.0"`` (always a decimal-point string, never bare ``"1"``)."""
        self.assertEqual(format_ru_charge(1.0), "1.0")

    def test_two_digit_decimal_renders_as_typed(self):
        """A two-decimal value renders verbatim — no rounding."""
        self.assertEqual(format_ru_charge(1.43), "1.43")

    def test_simple_decimal_keeps_trailing_zero_dropped(self):
        """``1.50`` (== ``1.5`` as a float) renders as ``"1.5"`` — Python's canonical form.

        Customer fixtures that string-match against
        ``x-ms-request-charge`` rely on this being the canonical
        ``str(float)`` form, not a fixed-precision form.
        """
        self.assertEqual(format_ru_charge(1.50), "1.5")

    def test_zero_renders_as_zero_point_zero(self):
        """``0.0`` → ``"0.0"`` (the free-tier read can show this; must not become ``"0"``)."""
        self.assertEqual(format_ru_charge(0.0), "0.0")

    def test_int_input_is_coerced_to_float(self):
        """An ``int`` argument is coerced to float so the output shape stays the same.

        Defensive: a future Rust-typed-field change that returns
        ``int`` for whole-RU values must not flip the request-byte string
        from ``"2.0"`` to ``"2"``.
        """
        self.assertEqual(format_ru_charge(2), "2.0")  # type: ignore[arg-type]

    def test_large_charge_does_not_use_scientific_notation(self):
        """Six-digit RU charges stay decimal — no ``"1.23e+05"`` flips."""
        self.assertEqual(format_ru_charge(123456.78), "123456.78")

    def test_negative_value_passes_through(self):
        """Negative input is formatted, not rejected — the helper must never raise.

        The Cosmos service does not return negative RU charges, but
        if a malformed response ever surfaced one, raising here
        (e.g. during exception construction) would mask the
        underlying error.
        """
        self.assertEqual(format_ru_charge(-1.5), "-1.5")


if __name__ == "__main__":
    unittest.main()
