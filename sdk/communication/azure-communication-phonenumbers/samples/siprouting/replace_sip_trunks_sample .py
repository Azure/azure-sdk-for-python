# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: replace_sip_trunks_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for replacing the collection of
    currently configured SIP trunks with new values.

USAGE:
    python replace_sip_trunks_sample.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_NEW_TRUNKS - the list of new SIP trunk values
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

class ReplaceSipTrunksSample(object):
    def __init__(self):
        connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
        self._client = SipRoutingClient.from_connection_string(connection_string)

    def replace_sip_trunks_sample(self):
        new_trunks = os.getenv("COMMUNICATION_SAMPLES_NEW_TRUNKS")
        sip_trunks = self._client.replace_trunks(new_trunks)

        for trunk in sip_trunks:
            print(trunk.fqdn)
            print(trunk.sip_signaling_port)

if __name__ == "__main__":
    sample = ReplaceSipTrunksSample()
    sample.replace_sip_trunks_sample()
