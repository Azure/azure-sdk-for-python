# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    These samples demonstrate authenticating an attestation client instance and
    an attestation administration client instance.

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) ATTESTATION_AAD_URL - the base URL for an attestation service instance in AAD mode.
    2) ATTESTATION_ISOLATED_URL - the base URL for an attestation service instance in Isolated mode.
    3) ATTESTATION_LOCATION_SHORT_NAME - the short name for the region in which the
        sample should be run - used to interact with the shared endpoint for that
        region.
    4) ATTESTATION_TENANT_ID - Tenant Instance for authentication.
    5) ATTESTATION_CLIENT_ID - Client identity for authentication.
    6) ATTESTATION_CLIENT_SECRET - Secret used to identify the client.
"""


from datetime import datetime, timedelta
import os
from dotenv import find_dotenv, load_dotenv
import base64
from sample_utils import write_banner

class AttestationClientCreateSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.aad_url = os.environ.get("ATTESTATION_AAD_URL")
        self.isolated_url = os.environ.get("ATTESTATION_ISOLATED_URL")
        if self.isolated_url:
            self.isolated_certificate = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE"))
            self.isolated_key = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY"))
        shared_short_name  = os.getenv("ATTESTATION_LOCATION_SHORT_NAME")
        self.shared_url = 'https://shared' + shared_short_name + '.' + shared_short_name + '.attest.azure.net'

    def close(self):
        # self._credentials.close()
        pass
        

    def create_attestation_client_aad(self):
        # Instantiate an attestation client using client secrets.

        write_banner("create_attestation_client_aad")
        # [START client_create]
        tenant_id = os.getenv("ATTESTATION_TENANT_ID")
        client_id = os.getenv("ATTESTATION_CLIENT_ID")
        secret = os.getenv("ATTESTATION_CLIENT_SECRET")

        if not tenant_id or not client_id or not secret:
            raise Exception("Must provide client credentials.")

        # Create azure-identity class
        from azure.identity import ClientSecretCredential
        credentials = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=secret)

        # And now create an AttestationClient.
        from azure.security.attestation import AttestationClient

        with AttestationClient(credentials, instance_url=self.aad_url) as client:
            print("Retrieve OpenID metadata from: ", self.aad_url)
            openid_metadata = client.get_openidmetadata()
            print(" Certificate URI: ", openid_metadata["jwks_uri"])
            print(" Issuer: ", openid_metadata["issuer"])

        # [END client_create]

    def create_attestation_client_shared(self):
        # Instantiate an attestation client using client secrets.
        write_banner("create_attestation_client_shared")
        # [START sharedclient_create]
        from azure.security.attestation import AttestationClient

        shared_short_name  = os.getenv("ATTESTATION_LOCATION_SHORT_NAME")
        shared_url = 'https://shared' + shared_short_name + '.' + shared_short_name + '.attest.azure.net'

        tenant_id = os.getenv("ATTESTATION_TENANT_ID")
        client_id = os.getenv("ATTESTATION_CLIENT_ID")
        secret = os.getenv("ATTESTATION_CLIENT_SECRET")

        if not tenant_id or not client_id or not secret:
            raise Exception("Must provide client credentials.")

        # Create azure-identity class
        from azure.identity import ClientSecretCredential
        credentials = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=secret)

        with AttestationClient(credentials, instance_url=shared_url) as client:
            print("Retrieve OpenID metadata from: ", shared_url)
            openid_metadata = client.get_openidmetadata()
            print(" Certificate URI: ", openid_metadata["jwks_uri"])
            print(" Issuer: ", openid_metadata["issuer"])

        # [END shared_client_create]


    def __enter__(self):
        return self

    def __exit__(self, *exc_type):
        self.close()

if __name__ == "__main__":
    with AttestationClientCreateSamples() as sample:
        sample.create_attestation_client_aad()
        sample.create_attestation_client_shared()
