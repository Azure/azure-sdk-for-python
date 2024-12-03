# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.maps.weather.aio import MapsWeatherClient
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async

from weather_preparer import MapsWeatherPreparer


# cSpell:disable
class TestMapsWeatherClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsWeatherClient(
            credential=AzureKeyCredential(os.getenv("AZURE_SUBSCRIPTION_KEY", "AzureSubscriptionKey"))
        )
        # print(self.client)
        assert self.client is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_air_quality_daily_forecasts(self):
        async with self.client:
            result = await self.client.get_air_quality_daily_forecasts(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_air_quality_daily_forecasts(self):
        async with self.client:
            result = await self.client.get_air_quality_daily_forecasts(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_air_quality_hourly_forecasts(self):
        async with self.client:
            result = await self.client.get_air_quality_hourly_forecasts(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_current_air_quality(self):
        async with self.client:
            result = await self.client.get_current_air_quality(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_current_conditions(self):
        async with self.client:
            result = await self.client.get_current_conditions(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_daily_forecast(self):
        async with self.client:
            result = await self.client.get_daily_forecast(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_daily_historical_actuals(self):
        async with self.client:
            result = await self.client.get_daily_historical_actuals(
                coordinates=[25.0338053, 121.5640089],
                start_date=datetime.date(2020, 2, 2),
                end_date=datetime.date(2020, 2, 8),
            )
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_daily_historical_normals(self):
        async with self.client:
            result = await self.client.get_daily_historical_normals(
                coordinates=[25.0338053, 121.5640089],
                start_date=datetime.date(2020, 2, 2),
                end_date=datetime.date(2020, 2, 8),
            )
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_daily_historical_records(self):
        async with self.client:
            result = await self.client.get_daily_historical_records(
                coordinates=[25.0338053, 121.5640089],
                start_date=datetime.date(2020, 2, 2),
                end_date=datetime.date(2020, 2, 8),
            )
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_daily_indices(self):
        async with self.client:
            result = await self.client.get_daily_indices(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_hourly_forecast(self):
        async with self.client:
            result = await self.client.get_hourly_forecast(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_minute_forecast(self):
        async with self.client:
            result = await self.client.get_minute_forecast(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_quarter_day_forecast(self):
        async with self.client:
            result = await self.client.get_quarter_day_forecast(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_severe_weather_alerts(self):
        async with self.client:
            result = await self.client.get_severe_weather_alerts(coordinates=[25.0338053, 121.5640089])
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_tropical_storm_active(self):
        async with self.client:
            result = await self.client.get_tropical_storm_active()
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_tropical_storm_forecast(self):
        async with self.client:
            result = await self.client.get_tropical_storm_forecast(year=2021, basin_id="NP", government_storm_id=2)
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_tropical_storm_locations(self):
        async with self.client:
            result = await self.client.get_tropical_storm_locations(year=2021, basin_id="NP", government_storm_id=2)
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_tropical_storm_search(self):
        async with self.client:
            result = await self.client.get_tropical_storm_search(year=2022)
            assert result is not None

    @MapsWeatherPreparer()
    @recorded_by_proxy_async
    async def test_get_weather_along_route(self):
        async with self.client:
            result = await self.client.get_weather_along_route(query="25.033075,121.525694,0:25.0338053,121.5640089,2")
            assert result is not None
