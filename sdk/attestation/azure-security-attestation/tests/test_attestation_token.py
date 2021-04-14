# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import datetime
from logging import critical
from typing import Dict
import unittest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from devtools_testutils import AzureTestCase, ResourceGroupPreparer, PowerShellPreparer
import functools
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from  cryptography.x509 import BasicConstraints, CertificateBuilder, NameOID
import base64
import pytest
from azure.security.attestation import AttestationToken, AttestationSigner, SigningKey


class TestAzureAttestationToken(unittest.TestCase):

    def setUp(self):
        super(TestAzureAttestationToken, self).setUp()

    def test_create_unsecured_token(self):
        token = AttestationToken(body={"val1":[1,2,3]})
        assert token.get_body() == {"val1":[1,2,3]}

    def test_create_signing_key(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        signer = SigningKey(key, cert)
        self.assertEqual(signer.certificate.subject, cert.subject)

    def test_create_signing_wrong_key(self):
        """ SigningKey should throw if the key and certificate don't match.
        """
        key1 = self._create_rsa_key()
        cert = self._create_x509_certificate(key1, u'test certificate')
        key2 = self._create_rsa_key()

        # This should throw an exception, fail if the exception isn't thrown.
        with self.assertRaises(Exception):
            signer = SigningKey(key2, cert)
            print(signer) # reference signer so pylint is happy.

    def test_create_signer_ecds(self):
        """ Generate an ECDS key and a certificate wrapping the key, then verify we can create a signing key over it.
        """
        eckey = self._create_ecds_key()
        certificate = self._create_x509_certificate(eckey, u'attestation.test')
        signer = SigningKey(eckey, certificate)
        self.assertEqual(signer.certificate.subject, x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'attestation.test')]))

    def test_create_secured_token(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        signer = SigningKey(key, cert)

        token = AttestationToken(body={"val1": [1, 2, 3]}, signer=signer)
        self.assertEqual(token.get_body(), {"val1": [1, 2, 3]})
        self.assertTrue(token.validate_token())

    # Helper functions to create keys and certificates wrapping those keys.
    @staticmethod
    def _create_ecds_key(): #type() -> EllipticCurvePrivateKey
        return ec.generate_private_key(ec.SECP256R1())

    @staticmethod
    def _create_rsa_key(): #type() -> EllipticCurvePrivateKey
        return rsa.generate_private_key(65537, 2048)

    @staticmethod
    def _create_x509_certificate(key, subject_name): #type(Union[EllipticCurvePrivateKey,RSAPrivateKey], str) -> Certificate
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
        builder = builder.public_key(key.public_key())
        builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(subject_name)]), critical=False)
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        return builder.sign(private_key=key, algorithm=hashes.SHA256())
