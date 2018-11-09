#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

import json
import time
import os
from ._internal import _a128cbc_hs256_encrypt, _a128cbc_hs256_decrypt, _JwsHeader, _JwsObject, \
    _JweHeader, _JweObject, _str_to_b64url, _bstr_to_b64url, _b64_to_bstr, _RsaKey


def generate_pop_key():
    """
    Generates a key which can be used for Proof Of Possession token authentication.
    :return:
    """
    return _RsaKey.generate()


class HttpMessageSecurity(object):
    """
    Used for message authorization, encryption and decrtyption.

    This class is intended for internal use only.  Details are subject to non-compatible changes, consumers of the
    azure-keyvault module should not take dependencies on this class or its current implementation.
    """
    def __init__(self, client_security_token=None,
                 client_signature_key=None,
                 client_encryption_key=None,
                 server_signature_key=None,
                 server_encryption_key=None):
        self.client_security_token = client_security_token
        self.client_signature_key = client_signature_key
        self.client_encryption_key = client_encryption_key
        self.server_signature_key = server_signature_key
        self.server_encryption_key = server_encryption_key

    def protect_request(self, request):
        """
        Adds authorization header, and encrypts and signs the request if supported on the specific request.
        :param request: unprotected request to apply security protocol
        :return: protected request with appropriate security protocal applied
        """
        # Setup the auth header on the request
        # Due to limitations in the service we hard code the auth scheme to 'Bearer' as the service will fail with any
        # other scheme or a different casing such as 'bearer', once this is fixed the following line should be replaced:
        # request.headers['Authorization'] = '{} {}'.format(auth[0], auth[1])
        request.headers['Authorization'] = '{} {}'.format('Bearer', self.client_security_token)

        # if the current message security doesn't support message protection, or the body is empty
        # skip protection and return the original request
        if not self.supports_protection() or len(request.body) == 0:
            return request

        plain_text = request.body

        # if the client encryption key is specified add it to the body of the request
        if self.client_encryption_key:
            # note that this assumes that the body is already json and not simple string content
            # this is true for all requests which currently support message encryption, but might
            # need to be revisited when the types of
            body_dict = json.loads(plain_text)
            body_dict['rek'] = {'jwk': self.client_encryption_key.to_jwk().serialize()}
            plain_text = json.dumps(body_dict).encode(encoding='utf8')

        # build the header for the jws body
        jws_header = _JwsHeader()
        jws_header.alg = 'RS256'
        jws_header.kid = self.client_signature_key.kid
        jws_header.at = self.client_security_token
        jws_header.ts = int(time.time())
        jws_header.typ = 'PoP'

        jws = _JwsObject()

        jws.protected = jws_header.to_compact_header()
        jws.payload = self._protect_payload(plain_text)
        data = (jws.protected + '.' + jws.payload).encode('ascii')
        jws.signature = _bstr_to_b64url(self.client_signature_key.sign(data))

        request.headers['Content-Type'] = 'application/jose+json'

        request.prepare_body(data=jws.to_flattened_jws(), files=None)

        return request

    def unprotect_response(self, response, **kwargs):
        """
        Removes protection from the specified response
        :param request: response from the key vault service
        :return: unprotected response with any security protocal encryption removed
        """
        body = response.content
        # if the current message security doesn't support message protection, the body is empty, or the request failed
        # skip protection and return the original response
        if not self.supports_protection() or len(response.content) == 0 or response.status_code != 200:
            return response

        # ensure the content-type is application/jose+json
        if 'application/jose+json' not in response.headers.get('content-type', '').lower():
            raise ValueError('Invalid protected response')

        # deserialize the response into a JwsObject, using response.text so requests handles the encoding
        jws = _JwsObject().deserialize(body)

        # deserialize the protected header
        jws_header = _JwsHeader.from_compact_header(jws.protected)

        # ensure the jws signature kid matches the key from original challenge
        # and the alg matches expected signature alg
        if jws_header.kid != self.server_signature_key.kid \
                or jws_header.alg != 'RS256':
            raise ValueError('Invalid protected response')

        # validate the signature of the jws
        data = (jws.protected + '.' + jws.payload).encode('ascii')
        # verify will raise an InvalidSignature exception if the signature doesn't match
        self.server_signature_key.verify(signature=_b64_to_bstr(jws.signature), data=data)

        # get the unprotected response body
        decrypted = self._unprotect_payload(jws.payload)

        response._content = decrypted
        response.headers['Content-Type'] = 'application/json'

        return response

    def supports_protection(self):
        """
        Determines if the the current HttpMessageSecurity object supports the message protection protocol.
        :return: True if the current object supports protection, otherwise False
        """
        return self.client_signature_key \
               and self.client_encryption_key \
               and self.server_signature_key \
               and self.server_encryption_key

    def _protect_payload(self, plaintext):
        # create the jwe header for the payload
        kek = self.server_encryption_key
        jwe_header = _JweHeader()
        jwe_header.alg = 'RSA-OAEP'
        jwe_header.kid = kek.kid
        jwe_header.enc = 'A128CBC-HS256'

        # create the jwe object
        jwe = _JweObject()
        jwe.protected = jwe_header.to_compact_header()

        # generate the content encryption key and iv
        cek = os.urandom(32)
        iv = os.urandom(16)
        jwe.iv = _bstr_to_b64url(iv)
        # wrap the cek using the server encryption key
        wrapped = _bstr_to_b64url(kek.encrypt(cek))
        jwe.encrypted_key = wrapped

        # encrypt the plaintext body with the cek using the protected header
        # as the authdata to get the ciphertext and the authtag
        ciphertext, tag = _a128cbc_hs256_encrypt(cek, iv, plaintext, jwe.protected.encode('ascii'))

        jwe.ciphertext = _bstr_to_b64url(ciphertext)
        jwe.tag = _bstr_to_b64url(tag)

        # flatten and encode the jwe for the final jws payload content
        flat = jwe.to_flattened_jwe()
        return _str_to_b64url(flat)

    def _unprotect_payload(self, payload):
        # deserialize the payload
        jwe = _JweObject().deserialize_b64(payload)

        # deserialize the payload header
        jwe_header = _JweHeader.from_compact_header(jwe.protected)

        # ensure the kid matches the specified client encryption key
        # and the key wrap alg and the data encryption enc match the expected
        if self.client_encryption_key.kid != jwe_header.kid \
                or jwe_header.alg != 'RSA-OAEP' \
                or jwe_header.enc != 'A128CBC-HS256':
            raise ValueError('Invalid protected response')

        # unwrap the cek using the client encryption key
        cek = self.client_encryption_key.decrypt(_b64_to_bstr(jwe.encrypted_key))

        # decrypt the cipher text to get the unprotected body content
        return _a128cbc_hs256_decrypt(cek,
                                      _b64_to_bstr(jwe.iv),
                                      _b64_to_bstr(jwe.ciphertext),
                                      jwe.protected.encode('ascii'),
                                      _b64_to_bstr(jwe.tag))