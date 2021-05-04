# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum


class KeyCurveName(str, Enum):
    """Supported elliptic curves"""

    p_256 = "P-256"  #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
    p_384 = "P-384"  #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
    p_521 = "P-521"  #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
    p_256_k = "P-256K"  #: The SECG SECP256K1 elliptic curve.


class KeyOperation(str, Enum):
    """Supported key operations"""

    encrypt = "encrypt"
    decrypt = "decrypt"
    import_key = "import"
    sign = "sign"
    verify = "verify"
    wrap_key = "wrapKey"
    unwrap_key = "unwrapKey"


class KeyType(str, Enum):
    """Supported key types"""

    ec = "EC"  #: Elliptic Curve
    ec_hsm = "EC-HSM"  #: Elliptic Curve with a private key which is not exportable from the HSM
    rsa = "RSA"
    rsa_hsm = "RSA-HSM"  #: RSA with a private key which is not exportable from the HSM
    oct = "oct"  #: Octet sequence (used to represent symmetric keys)
    oct_hsm = "oct-HSM"  #: Octet sequence with a private key which is not exportable from the HSM
