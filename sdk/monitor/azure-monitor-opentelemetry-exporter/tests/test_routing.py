# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

from azure.monitor.opentelemetry.exporter._routing import _get_ingestion_endpoint, _get_instrumentation_key


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


class TestIngestionEndpoint(unittest.TestCase):
    def test_normalize_endpoint(self):
        for value, expected in (
            ("HTTPS://Example.COM.:443", "https://example.com/"),
            ("https://gateway.example:8443/ingest///", "https://gateway.example:8443/ingest/"),
            ("https://localhost:9000/", "https://localhost:9000/"),
            ("https://dc.applicationinsights.azure.cn/", "https://dc.applicationinsights.azure.cn/"),
            ("https://[2001:0DB8:0:0:0:0:0:1]:443/", "https://[2001:db8::1]/"),
            ("https://[::1]:8443/", "https://[::1]:8443/"),
            ("https://b\u00fccher.example/", "https://b\u00fccher.example/"),
            ("https://fa\u00df.de/", "https://fa\u00df.de/"),
            ("https://xn--fa-hia.de/", "https://xn--fa-hia.de/"),
            ("https://example\u3002com/", "https://example\u3002com/"),
            (" https://example.com/ ", "https://example.com/"),
        ):
            with self.subTest(value=value):
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": value}), expected)
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": expected}), expected)

    def test_missing_or_non_string_endpoint(self):
        for attributes in (None, {}, {"unrelated": "https://example.com/"}):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must be a nonempty string"):
                    _get_ingestion_endpoint(attributes)
        for value in (None, "", " \t\n", 42, True, ("https://example.com/",), b"https://example.com/"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must be a nonempty string"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_invalid_endpoint(self):
        for value in (
            "/relative",
            "not-a-uri",
            "http://example.com/",
            "ftp://example.com/",
            "https:///path",
            "https://user:password@example.com/",
            "https://@example.com/",
            "https://example.com/?a=b",
            "https://example.com/?",
            "https://example.com/#fragment",
            "https://example.com/#",
            "https://example.com:invalid/",
            "https://example.com:65536/",
            "https://example.com:/",
            "https://exa\nmple.com/",
            "https://example.com/\x00",
            "https://example.com\\other/",
            "https://[::1",
            "https://[::1]extra:8443/",
            "https://bad host/",
            "https://%65xample.com/",
            "https://./",
            "https://bad!host/",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_endpoint_length_before_trimming(self):
        prefix = "https://example.com/"
        endpoint = prefix + "a" * (2048 - len(prefix))
        self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint}), endpoint + "/")
        for value in (endpoint + "a", " " + endpoint):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must not exceed 2048 characters"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_invalid_endpoint_does_not_expose_credentials(self):
        endpoint = "https://user:password@example.com/?token=secret"
        with self.assertRaises(ValueError) as raised:
            _get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint})
        self.assertNotIn(endpoint, str(raised.exception))
        self.assertTrue(raised.exception.__suppress_context__)

    def test_unicode_host_spelling_is_preserved_for_transport(self):
        for host in ("B\u00dcCHER.Example", "\u039f\u03a3.example", "e\u0301.example", "xn--\u00fc.example"):
            with self.subTest(host=host):
                endpoint = f"https://{host}/"
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint}), endpoint)
