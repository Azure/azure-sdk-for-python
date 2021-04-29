# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import os

from azure.keyvault.certificates import CertificatePolicy, WellKnownIssuerNames
from OpenSSL import crypto

from _shared.json_attribute_matcher import json_attribute_matcher
from _shared.test_case import KeyVaultTestCase
from _test_case import client_setup, get_decorator, CertificatesTestCase


all_api_versions = get_decorator()


class MergeCertificateTest(CertificatesTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        kwargs["match_body"] = False
        kwargs["custom_request_matchers"] = [json_attribute_matcher]
        super(MergeCertificateTest, self).__init__(*args, **kwargs)

    @all_api_versions()
    @client_setup
    def test_merge_certificate(self, client, **kwargs):
        cert_name = self.get_resource_name("mergeCertificate")
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.unknown, subject="CN=MyCert", certificate_transparency=False
        )
        dirname = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.abspath(os.path.join(dirname, "ca.key")), "rt") as f:
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
        with open(os.path.abspath(os.path.join(dirname, "ca.crt")), "rt") as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        client.begin_create_certificate(certificate_name=cert_name, policy=cert_policy).wait()

        csr = (
            "-----BEGIN CERTIFICATE REQUEST-----\n"
            + base64.b64encode(client.get_certificate_operation(certificate_name=cert_name).csr).decode()
            + "\n-----END CERTIFICATE REQUEST-----"
        )
        req = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)

        cert = crypto.X509()
        cert.set_serial_number(1)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(60)  # Testing certificates need not be long lived
        cert.set_issuer(ca_cert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(pkey, "sha256")
        signed_certificate_bytes = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode().replace("\n", "")
        signed_certificate_bytes = signed_certificate_bytes.lstrip("-----BEGIN CERTIFICATE-----")
        signed_certificate_bytes = signed_certificate_bytes.rstrip("-----END CERTIFICATE-----")

        client.merge_certificate(certificate_name=cert_name, x509_certificates=[signed_certificate_bytes.encode()])
