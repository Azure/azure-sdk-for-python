# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import os
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.maps.timezone import MapsTimezoneClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live
from timezone_preparer import MapsTimezonePreparer


logger = logging.getLogger(__name__)


class TestMapsTimezoneClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsTimezoneClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_timezone_by_id(self, **kwargs):
        timezone = self.client.get_timezone_by_id("America/New_York")

        assert timezone is not None
        assert timezone.version == '2022c'
        assert len(timezone.time_zones) == 1
        assert timezone.time_zones[0].id == "America/New_York"
        assert timezone.time_zones[0].names.generic == "Eastern Time"
        assert timezone.time_zones[0].names.standard == "Eastern Standard Time"
        assert timezone.time_zones[0].names.daylight == "Eastern Daylight Time"
        assert timezone.time_zones[0].reference_time.tag == "EDT"
        assert timezone.time_zones[0].reference_time.standard_offset == "-05:00:00"
        assert timezone.time_zones[0].reference_time.daylight_savings == "01:00:00"

    # cSpell:ignore CEST
    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_timezone_by_coordinate(self, **kwargs):
        timezone = self.client.get_timezone_by_coordinates(coordinates=(52.5069,13.2843))

        assert timezone is not None
        assert timezone.version == '2022c'
        assert len(timezone.time_zones) == 1
        assert timezone.time_zones[0].id == "Europe/Berlin"
        assert timezone.time_zones[0].names.generic == "Central European Time"
        assert timezone.time_zones[0].reference_time.tag == "CEST"
        assert timezone.time_zones[0].reference_time.standard_offset == "01:00:00"
        assert timezone.time_zones[0].reference_time.daylight_savings == "01:00:00"

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_windows_timezone_ids(self, **kwargs):
        ids = self.client.get_windows_timezone_ids()

        assert ids is not None
        assert len(ids) > 300
        assert ids[0].windows_id == "Dateline Standard Time"
        assert ids[0].territory == "001"
        assert len(ids[0].iana_ids) == 1
        assert ids[0].iana_ids[0] == "Etc/GMT+12"

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_iana_timezone_ids(self, **kwargs):
        ids = self.client.get_iana_timezone_ids()

        assert ids is not None
        assert len(ids) > 300
        assert ids[0].id == "Africa/Accra"
        assert ids[0].is_alias is True
        assert ids[0].alias_of == "Africa/Abidjan"
        assert ids[0].has_zone1970_location is True

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_get_iana_version(self, **kwargs):
        version = self.client.get_iana_version()

        assert version.version == "2022c"

    @MapsTimezonePreparer()
    @recorded_by_proxy
    def test_convert_windows_timezone_to_iana(self, **kwargs):
        iana = self.client.convert_windows_timezone_to_iana(windows_timezone_id="pacific standard time")

        assert len(iana) == 3
        assert iana[0].id == "America/Vancouver"
        assert iana[0].is_alias is False
        assert iana[0].has_zone1970_location is True