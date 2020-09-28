# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import os
import colorama

from azure.appconfiguration.aio import AppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError, ResourceNotModifiedError
from azure.core import MatchConditions


async def main():
    connection_string = os.environ.get('APP_CONFIG_CONN_STR')
    client = AppConfigurationClient.from_connection_string(connection_string)

    # Retrieve initial color value
    try:
        first_color = await client.get_configuration_setting('FontColor')
    except ResourceNotFoundError:
        raise
    
    # Get latest color value, only if it has changed
    try:
        new_color = await client.get_configuration_setting(
            key='FontColor',
            match_condition=MatchConditions.IfModified,
            etag=first_color.etag
        )
    except ResourceNotModifiedError:
        new_color = first_color

    print(f'{new_color.value}Hello!{colorama.Style.RESET_ALL}')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())