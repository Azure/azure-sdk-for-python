# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.timezone import MapsTimezoneClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live

from timezone_preparer import MapsTimezonePreparer


# cSpell:disable
class TestMapsTimezoneClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsTimezoneClient(
            credential=AzureKeyCredential(os.getenv("AZURE_SUBSCRIPTION_KEY", "AzureSubscriptionKey"))
        )
        assert self.client is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_timezone_by_coordinates(self):
        result = self.client.get_timezone_by_coordinates(coordinates=[25.0338053, 121.5640089])

        assert result is not None and "TimeZones" in result

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_timezone_by_id(self):
        result = self.client.get_timezone_by_id(timezone_id="sr-Latn-RS")

        assert result is not None and "TimeZones" in result

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_iana_version(self):
        expected_result = {'Version': '2024a'}
        result = self.client.get_iana_version()

        assert result == expected_result

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_iana_timezone_ids(self):
        result = self.client.get_iana_timezone_ids()

        assert result is not None and len(result) > 0

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_windows_timezone_ids(self):
        result = self.client.get_windows_timezone_ids()

        assert result is not None and len(result) > 0

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_convert_windows_timezone_to_iana(self):
        expected_result = [
            {'HasZone1970Location': True, 'Id': 'America/Vancouver', 'IsAlias': False},
            {'HasZone1970Location': True, 'Id': 'America/Los_Angeles', 'IsAlias': False},
            {'HasZone1970Location': False, 'Id': 'PST8PDT', 'IsAlias': False}
        ]
        result = self.client.convert_windows_timezone_to_iana(windows_timezone_id="Pacific Standard Time")

        assert result == expected_result
