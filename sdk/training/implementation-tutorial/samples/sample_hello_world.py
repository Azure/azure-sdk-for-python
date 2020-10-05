# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from colorama import init, Style
init()

from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError

def main():
    url = os.environ.get('APP_CONFIG_URL')
    credential = DefaultAzureCredential()
    client = AppConfigurationClient(account_url=url, credential=credential)

    try:
        color_setting = client.get_configuration_setting('FontColor')
        color = color_setting.value
        text_setting = client.get_configuration_setting('Greeting')
        greeting = text_setting.value
    except ResourceNotFoundError:
        color = '\033[31m'
        greeting = 'Default greeting'

    print(f'{color}{greeting}{Style.RESET_ALL}')


if __name__ == "__main__":
    main()