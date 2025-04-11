# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_client_side_encryption_keyvault.py

DESCRIPTION:
    This sample contains code demonstrating how to configure the storage blob
    service for client side encryption, storing and retrieving the key encryption key
    (kek) from within Azure KeyVault. This sample requires a service principal be set
    configured with access to KeyVault, and that the vault contains a 256-bit base64-
    encoded key named "symmetric-key". Additionally, a number of environment
    variables, listed below, must be set. Since these often contain sensitive information,
    they SHOULD NOT be replaced with hardcoded values in any code derived from this sample.

USAGE: python blob_samples_client_side_encryption_keyvault.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_ACCOUNT_URL - the storage account url
    2) AZURE_KEYVAULT_DNS_NAME: The keyvault account dns name
"""

import os
import sys
import uuid

from azure.identity import DefaultAzureCredential

from azure.keyvault.keys.crypto import CryptographyClient, KeyWrapAlgorithm
from azure.keyvault.keys import KeyClient

from azure.storage.blob import BlobServiceClient

# Environment variable keys which must be set to run this sample
STORAGE_URL = 'STORAGE_ACCOUNT_BLOB_URL'
KEYVAULT_URL = 'KEYVAULT_URL'

def get_env_var(key):
    try:
        return os.environ[key]
    except KeyError:
        print('{} must be set.'.format(key))
        sys.exit(1)

def make_resource_name(prefix):
    return '{}{}'.format(prefix, str(uuid.uuid4()).replace('-', ''))

class KeyWrapper:
    """ Class that fulfills the interface used by the storage SDK's
        automatic client-side encyrption and decryption routines. """

    def __init__(self, kek, credential):
        self.algorithm = KeyWrapAlgorithm.rsa_oaep_256
        self.kek = kek
        self.kid = kek.id
        self.client = CryptographyClient(kek, credential)

    def wrap_key(self, key):
        if self.algorithm != KeyWrapAlgorithm.rsa_oaep_256:
            raise ValueError('Unknown key wrap algorithm. {}'.format(self.algorithm))
        wrapped = self.client.wrap_key(key=key, algorithm=self.algorithm)
        return wrapped.encrypted_key

    def unwrap_key(self, key, _):
        if self.algorithm != KeyWrapAlgorithm.rsa_oaep_256:
            raise ValueError('Unknown key wrap algorithm. {}'.format(self.algorithm))
        unwrapped = self.client.unwrap_key(encrypted_key=key, algorithm=self.algorithm)
        return unwrapped.key

    def get_key_wrap_algorithm(self):
        return self.algorithm

    def get_kid(self):
        return self.kid

# Retrieve sensitive data from environment variables
storage_url = get_env_var(STORAGE_URL)
keyvault_url = get_env_var(KEYVAULT_URL)

# Construct a token credential for use by Storage and KeyVault clients.
credential = DefaultAzureCredential()
key_client = KeyClient(keyvault_url, credential=credential)

# The key is url-safe base64 encoded bytes
kvk = key_client.create_rsa_key(name="symmetric-key", size=2048, key_operations=["unwrapKey", "wrapKey"])
kek = KeyWrapper(kvk, credential)

storage_client = BlobServiceClient(storage_url, credential=credential)
container_name = make_resource_name('container')
blob_name = make_resource_name('blob')

container_client = storage_client.get_container_client(container_name)
container_client.key_encryption_key = kek
container_client.encryption_version = '2.0'
container_client.create_container()
try:
    container_client.upload_blob(blob_name, 'This is my blob.')

    # Download without decrypting
    container_client.key_encryption_key = None
    result = container_client.get_blob_client(blob_name).download_blob().readall()
    print(result)

    # Download and decrypt
    container_client.key_encryption_key = kek
    result = container_client.get_blob_client(blob_name).download_blob().readall()
    print(result)

finally:
    # Clean up the container
    container_client.delete_container()
