# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME,
    _DEFAULT_EU_STATS_CONNECTION_STRING,
    _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _get_region_from_endpoint,
    _get_stats_connection_string,
)

# cSpell:disable


# pylint: disable=protected-access
class TestGetRegionFromEndpoint(unittest.TestCase):
    def test_strips_stamp_index(self):
        self.assertEqual(
            _get_region_from_endpoint("https://westeurope-5.in.applicationinsights.azure.com/"),
            "westeurope",
        )

    def test_region_without_stamp_index(self):
        self.assertEqual(
            _get_region_from_endpoint("https://westeurope.in.applicationinsights.azure.com/"),
            "westeurope",
        )

    def test_multi_token_region_is_not_truncated(self):
        # Region labels are a single hyphen-free token, so splitting on "-" must strip only the
        # stamp index and never part of the region name itself.
        self.assertEqual(
            _get_region_from_endpoint("https://germanywestcentral-0.in.applicationinsights.azure.com/"),
            "germanywestcentral",
        )
        self.assertEqual(
            _get_region_from_endpoint("https://switzerlandnorth-1.in.applicationinsights.azure.com/"),
            "switzerlandnorth",
        )

    def test_is_case_insensitive(self):
        self.assertEqual(
            _get_region_from_endpoint("https://WestEurope-5.in.applicationinsights.azure.com/"),
            "westeurope",
        )

    def test_global_endpoint_has_no_region(self):
        self.assertEqual(_get_region_from_endpoint("https://dc.services.visualstudio.com"), "dc")

    def test_empty_endpoint(self):
        self.assertEqual(_get_region_from_endpoint(""), "")

    def test_malformed_endpoint(self):
        self.assertEqual(_get_region_from_endpoint("not a url"), "")


class TestGetStatsConnectionString(unittest.TestCase):
    def setUp(self):
        # Ensure the environment override never leaks in from another test.
        self._env_patcher = mock.patch.dict("os.environ", {}, clear=False)
        self._env_patcher.start()
        import os

        os.environ.pop(_APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME, None)

    def tearDown(self):
        self._env_patcher.stop()

    def test_environment_override_wins(self):
        import os

        os.environ[_APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME] = "InstrumentationKey=custom"
        self.assertEqual(
            _get_stats_connection_string("https://westeurope-5.in.applicationinsights.azure.com/"),
            "InstrumentationKey=custom",
        )

    def test_eu_region_with_stamp_index(self):
        self.assertEqual(
            _get_stats_connection_string("https://westeurope-5.in.applicationinsights.azure.com/"),
            _DEFAULT_EU_STATS_CONNECTION_STRING,
        )

    def test_germany_north_is_eu(self):
        self.assertEqual(
            _get_stats_connection_string("https://germanynorth-1.in.applicationinsights.azure.com/"),
            _DEFAULT_EU_STATS_CONNECTION_STRING,
        )

    def test_germany_west_central_is_eu(self):
        self.assertEqual(
            _get_stats_connection_string("https://germanywestcentral-0.in.applicationinsights.azure.com/"),
            _DEFAULT_EU_STATS_CONNECTION_STRING,
        )

    def test_non_eu_region(self):
        self.assertEqual(
            _get_stats_connection_string("https://westus-0.in.applicationinsights.azure.com/"),
            _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
        )

    def test_global_endpoint_is_non_eu(self):
        self.assertEqual(
            _get_stats_connection_string("https://dc.services.visualstudio.com"),
            _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
        )

    def test_malformed_endpoint_falls_back_to_non_eu(self):
        self.assertEqual(
            _get_stats_connection_string("not a url"),
            _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
        )

    def test_region_is_matched_exactly_not_by_substring(self):
        """An EU region name appearing elsewhere in the URL must not classify the endpoint as EU."""
        self.assertEqual(
            _get_stats_connection_string("https://eastus-0.in.westeurope.example.com/"),
            _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
        )
        self.assertEqual(
            _get_stats_connection_string("https://eastus-0.in.applicationinsights.azure.com/ukwest"),
            _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
        )


if __name__ == "__main__":
    unittest.main()
