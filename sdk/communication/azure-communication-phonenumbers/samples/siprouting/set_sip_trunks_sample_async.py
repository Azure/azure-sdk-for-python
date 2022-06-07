# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: set_sip_trunks_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for replacing the collection of
    currently configured SIP trunks with new values.

USAGE:
    python set_sip_trunks_sample_async.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient
from azure.communication.phonenumbers.siprouting import SipTrunk

TRUNKS = [SipTrunk(fqdn="sbs1.sipsampletest.com", sip_signaling_port=1122), SipTrunk(fqdn="sbs2.sipsampletest.com", sip_signaling_port=1123)]
connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)

async def set_sip_trunks_sample():
    async with client:
        await client.set_trunks(TRUNKS)

if __name__ == "__main__":
    asyncio.run(set_sip_trunks_sample())

