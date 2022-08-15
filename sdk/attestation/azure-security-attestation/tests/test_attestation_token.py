# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from time import time
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509 import (
    BasicConstraints,
    CertificateBuilder,
    NameOID,
    SubjectAlternativeName,
    load_pem_x509_certificate,
)
import pytest
from azure.security.attestation import (
    AttestationToken,
    AttestationTokenValidationException,
)


class TestAzureAttestationToken(object):
    def test_create_signing_key(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u"test certificate")

        certificate = load_pem_x509_certificate(
            cert.encode("ascii"), backend=default_backend()
        )
        assert certificate.subject == x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, u"test certificate")]
        )

    def test_create_signer_ecds(self):
        """Generate an ECDS key and a certificate wrapping the key, then verify we can create a signing key over it."""
        eckey = self._create_ecds_key()
        certificate = self._create_x509_certificate(eckey, u"attestation.test")

        certificate = load_pem_x509_certificate(
            certificate.encode("ascii"), backend=default_backend()
        )
        assert certificate.subject == x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, u"attestation.test")]
        )

    def test_create_unsecured_token(self):
        token = AttestationToken(body={"val1": [1, 2, 3]})
        assert token._get_body() == {"val1": [1, 2, 3]}

    def test_create_unsecured_empty_token(self):
        token = AttestationToken(body=None)
        assert token._get_body() is None
        token._validate_token()

    def test_create_secured_token(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u"test certificate")

        token = AttestationToken(
            body={"val1": [1, 2, 3]}, signing_key=key, signing_certificate=cert
        )
        assert token._get_body() == {"val1": [1, 2, 3]}
        token._validate_token()

    def test_create_secured_empty_token(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u"test certificate")

        token = AttestationToken(body=None, signing_key=key, signing_certificate=cert)
        assert token._get_body() is None
        token._validate_token()

    def test_token_callback(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u"test certificate")

        token = AttestationToken(
            body={"val1": [1, 2, 3]}, signing_key=key, signing_certificate=cert
        )
        assert token._get_body() == {"val1": [1, 2, 3]}

        global callback_invoked
        callback_invoked = False

        def callback(token, signer):
            global callback_invoked
            callback_invoked = True
            assert signer.certificates[0] == cert

        token._validate_token(validation_callback=callback)
        assert callback_invoked

    def test_token_callback_rejected(self):
        key = self._create_rsa_key()
        cert = self._create_x509_certificate(key, u"test certificate")

        token = AttestationToken(
            body={"val1": [1, 2, 3]}, signing_key=key, signing_certificate=cert
        )
        assert token._get_body() == {"val1": [1, 2, 3]}

        global callback_invoked
        callback_invoked = False

        def callback(token, signer):
            assert signer.certificates[0] == cert
            raise ValueError("Validation failed.")

        with pytest.raises(ValueError):
            token._validate_token(validation_callback=callback)

    # Verify that the token expiration checks work correctly.

    def test_token_expiration(self):
        token30sec = AttestationToken(
            body={
                "exp": time() + 30,  # Expires in 30 seconds
                "iat": time(),
                "nbf": time(),  # Not valid before now.
            }
        )
        token30sec._validate_token()

        expired_token = AttestationToken(
            body={
                "exp": time() - 30,  # Expired 30 seconds ago
                "iat": time(),
                "nbf": time() + 5,  # Not valid for 5 seconds.
            }
        )
        with pytest.raises(AttestationTokenValidationException):
            expired_token._validate_token()

        early_token = AttestationToken(
            body={
                "exp": time() + 30,  # Expires in 30 seconds
                "iat": time(),
                "nbf": time() + 5,  # Not valid for 5 seconds.
            }
        )
        with pytest.raises(AttestationTokenValidationException):
            early_token._validate_token()

        # Specify 40 seconds of slack, so we're within the slack.
        # Token validation should start succeeding now because the slack
        # lets it work.
        expired_token._validate_token(validation_slack=40)
        early_token._validate_token(validation_slack=40)

    # Helper functions to create keys and certificates wrapping those keys.

    @staticmethod
    def _create_ecds_key():  # type: () -> str
        return (
            ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
            .private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
            .decode("ascii")
        )

    @staticmethod
    def _create_rsa_key():  # type: () -> str
        return (
            rsa.generate_private_key(65537, 2048, backend=default_backend())
            .private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
            .decode("ascii")
        )

    @staticmethod
    def _create_x509_certificate(key_pem, subject_name):  # type: (str, str) -> str
        signing_key = serialization.load_pem_private_key(
            key_pem.encode("utf-8"), password=None, backend=default_backend()
        )
        builder = CertificateBuilder()
        builder = builder.subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
                ]
            )
        )
        builder = builder.issuer_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
                ]
            )
        )

        one_day = datetime.timedelta(1, 0, 0)
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(signing_key.public_key())
        builder = builder.add_extension(
            SubjectAlternativeName([x509.DNSName(subject_name)]), critical=False
        )
        builder = builder.add_extension(
            BasicConstraints(ca=False, path_length=None), critical=True
        )
        return (
            builder.sign(
                private_key=signing_key,
                algorithm=hashes.SHA256(),
                backend=default_backend(),
            )
            .public_bytes(serialization.Encoding.PEM)
            .decode("ascii")
        )
