# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import codecs
import hashlib
import json
import os
from urllib.parse import urlparse

import pytest

from azure.keyvault.securitydomain.models import CertificateInfo, SecurityDomainJsonWebKey

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import load_pem_x509_certificate

from _shared.test_case import KeyVaultTestCase
from _test_case import ClientPreparer
from utils import Utils


def _int_to_bytes(i):
    h = hex(i)
    if len(h) > 1 and h[0:2] == "0x":
        h = h[2:]
    # need to strip L in python 2.x
    h = h.strip("L")
    if len(h) % 2:
        h = "0" + h
    return codecs.decode(h, "hex")


def _public_rsa_key_to_jwk(rsa_key, encoding=None):
    pubv = rsa_key.public_numbers()
    n = _int_to_bytes(pubv.n)
    if encoding:
        n = encoding(n)
    e = _int_to_bytes(pubv.e)
    if encoding:
        e = encoding(e)
    return (n, e)


class TestSecurityDomain(KeyVaultTestCase):
    @pytest.mark.live_test_only
    @ClientPreparer()
    def test_security_domain_download_and_upload(self, client, upload_client, **kwargs):
        path_prefix = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
        hsm_url = os.environ["AZURE_MANAGEDHSM_URL"]
        hsm_name = urlparse(hsm_url).netloc.split(".")[0]
        certs_path = f"{path_prefix}{hsm_name}-certificate"
        sd_wrapping_keys = [f"{certs_path}0.cer", f"{certs_path}1.cer", f"{certs_path}2.cer"]
        certificates = []
        for path in sd_wrapping_keys:
            with open(path, "rb") as f:
                pem_data = f.read()

            cert = load_pem_x509_certificate(pem_data, backend=default_backend())
            public_key = cert.public_key()
            public_bytes = cert.public_bytes(Encoding.DER)
            x5c = [Utils.security_domain_b64_url_encode_for_x5c(public_bytes)]  # only one cert, not a chain
            x5t = Utils.security_domain_b64_url_encode(hashlib.sha1(public_bytes).digest())
            x5tS256 = Utils.security_domain_b64_url_encode(hashlib.sha256(public_bytes).digest())
            key_ops = ["verify", "encrypt", "wrapKey"]

            # populate key into jwk
            kty = "RSA"
            alg = "RSA-OAEP-256"
            n, e = _public_rsa_key_to_jwk(public_key, encoding=Utils.security_domain_b64_url_encode)

            certificates.append(
                SecurityDomainJsonWebKey(
                    kid=cert.subject.rfc4514_string(),
                    kty=kty,
                    key_ops=key_ops,
                    n=n,
                    e=e,
                    x5_c=x5c,
                    alg=alg,
                    x5_t=x5t,
                    x5_t_s256=x5tS256,
                )
            )
        certs_object = CertificateInfo(certificates=certificates)
        poller = client.begin_download(certificate_info_object=certs_object, skip_activation_polling=True)
        result = poller.result()
        assert result.value

        transfer_key = json.loads(upload_client.get_transfer_key().transfer_key_jwk)
        secondary_hsm_url = os.environ["SECONDARY_MANAGEDHSM_URL"]
        secondary_hsm_name = urlparse(secondary_hsm_url).netloc.split(".")[0]
        key_path = f"{path_prefix}{secondary_hsm_name}-transfer-key.pem"

        def get_x5c_as_pem():
            x5c = transfer_key.get("x5c", [])
            if not x5c:
                raise ValueError("Insufficient x5c.")
            b64cert = x5c[0]
            header = "-----BEGIN CERTIFICATE-----"
            footer = "-----END CERTIFICATE-----"
            pem = [header]
            for i in range(0, len(b64cert), 65):
                line_len = min(65, len(b64cert) - i)
                line = b64cert[i : i + line_len]
                pem.append(line)
            pem.append(footer)
            return "\n".join(pem)

        try:
            with open(key_path, "w") as f:
                f.write(get_x5c_as_pem())
        except Exception as ex:  # pylint: disable=broad-except
            if os.path.isfile(key_path):
                os.remove(key_path)
            raise ex

        poller = upload_client.begin_upload(security_domain=result)
        result = poller.result()
        assert result.status.lower() == "success"
