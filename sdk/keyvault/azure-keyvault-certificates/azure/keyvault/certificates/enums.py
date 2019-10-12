# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum


class ActionType(str, Enum):
    """The supported action types for the lifetime of a certificate"""

    email_contacts = "EmailContacts"
    auto_renew = "AutoRenew"


class SecretContentType(str, Enum):
    """Content type of the secrets as specified in Certificate Policy"""

    PKCS12 = "application/x-pkcs12"
    PEM = "application/x-pem-file"


class KeyUsageType(str, Enum):
    """The supported types of key usages"""

    digital_signature = "digitalSignature"
    non_repudiation = "nonRepudiation"
    key_encipherment = "keyEncipherment"
    data_encipherment = "dataEncipherment"
    key_agreement = "keyAgreement"
    key_cert_sign = "keyCertSign"
    crl_sign = "cRLSign"
    encipher_only = "encipherOnly"
    decipher_only = "decipherOnly"


class KeyType(str, Enum):
    """Supported key types"""

    ec = "EC"  #: Elliptic Curve
    ec_hsm = "EC-HSM"  #: Elliptic Curve with a private key which is not exportable from the HSM
    rsa = "RSA"  #: RSA (https://tools.ietf.org/html/rfc3447)
    rsa_hsm = "RSA-HSM"  #: RSA with a private key which is not exportable from the HSM
    oct = "oct"  #: Octet sequence (used to represent symmetric keys)


class KeyCurveName(str, Enum):
    """Supported elliptic curves"""

    p_256 = "P-256"  #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
    p_384 = "P-384"  #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
    p_521 = "P-521"  #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
    p_256_k = "P-256K"  #: The SECG SECP256K1 elliptic curve.
