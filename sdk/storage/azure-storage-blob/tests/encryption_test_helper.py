# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

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


class KeyWrapper:
    def __init__(self, kid='local:key1'):
        # Must have constant key value for recorded tests, otherwise we could use a random generator.
        self.kek = b'\xbe\xa4\x11K\x9eJ\x07\xdafF\x83\xad+\xadvA C\xe8\xbc\x90\xa4\x11}G\xc3\x0f\xd4\xb4\x19m\x11'
        self.backend = default_backend()
        self.kid = kid

    def wrap_key(self, key, algorithm='A256KW'):
        if algorithm == 'A256KW':
            return aes_key_wrap(self.kek, key, self.backend)

        raise ValueError(_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM)

    def unwrap_key(self, key, algorithm):
        if algorithm == 'A256KW':
            return aes_key_unwrap(self.kek, key, self.backend)

        raise ValueError(_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM)

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
    def __init__(self, kid='local:key2'):
        self.private_key = generate_private_key(public_exponent=65537,
                                                key_size=2048,
                                                backend=default_backend())
        self.public_key = self.private_key.public_key()
        self.kid = kid

    def wrap_key(self, key, algorithm='RSA'):
        if algorithm == 'RSA':
            return self.public_key.encrypt(key,
                                           OAEP(
                                               mgf=MGF1(algorithm=SHA1()),  # nosec
                                               algorithm=SHA1(),    # nosec
                                               label=None)
                                           )

        raise ValueError(_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM)

    def unwrap_key(self, key, algorithm):
        if algorithm == 'RSA':
            return self.private_key.decrypt(key,
                                            OAEP(
                                                mgf=MGF1(algorithm=SHA1()), # nosec
                                                algorithm=SHA1(),   # nosec
                                                label=None)
                                            )

        raise ValueError(_ERROR_UNKNOWN_KEY_WRAP_ALGORITHM)

    def get_key_wrap_algorithm(self):
        return 'RSA'

    def get_kid(self):
        return self.kid


def mock_urandom(size: int) -> bytes:
    """
    Used to mock os.urandom to return fixed values for creation of IV (16 bytes), encryption keys
    (32 bytes), and nonces (12 bytes) internal to the encryption algorithm. This allows these tests
    to be recorded.
    """
    if size == 12:
        return b'Mb\xd5N\xc2\xbd\xa0\xc8\xa4L\xfb\xa0'
    elif size == 16:
        return b'\xbb\xd6\x87\xb6j\xe5\xdc\x93\xb0\x13\x1e\xcc\x9f\xf4\xca\xab'
    elif size == 32:
        return b'\x08\xe0A\xb6\xf2\xb7x\x8f\xe5\xdap\x87^6x~\xa4F\xc4\xe9\xb1\x8a:\xfbC%S\x0cZ\xbb\xbe\x88'
    else:
        return os.urandom(size)
