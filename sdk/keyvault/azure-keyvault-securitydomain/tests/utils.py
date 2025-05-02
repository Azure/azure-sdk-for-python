# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import array
import base64
import codecs
import hashlib
import os
import secrets
from urllib.parse import urlparse

from azure.keyvault.securitydomain.models import CertificateInfo, SecurityDomainJsonWebKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import load_pem_x509_certificate


PATH_PREFIX = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, os.pardir))


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
    public_numbers = rsa_key.public_numbers()
    n = _int_to_bytes(public_numbers.n)
    if encoding:
        n = encoding(n)
    e = _int_to_bytes(public_numbers.e)
    if encoding:
        e = encoding(e)
    return (n, e)


class Utils:
    @staticmethod
    def is_little_endian():
        a = bytes(array.array("H", [1]))
        # little endian: b'\x01\x00'
        # big endian: b'\x00\x01'
        return a[0] == 1

    @staticmethod
    def convert_to_uint16(b: bytearray):
        ret = [0 for _ in range(len(b) // 2)]
        for i in range(0, len(b), 2):
            byte_order = "little" if Utils.is_little_endian() else "big"
            ret[i // 2] = int.from_bytes(bytearray([b[i], b[i + 1]]), byteorder=byte_order, signed=False)
        return ret

    @staticmethod
    def get_random(cb):
        ret = bytearray()
        for _ in range(cb):
            ret.append(secrets.randbits(8))
        return ret

    @staticmethod
    def get_SHA256_thumbprint(cert):
        public_bytes = cert.public_bytes(Encoding.DER)
        return hashlib.sha256(public_bytes).digest()

    @staticmethod
    def security_domain_b64_url_encode_for_x5c(s):
        return base64.b64encode(s).decode("ascii")

    @staticmethod
    def security_domain_b64_url_encode(s):
        return base64.b64encode(s).decode("ascii").strip("=").replace("+", "-").replace("/", "_")


def get_certificate_info() -> CertificateInfo:
    hsm_url = os.environ["AZURE_MANAGEDHSM_URL"]
    hsm_name = urlparse(hsm_url).netloc.split(".")[0]
    certs_path = f"{PATH_PREFIX}/{hsm_name}-certificate"
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
    return CertificateInfo(certificates=certificates)


def write_security_domain(security_domain: str) -> None:
    secondary_hsm_url = os.environ["SECONDARY_MANAGEDHSM_URL"]
    secondary_hsm_name = urlparse(secondary_hsm_url).netloc.split(".")[0]
    sd_path = f"{PATH_PREFIX}/{secondary_hsm_name}-security-domain.json"
    try:
        with open(sd_path, "w") as f:
            f.write(security_domain)
    except Exception as ex:  # pylint: disable=broad-except
        if os.path.isfile(sd_path):
            os.remove(sd_path)
        raise ex


def write_transfer_key(transfer_key: dict) -> None:
    secondary_hsm_url = os.environ["SECONDARY_MANAGEDHSM_URL"]
    secondary_hsm_name = urlparse(secondary_hsm_url).netloc.split(".")[0]
    key_path = f"{PATH_PREFIX}/{secondary_hsm_name}-transfer-key.pem"

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


if __name__ == "__main__":
    print(Utils.convert_to_uint16(bytearray([40, 30, 20, 10])))
