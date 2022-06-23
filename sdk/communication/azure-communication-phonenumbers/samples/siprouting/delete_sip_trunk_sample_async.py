# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: delete_sip_trunk_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for deleting the configuration
    of a single SIP trunk.

USAGE:
    python delete_sip_trunk_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_TRUNK_FQDN - fqdn of the trunk to be deleted
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)

async def delete_sip_trunk_sample():
    trunk_fqdn = os.getenv("COMMUNICATION_SAMPLES_TRUNK_FQDN")
    async with client:
        await client.delete_trunk(trunk_fqdn)

if __name__ == "__main__":
    asyncio.run(delete_sip_trunk_sample())