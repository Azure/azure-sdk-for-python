# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import os

from azure.keyvault.certificates import CertificatePolicy, WellKnownIssuerNames
from azure.keyvault.certificates.aio import CertificateClient
from devtools_testutils import PowerShellPreparer
from OpenSSL import crypto

from _shared.json_attribute_matcher import json_attribute_matcher
from _shared.test_case_async import KeyVaultTestCase


class MergeCertificateTest(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, match_body=False, custom_request_matchers=[json_attribute_matcher], **kwargs)

    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(CertificateClient, is_async=True)
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    @PowerShellPreparer("keyvault", azure_keyvault_url="https://vaultname.vault.azure.net")
    async def test_merge_certificate(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("mergeCertificate")
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.unknown, subject="CN=MyCert", certificate_transparency=False
        )

        dirname = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.abspath(os.path.join(dirname, "ca.key")), "rt") as f:
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
        with open(os.path.abspath(os.path.join(dirname, "ca.crt")), "rt") as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        # the poller will stop immediately because the issuer is `Unknown`
        await client.create_certificate(certificate_name=cert_name, policy=cert_policy)

        certificate_operation = await client.get_certificate_operation(certificate_name=cert_name)

        csr = (
            "-----BEGIN CERTIFICATE REQUEST-----\n"
            + base64.b64encode(certificate_operation.csr).decode()
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

        await client.merge_certificate(cert_name, [signed_certificate_bytes.encode()])
