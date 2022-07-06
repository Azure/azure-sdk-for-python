# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_sip_trunk_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for retrieving the configuration
    of a single SIP trunk.

USAGE:
    python get_sip_trunk_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_TRUNK_FQDN - fqdn of the trunk to be retrieved
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)

async def get_sip_trunk_sample():
    trunk_fqdn = os.getenv("COMMUNICATION_SAMPLES_TRUNK_FQDN")
    async with client:
        sip_trunk = await client.get_trunk(trunk_fqdn)
    print(sip_trunk.fqdn)
    print(sip_trunk.sip_signaling_port)

if __name__ == "__main__":
    asyncio.run(get_sip_trunk_sample())
