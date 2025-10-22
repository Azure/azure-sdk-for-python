# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest

from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser


# pylint: disable=too-many-public-methods
class TestConnectionStringParser(unittest.TestCase):
    def setUp(self):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        self._valid_connection_string = "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab"
        self._valid_instrumentation_key = "1234abcd-5678-4efa-8abc-1234567890ab"

    def test_validate_connection_String(self):
        parser = ConnectionStringParser(connection_string=self._valid_connection_string)
        self.assertEqual(parser._connection_string, self._valid_connection_string)

    def test_invalid_key_empty(self):
        self.assertRaises(ValueError, lambda: ConnectionStringParser(connection_string=""))

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
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcda5678-4efa-8abc-1234567890ab"),
        )

    def test_invalid_key_section1_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcda-678-4efa-8abc-1234567890ab"),
        )

    def test_invalid_key_section2_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-678-a4efa-8abc-1234567890ab"),
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
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-678-4efa-8bc-11234567890ab"),
        )

    def test_invalid_key_section5_length(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=234abcd-678-4efa-8abc-11234567890ab"),
        )

    def test_invalid_key_section1_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=x234abcd-5678-4efa-8abc-1234567890ab"),
        )

    def test_invalid_key_section2_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-x678-4efa-8abc-1234567890ab"),
        )

    def test_invalid_key_section3_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"),
        )

    def test_invalid_key_section4_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"),
        )

    def test_invalid_key_section5_hex(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(connection_string="InstrumentationKey=1234abcd-5678-4xfa-8abc-1234567890ab"),
        )

    def test_process_options_ikey_code_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "Authorization=ikey;InstrumentationKey=789"
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;InstrumentationKey=" + self._valid_instrumentation_key,
        )
        self.assertEqual(parser.instrumentation_key, self._valid_instrumentation_key)

    def test_process_options_ikey_env_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;InstrumentationKey=" + self._valid_instrumentation_key
        )
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "101112"
        parser = ConnectionStringParser(connection_string=None)
        self.assertEqual(parser.instrumentation_key, self._valid_instrumentation_key)

    def test_process_options_ikey_env_ikey(self):
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = self._valid_instrumentation_key
        parser = ConnectionStringParser(connection_string=None)
        self.assertEqual(parser.instrumentation_key, self._valid_instrumentation_key)

    def test_process_options_endpoint_code_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        )
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;IngestionEndpoint=123",
        )
        self.assertEqual(parser.endpoint, "123")

    def test_process_options_endpoint_env_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        )
        parser = ConnectionStringParser(
            connection_string=None,
        )
        self.assertEqual(parser.endpoint, "456")

    def test_process_options_endpoint_default(self):
        parser = ConnectionStringParser(
            connection_string=self._valid_connection_string,
        )
        self.assertEqual(parser.endpoint, "https://dc.services.visualstudio.com")

    def test_process_options_live_endpoint_code_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;IngestionEndpoint=456;InstrumentationKey=" + self._valid_instrumentation_key
        )
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;IngestionEndpoint=123;LiveEndpoint=111",
        )
        self.assertEqual(parser.endpoint, "123")
        self.assertEqual(parser.live_endpoint, "111")

    def test_process_options_live_endpoint_env_cs(self):
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "Authorization=ikey;IngestionEndpoint=456;LiveEndpoint=111;InstrumentationKey="
            + self._valid_instrumentation_key
        )
        parser = ConnectionStringParser(
            connection_string=None,
        )
        self.assertEqual(parser.endpoint, "456")
        self.assertEqual(parser.live_endpoint, "111")

    def test_process_options_live_endpoint_default(self):
        parser = ConnectionStringParser(
            connection_string=self._valid_connection_string,
        )
        self.assertEqual(parser.live_endpoint, "https://rt.services.visualstudio.com")

    def test_parse_connection_string_invalid(self):
        self.assertRaises(ValueError, lambda: ConnectionStringParser(connection_string="asd"))

    def test_parse_connection_string_invalid_auth(self):
        self.assertRaises(
            ValueError,
            lambda: ConnectionStringParser(
                connection_string="Authorization=asd",
            ),
        )

    def test_parse_connection_string_suffix(self):
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;EndpointSuffix=123;Location=US;InstrumentationKey="
            + self._valid_instrumentation_key,
        )
        self.assertEqual(parser.endpoint, "https://US.dc.123")

    def test_parse_connection_string_suffix_no_location(self):
        parser = ConnectionStringParser(
            connection_string="Authorization=ikey;EndpointSuffix=123;InstrumentationKey="
            + self._valid_instrumentation_key,
        )
        self.assertEqual(parser.endpoint, "https://dc.123")

    # Region extraction tests
    def test_region_extraction_from_endpoint_with_number(self):
        """Test region extraction from endpoint URL with number suffix."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/"
        )
        self.assertEqual(parser.region, "westeurope")

    def test_region_extraction_from_endpoint_without_number(self):
        """Test region extraction from endpoint URL without number suffix."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://westeurope.in.applicationinsights.azure.com/"
        )
        self.assertEqual(parser.region, "westeurope")

    def test_region_extraction_from_endpoint_two_digit_number(self):
        """Test region extraction from endpoint URL with two-digit number."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://eastus-12.in.applicationinsights.azure.com/"
        )
        self.assertEqual(parser.region, "eastus")

    def test_region_extraction_from_endpoint_three_digit_number(self):
        """Test region extraction from endpoint URL with three-digit number."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://northeurope-999.in.applicationinsights.azure.com/"
        )
        self.assertEqual(parser.region, "northeurope")

    def test_region_extraction_various_regions(self):
        """Test region extraction for various Azure regions."""
        test_cases = [
            ("westeurope-1.in.applicationinsights.azure.com", "westeurope"),
            ("eastus-2.in.applicationinsights.azure.com", "eastus"),
            ("southeastasia-5.in.applicationinsights.azure.com", "southeastasia"),
            ("australiaeast-3.in.applicationinsights.azure.com", "australiaeast"),
            ("westus2-7.in.applicationinsights.azure.com", "westus2"),
            ("francecentral.in.applicationinsights.azure.com", "francecentral"),
        ]
        
        for endpoint_suffix, expected_region in test_cases:
            with self.subTest(endpoint=endpoint_suffix):
                parser = ConnectionStringParser(
                    connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
                    f";IngestionEndpoint=https://{endpoint_suffix}/"
                )
                self.assertEqual(parser.region, expected_region)

    def test_region_extraction_no_region_global_endpoint(self):
        """Test that no region is extracted from global endpoints."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://dc.services.visualstudio.com"
        )
        self.assertIsNone(parser.region)

    def test_region_extraction_no_region_default_endpoint(self):
        """Test that no region is extracted when using default endpoint."""
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key
        )
        self.assertIsNone(parser.region)

    def test_region_extraction_invalid_endpoint_format(self):
        """Test that no region is extracted from invalid endpoint formats."""
        invalid_endpoints = [
            "https://invalid.endpoint.com",
            "https://westeurope.wrong.domain.com",
            "https://not-a-region.in.applicationinsights.azure.com",
            "ftp://westeurope-5.in.applicationinsights.azure.com",
        ]
        
        for endpoint in invalid_endpoints:
            with self.subTest(endpoint=endpoint):
                parser = ConnectionStringParser(
                    connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
                    f";IngestionEndpoint={endpoint}"
                )
                self.assertIsNone(parser.region)

    def test_region_extraction_from_environment_endpoint(self):
        """Test region extraction from endpoint set via environment variable."""
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/"
        )
        parser = ConnectionStringParser(connection_string=None)
        self.assertEqual(parser.region, "westeurope")

    def test_region_extraction_code_endpoint_takes_priority(self):
        """Test that endpoint from code connection string takes priority over environment."""
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            "InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://eastus-1.in.applicationinsights.azure.com/"
        )
        parser = ConnectionStringParser(
            connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
            ";IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/"
        )
        self.assertEqual(parser.region, "westeurope")

    def test_region_extraction_with_trailing_slash(self):
        """Test region extraction works with and without trailing slash."""
        test_cases = [
            "https://westeurope-5.in.applicationinsights.azure.com/",
            "https://westeurope-5.in.applicationinsights.azure.com",
        ]
        
        for endpoint in test_cases:
            with self.subTest(endpoint=endpoint):
                parser = ConnectionStringParser(
                    connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
                    f";IngestionEndpoint={endpoint}"
                )
                self.assertEqual(parser.region, "westeurope")

    def test_region_extraction_alphanumeric_regions(self):
        """Test region extraction for regions with numbers in the name."""
        test_cases = [
            ("westus2-1.in.applicationinsights.azure.com", "westus2"),
            ("eastus2-5.in.applicationinsights.azure.com", "eastus2"),
            ("southcentralus-3.in.applicationinsights.azure.com", "southcentralus"),
        ]
        
        for endpoint_suffix, expected_region in test_cases:
            with self.subTest(endpoint=endpoint_suffix):
                parser = ConnectionStringParser(
                    connection_string="InstrumentationKey=" + self._valid_instrumentation_key +
                    f";IngestionEndpoint=https://{endpoint_suffix}"
                )
                self.assertEqual(parser.region, expected_region)
