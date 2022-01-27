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
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

class GetSIPConfigurationSample(object):
    def __init__(self):
        connection_string = os.getenv(
            "COMMUNICATION_SAMPLES_CONNECTION_STRING")
        self._client = SipRoutingClient.from_connection_string(
            connection_string)

    def get_sip_configuration_sample(self):
        configuration = self._client.get_sip_configuration()
        print(configuration)

if __name__ == '__main__':
    sample = GetSIPConfigurationSample()
    sample.get_sip_configuration_sample()