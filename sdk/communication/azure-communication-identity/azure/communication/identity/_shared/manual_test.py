# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# from azure.core.credentials import AccessToken
from token_exchange import TokenExchangeClient
from azure.core.credentials import AccessToken
from user_credential import CommunicationTokenCredential
#from user_credential_async import CommunicationTokenCredential
import asyncio


def main():
    # TODO: Replace these values with your real endpoint and customer token
    endpoint = "https://acs-auth-ppe-us-ops.unitedstates.ppe.communication.azure.net"
    customer_token = ""

    # Set up the required options for TokenExchangeClient
    class CustomTokenCredential:
        def get_token(self, *scopes, **kwargs):
            # Provide a hardcoded token and expiry (e.g., far future timestamp)
            return AccessToken("entra_token", 9999999999)


        #token_credential=InteractiveBrowserCredential(redirect_uri="http://localhost", tenant_id="be5c2424-1562-4d62-8d98-815720d06e4a", client_id="c6ec4113-4e29-48a9-a814-e9df50ca033e")


    #credentialOld = CommunicationTokenCredential(token="skypetoken")
    # Example usage of user_credential_async.get_token (assuming user_credential_async is defined/imported)
    # Initialize the credential with resource_endpoint and custom token_credential
    credential = CommunicationTokenCredential(
        resource_endpoint=endpoint,
        token_credential=CustomTokenCredential(),
        scopes=["https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"]
    )

        # Example call to get_token (update scopes as needed)
    token = credential.get_token("https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls")
    print("User Credential Async Token:", token.token)

    token = credential.get_token("https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls")
    print("User Credential Async Token:", token.token)

    async def get_async_token():
        token = await credential.get_token("https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls")
        print("User Credential Async Token (async):", token.token)

        token = await credential.get_token("https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls")
        print("User Credential Async Token (async):", token.token)

    asyncio.run(get_async_token())

    client = TokenExchangeClient(resource_endpoint=endpoint, token_credential=CustomTokenCredential(), scopes=["https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"],)
    try:
        access_token = client.exchange_entra_token()
        print("Access Token:", access_token.token)
        print("Expires On:", access_token.expires_on)
    except Exception as ex:
        print("Token exchange failed:", ex)


if __name__ == "__main__":
    main()
