# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

from azure.monitor.opentelemetry.exporter._routing import _get_instrumentation_key


class TestRouting(unittest.TestCase):
    def test_instrumentation_key(self):
        for value, expected in (
            ("customer-key", "customer-key"),
            (" \tCUSTOMER-KEY\n", "CUSTOMER-KEY"),
            ("k" * 200, "k" * 200),
            (" " * 99 + "k" + " " * 100, "k"),
        ):
            with self.subTest(value=value):
                self.assertEqual(_get_instrumentation_key({"microsoft.instrumentation_key": value}), expected)

    def test_missing_instrumentation_key(self):
        for attributes in (None, {}, {"unrelated": "customer-key"}):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must be a nonempty string"):
                    _get_instrumentation_key(attributes)

    def test_invalid_instrumentation_key(self):
        for value in (None, "", " \t\n", 42, True, ("customer-key",), b"customer-key"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must be a nonempty string"):
                    _get_instrumentation_key({"microsoft.instrumentation_key": value})

    def test_instrumentation_key_length_before_trimming(self):
        for value in ("k" * 201, " " + "k" * 200, " " * 201):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must not exceed 200 characters"):
                    _get_instrumentation_key({"microsoft.instrumentation_key": value})
