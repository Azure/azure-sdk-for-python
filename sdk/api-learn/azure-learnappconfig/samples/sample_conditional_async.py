# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import os
from colorama import init, Style, Fore
init()

from azure.identity.aio import DefaultAzureCredential
from azure.learnappconfig.aio import AppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError, ResourceNotModifiedError
from azure.core import MatchConditions


async def main():
    url = os.environ.get('API-LEARN_ENDPOINT')
    credential = DefaultAzureCredential()
    async with AppConfigurationClient(account_url=url, credential=credential) as client:

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
        greeting = 'Hello!'
        print(f'{color}{greeting}{Style.RESET_ALL}')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
