# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
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
