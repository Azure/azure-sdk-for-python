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
    2) COMMUNICATION_SAMPLES_FQDN - FQDN of SipTrunk object to be set
    3) COMMUNICATION_SAMPLES_SIGNALING_PORT - SIP signaling port of SipTrunk object to be set
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting import SipTrunk

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
fqdn = os.getenv("COMMUNICATION_SAMPLES_FQDN")
signaling_port = os.getenv("COMMUNICATION_SAMPLES_SIGNALING_PORT")
client = SipRoutingClient.from_connection_string(connection_string)
new_trunk = SipTrunk(fqdn=fqdn, sip_signaling_port=signaling_port)

async def set_sip_trunk_sample():
    async with client:
        await client.set_trunk(new_trunk)

if __name__ == "__main__":
    asyncio.run(set_sip_trunk_sample())

