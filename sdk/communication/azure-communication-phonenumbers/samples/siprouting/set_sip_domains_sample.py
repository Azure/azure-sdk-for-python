# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: set_sip_domains_sample.py
DESCRIPTION:
    This sample shows the usage of SIP routing client for replacing the collection of
    currently configured SIP domains with new values.

USAGE:
    python set_sip_domains_sample.py
        Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS account
    2) COMMUNICATION_SAMPLES_DOMAIN_FQDN - FQDN of SipDomain object to be set
"""

import os
from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipDomain

connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
client = SipRoutingClient.from_connection_string(connection_string)
fqdn = os.getenv("COMMUNICATION_SAMPLES_DOMAIN_FQDN")
DOMAINS = [SipDomain(fqdn=fqdn, enabled=True)]


def set_sip_domains_sample():
    client.set_domains(DOMAINS)


if __name__ == "__main__":
    set_sip_domains_sample()
