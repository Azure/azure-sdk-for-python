# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""In-process unit tests for ``_helpers/_format_ru.py`` â—” no network, no Cosmos emulator.

The function is a single one-liner today. The tests pin the exact
string output for representative RU values so a future change to the
formatting (e.g. adopting a fixed-precision form to match real
service behaviour) is a deliberate decision recorded in this file.
"""
import unittest

from azure.cosmos._helpers._format_ru import format_ru_charge


class TestFormatRuCharge(unittest.TestCase):
    """The output is the byte-stable wire string for ``x-ms-request-charge``."""

    def test_whole_ru_renders_with_decimal_zero(self):
        # 1.0 must NOT render as "1" â—” the legacy header value is
        # always a decimal-point string. ``str(1.0)`` produces "1.0".
        self.assertEqual(format_ru_charge(1.0), "1.0")

    def test_two_digit_decimal_renders_as_typed(self):
        self.assertEqual(format_ru_charge(1.43), "1.43")

    def test_simple_decimal_keeps_trailing_zero_dropped(self):
        # 1.50 in Python is the same float as 1.5; the canonical str
        # form is "1.5". This is what every existing customer test
        # fixture expects.
        self.assertEqual(format_ru_charge(1.50), "1.5")

    def test_zero_renders_as_zero_point_zero(self):
        # The free-tier read sometimes shows 0.0 RUs. Catch a future
        # change that would render this as "0".
        self.assertEqual(format_ru_charge(0.0), "0.0")

    def test_int_input_is_coerced_to_float(self):
        # The function signature says float, but if a caller hands us
        # an int we still produce a string â—” that protects against a
        # future Rust-typed-field change that returns int for the
        # whole-RU case.
        self.assertEqual(format_ru_charge(2), "2.0")  # type: ignore[arg-type]

    def test_large_charge_does_not_use_scientific_notation(self):
        # Six-digit RU charges (uncommon but valid) must stay decimal,
        # not flip to "1e+06".
        self.assertEqual(format_ru_charge(123456.78), "123456.78")

    def test_negative_value_passes_through(self):
        # The Cosmos service does not return negative RU charges, but
        # the helper should not raise on one â—” letting an exception
        # escape during another exception build would mask
        # the underlying error.
        self.assertEqual(format_ru_charge(-1.5), "-1.5")


if __name__ == "__main__":
    unittest.main()
