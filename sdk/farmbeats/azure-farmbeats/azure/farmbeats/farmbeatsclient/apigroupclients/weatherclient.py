import time
from datetime import datetime, timedelta


class WeatherClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    
    def get_weather_data(
        self,
        farmer_id,
        field_id,
        extension_id,
        weather_data_type,
        granularity,
        start_date_time=None,
        end_date_time=None,
        # limit=1000
    ):
        return self.client.get_weather_data(
            farmer_id,
            field_id,
            extension_id,
            weather_data_type,
            granularity,
            start_date_time,
            end_date_time,
            1000,
        ).value
