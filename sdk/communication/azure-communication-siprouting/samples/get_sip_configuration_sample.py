# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_sip_configuration_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for retrieving the
    SIP configuration.

USAGE:
    python get_sip_configuration_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING - the connection string in your ACS account
"""

import os

from azure.communication.siprouting import SIPRoutingClient

def get_sip_configuration_sample():
    connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
    sip_routing_client = SIPRoutingClient.from_connection_string(connection_string)
    
    configuration = sip_routing_client.get_sip_configuration()
    print(configuration)

if __name__ == '__main__':
    get_sip_configuration_sample()