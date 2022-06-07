# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_sip_routes_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for retrieving the collection of
    currently configured SIP routes.

USAGE:
    python get_sip_routes_sample.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)

def get_sip_routes_sample():
    sip_routes = client.get_routes()

    for route in sip_routes:
        print(route.name)
        print(route.description)
        print(route.number_pattern)
            
        for trunk_fqdn in route.trunks:
            print(trunk_fqdn)

if __name__ == "__main__":
    get_sip_routes_sample()
