# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: set_sip_trunk_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for setting the configuration
    of a single SIP trunk.

USAGE:
    python set_sip_trunk_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_TRUNK - SipTrunk object to be set
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient

class SetSipTrunkSampleAsync(object):
    def __init__(self):
        connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
        self._client = SipRoutingClient.from_connection_string(connection_string)

    async def set_sip_trunk_sample(self):
        sip_trunk = os.getenv("COMMUNICATION_SAMPLES_TRUNK")
        await self._client.set_trunk(sip_trunk)
        
if __name__ == "__main__":
    sample = SetSipTrunkSampleAsync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample.set_sip_trunk_sample())
    loop.run_until_complete(sample._client.close())
