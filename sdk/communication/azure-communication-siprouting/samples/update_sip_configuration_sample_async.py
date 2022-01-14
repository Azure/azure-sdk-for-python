# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: update_sip_configuration_samples_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for updating the
    SIP configuration.

USAGE:
    python update_sip_configuration_samples_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - the connection string in your ACS account
    2) SAMPLE_TRUNK_NAME - the name of the SIP trunk
    3) SAMPLE_TRUNK_SIP_PORT - the number of the SIP trunk port
    4) SAMPLE_TRUNK_ROUTE_NAME - the name of the SIP trunk route
    5) SAMPLE_NUMBER_PATTERN - the number pattern of the SIP trunk route
"""

import os
import asyncio
from azure.communication.siprouting.aio import SipRoutingClient
from azure.communication.siprouting._generated.models import SipConfiguration, Trunk, TrunkRoute


class UpdateSIPConfigurationSampleAsync(object):
    def __init__(self):
        connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
        self._client = SipRoutingClient.from_connection_string(connection_string)

    async def update_sip_configuration_sample(self):
        test_trunks = {
            os.getenv("SAMPLE_TRUNK_NAME"): Trunk(
                sip_signaling_port=int(os.getenv("SAMPLE_TRUNK_SIP_PORT"))
            )
        }
        test_trunk_routes = [
            TrunkRoute(
                name=os.getenv("SAMPLE_TRUNK_ROUTE_NAME"),
                number_pattern=os.getenv("SAMPLE_NUMBER_PATTERN"),
                trunks=[os.getenv("SAMPLE_TRUNK_NAME")],
            )
        ]

        response = await self._client.update_sip_configuration(
            SipConfiguration(trunks=test_trunks, routes=test_trunk_routes)
        )
        print(response)

    async def update_sip_trunks_sample(self):
        test_trunks = {
            os.getenv("SAMPLE_TRUNK_NAME"): Trunk(
                sip_signaling_port=(int(os.getenv("SAMPLE_TRUNK_SIP_PORT")))
            )
        }

        response = await self._client.update_sip_configuration(trunks=test_trunks)
        print(response)

    async def update_sip_routes_sample(self):
        test_trunk_routes = [
            TrunkRoute(
                name=os.getenv("SAMPLE_TRUNK_ROUTE_NAME"),
                number_pattern=os.getenv("SAMPLE_NUMBER_PATTERN"),
                trunks=[os.getenv("SAMPLE_TRUNK_NAME")],
            )
        ]

        response = await self._client.update_sip_configuration(routes=test_trunk_routes)
        print(response)


if __name__ == "__main__":
    sample = UpdateSIPConfigurationSampleAsync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.update_sip_configuration_sample())
    loop.run_until_complete(sample.update_sip_trunks_sample())
    loop.run_until_complete(sample.update_sip_routes_sample())
    loop.run_until_complete(sample._client.close())
