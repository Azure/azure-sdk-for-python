# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates user authentication using InteractiveBrowserCredential. DeviceCodeCredential supports the same API."""

import os
import sys
from azure.identity import AuthenticationRecord, InteractiveBrowserCredential, TokenCachePersistenceOptions
from azure.keyvault.secrets import SecretClient


# This sample uses Key Vault only for demonstration. Any client accepting azure-identity credentials will work the same.
VAULT_URL = os.environ.get("VAULT_URL")
if not VAULT_URL:
    print("This sample expects environment variable 'VAULT_URL' to be set with the URL of a Key Vault.")
    sys.exit(1)


# Persistent caching is optional. By default, interactive credentials cache in memory only.
# To enable persistent caching, give the credential an instance of TokenCachePersistenceOptions.
# (see the API documentation for more information about TokenCachePersistenceOptions)
credential = InteractiveBrowserCredential(cache_persistence_options=TokenCachePersistenceOptions())

# The 'authenticate' method begins interactive authentication. Call it whenever it's convenient
# for your application to authenticate a user. It returns a record of the authentication.
record = credential.authenticate()
print("\nAuthenticated first credential")

# The record contains no authentication secrets. You can serialize it to JSON for storage.
record_json = record.serialize()

# An authenticated credential is ready for use with a client. This request should succeed
# without prompting for authentication again.
client = SecretClient(VAULT_URL, credential)
secret_names = [s.name for s in client.list_properties_of_secrets()]
print("\nCompleted request with first credential")

# An authentication record stored by your application enables other credentials to access data from
# past authentications. If the cache contains sufficient data, this eliminates the need for your
# application to prompt for authentication every time it runs.
deserialized_record = AuthenticationRecord.deserialize(record_json)
new_credential = InteractiveBrowserCredential(
    cache_persistence_options=TokenCachePersistenceOptions(), authentication_record=deserialized_record
)

# This request should also succeed without prompting for authentication.
client = SecretClient(VAULT_URL, new_credential)
secret_names = [s.name for s in client.list_properties_of_secrets()]
print("\nCompleted request with credential using shared cache")

# To isolate the token cache from other applications, you can provide a cache name to TokenCachePersistenceOptions.
separate_cache_credential = InteractiveBrowserCredential(
    cache_persistence_options=TokenCachePersistenceOptions(name="my_app"), authentication_record=deserialized_record
)

# This request should prompt for authentication since the credential is using a separate cache.
client = SecretClient(VAULT_URL, separate_cache_credential)
secret_names = [s.name for s in client.list_properties_of_secrets()]
print("\nCompleted request with credential using separate cache")
