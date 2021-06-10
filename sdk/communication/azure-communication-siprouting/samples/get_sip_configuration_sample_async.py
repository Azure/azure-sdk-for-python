# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_sip_configuration_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for retrieving the
    SIP configuration.

USAGE:
    python get_sip_configuration_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - the connection string in your ACS account
"""

import os
import asyncio
from azure.communication.siprouting.aio import SIPRoutingClient


class GetSIPConfigurationSampleAsync(object):
    def __init__(self):
        connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
        self._client = SIPRoutingClient.from_connection_string(connection_string)

    async def get_sip_configuration_sample(self):
        configuration = await self._client.get_sip_configuration()
        print(configuration)


if __name__ == "__main__":
    sample = GetSIPConfigurationSampleAsync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.get_sip_configuration_sample())
    loop.run_until_complete(sample._client.close())
