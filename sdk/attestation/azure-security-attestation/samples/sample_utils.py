# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_helpers.py
DESCRIPTION:
    Helper functions used for the azure attestation samples.

"""
import datetime 
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from  cryptography.x509 import BasicConstraints, CertificateBuilder, NameOID, SubjectAlternativeName
from cryptography.hazmat.primitives import hashes, serialization

def write_banner(banner):
    #type:(str) -> None
    """
    Write a banner which can be used to visually separate the output of the samples.
    """
    separator = '*'*80
    print("\n")
    print(separator)
    print("        ", banner)
    print(separator)

def create_rsa_key(): #type() -> RSAPrivateKey
    """
    Create an RSA Asymmetric 2048 bit key.
    """
    return rsa.generate_private_key(65537, 2048, backend=default_backend()).private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption())

def create_x509_certificate(key_der, subject_name): #type(Union[EllipticCurvePrivateKey,RSAPrivateKey], str) -> Certificate
    """
    Given an RSA or ECDS private key, create a self-signed X.509 certificate
    with the specified subject name signed with that key.
    """
    signing_key = serialization.load_der_private_key(key_der, password=None, backend=default_backend())
    builder = CertificateBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
    ]))
    builder = builder.issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
    ]))

    one_day = datetime.timedelta(1, 0, 0)
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
    builder = builder.serial_number(x509.random_serial_number())        
    builder = builder.public_key(signing_key.public_key())
    builder = builder.add_extension(SubjectAlternativeName([x509.DNSName(subject_name)]), critical=False)
    builder = builder.add_extension(BasicConstraints(ca=False, path_length=None), critical=True)
    return builder.sign(private_key=signing_key, algorithm=hashes.SHA256(), backend=default_backend()).public_bytes(serialization.Encoding.DER)
