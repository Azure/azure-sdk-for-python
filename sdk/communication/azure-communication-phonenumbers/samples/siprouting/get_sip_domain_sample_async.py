# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_sip_domain_sample_async.py
DESCRIPTION:
    This sample shows the usage of asynchronous SIP routing client for retrieving the configuration
    of a single SIP domain.

USAGE:
    python get_sip_domain_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_DOMAIN_FQDN - fqdn of the domain to be retrieved
"""

import os
import asyncio
from azure.communication.phonenumbers.siprouting.aio import SipRoutingClient

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)


async def get_sip_domain_sample():
    domain_fqdn = os.getenv("COMMUNICATION_SAMPLES_DOMAIN_FQDN")
    try:
        async with client:
            sip_domain = await client.get_domain(domain_fqdn)
        print(sip_domain.fqdn)
        print(sip_domain.enabled)
    except KeyError:
        print("Domain not found")


if __name__ == "__main__":
    asyncio.run(get_sip_domain_sample())
