# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Enums for use with JSON Web Key APIs"""

from enum import Enum


class JsonWebKeyCurveName:
    """Elliptic curve algorithm names"""

    class v7_0(str, Enum):
        """Curves supported by Key Vault API version 7.0. This is the default version."""

        p_256 = "P-256"  #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
        p_384 = "P-384"  #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
        p_521 = "P-521"  #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
        p_256_k = "P-256K"  #: The SECG SECP256K1 elliptic curve.

    default = v7_0

    class v2016_10_01(str, Enum):
        """Curves supported by Key Vault API version 2016-10-01"""

        p_256 = "P-256"  #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
        p_384 = "P-384"  #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
        p_521 = "P-521"  #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
        secp256_k1 = "SECP256K1"  #: The SECG SECP256K1 elliptic curve.


class JsonWebKeyEncryptionAlgorithm:
    """Encryption algorithm names"""

    class v7_0(str, Enum):
        """Algorithms supported by Key Vault API version 7.0. This is the default version."""

        rsa_oaep = "RSA-OAEP"
        rsa_oaep_256 = "RSA-OAEP-256"
        rsa1_5 = "RSA1_5"

    default = v7_0

    class v2016_10_01(str, Enum):
        """Algorithms supported by Key Vault API version 2016-10-01"""

        rsa_oaep = "RSA-OAEP"
        rsa_oaep_256 = "RSA-OAEP-256"
        rsa1_5 = "RSA1_5"


class JsonWebKeySignatureAlgorithm:
    """Signature algorithm names"""

    class v7_0(str, Enum):
        """Algorithms supported by Key Vault API version 7.0. This is the default version."""

        ps256 = (
            "PS256"
        )  #: RSASSA-PSS using SHA-256 and MGF1 with SHA-256, as described in https://tools.ietf.org/html/rfc7518
        ps384 = (
            "PS384"
        )  #: RSASSA-PSS using SHA-384 and MGF1 with SHA-384, as described in https://tools.ietf.org/html/rfc7518
        ps512 = (
            "PS512"
        )  #: RSASSA-PSS using SHA-512 and MGF1 with SHA-512, as described in https://tools.ietf.org/html/rfc7518
        rs256 = "RS256"  #: RSASSA-PKCS1-v1_5 using SHA-256, as described in https://tools.ietf.org/html/rfc7518
        rs384 = "RS384"  #: RSASSA-PKCS1-v1_5 using SHA-384, as described in https://tools.ietf.org/html/rfc7518
        rs512 = "RS512"  #: RSASSA-PKCS1-v1_5 using SHA-512, as described in https://tools.ietf.org/html/rfc7518
        rsnull = "RSNULL"  #: Reserved
        es256 = "ES256"  #: ECDSA using P-256 and SHA-256, as described in https://tools.ietf.org/html/rfc7518.
        es384 = "ES384"  #: ECDSA using P-384 and SHA-384, as described in https://tools.ietf.org/html/rfc7518
        es512 = "ES512"  #: ECDSA using P-521 and SHA-512, as described in https://tools.ietf.org/html/rfc7518
        es256_k = "ES256K"  #: ECDSA using P-256K and SHA-256, as described in https://tools.ietf.org/html/rfc7518

    default = v7_0

    class v2016_10_01(str, Enum):
        """Algorithms supported by Key Vault API version 2016-10-01"""

        ps256 = "PS256"
        ps384 = "PS384"
        ps512 = "PS512"
        rs256 = "RS256"
        rs384 = "RS384"
        rs512 = "RS512"
        rsnull = "RSNULL"
        es256 = "ES256"
        es384 = "ES384"
        es512 = "ES512"
        ecdsa256 = "ECDSA256"


class JsonWebKeyType:
    """JSON Web Key types"""

    class v7_0(str, Enum):
        """Algorithms supported by Key Vault API version 7.0. This is the default version."""

        ec = "EC"  #: Elliptic Curve.
        ec_hsm = "EC-HSM"  #: Elliptic Curve with a private key which is not exportable from the HSM.
        rsa = "RSA"  #: RSA (https://tools.ietf.org/html/rfc3447)
        rsa_hsm = "RSA-HSM"  #: RSA with a private key which is not exportable from the HSM.
        oct = "oct"  #: Octet sequence (used to represent symmetric keys)

    default = v7_0

    class v2016_10_01(str, Enum):
        """Key types supported by Key Vault API version 2016-10-01"""

        ec = "EC"
        ec_hsm = "EC-HSM"
        rsa = "RSA"
        rsa_hsm = "RSA-HSM"
        oct = "oct"
