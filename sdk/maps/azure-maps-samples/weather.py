# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import os

from azure.maps.weather import WeatherClient
from azure.maps.weather.models import ResponseFormat


parser = argparse.ArgumentParser(
    description='Weather Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = WeatherClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

print("Get Current Conditions")
print(client.weather.get_current_conditions(
    ResponseFormat.JSON, "47.641268,-122.125679"))


print("Get Daily Forecast")
print(client.weather.get_daily_forecast(
    ResponseFormat.JSON, "62.6490341,30.0734812", duration=5))


print("Get Daily Indices")
print(client.weather.get_daily_indices(
    ResponseFormat.JSON, "43.84745,-79.37849", index_group_id=11))


print("Get Hourly Forecast")
print(client.weather.get_hourly_forecast(
    ResponseFormat.JSON, "47.632346,-122.138874", duration=12))


print("Get Minute Forecast")
print(client.weather.get_minute_forecast(
    ResponseFormat.JSON, "47.632346,-122.138874", interval=15))


print("Get Quarter Day Forecast")
print(client.weather.get_quarter_day_forecast(
    ResponseFormat.JSON, "47.632346,-122.138874", duration=1))


print("Get Severe Weather Alerts")
print(client.weather.get_severe_weather_alerts(
    ResponseFormat.JSON, "48.057,-81.091"))


print("Get Weather Along Route")
print(client.weather.get_weather_along_route(
    ResponseFormat.JSON, "38.907,-77.037,0:38.907,-77.009,10:38.926,-76.928,20:39.033,-76.852,30:39.168,-76.732,40:39.269,-76.634,50:39.287,-76.612,60"))
