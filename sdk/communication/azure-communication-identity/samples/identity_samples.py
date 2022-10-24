# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: identity_sample.py
DESCRIPTION:
    These samples demonstrate creating a user, issuing a token, revoking a token and deleting a user.

USAGE:
    python identity_samples.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your Communication Services resource
    2) AZURE_CLIENT_ID - the client ID of your active directory application
    3) AZURE_CLIENT_SECRET - the secret of your active directory application
    4) AZURE_TENANT_ID - the tenant ID of your active directory application
    5) COMMUNICATION_M365_APP_ID - the application id of Microsoft 365
    6) COMMUNICATION_M365_AAD_AUTHORITY - the Azure AD authority of Microsoft 365  
    7) COMMUNICATION_M365_AAD_TENANT - the tenant ID of Microsoft 365 application
    8) COMMUNICATION_MSAL_USERNAME - the username for authenticating via MSAL library
    9) COMMUNICATION_MSAL_PASSWORD - the password for authenticating via MSAL library
"""
from datetime import timedelta
import os
from azure.communication.identity._shared.utils import parse_connection_str
from msal import PublicClientApplication
class CommunicationIdentityClientSamples(object):

    def __init__(self):
        self.connection_string = os.getenv('COMMUNICATION_SAMPLES_CONNECTION_STRING')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.m365_client_id = os.getenv('COMMUNICATION_M365_APP_ID') 
        self.m365_aad_authority = os.getenv('COMMUNICATION_M365_AAD_AUTHORITY') 
        self.m365_aad_tenant = os.getenv('COMMUNICATION_M365_AAD_TENANT')
        self.msal_username = os.getenv('COMMUNICATION_MSAL_USERNAME') 
        self.msal_password = os.getenv('COMMUNICATION_MSAL_PASSWORD')

    def get_token(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        print("Getting token for: " + user.properties.get('id'))
        tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        print("Token issued with value: " + tokenresponse.token)
        
    def get_token_with_custom_expiration(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        print("Getting token for: " + user.properties.get('id'))
        token_expires_in = timedelta(hours=1)
        tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in)
        print("Issued token with custom expiration" + tokenresponse.token)

    def revoke_tokens(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        print("Revoking token: " + tokenresponse.token)
        identity_client.revoke_tokens(user)
        print(tokenresponse.token + " revoked successfully")

    def create_user(self):
        from azure.communication.identity import CommunicationIdentityClient

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        print("Creating new user")
        user = identity_client.create_user()
        print("User created with id:" + user.properties.get('id'))

    def create_user_and_token(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        print("Creating new user with token")
        user, tokenresponse = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        print("User created with id:" + user.properties.get('id'))
        print("Token issued with value: " + tokenresponse.token)
        
    def create_user_and_token_with_custom_expiration(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        print("Creating new user with token")
        token_expires_in = timedelta(hours=1)
        user, tokenresponse = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in)
        print("User created with id:" + user.properties.get('id'))
        print("Issued token with custom expiration: " + tokenresponse.token)

    def delete_user(self):
        from azure.communication.identity import CommunicationIdentityClient

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        print("Deleting user: " + user.properties.get('id'))
        identity_client.delete_user(user)
        print(user.properties.get('id') + " deleted")

    def get_token_for_teams_user(self):
        if (os.getenv("SKIP_INT_IDENTITY_EXCHANGE_TOKEN_TEST") == "true"):
            print("Skipping the Get Access Token for Teams User sample")
            return
        from azure.communication.identity import CommunicationIdentityClient

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        
        msal_app = PublicClientApplication(client_id=self.m365_client_id, authority="{}/{}".format(self.m365_aad_authority, self.m365_aad_tenant))
        scopes = [ 
            "https://auth.msft.communication.azure.com/Teams.ManageCalls",
            "https://auth.msft.communication.azure.com/Teams.ManageChats"
        ]
        result = msal_app.acquire_token_by_username_password(
            username=self.msal_username,
            password=self.msal_password,
            scopes=scopes)
        aad_token =  result["access_token"]
        teams_user_oid = result["id_token_claims"]["oid"] 
        print("AAD access token of a Teams User: " + aad_token)

        tokenresponse = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, teams_user_oid)
        print("Token issued with value: " + tokenresponse.token)


if __name__ == '__main__':
    sample = CommunicationIdentityClientSamples()
    sample.create_user()
    sample.create_user_and_token()
    sample.get_token()
    sample.revoke_tokens()
    sample.delete_user() 
    sample.get_token_for_teams_user()
