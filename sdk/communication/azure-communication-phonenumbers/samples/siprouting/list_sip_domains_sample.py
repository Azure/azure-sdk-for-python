# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_sip_domains_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for retrieving the collection of
    currently configured SIP domains.

USAGE:
    python list_sip_domains_sample.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)


def list_sip_domains_sample():
    sip_domains = client.list_domains()

    for domain in sip_domains:
        print(domain.fqdn)
        print(domain.enabled)


if __name__ == "__main__":
    list_sip_domains_sample()
