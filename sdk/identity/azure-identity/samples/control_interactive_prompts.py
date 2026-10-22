# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates controlling the timing of interactive authentication using InteractiveBrowserCredential.

DeviceCodeCredential supports the same API.
"""

import os
import sys
from azure.identity import AuthenticationRequiredError, InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient


# This sample uses Key Vault only for demonstration. Any client accepting azure-identity credentials will work the same.
VAULT_URL = os.environ.get("VAULT_URL")
if not VAULT_URL:
    print("This sample expects environment variable 'VAULT_URL' to be set with the URL of a Key Vault.")
    sys.exit(1)

# If it's important for your application to prompt for authentication only at certain times,
# create the credential with disable_automatic_authentication=True. This configures the credential to raise
# when interactive authentication is required, instead of immediately beginning that authentication.
credential = InteractiveBrowserCredential(disable_automatic_authentication=True)
client = SecretClient(VAULT_URL, credential)

try:
    secret_names = [s.name for s in client.list_properties_of_secrets()]
except AuthenticationRequiredError as ex:
    # Interactive authentication is necessary to authorize the client's request. The exception carries the
    # requested authentication scopes as well as any additional claims the service requires. If you pass
    # both to 'authenticate', it will cache an access token for the necessary scopes.
    credential.authenticate(scopes=ex.scopes, claims=ex.claims)

# the client operation should now succeed
secret_names = [s.name for s in client.list_properties_of_secrets()]
