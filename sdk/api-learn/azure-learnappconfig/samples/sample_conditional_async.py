import asyncio
import os
from colorama import init, Style, Fore
init()

from azure.identity.aio import DefaultAzureCredential
from azure.learnappconfig.aio import AppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError, ResourceNotModifiedError
from azure.core import MatchConditions

async def main():
    endpoint = os.environ['API-LEARN_ENDPOINT']
    credentials = DefaultAzureCredential()
    client = AppConfigurationClient(endpoint, credentials)

    # Retrieve initial color value
    try:
        first_color = await client.get_configuration_setting(os.environ['API-LEARN_SETTING_COLOR_KEY'])
    except ResourceNotFoundError:
        raise

    # Get latest color value, only if it has changed
    try:
        new_color = await client.get_configuration_setting(
            key=os.environ['API-LEARN_SETTING_COLOR_KEY'],
            match_condition=MatchConditions.IfModified,
            etag=first_color.etag
        )
    except ResourceNotModifiedError:
        new_color = first_color

    color = getattr(Fore, new_color.value.upper())
    print(f'{color}Hello!{Style.RESET_ALL}')