# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: set_sip_routes_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for replacing current
    configuration of SIP routes with new values.

USAGE:
    python set_sip_routes_sample.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunkRoute

ROUTES = [SipTrunkRoute(name="First rule", description="Handle numbers starting with '+123'", number_pattern="\+123[0-9]+", trunks=["sbs1.sipsampletest.com"])]
connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)

def set_sip_routes_sample():
    client.set_routes(ROUTES)

if __name__ == "__main__":
    set_sip_routes_sample()
