import unittest
import os
import random
import string
import json
import uuid
import time
from azure.keyvault.custom.internal import _bytes_to_int, _int_to_bytes, _int_to_bigendian_8_bytes, \
    _bstr_to_b64url, _b64_to_bstr, _b64_to_str, _str_to_b64url, _a128cbc_hs256_decrypt, _a128cbc_hs256_encrypt, \
    _RsaKey, _JwsHeader, _JweHeader, _JwsObject, _JweObject


class EncodingTests(unittest.TestCase):
    def test_int_byte_conversion(self):
        # generate a random byte
        b = os.urandom(1)
        i = _bytes_to_int(b)
        self._assert_bytes_significantly_equal(b, _int_to_bytes(i))

        # generate a random number of random bytes
        b = os.urandom(random.randint(1, 32))
        i = _bytes_to_int(b)
        self._assert_bytes_significantly_equal(b, _int_to_bytes(i))

        # generate random 4096 bits (4k key)
        b = os.urandom(512)
        i = _bytes_to_int(b)
        self._assert_bytes_significantly_equal(b, _int_to_bytes(i))

        #
        b = b'\x00\x00\x00\x01'
        i = _bytes_to_int(b)
        self._assert_bytes_significantly_equal(b, _int_to_bytes(i))

        b = b''
        with self.assertRaises(ValueError):
            _bytes_to_int(b)

        b = None
        with self.assertRaises(ValueError):
            _bytes_to_int(b)

    def test_int_to_bigendian_8_bytes(self):
        i = 0xFFFFFFFFFFFFFFFF
        b = _int_to_bigendian_8_bytes(i)
        self.assertEqual(b, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

        i = 0
        b = _int_to_bigendian_8_bytes(i)
        self.assertEqual(b, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        i = random.randint(1, 0xFFFFFFFFFFFFFFFF)
        b = _int_to_bigendian_8_bytes(i)
        self.assertEqual(len(b), 8)
        self.assertEqual(i, _bytes_to_int(b))

        i = random.randint(0xFFFFFFFFFFFFFFFF01, 0xFFFFFFFFFFFFFFFFFF)
        with self.assertRaises(ValueError):
            _int_to_bigendian_8_bytes(i)

    def test_bstr_encode_decode(self):
        b = b''
        b64 = _bstr_to_b64url(b)
        self.assertEqual(b, _b64_to_bstr(b64))

        b = os.urandom(1)
        b64 = _bstr_to_b64url(b)
        self.assertEqual(b, _b64_to_bstr(b64))

        b = os.urandom(random.randint(2, 32))
        b64 = _bstr_to_b64url(b)
        self.assertEqual(b, _b64_to_bstr(b64))

        b = os.urandom(512)
        b64 = _bstr_to_b64url(b)
        self.assertEqual(b, _b64_to_bstr(b64))

    def test_str_encode_decode(self):
        s = ''
        b64 = _str_to_b64url(s)
        self.assertEqual(s, _b64_to_str(b64))

        s = self._random_str(1)
        b64 = _str_to_b64url(s)
        self.assertEqual(s, _b64_to_str(b64))

        s = self._random_str(random.randint(2, 32))
        b64 = _str_to_b64url(s)
        self.assertEqual(s, _b64_to_str(b64))

        s = self._random_str(4096)
        b64 = _str_to_b64url(s)
        self.assertEqual(s, _b64_to_str(b64))

    def test_a128cbc_hs256_encrypt_decrypt(self):
        key = os.urandom(32)
        iv = os.urandom(16)

        plain_text = os.urandom(random.randint(1024, 4096))
        auth_data = os.urandom(random.randint(128, 512))

        cipher_text, auth_tag = _a128cbc_hs256_encrypt(key, iv, plain_text, auth_data)
        self.assertEqual(plain_text, _a128cbc_hs256_decrypt(key, iv, cipher_text, auth_data, auth_tag))

    def test_a128cbc_hs256_encrypt_error(self):
        key = os.urandom(32)
        iv = os.urandom(16)
        plain_text = os.urandom(random.randint(1024, 4096))
        auth_data = os.urandom(random.randint(128, 512))

        with self.assertRaises(ValueError):
            # key not specified
            _a128cbc_hs256_encrypt(key=None, iv=iv, plaintext=plain_text, authdata=auth_data)
            _a128cbc_hs256_encrypt(key=b'', iv=iv, plaintext=plain_text, authdata=auth_data)
            # key insufficient len
            _a128cbc_hs256_encrypt(key=os.urandom(31), iv=iv, plaintext=plain_text, authdata=auth_data)

            # iv not specified
            _a128cbc_hs256_encrypt(key=key, iv=None, plaintext=plain_text, authdata=auth_data)
            _a128cbc_hs256_encrypt(key=key, iv=b'', plaintext=plain_text, authdata=auth_data)
            # iv incorrect len
            _a128cbc_hs256_encrypt(key=key, iv=os.urandom(15), plaintext=plain_text, authdata=auth_data)
            _a128cbc_hs256_encrypt(key=key, iv=os.urandom(17), plaintext=plain_text, authdata=auth_data)

            # plaintext not specified
            _a128cbc_hs256_encrypt(key=key, iv=iv, plaintext=None, authdata=auth_data)
            _a128cbc_hs256_encrypt(key=key, iv=iv, plaintext=b'', authdata=auth_data)

            # authdata not specified
            _a128cbc_hs256_encrypt(key=key, iv=iv, plaintext=plain_text, authdata=None)
            _a128cbc_hs256_encrypt(key=key, iv=iv, plaintext=plain_text, authdata=b'')
            
    def test_a128cbc_hs256_decrypt_error(self):
        key = os.urandom(32)
        iv = os.urandom(16)
        cipher_text = os.urandom(random.randint(1024, 4096))
        auth_data = os.urandom(random.randint(128, 512))
        auth_tag = os.urandom(16)

        with self.assertRaises(ValueError):
            # key not specified
            _a128cbc_hs256_decrypt(key=None, iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)
            _a128cbc_hs256_decrypt(key=b'', iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)
            # key insufficient len
            _a128cbc_hs256_decrypt(key=os.urandom(31), iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)

            # iv not specified
            _a128cbc_hs256_decrypt(key=key, iv=None, ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)
            _a128cbc_hs256_decrypt(key=key, iv=b'', ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)
            # iv incorrect len
            _a128cbc_hs256_decrypt(key=key, iv=os.urandom(15), ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)
            _a128cbc_hs256_decrypt(key=key, iv=os.urandom(17), ciphertext=cipher_text, authdata=auth_data, authtag=auth_tag)

            # ciphertext not specified
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=None, authdata=auth_data, authtag=auth_tag)
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=b'', authdata=auth_data, authtag=auth_tag)

            # authdata not specified
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=None, authtag=auth_tag)
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=b'', authtag=auth_tag)

            # authtag not specified
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=None)
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=b'')
            # authtag invalid len
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=os.urandom(17))
            _a128cbc_hs256_decrypt(key=key, iv=iv, ciphertext=cipher_text, authdata=auth_data, authtag=os.urandom(15))

    def test_private_rsakey_to_from_jwk(self):
        # create a key1 export to jwk and import as key2
        key1 = _RsaKey.generate()
        jwk = key1.to_jwk(include_private=True)
        key2 = _RsaKey.from_jwk(jwk)

        # validate that key2 is a private key
        self.assertTrue(key2.is_private_key())

        # validate that key2 can encrypt and decrypt properly
        unwrapped = os.urandom(32)
        wrapped = key1.encrypt(unwrapped)
        self.assertEqual(unwrapped, key2.decrypt(wrapped))
        wrapped = key2.encrypt(unwrapped)
        self.assertEqual(unwrapped, key1.decrypt(wrapped))

        # validate that key2 can sign and verify properly
        data = os.urandom(random.randint(1024, 4096))
        signature = key1.sign(data)
        key2.verify(signature, data)
        signature = key2.sign(data)
        key1.verify(signature, data)

        # validate that all numbers, both public and private are consistent
        self.assertEqual(key1.kid, key2.kid)
        self.assertEqual(key1.kty, key2.kty)
        self.assertEqual(key1.key_ops, key2.key_ops)
        self.assertEqual(key1.n, key2.n)
        self.assertEqual(key1.e, key2.e)
        self.assertEqual(key1.q, key2.q)
        self.assertEqual(key1.p, key2.p)
        self.assertEqual(key1.d, key2.d)
        self.assertEqual(key1.dq, key2.dq)
        self.assertEqual(key1.dp, key2.dp)
        self.assertEqual(key1.qi, key2.qi)

        # validate that key2 serializes to the same jwk
        self.assertEqual(json.dumps(jwk.serialize()), json.dumps(key2.to_jwk(include_private=True).serialize()))

    def test_public_rsakey_to_from_jwk(self):
        # create key1 export public components and import as key2
        key1 = _RsaKey.generate()
        jwk = key1.to_jwk()
        key2 = _RsaKey.from_jwk(jwk)

        # validate that key2 is not a private key
        self.assertFalse(key2.is_private_key())

        # validate that key2 can encrypt properly
        unwrapped = os.urandom(32)
        wrapped = key2.encrypt(unwrapped)
        self.assertEqual(unwrapped, key1.decrypt(wrapped))

        # validate that key2 can verify properly
        data = os.urandom(random.randint(1024, 4096))
        signature = key1.sign(data)
        key2.verify(signature, data)

        # validate that all public numbers consistent
        self.assertEqual(key1.kid, key2.kid)
        self.assertEqual(key1.kty, key2.kty)
        self.assertEqual(key1.n, key2.n)
        self.assertEqual(key1.e, key2.e)

        # validate that all private numbers are not present
        self.assertIsNone(key2.q)
        self.assertIsNone(key2.p)
        self.assertIsNone(key2.d)
        self.assertIsNone(key2.dq)
        self.assertIsNone(key2.dp)
        self.assertIsNone(key2.qi)

        # validate that key2 serializes to the same public jwk
        self.assertEqual(json.dumps(jwk.serialize()), json.dumps(key2.to_jwk().serialize()))

    def test_jws_header_to_from_compact_header(self):
        head1 = _JwsHeader()
        head1.alg = 'RS256'
        head1.kid = str(uuid.uuid4())
        head1.at = self._random_str(random.randint(512, 1024))
        head1.ts = int(time.time())
        head1.typ = 'PoP'

        compact = head1.to_compact_header()

        head2 = _JwsHeader.from_compact_header(compact)

        # assert that all header values match
        self.assertEqual(head1.alg, head2.alg)
        self.assertEqual(head1.kid, head2.kid)
        self.assertEqual(head1.at, head2.at)
        self.assertEqual(head1.ts, head2.ts)
        self.assertEqual(head1.typ, head2.typ)

    def test_jwe_header_to_from_compact_header(self):
        head1 = _JweHeader()
        head1.alg = 'RSA-OAEP'
        head1.kid = str(uuid.uuid4())
        head1.enc = 'A128CBC-HS256'

        compact = head1.to_compact_header()
        head2 = _JweHeader.from_compact_header(compact)

        # assert that all header values match
        self.assertEqual(head1.alg, head2.alg)
        self.assertEqual(head1.kid, head2.kid)
        self.assertEqual(head1.enc, head2.enc)

    def _random_str(self, length):
        return ''.join(random.choice(string.printable) for i in range(length))

    def _assert_bytes_significantly_equal(self, b1, b2):
        self.assertEqual(b1.lstrip(b'\x00'), b2.lstrip(b'\x00'))
