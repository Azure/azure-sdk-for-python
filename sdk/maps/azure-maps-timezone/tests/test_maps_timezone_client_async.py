# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.timezone.aio import AzureTimezoneClient
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async

from timezone_preparer import MapsTimezonePreparer


# cSpell:disable
class TestMapsTimezoneClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = AzureTimezoneClient(
            credential=AzureKeyCredential(os.getenv("AZURE_SUBSCRIPTION_KEY", "AzureSubscriptionKey"))
        )
        assert self.client is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_get_timezone_by_coordinates(self):
        async with self.client:
            result = await self.client.get_timezone_by_coordinates(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_get_timezone_by_id(self):
        async with self.client:
            result = await self.client.get_timezone_by_id(timezone_id="sr-Latn-RS")
            assert result is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_get_iana_version(self):
        async with self.client:
            result = await self.client.get_iana_version()
            assert result is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_get_iana_timezone_ids(self):
        async with self.client:
            result = self.client.get_iana_timezone_ids()
            assert result is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_get_windows_timezone_ids(self):
        async with self.client:
            result = await self.client.get_windows_timezone_ids()
            assert result is not None

    @MapsTimezonePreparer()
    @recorded_by_proxy_async
    async def test_convert_windows_timezone_to_iana(self):
        async with self.client:
            result = await self.client.convert_windows_timezone_to_iana(windows_timezone_id="Pacific Standard Time")
            assert result is not None
