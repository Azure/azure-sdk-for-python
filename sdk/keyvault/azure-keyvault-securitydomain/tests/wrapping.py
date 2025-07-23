# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# The core utilities in this file are copied from the Azure CLI's Security Domain module:
# https://github.com/Azure/azure-cli/tree/dev/src/azure-cli/azure/cli/command_modules/keyvault/security_domain
import array
import hashlib
import json
import os
import secrets

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate

from jwe import JWE, KDF
from utils import Utils


PATH_PREFIX = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, "resources"))
CERT_PATH_PREFIX = f"{PATH_PREFIX}/certificate"
SECURITY_DOMAIN_PATH = f"{PATH_PREFIX}/security-domain.json"
TRANSFER_KEY_PATH = f"{PATH_PREFIX}/transfer-key.json"


class ModMath:
    @staticmethod
    def reduce(x):
        t = (x & 0xff) - (x >> 8)
        t += (t >> 31) & 257
        return t

    @staticmethod
    def multiply(x, y):
        return ModMath.reduce(x * y)

    @staticmethod
    def invert(x):
        ret = x
        for _ in range(7):
            ret = ModMath.multiply(ret, ret)
            ret = ModMath.multiply(ret, x)
        return ret

    @staticmethod
    def add(x, y):
        return ModMath.reduce(x + y)

    @staticmethod
    def subtract(x, y):
        return ModMath.reduce(x - y + 257)

    @staticmethod
    def get_random():
        return ModMath.reduce(secrets.randbits(16))


class Share:
    def __init__(self, x, v):
        self.x = x
        self.v = v

    @staticmethod
    def from_uint16(w):
        x = w >> 9
        v = w & 0x1ff
        return Share(x, v)

    def to_uint16(self):
        return (self.x << 8) | self.v


class ByteShares:
    def __init__(self, required, secret_byte):
        self.coefficients = ByteShares.init_coefficients(required, secret_byte)

    @staticmethod
    def init_coefficients(required, secret_byte):
        coefficients = array.array('H')
        for _ in range(required - 1):
            coefficients.append(ModMath.get_random())
        coefficients.append(secret_byte)
        return coefficients

    def set_secret_byte(self, secret_byte):
        self.coefficients[-1] = secret_byte

    def make_share(self, x):
        v = ModMath.multiply(self.coefficients[0], x)
        v = ModMath.add(v, self.coefficients[1])

        for i in range(2, len(self.coefficients)):
            v = ModMath.multiply(v, x)
            v = ModMath.add(v, self.coefficients[i])
        return Share(x, v)

    @staticmethod
    def get_secret(shares, required):
        secret = 0
        for i in range(required):
            numerator = denominator = 1
            si = Share.from_uint16(shares[i])
            for j in range(required):
                if i == j:
                    continue
                sj = Share.from_uint16(shares[j])
                numerator = ModMath.multiply(numerator, sj.x)
                diff = ModMath.subtract(sj.x, si.x)
                denominator = ModMath.multiply(diff, denominator)

            invert = ModMath.invert(denominator)
            ci = ModMath.multiply(numerator, invert)
            tmp = ModMath.multiply(ci, si.v)
            secret = ModMath.add(secret, tmp)

        return secret


class SharedSecret:
    max_shares = 126

    def __init__(self, shares=None, required=0):
        if shares is None:
            shares = 0
        else:
            if shares > SharedSecret.max_shares or required > shares:
                raise ValueError('Incorrect share or required count.')

        self.shares = shares
        self.required = required
        self.byte_shares = ByteShares(required, 0)

    def make_byte_shares(self, b):
        share_array = []
        self.byte_shares.set_secret_byte(b)

        for x in range(1, self.shares + 1):
            s = self.byte_shares.make_share(x)
            share_array.append(s.to_uint16())

        return share_array

    def make_shares(self, plaintext):
        share_arrays = []
        for i, p in enumerate(plaintext):
            share_array = self.make_byte_shares(p)
            for sa in share_array:
                if i == 0:
                    share_arrays.append(array.array('H'))
                current_share_array = sa
                current_share_array.append(sa)
        return share_arrays

    @staticmethod
    def get_secret_byte(share_array, required):
        return ByteShares.get_secret(share_array, required)

    @staticmethod
    def get_plaintext(share_arrays, required):
        plaintext = bytearray()
        plaintext_len = len(share_arrays[0])

        for j in range(plaintext_len):
            sv = array.array('H')
            for i in range(required):
                sa = share_arrays[i]
                sv.append(sa[j])

            text = SharedSecret.get_secret_byte(sv, required)
            plaintext.append(text)

        return plaintext


class Key:
    def __init__(self, enc_key=None, x5t_256=None):
        self.enc_key = enc_key
        self.x5t_256 = x5t_256

    def to_json(self):
        return {
            'enc_key': self.enc_key if self.enc_key else '',
            'x5t_256': self.x5t_256 if self.x5t_256 else ''
        }


class EncData:
    def __init__(self):
        self.data = []
        self.kdf = None

    def to_json(self):
        return {
            'data': [x.to_json() for x in self.data],
            'kdf': self.kdf if self.kdf else ''
        }


class Datum:
    def __init__(self, compact_jwe=None, tag=None):
        self.compact_jwe = compact_jwe
        self.tag = tag

    def to_json(self):
        return {
            'compact_jwe': self.compact_jwe if self.compact_jwe else '',
            'tag': self.tag if self.tag else ''
        }


class SecurityDomainRestoreData:
    def __init__(self):
        self.enc_data = EncData()
        self.wrapped_key = Key()

    def to_json(self):
        return {
            'EncData': self.enc_data.to_json(),
            'WrappedKey': self.wrapped_key.to_json()
        }


def _security_domain_gen_share_arrays(sd_wrapping_keys, shared_keys, required):
    matched = 0
    share_arrays = []
    ok = False

    for private_key_path in sd_wrapping_keys:
        if ok:
            break

        prefix = '.'.join(private_key_path.split('.')[:-1])
        cert_path = prefix + '.cer'

        with open(private_key_path, 'rb') as f:
            pem_data = f.read()
            private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())

        with open(cert_path, 'rb') as f:
            pem_data = f.read()
            cert = load_pem_x509_certificate(pem_data, backend=default_backend())
            public_bytes = cert.public_bytes(Encoding.DER)
            x5tS256 = Utils.security_domain_b64_url_encode(hashlib.sha256(public_bytes).digest())
            for item in shared_keys['enc_shares']:
                if x5tS256 == item['x5t_256']:
                    jwe = JWE(compact_jwe=item['enc_key'])
                    share = jwe.decrypt_using_private_key(private_key)
                    if not share:
                        continue

                    share_arrays.append(Utils.convert_to_uint16(share))  # type: ignore
                    matched += 1
                    if matched >= required:
                        ok = True
                        break

    return share_arrays


def _security_domain_gen_blob(transfer_key, share_arrays, enc_data, required):
    master_key = SharedSecret.get_plaintext(share_arrays, required=required)

    plaintext_list = []
    for item in enc_data['data']:
        compact_jwe = item['compact_jwe']
        tag = item['tag']
        enc_key = KDF.sp800_108(master_key, label=tag, context='', bit_length=512)
        jwe_data = JWE(compact_jwe)
        plaintext = jwe_data.decrypt_using_bytes(enc_key)
        plaintext_list.append((plaintext, tag))

    # encrypt
    security_domain_restore_data = SecurityDomainRestoreData()
    security_domain_restore_data.enc_data.kdf = 'sp108_kdf'  # type: ignore
    master_key = Utils.get_random(32)

    for plaintext, tag in plaintext_list:
        enc_key = KDF.sp800_108(master_key, label=tag, context='', bit_length=512)
        jwe = JWE()
        jwe.encrypt_using_bytes(enc_key, plaintext, alg_id='A256CBC-HS512', kid=tag)
        datum = Datum(compact_jwe=jwe.encode_compact(), tag=tag)
        security_domain_restore_data.enc_data.data.append(datum)

    with open(transfer_key, 'rb') as f:
        pem_data = f.read()
        exchange_cert = load_pem_x509_certificate(pem_data, backend=default_backend())

    # make the wrapped key
    jwe_wrapped = JWE()
    jwe_wrapped.encrypt_using_cert(exchange_cert, master_key)
    security_domain_restore_data.wrapped_key.enc_key = jwe_wrapped.encode_compact()
    thumbprint = Utils.get_SHA256_thumbprint(exchange_cert)
    security_domain_restore_data.wrapped_key.x5t_256 = Utils.security_domain_b64_url_encode(thumbprint)
    return json.dumps(security_domain_restore_data.to_json())


def _security_domain_make_restore_blob(sd_wrapping_keys, transfer_key, enc_data, shared_keys, required):
    share_arrays = _security_domain_gen_share_arrays(sd_wrapping_keys, shared_keys, required)
    return _security_domain_gen_blob(transfer_key, share_arrays, enc_data, required)


def _security_domain_restore_blob(sd_file, transfer_key, sd_wrapping_keys):
    """Using the wrapping keys, prepare the security domain for upload."""
    with open(sd_file) as f:
        sd_data = json.load(f)
        if not sd_data or 'EncData' not in sd_data or 'SharedKeys' not in sd_data:
            raise ValueError('Invalid SD file.')
        enc_data = sd_data['EncData']
        shared_keys = sd_data['SharedKeys']
    required = shared_keys['required']

    restore_blob_value = _security_domain_make_restore_blob(
        sd_wrapping_keys=sd_wrapping_keys,
        transfer_key=transfer_key,
        enc_data=enc_data,
        shared_keys=shared_keys,
        required=required
    )
    return restore_blob_value

def use_wrapping_keys() -> dict:
    key_paths = [f"{CERT_PATH_PREFIX}0.pem", f"{CERT_PATH_PREFIX}1.pem"]
    blob_value = _security_domain_restore_blob(SECURITY_DOMAIN_PATH, TRANSFER_KEY_PATH, key_paths)
    return {'value': blob_value}
