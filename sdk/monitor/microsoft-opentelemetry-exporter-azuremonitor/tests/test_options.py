# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest

from microsoft.opentelemetry.exporter.azuremonitor.options import ExporterOptions


# pylint: disable=too-many-public-methods
class TestOptions(unittest.TestCase):
    def setUp(self):
        os.environ.clear()
        self._valid_instrumentation_key = (
            "1234abcd-5678-4efa-8abc-1234567890ab"
        )

    def test_validate_instrumentation_key(self):
        options = ExporterOptions(
            instrumentation_key=self._valid_instrumentation_key
        )
        self.assertEqual(
            options.instrumentation_key, self._valid_instrumentation_key
        )

    def test_invalid_key_none(self):
        self.assertRaises(
            ValueError, lambda: ExporterOptions(instrumentation_key=None)
        )

    def test_invalid_key_empty(self):
        self.assertRaises(
            ValueError, lambda: ExporterOptions(instrumentation_key="")
        )

    def test_invalid_key_prefix(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="test1234abcd-5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_suffix(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4efa-8abc-1234567890abtest"
            ),
        )

    def test_invalid_key_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4efa-8abc-12234567890ab"
            ),
        )

    def test_invalid_key_dashes(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcda5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section1_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcda-678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section2_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-678-a4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section3_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-6789-4ef-8cabc-1234567890ab"
            ),
        )

    def test_invalid_key_section4_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-678-4efa-8bc-11234567890ab"
            ),
        )

    def test_invalid_key_section5_length(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="234abcd-678-4efa-8abc-11234567890ab"
            ),
        )

    def test_invalid_key_section1_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="x234abcd-5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section2_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-x678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section3_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section4_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section5_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_version(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-6efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_variant(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                instrumentation_key="1234abcd-5678-4efa-2abc-1234567890ab"
            ),
        )

    def test_process_options_ikey_code_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;InstrumentationKey=789"
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        options = ExporterOptions(
            connection_string="Authorization=ikey;InstrumentationKey="
            + self._valid_instrumentation_key,
            instrumentation_key="456",
        )
        self.assertEqual(
            options.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_ikey_code_ikey(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;InstrumentationKey=789"
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        options = ExporterOptions(
            connection_string=None,
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(
            options.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_ikey_env_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;InstrumentationKey="
            + self._valid_instrumentation_key
        )
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        options = ExporterOptions(
            connection_string=None, instrumentation_key=None
        )
        self.assertEqual(
            options.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_ikey_env_ikey(self):
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = self._valid_instrumentation_key
        options = ExporterOptions(
            connection_string=None, instrumentation_key=None
        )
        self.assertEqual(
            options.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_endpoint_code_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey="
        options = ExporterOptions(
            connection_string="Authorization=ikey;IngestionEndpoint=123",
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(options.endpoint, "123")

    def test_process_options_endpoint_env_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456"
        options = ExporterOptions(
            connection_string=None,
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(options.endpoint, "456")

    def test_process_options_endpoint_default(self):
        options = ExporterOptions(
            connection_string=None,
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(
            options.endpoint, "https://dc.services.visualstudio.com"
        )

    def test_process_options_proxies_default(self):
        options = ExporterOptions(
            connection_string=None,
            instrumentation_key=self._valid_instrumentation_key,
            proxies={},
        )
        self.assertEqual(options.proxies, {})

    def test_process_options_proxies_set_proxies(self):
        options = ExporterOptions(
            connection_string=None,
            instrumentation_key=self._valid_instrumentation_key,
            proxies={"https": "https://test-proxy.com"},
        )
        self.assertEqual(options.proxies, {"https": "https://test-proxy.com"})

    def test_parse_connection_string_invalid(self):
        self.assertRaises(
            ValueError, lambda: ExporterOptions(connection_string="asd")
        )

    def test_parse_connection_string_invalid_auth(self):
        self.assertRaises(
            ValueError,
            lambda: ExporterOptions(
                connection_string="Authorization=asd",
                instrumentation_key=self._valid_instrumentation_key,
            ),
        )

    def test_parse_connection_string_suffix(self):
        options = ExporterOptions(
            connection_string="Authorization=ikey;EndpointSuffix=123;Location=US",
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(options.endpoint, "https://US.dc.123")

    def test_parse_connection_string_suffix_no_location(self):
        options = ExporterOptions(
            connection_string="Authorization=ikey;EndpointSuffix=123",
            instrumentation_key=self._valid_instrumentation_key,
        )
        self.assertEqual(options.endpoint, "https://dc.123")
