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

AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
#            attestation_azure_authority_host='xxx',
#            attestation_resource_group='yyyy',
#            attestation_subscription_id='xxx',
#            attestation_location_short_name='xxx',
#            attestation_environment='AzureCloud',
            attestation_policy_signing_key0='keyvalue',
            attestation_policy_signing_key1='keyvalue',
            attestation_policy_signing_key2='keyvalue',
            attestation_policy_signing_certificate0='more junk',
            attestation_policy_signing_certificate1='more junk',
            attestation_policy_signing_certificate2='more junk',
            attestation_serialized_policy_signing_key0="junk",
            attestation_serialized_policy_signing_key1="junk",
            attestation_serialized_policy_signing_key2="junk",
            attestation_serialized_isolated_signing_key='yyyy',
            attestation_isolated_signing_key='xxxx',
            attestation_isolated_signing_certificate='xxxx',
            attestation_service_management_url='https://management.core.windows.net/',
            attestation_location_short_name='xxxx',
            attestation_client_id='xxxx',
            attestation_client_secret='secret',
            attestation_tenant_id='tenant',
            attestation_isolated_url='https://fakeresource.wus.attest.azure.net',
            attestation_aad_url='https://fakeresource.wus.attest.azure.net',
#            attestation_resource_manager_url='https://resourcemanager/zzz'
        )

class AzureAttestationTokenTest(AzureTestCase):

    def setUp(self):
        super(AzureAttestationTokenTest, self).setUp()

    @AttestationPreparer()
    def test_create_unsecured_token(self):
        token = AttestationToken(body={"val1":[1,2,3]})
        assert token.get_body() == {"val1":[1,2,3]}

    @AttestationPreparer()
    def test_create_signing_key(self, attestation_policy_signing_key0, attestation_policy_signing_certificate0):
        der_cert = base64.b64decode(attestation_policy_signing_certificate0)
        cert = x509.load_der_x509_certificate(der_cert)

        der_key = base64.b64decode(attestation_policy_signing_key0)
        key = serialization.load_der_private_key(der_key, password=None)


        signer = SigningKey(key, cert)
        assert signer.certificate.subject == cert.subject

    @AttestationPreparer()
    def test_create_signer_ecds(self):
        eckey = ec.generate_private_key(ec.SECP256R1())
        builder = CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'attestation.test'),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'attestation.test'),
        ]))

        one_day = datetime.timedelta(1, 0, 0)
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
        builder = builder.serial_number(x509.random_serial_number())        
        builder = builder.public_key(eckey.public_key())
        builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(u'attestation.test')]), critical=False)
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        certificate = builder.sign(private_key=eckey, algorithm=hashes.SHA256())
        signer = SigningKey(eckey, certificate)
        assert  signer.certificate.subject==x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'attestation.test')])
