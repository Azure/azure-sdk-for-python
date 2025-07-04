# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import array
import base64
import codecs
import hashlib
import hmac
import json
import os
import secrets

from azure.keyvault.securitydomain.models import CertificateInfo, SecurityDomainJsonWebKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate


PATH_PREFIX = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, "resources"))
CERT_PATH_PREFIX = f"{PATH_PREFIX}/certificate"
SECURITY_DOMAIN_PATH = f"{PATH_PREFIX}/security-domain.json"
TRANSFER_KEY_PATH = f"{PATH_PREFIX}/transfer-key.json"


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


class KDF:
    @staticmethod
    def to_big_endian_32bits(value):
        result = bytearray()
        result.append((value & 0xFF000000) >> 24)
        result.append((value & 0x00FF0000) >> 16)
        result.append((value & 0x0000FF00) >> 8)
        result.append(value & 0x000000FF)
        return result

    @staticmethod
    def to_big_endian_64bits(value):
        result = bytearray()
        result.append((value & 0xFF00000000000000) >> 56)
        result.append((value & 0x00FF000000000000) >> 48)
        result.append((value & 0x0000FF0000000000) >> 40)
        result.append((value & 0x000000FF00000000) >> 32)
        result.append((value & 0x00000000FF000000) >> 24)
        result.append((value & 0x0000000000FF0000) >> 16)
        result.append((value & 0x000000000000FF00) >> 8)
        result.append(value & 0x00000000000000FF)
        return result

    @staticmethod
    def test_sp800_108():
        label = 'label'
        context = 'context'
        bit_length = 256
        hex_result = 'f0ca51f6308791404bf68b56024ee7c64d6c737716f81d47e1e68b5c4e399575'
        key = bytearray()
        key.extend([0x41] * 32)

        new_key = KDF.sp800_108(key, label, context, bit_length)
        hex_value = new_key.hex().replace('-', '')  # type: ignore
        return hex_value.lower() == hex_result

    @staticmethod
    def sp800_108(key_in: bytearray, label: str, context: str, bit_length):
        """
        Note - initialize out to be the number of bytes of keying material that you need
        This implements SP 800-108 in counter mode, see section 5.1

        Fixed values:
            1. h - The length of the output of the PRF in bits, and
            2. r - The length of the binary representation of the counter i.

        Input: KI, Label, Context, and L.

        Process:
            1. n := ⎡L/h⎤.
            2. If n > 2^(r-1), then indicate an error and stop.
            3. result(0):= ∅.
            4. For i = 1 to n, do
                a. K(i) := PRF (KI, [i]2 || Label || 0x00 || Context || [L]2)
                b. result(i) := result(i-1) || K(i).

            5. Return: KO := the leftmost L bits of result(n).
        """

        if bit_length <= 0 or bit_length % 8 != 0:
            return None

        L = bit_length
        bytes_needed = bit_length // 8
        hMAC = hmac.HMAC(key_in, digestmod=hashlib.sha512)
        hash_bits = hMAC.digest_size
        n = L // hash_bits
        if L % hash_bits != 0:
            n += 1

        hmac_data_suffix = bytearray()
        hmac_data_suffix.extend(label.encode('UTF-8'))
        hmac_data_suffix.append(0)
        hmac_data_suffix.extend(context.encode('UTF-8'))
        hmac_data_suffix.extend(KDF.to_big_endian_32bits(bit_length))

        out_value = bytearray()
        for i in range(n):
            hmac_data = bytearray()
            hmac_data.extend(KDF.to_big_endian_32bits(i + 1))
            hmac_data.extend(hmac_data_suffix)
            hMAC.update(hmac_data)
            hash_value = hMAC.digest()

            if bytes_needed > len(hash_value):
                out_value.extend(hash_value)
                bytes_needed -= len(hash_value)
            else:
                out_value.extend(hash_value[len(out_value): len(out_value) + bytes_needed])
                return out_value

        return None


class JWEHeader:  # pylint: disable=too-many-instance-attributes
    _fields = ['alg', 'enc', 'zip', 'jku', 'jwk', 'kid', 'x5u', 'x5c', 'x5t', 'x5t_S256', 'typ', 'cty', 'crit']

    def __init__(self, alg=None, enc=None, zip=None,  # pylint: disable=redefined-builtin
                 jku=None, jwk=None, kid=None, x5u=None, x5c=None, x5t=None,
                 x5t_S256=None, typ=None, cty=None, crit=None):
        """
            JWE header
        :param alg: algorithm
        :param enc: encryption algorithm
        :param zip: compression algorithm
        :param jku: JWK set URL
        :param jwk: JSON Web key
        :param kid: Key ID
        :param x5u: X.509 certificate URL
        :param x5c: X.509 certificate chain
        :param x5t: X.509 certificate SHA-1 Thumbprint
        :param x5t_S256: X.509 certificate SHA-256 Thumbprint
        :param typ: type
        :param cty: content type
        :param crit: critical
        """
        self.alg = alg
        self.enc = enc
        self.zip = zip
        self.jku = jku
        self.jwk = jwk
        self.kid = kid
        self.x5u = x5u
        self.x5c = x5c
        self.x5t = x5t
        self.x5t_S256 = x5t_S256
        self.typ = typ
        self.cty = cty
        self.crit = crit

    @staticmethod
    def from_json_str(json_str):
        json_dict = json.loads(json_str)
        jwe_header = JWEHeader()
        for k in jwe_header._fields:
            if k == 'x5t_S256':
                v = json_dict.get('x5t#S256', None)
            else:
                v = json_dict.get(k, None)
            if v is not None:
                setattr(jwe_header, k, v)
        return jwe_header

    def to_json_str(self):
        json_dict = {}
        for k in self._fields:
            v = getattr(self, k, None)
            if v is not None:
                if k == 'x5t_S256':
                    json_dict['x5t#S256'] = v
                else:
                    json_dict[k] = v
        return json.dumps(json_dict)


class JWEDecode:
    def __init__(self, compact_jwe=None):
        if compact_jwe is None:
            self.encoded_header = ''
            self.encrypted_key = None
            self.init_vector = None
            self.ciphertext = None
            self.auth_tag = None
            self.protected_header = JWEHeader()
        else:
            parts = compact_jwe.split('.')

            self.encoded_header = parts[0]
            header = base64.urlsafe_b64decode(self.encoded_header + '===').decode('ascii')  # Fix incorrect padding
            self.protected_header = JWEHeader.from_json_str(header)
            self.encrypted_key = base64.urlsafe_b64decode(parts[1] + '===')
            self.init_vector = base64.urlsafe_b64decode(parts[2] + '===')
            self.ciphertext = base64.urlsafe_b64decode(parts[3] + '===')
            self.auth_tag = base64.urlsafe_b64decode(parts[4] + '===')

    def encode_header(self):
        header_json = self.protected_header.to_json_str().replace('": ', '":').replace('", ', '",')
        self.encoded_header = Utils.security_domain_b64_url_encode(header_json.encode('ascii'))

    def encode_compact(self):
        ret = [self.encoded_header + '.']

        if self.encrypted_key is not None:
            ret.append(Utils.security_domain_b64_url_encode(self.encrypted_key))
        ret.append('.')

        if self.init_vector is not None:
            ret.append(Utils.security_domain_b64_url_encode(self.init_vector))
        ret.append('.')

        if self.ciphertext is not None:
            ret.append(Utils.security_domain_b64_url_encode(self.ciphertext))
        ret.append('.')

        if self.auth_tag is not None:
            ret.append(Utils.security_domain_b64_url_encode(self.auth_tag))

        return ''.join(ret)


class JWE:
    def __init__(self, compact_jwe=None):
        self.jwe_decode = JWEDecode(compact_jwe=compact_jwe)

    def encode_compact(self):
        return self.jwe_decode.encode_compact()

    def get_padding_mode(self):
        alg = self.jwe_decode.protected_header.alg

        if alg == 'RSA-OAEP-256':
            algorithm = hashes.SHA256()
            return asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=algorithm), algorithm=algorithm, label=None)

        if alg == 'RSA-OAEP':
            algorithm = hashes.SHA1()
            return asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=algorithm), algorithm=algorithm, label=None)

        if alg == 'RSA1_5':
            return asymmetric_padding.PKCS1v15()

        return None

    def get_cek(self, private_key):
        return private_key.decrypt(
            self.jwe_decode.encrypted_key,
            self.get_padding_mode()
        )

    def set_cek(self, cert, cek):
        public_key = cert.public_key()
        self.jwe_decode.encrypted_key = public_key.encrypt(bytes(cek), self.get_padding_mode())

    @staticmethod
    def dek_from_cek(cek):
        dek = bytearray()
        for i in range(32):
            dek.append(cek[i + 32])
        return dek

    @staticmethod
    def hmac_key_from_cek(cek):
        hk = bytearray()
        for i in range(32):
            hk.append(cek[i])
        return hk

    def get_mac(self, hk):
        header_bytes = bytearray()
        header_bytes.extend(self.jwe_decode.encoded_header.encode('ascii'))
        auth_bits = len(header_bytes) * 8

        hash_data = bytearray()
        hash_data.extend(header_bytes)
        hash_data.extend(self.jwe_decode.init_vector)  # type: ignore
        hash_data.extend(self.jwe_decode.ciphertext)  # type: ignore
        hash_data.extend(KDF.to_big_endian_64bits(auth_bits))

        hMAC = hmac.HMAC(hk, msg=hash_data, digestmod=hashlib.sha512)
        return hMAC.digest()

    def Aes256HmacSha512Decrypt(self, cek):
        dek = JWE.dek_from_cek(cek)
        hk = JWE.hmac_key_from_cek(cek)
        mac_value = self.get_mac(hk)

        test = 0
        i = 0
        while i < len(self.jwe_decode.auth_tag) == 32:  # type: ignore
            test |= (self.jwe_decode.auth_tag[i] ^ mac_value[i])  # type: ignore
            i += 1

        if test != 0:
            return None

        aes_key = dek
        aes_iv = self.jwe_decode.init_vector
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())  # type: ignore
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(self.jwe_decode.ciphertext) + decryptor.finalize()  # type: ignore

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(bytes(plaintext)) + unpadder.finalize()

        return plaintext

    def Aes256HmacSha512Encrypt(self, cek, plaintext):
        dek = JWE.dek_from_cek(cek)
        hk = JWE.hmac_key_from_cek(cek)

        padder = padding.PKCS7(128).padder()
        plaintext = padder.update(bytes(plaintext)) + padder.finalize()

        aes_key = dek
        aes_iv = Utils.get_random(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())  # type: ignore
        encryptor = cipher.encryptor()
        self.jwe_decode.ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        self.jwe_decode.init_vector = aes_iv  # type: ignore

        mac_value = self.get_mac(hk)
        self.jwe_decode.auth_tag = bytearray()  # type: ignore
        for i in range(32):
            self.jwe_decode.auth_tag.append(mac_value[i])  # type: ignore

    def decrypt_using_bytes(self, cek):
        if self.jwe_decode.protected_header.enc == 'A256CBC-HS512':
            return self.Aes256HmacSha512Decrypt(cek)
        return None

    def get_cek_from_private_key(self, private_key):
        return private_key.decrypt(self.jwe_decode.encrypted_key, self.get_padding_mode())

    def decrypt_using_private_key(self, private_key):
        cek = self.get_cek_from_private_key(private_key)
        return self.decrypt_using_bytes(cek)

    def encrypt_using_bytes(self, cek, plaintext, alg_id, kid=None):
        if kid is not None:
            self.jwe_decode.protected_header.alg = 'dir'
            self.jwe_decode.protected_header.kid = kid

        if alg_id == 'A256CBC-HS512':
            self.jwe_decode.protected_header.enc = alg_id
            self.jwe_decode.encode_header()
            self.Aes256HmacSha512Encrypt(cek, plaintext)

    def encrypt_using_cert(self, cert, plaintext):
        self.jwe_decode.protected_header.alg = 'RSA-OAEP-256'
        self.jwe_decode.protected_header.kid = 'not used'
        cek = Utils.get_random(64)
        self.set_cek(cert, cek)
        self.encrypt_using_bytes(cek, plaintext, alg_id='A256CBC-HS512')


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
    sd_wrapping_keys = [f"{CERT_PATH_PREFIX}0.cer", f"{CERT_PATH_PREFIX}1.cer", f"{CERT_PATH_PREFIX}2.cer"]
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
                n=n,  # type: ignore
                e=e,  # type: ignore
                x5_c=x5c,
                alg=alg,
                x5_t=x5t,
                x5_t_s256=x5tS256,
            )
        )
    return CertificateInfo(certificates=certificates, required=2)


def use_wrapping_keys() -> dict:
    key_paths = [f"{CERT_PATH_PREFIX}0.pem", f"{CERT_PATH_PREFIX}1.pem"]
    blob_value = _security_domain_restore_blob(SECURITY_DOMAIN_PATH, TRANSFER_KEY_PATH, key_paths)
    return {'value': blob_value}


def write_security_domain(security_domain: str) -> None:
    try:
        with open(SECURITY_DOMAIN_PATH, "w") as f:
            f.write(security_domain)
    except Exception as ex:  # pylint: disable=broad-except
        if os.path.isfile(SECURITY_DOMAIN_PATH):
            os.remove(SECURITY_DOMAIN_PATH)
        raise ex


def write_transfer_key(transfer_key: dict) -> None:
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
        with open(TRANSFER_KEY_PATH, "w") as f:
            f.write(get_x5c_as_pem())
    except Exception as ex:  # pylint: disable=broad-except
        if os.path.isfile(TRANSFER_KEY_PATH):
            os.remove(TRANSFER_KEY_PATH)
        raise ex


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


if __name__ == "__main__":
    print(Utils.convert_to_uint16(bytearray([40, 30, 20, 10])))
