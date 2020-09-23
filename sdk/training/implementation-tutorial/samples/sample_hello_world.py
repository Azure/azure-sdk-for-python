# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import colorama

from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError

def main():
    endpoint = os.environ['APP_CONFIG_URL']
    credentials = DefaultAzureCredential()
    client = AppConfigurationClient(endpoint, credentials)

    try:
        color_setting = client.get_configuration_setting('FontColor')
        color = color_setting.value
        text_setting = client.get_configuration_setting('Greeting')
        greeting = text_setting.value
    except ResourceNotFoundError:
        color = '\x1b[32m'
        greeting = 'Default greeting'

    print(f'{color}{greeting}{colorama.Style.RESET_ALL}')


if __name__ == "__main__":
    main()