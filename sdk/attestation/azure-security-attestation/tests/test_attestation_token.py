# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from time import time
from logging import critical
from typing import Dict
import unittest
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from devtools_testutils import AzureTestCase, ResourceGroupPreparer, PowerShellPreparer
import functools
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from  cryptography.x509 import BasicConstraints, CertificateBuilder, NameOID, SubjectAlternativeName
import base64
import pytest
from azure.security.attestation import (
    AttestationToken,
    AttestationSigningKey,
    TokenValidationOptions,
    AttestationTokenValidationException)


class TestAzureAttestationToken(object):

    def test_create_signing_key(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        signer = AttestationSigningKey(key, cert)
        assert signer._certificate.subject==x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'test certificate')])

    def test_create_signing_wrong_key(self):
        """ SigningKey should throw if the key and certificate don't match.
        """
        key1 = self._create_rsa_key()
        cert = self._create_x509_certificate(key1, u'test certificate')
        key2 = self._create_rsa_key()

        # This should throw an exception, fail if the exception isn't thrown.
        with pytest.raises(ValueError):
            signer = AttestationSigningKey(key2, cert)
            print(signer) # reference signer so pylint is happy.

    def test_create_signer_ecds(self):
        """ Generate an ECDS key and a certificate wrapping the key, then verify we can create a signing key over it.
        """
        eckey = self._create_ecds_key()
        certificate = self._create_x509_certificate(eckey, u'attestation.test')
        signer = AttestationSigningKey(eckey, certificate)
        assert signer._certificate.subject== x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'attestation.test')])

    def test_create_unsecured_token(self):
        token = AttestationToken(body={"val1":[1,2,3]})
        assert token.get_body() == {"val1":[1,2,3]}

    def test_create_unsecured_empty_token(self):
        token = AttestationToken(body=None)
        assert token.get_body()== None
        assert token.validate_token()


    def test_create_secured_token(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        signer = AttestationSigningKey(key, cert)

        token = AttestationToken(body={"val1": [1, 2, 3]}, signer=signer)
        assert token.get_body()== {"val1": [1, 2, 3]}
        assert token.validate_token()

    def test_create_secured_empty_token(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        signer = AttestationSigningKey(key, cert)

        token = AttestationToken(body=None, signer=signer)
        assert token.get_body()== None
        assert token.validate_token()



    def test_token_callback(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        token_signer = AttestationSigningKey(key, cert)

        token = AttestationToken(body={"val1": [1, 2, 3]}, signer=token_signer)
        assert token.get_body()== {"val1": [1, 2, 3]}

        global callback_invoked
        callback_invoked = False

        def callback(token, signer):
            global callback_invoked
            callback_invoked = True
            assert signer.certificates[0]==cert
            return True

        options = TokenValidationOptions(validation_callback = callback)
        
        assert token.validate_token(options)
        assert callback_invoked


    def test_token_callback_rejected(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u'test certificate')

        token_signer = AttestationSigningKey(key, cert)

        token = AttestationToken(body={"val1": [1, 2, 3]}, signer=token_signer)
        assert token.get_body()== {"val1": [1, 2, 3]}

        global callback_invoked
        callback_invoked = False

        def callback(token, signer):
            assert signer.certificates[0]==cert
            return False

        options = TokenValidationOptions(validation_callback = callback)
        with pytest.raises(AttestationTokenValidationException):
            assert token.validate_token(options) is False


    # Verify that the token expiration checks work correctly.
    def test_token_expiration(self):
        token30sec = AttestationToken(body={
            "exp": time()+30, # Expires in 30 seconds
            "iat": time(),
            "nbf": time() # Not valid before now.
        })
        assert token30sec.validate_token() is True

        expired_token=AttestationToken(body={
            "exp": time()-30, # Expired 30 seconds ago
            "iat": time(),
            "nbf": time()+5 # Not valid for 5 seconds.
        })
        with pytest.raises(AttestationTokenValidationException):
            assert expired_token.validate_token() is False

        early_token=AttestationToken(body={
            "exp": time()+30, # Expires in 30 seconds
            "iat": time(),
            "nbf": time()+5 # Not valid for 5 seconds.
        })
        with pytest.raises(AttestationTokenValidationException):
            assert early_token.validate_token() is False

        # Specify 40 seconds of slack, so we're within the slack.
        # Token validation should start succeeding now because the slack
        # lets it work.
        token_options=TokenValidationOptions(validation_slack=40)
        assert expired_token.validate_token(token_options) is True
        assert early_token.validate_token(token_options) is True


    # Helper functions to create keys and certificates wrapping those keys.
    @staticmethod
    def _create_ecds_key(): #type() -> EllipticCurvePrivateKey
        return ec.generate_private_key(ec.SECP256R1(), backend=default_backend()).private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())

    @staticmethod
    def _create_rsa_key(): #type() -> EllipticCurvePrivateKey
        return rsa.generate_private_key(65537, 2048, backend=default_backend()).private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())

    @staticmethod
    def _create_x509_certificate(key_der, subject_name): #type(Union[EllipticCurvePrivateKey,RSAPrivateKey], str) -> Certificate
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
