# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_client_side_encryption.py

DESCRIPTION:
    This example contains sample code for the KeyWrapper and KeyResolver classes
    needed to use Storage client side encryption, as well as code that illustrates
    key usage patterns for client side encryption features. This sample expects that
    the `AZURE_STORAGE_CONNECTION_STRING` environment variable is set. It SHOULD NOT
    be hardcoded in any code derived from this sample.

USAGE: python blob_samples_client_side_encryption.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import sys
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import (
    OAEP,
    MGF1,
)
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.keywrap import (
    aes_key_wrap,
    aes_key_unwrap,
)

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError


# Sample implementations of the encryption-related interfaces.
class KeyWrapper:
    def __init__(self, kid):
        self.kek = os.urandom(32)
        self.backend = default_backend()
        self.kid = 'local:' + kid

    def wrap_key(self, key, algorithm='A256KW'):
        if algorithm == 'A256KW':
            return aes_key_wrap(self.kek, key, self.backend)
        raise ValueError('Unknown key wrap algorithm.')

    def unwrap_key(self, key, algorithm):
        if algorithm == 'A256KW':
            return aes_key_unwrap(self.kek, key, self.backend)
        raise ValueError('Unknown key wrap algorithm.')

    def get_key_wrap_algorithm(self):
        return 'A256KW'

    def get_kid(self):
        return self.kid


class KeyResolver:
    def __init__(self):
        self.keys = {}

    def put_key(self, key):
        self.keys[key.get_kid()] = key

    def resolve_key(self, kid):
        return self.keys[kid]


class RSAKeyWrapper:
    def __init__(self, kid):
        self.private_key = generate_private_key(public_exponent=65537,
                                                key_size=2048,
                                                backend=default_backend())
        self.public_key = self.private_key.public_key()
        self.kid = 'local:' + kid

    def wrap_key(self, key, algorithm='RSA'):
        if algorithm == 'RSA':
            return self.public_key.encrypt(key,
                                           OAEP(
                                               mgf=MGF1(algorithm=SHA1()),  # nosec
                                               algorithm=SHA1(),    # nosec
                                               label=None)
                                           )
        raise ValueError('Unknown key wrap algorithm.')

    def unwrap_key(self, key, algorithm):
        if algorithm == 'RSA':
            return self.private_key.decrypt(key,
                                            OAEP(
                                                mgf=MGF1(algorithm=SHA1()), # nosec
                                                algorithm=SHA1(),   # nosec
                                                label=None)
                                            )
        raise ValueError('Unknown key wrap algorithm.')

    def get_key_wrap_algorithm(self):
        return 'RSA'

    def get_kid(self):
        return self.kid


class BlobEncryptionSamples():
    def __init__(self, bsc: BlobServiceClient):
        self.bsc = bsc

    def run_all_samples(self):
        self.put_encrypted_blob()
        self.get_encrypted_blob()
        self.get_encrypted_blob_key_encryption_key()
        self.require_encryption()
        self.alternate_key_algorithms()

    def _get_resource_reference(self, prefix: str) -> str:
        return '{}{}'.format(prefix, str(uuid.uuid4()).replace('-', ''))

    def _get_blob_reference(self, prefix: str = 'blob') -> str:
        return self._get_resource_reference(prefix)

    def _create_container(self, prefix: str = 'container') -> str:
        container_name = self._get_resource_reference(prefix)
        self.container_client = self.bsc.get_container_client(container_name)
        self.container_client.create_container()
        return container_name

    def put_encrypted_blob(self):
        self._create_container()
        try:
            block_blob_name = self._get_blob_reference(prefix='block_blob_')

            # KeyWrapper implements the key encryption key interface. Setting
            # this property will tell the service to encrypt the blob. Blob encryption
            # is supported only for uploading whole blobs and only at the time of creation.
            kek = KeyWrapper('key1')
            self.container_client.key_encryption_key = kek
            self.container_client.encryption_version = '2.0'

            self.container_client.upload_blob(block_blob_name, b'ABC')

            # Even when encrypting, uploading large blobs will still automatically 
            # chunk the data.
            max_single_put_size = self.bsc._config.max_single_put_size
            self.container_client.upload_blob(block_blob_name, b'ABC' * max_single_put_size, overwrite=True)
        finally:
            self.container_client.delete_container()

    def get_encrypted_blob(self):
        self._create_container()
        try:
            block_blob_name = self._get_blob_reference(prefix='block_blob')

            kek = KeyWrapper('key1')
            self.container_client.key_encryption_key = kek
            self.container_client.encryption_version = '2.0'

            data = os.urandom(13 * self.bsc._config.max_single_put_size + 1)
            self.container_client.upload_blob(block_blob_name, data)

            # Setting the key_resolver_function will tell the service to automatically
            # try to decrypt retrieved blobs. The key_resolver is a function that
            # takes in a key_id and returns a corresponding key_encryption_key.
            key_resolver = KeyResolver()
            key_resolver.put_key(kek)
            self.container_client.key_resolver_function = key_resolver.resolve_key

            # Downloading works as usual with support for decrypting both entire blobs
            # and decrypting range gets.
            block_blob_client = self.container_client.get_blob_client(block_blob_name)
            blob_full = block_blob_client.download_blob().readall()
            blob_range = block_blob_client.download_blob(offset=len(data) // 2,
                                                         length=len(data) // 4).readall()
        finally:
            self.container_client.delete_container()

    def get_encrypted_blob_key_encryption_key(self):
        self._create_container()
        try:
            block_blob_name = self._get_blob_reference(prefix='block_blob')

            kek = KeyWrapper('key1')
            self.container_client.key_encryption_key = kek
            self.container_client.encryption_version = '2.0'

            data = b'ABC'
            self.container_client.upload_blob(block_blob_name, data)

            # If the key_encryption_key property is set on download, the blobservice
            # will try to decrypt blobs using that key. If both the key_resolver and 
            # key_encryption_key are set, the result of the key_resolver will take precedence
            # and the decryption will fail if that key is not successful.
            self.container_client.key_resolver_function = None
            blob = self.container_client.get_blob_client(block_blob_name).download_blob().readall()
        finally:
            self.container_client.delete_container()

    def require_encryption(self):
        self._create_container()
        try:
            encrypted_blob_name = self._get_blob_reference(prefix='block_blob_')
            unencrypted_blob_name = self._get_blob_reference(prefix='unencrypted_blob_')

            self.container_client.key_encryption_key = None
            self.container_client.key_resolver_function = None
            self.container_client.require_encryption = False
            self.container_client.encryption_version = '2.0'

            data = b'ABC'
            self.container_client.upload_blob(unencrypted_blob_name, data)

            # If the require_encryption flag is set, the service object will throw if 
            # there is no encryption policy set on upload.
            self.container_client.require_encryption = True
            try:
                self.container_client.upload_blob(encrypted_blob_name, data)
                raise Exception
            except ValueError:
                pass

            # If the require_encryption flag is set, the service object will throw if
            # there is no encryption policy set on download.
            kek = KeyWrapper('key1')
            key_resolver = KeyResolver()
            key_resolver.put_key(kek)

            self.container_client.key_encryption_key = kek
            self.container_client.upload_blob(encrypted_blob_name, data)

            self.container_client.key_encryption_key = None
            try:
                self.container_client.get_blob_client(encrypted_blob_name).download_blob()
                raise Exception
            except ValueError:
                pass

            # If the require_encryption flag is set, but the retrieved blob is not
            # encrypted, the service object will throw.
            self.container_client.key_resolver_function = key_resolver.resolve_key
            try:
                self.container_client.get_blob_client(unencrypted_blob_name).download_blob()
                raise Exception
            except HttpResponseError:
                pass
        finally:
            self.container_client.delete_container()

    def alternate_key_algorithms(self):
        self._create_container()
        try:
            block_blob_name = self._get_blob_reference(prefix='block_blob')

            # The key wrapping algorithm used by the key_encryption_key
            # is entirely up to the choice of the user. For example,
            # RSA may be used.
            kek = RSAKeyWrapper('key2')
            key_resolver = KeyResolver()
            key_resolver.put_key(kek)
            self.container_client.key_encryption_key = kek
            self.container_client.key_resolver_function = key_resolver.resolve_key
            self.container_client.encryption_version = '2.0'

            self.container_client.upload_blob(block_blob_name, b'ABC')
            blob = self.container_client.get_blob_client(block_blob_name).download_blob().readall()
        finally:
            self.container_client.delete_container()

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    sys.exit(1)

# Configure max_single_put_size to make blobs in this sample smaller
bsc = BlobServiceClient.from_connection_string(CONNECTION_STRING, max_single_put_size=4 * 1024 * 1024)
samples = BlobEncryptionSamples(bsc)
samples.run_all_samples()
