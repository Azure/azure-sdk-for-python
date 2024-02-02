# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest

from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser


# pylint: disable=too-many-public-methods
class TestConnectionStringParser(unittest.TestCase):
    def setUp(self):
        os.environ.clear()
        self._valid_connection_string = (
            "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab"
        )
        self._valid_instrumentation_key = (
            "1234abcd-5678-4efa-8abc-1234567890ab"
        )

    def test_validate_connection_String(self):
        parser = ConnectionStringParser(
            connection_string=self._valid_connection_string
        )
        self.assertEqual(
            parser._connection_string, self._valid_connection_string
        )

    def test_invalid_key_empty(self):
        self.assertRaises(
            ValueError, lambda: ConnectionStringParser(connection_string="")
        )

    def test_invalid_key_prefix(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=test1234abcd-5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_suffix(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890abtest"
            ),
        )

    def test_invalid_key_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-5678-4efa-8abc-12234567890ab"
            ),
        )

    def test_invalid_key_dashes(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcda5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section1_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcda-678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section2_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-678-a4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section3_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                # spell-checker:ignore cabc
                connection_string="InstrumentationKey=1234abcd-6789-4ef-8cabc-1234567890ab"
            ),
        )

    def test_invalid_key_section4_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-678-4efa-8bc-11234567890ab"
            ),
        )

    def test_invalid_key_section5_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=234abcd-678-4efa-8abc-11234567890ab"
            ),
        )

    def test_invalid_key_section1_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=x234abcd-5678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section2_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-x678-4efa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section3_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section4_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_invalid_key_section5_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"
            ),
        )

    def test_process_options_ikey_code_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;InstrumentationKey=789"
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;InstrumentationKey="
            + self._valid_instrumentation_key,
        )
        self.assertEqual(
            parser.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_ikey_env_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;InstrumentationKey="
            + self._valid_instrumentation_key
        )
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        parser = ConnectionStringParser(
            connection_string=None
        )
        self.assertEqual(
            parser.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_ikey_env_ikey(self):
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = self._valid_instrumentation_key
        parser = ConnectionStringParser(
            connection_string=None
        )
        self.assertEqual(
            parser.instrumentation_key, self._valid_instrumentation_key
        )

    def test_process_options_endpoint_code_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;IngestionEndpoint=123",
        )
        self.assertEqual(parser.endpoint, "123")

    def test_process_options_endpoint_env_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        parser = ConnectionStringParser(
            connection_string=None,
        )
        self.assertEqual(parser.endpoint, "456")

    def test_process_options_endpoint_default(self):
        parser = ConnectionStringParser(
            connection_string=self._valid_connection_string,
        )
        self.assertEqual(
            parser.endpoint, "https://dc.services.visualstudio.com"
        )

    def test_process_options_live_endpoint_code_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;IngestionEndpoint=123;LiveEndpoint=111",
        )
        self.assertEqual(parser.endpoint, "123")
        self.assertEqual(parser.live_endpoint, "111")

    def test_process_options_live_endpoint_env_cs(self):
        os.environ[
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ] = "Authorization=ikey;IngestionEndpoint=456;LiveEndpoint=111;InstrumentationKey=" + self._valid_instrumentation_key
        parser = ConnectionStringParser(
            connection_string=None,
        )
        self.assertEqual(parser.endpoint, "456")
        self.assertEqual(parser.live_endpoint, "111")

    def test_process_options_live_endpoint_default(self):
        parser = ConnectionStringParser(
            connection_string=self._valid_connection_string,
        )
        self.assertEqual(
            parser.live_endpoint, "https://rt.services.visualstudio.com"
        )

    def test_parse_connection_string_invalid(self):
        self.assertRaises(
            ValueError, lambda: ConnectionStringParser(connection_string="asd")
        )

    def test_parse_connection_string_invalid_auth(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="Authorization=asd",
            ),
        )

    def test_parse_connection_string_suffix(self):
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;EndpointSuffix=123;Location=US;InstrumentationKey=" +
            self._valid_instrumentation_key,
        )
        self.assertEqual(parser.endpoint, "https://US.dc.123")

    def test_parse_connection_string_suffix_no_location(self):
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;EndpointSuffix=123;InstrumentationKey=" +
            self._valid_instrumentation_key,
        )
        self.assertEqual(parser.endpoint, "https://dc.123")
