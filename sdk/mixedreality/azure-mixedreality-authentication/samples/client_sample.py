
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: client_sample.py
DESCRIPTION:
    These samples demonstrate creating a client and requesting a token.

USAGE:
    python client_sample.py
    Set the environment variables with your own values before running the sample:
    1) MIXEDREALITY_ACCOUNT_DOMAIN - the Mixed Reality account domain.
    2) MIXEDREALITY_ACCOUNT_ID - the Mixed Reality account identifier.
    3) MIXEDREALITY_ACCOUNT_KEY - the Mixed Reality account primary or secondary key.
"""


import os


class ClientSamples(object):
    from azure.core.credentials import AzureKeyCredential

    account_domain = os.environ.get("MIXEDREALITY_ACCOUNT_DOMAIN", None)
    if not account_domain:
        raise ValueError("Set MIXEDREALITY_ACCOUNT_DOMAIN env before run this sample.")

    account_id = os.environ.get("MIXEDREALITY_ACCOUNT_ID", None)
    if not account_id:
        raise ValueError("Set MIXEDREALITY_ACCOUNT_ID env before run this sample.")

    account_key = os.environ.get("MIXEDREALITY_ACCOUNT_KEY", None)
    if not account_key:
        raise ValueError("Set MIXEDREALITY_ACCOUNT_KEY env before run this sample.")

    key_credential = AzureKeyCredential(account_key)

    def create_client(self):
        # [START create_client]
        from azure.mixedreality.authentication import MixedRealityStsClient
        client = MixedRealityStsClient(self.account_id, self.account_domain, self.key_credential)
        # [END create_client]

        print("client created")

    def get_token(self):
        # [START get_token]
        from azure.mixedreality.authentication import MixedRealityStsClient
        client = MixedRealityStsClient(self.account_id, self.account_domain, self.key_credential)
        access_token = client.get_token()
        # [END get_token]

        print("token retrieved: " + access_token.token)


if __name__ == '__main__':
    sample = ClientSamples()
    sample.create_client()
    sample.get_token()
