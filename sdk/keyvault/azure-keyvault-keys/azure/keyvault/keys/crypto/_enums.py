# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum


class KeyWrapAlgorithm(str, Enum):
    """Key wrapping algorithms"""

    aes_128 = "A128KW"
    aes_192 = "A192KW"
    aes_256 = "A256KW"
    rsa_oaep = "RSA-OAEP"
    rsa_oaep_256 = "RSA-OAEP-256"
    rsa1_5 = "RSA1_5"


class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""

    rsa_oaep = "RSA-OAEP"
    rsa_oaep_256 = "RSA-OAEP-256"
    rsa1_5 = "RSA1_5"
    a128_gcm = "A128GCM"
    a192_gcm = "A192GCM"
    a256_gcm = "A256GCM"
    a128_cbc = "A128CBC"
    a192_cbc = "A192CBC"
    a256_cbc = "A256CBC"
    a128_cbcpad = "A128CBCPAD"
    a192_cbcpad = "A192CBCPAD"
    a256_cbcpad = "A256CBCPAD"


class SignatureAlgorithm(str, Enum):
    """Signature algorithms, described in https://tools.ietf.org/html/rfc7518"""

    ps256 = "PS256"  #: RSASSA-PSS using SHA-256 and MGF1 with SHA-256
    ps384 = "PS384"  #: RSASSA-PSS using SHA-384 and MGF1 with SHA-384
    ps512 = "PS512"  #: RSASSA-PSS using SHA-512 and MGF1 with SHA-512
    rs256 = "RS256"  #: RSASSA-PKCS1-v1_5 using SHA-256
    rs384 = "RS384"  #: RSASSA-PKCS1-v1_5 using SHA-384
    rs512 = "RS512"  #: RSASSA-PKCS1-v1_5 using SHA-512
    es256 = "ES256"  #: ECDSA using P-256 and SHA-256
    es384 = "ES384"  #: ECDSA using P-384 and SHA-384
    es512 = "ES512"  #: ECDSA using P-521 and SHA-512
    es256_k = "ES256K"  #: ECDSA using P-256K and SHA-256
