# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)
from enum import Enum
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta


class CertificatePolicyAction(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The supported action types for the lifetime of a certificate"""

    email_contacts = "EmailContacts"
    auto_renew = "AutoRenew"


class CertificateContentType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Content type of the secrets as specified in Certificate Policy"""

    pkcs12 = "application/x-pkcs12"
    pem = "application/x-pem-file"


class KeyUsageType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
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


class KeyType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Supported key types"""

    ec = "EC"  #: Elliptic Curve
    ec_hsm = "EC-HSM"  #: Elliptic Curve with a private key which is not exportable from the HSM
    rsa = "RSA"  #: RSA (https://tools.ietf.org/html/rfc3447)
    rsa_hsm = "RSA-HSM"  #: RSA with a private key which is not exportable from the HSM
    oct = "oct"  #: Octet sequence (used to represent symmetric keys)
    oct_hsm = "oct-HSM"  #: Octet sequence with a private key which is not exportable from the HSM

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"{value} is not a valid KeyType")


class KeyCurveName(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Supported elliptic curves"""

    p_256 = "P-256"  #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
    p_384 = "P-384"  #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
    p_521 = "P-521"  #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
    p_256_k = "P-256K"  #: The SECG SECP256K1 elliptic curve.


class WellKnownIssuerNames(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Collection of well-known issuer names"""

    self = "Self"  #: Use this issuer for a self-signed certificate
    unknown = "Unknown"
    """
    If you use this issuer, you must manually get an x509 certificate from the issuer of your choice.
    You must then call :func:`~azure.keyvault.certificates.CertificateClient.merge_certificate` to
    merge the public x509 certificate with your key vault certificate pending object to complete creation.
    """
