# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.core.rest import HttpRequest
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://learn.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, get, and delete permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the `send_request` method for making custom HTTP requests using a client pipeline.
#
# 1. Create a new key (create_rsa_key)
#
# 2. Get an existing key (send_request)
#
# 3. Delete a key (begin_delete_key)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a key client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)

# First, create a key with a standard client method. We'll create an RSA key that has default attributes.
print("\n.. Create a key")
key_name = "sampleKey"
key = client.create_rsa_key(key_name)
print(f"\n.. RSA key with name {key.name} created")

# Other Key Vault client methods are convenient, but the `send_request` method offers flexibility.
# The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
# while adding convenience for endpoint construction and service API versioning.
# See the Key Vault REST API reference at https://learn.microsoft.com/rest/api/keyvault

# Now let's use the `send_request` method to make a key fetching request.
# The URL of the request can be relative (your vault endpoint is the default base URL),
# and the API version of your client will automatically be used for the request.
print("\n.. Get a key with the `send_request` method")
request = HttpRequest("GET", f"keys/{key.name}/{key.properties.version}")
response = client.send_request(request)

# The return value is an azure.core.rest.HttpResponse -- the key information is in the response body.
# We can get a dictionary of the body content with the `json` method. 
response_body = response.json()
print(f"\n.. Key with ID {response_body['key']['kid']} was found.")

# The sample key isn't needed anymore; we can delete it with a client convenience method.
print("\n.. Delete the key")
client.begin_delete_key(key.name)
print(f"\n.. Deleted key {key.name}")
