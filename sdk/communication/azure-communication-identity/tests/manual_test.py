# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# from azure.core.credentials import AccessToken
#from token_exchange import TokenExchangeClient
#from entra_token_credential_options import EntraCommunicationTokenCredentialOptions
from azure.communication.identity import *
from azure.core.credentials import AccessToken
#from azure.identity import DefaultAzureCredential
from azure.identity import InteractiveBrowserCredential


def main():
    # TODO: Replace these values with your real endpoint and customer token
    endpoint = "https://acs-auth-ppe-us-ops.unitedstates.ppe.communication.azure.net"
    customer_token = ""

    # Set up the required options for TokenExchangeClient
    class CustomTokenCredential:
        def get_token(self, *scopes, **kwargs):
            # Provide a hardcoded token and expiry (e.g., far future timestamp)
            return AccessToken("kk", 9999999999)

    options = EntraCommunicationTokenCredentialOptions(
        resource_endpoint=endpoint,
        scopes=["https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"],
        token_credential=InteractiveBrowserCredential(redirect_uri="http://localhost", tenant_id="be5c2424-1562-4d62-8d98-815720d06e4a", client_id="c6ec4113-4e29-48a9-a814-e9df50ca033e")
    )

    client = TokenExchangeClient(options)
    try:
        access_token = client._exchange_entra_token()
        print("Access Token:", access_token.token)
        print("Expires On:", access_token.expires_on)
    except Exception as ex:
        print("Token exchange failed:", ex)


if __name__ == "__main__":
    main()
