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
    2) COMMUNICATION_SAMPLES_NEW_ROUTES - the list of new SIP route values
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

class SetSipRoutesSample(object):
    def __init__(self):
        connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
        self._client = SipRoutingClient.from_connection_string(connection_string)

    def set_sip_routes_sample(self):
        new_routes = os.getenv("COMMUNICATION_SAMPLES_NEW_ROUTES")
        sip_routes = self._client.set_routes(new_routes)

        for route in sip_routes:
            print(route.name)
            print(route.description)
            print(route.number_pattern)
            
            for trunk_fqdn in route.trunks:
                print(trunk_fqdn)

if __name__ == "__main__":
    sample = SetSipRoutesSample()
    sample.set_sip_routes_sample()
