# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import base64
import json
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from ._common import Base64Url
from ._generated.models import PolicyResult, AttestationResult, StoredAttestationPolicy, JSONWebKey, CertificateModification, AttestationType
from typing import Any, Callable, List, Type, TypeVar, Generic, Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import Certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from json import JSONDecoder, JSONEncoder
from datetime import datetime

T = TypeVar('T', PolicyResult, AttestationResult, StoredAttestationPolicy)


class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    :param list[bytes] certificates: A list of Base64 encoded X.509
        Certificates representing an X.509 certificate chain. The first of these
        certificates will be used to sign an :class:`AttestationToken`. 
    :param str key_id: A string which identifies a signing key, See 
        `RFC 7517 Section 4.5 <https://tools.ietf.org/html/rfc7517#section-4.5>`_

    """
    def __init__(self, certificates, key_id, **kwargs):
        # type: (list[bytes], str, Any) -> None
        self.certificates = certificates
        self.key_id = key_id

class PolicyCertificatesModificationResult(object):
    """The result of a policy certificate modification.

    :param certificate_thumbprint: Hex encoded SHA1 Hash of the binary representation certificate
     which was added or removed.
    :type certificate_thumbprint: str
    :param certificate_resolution: The result of the operation. Possible values include:
     "IsPresent", "IsAbsent".
    :type certificate_resolution: str or
     ~azure.security.attestation._generated.models.CertificateModification
    """

    def __init__(self, certificate_thumbprint, certificate_resolution):
        #type:(str, CertificateModification)->None
        self.certificate_thumbprint = certificate_thumbprint
        self.certificate_resolution = certificate_resolution

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls
        return cls(generated.certificate_thumbprint, generated.certificate_resolution)


class AttestationData(object):
    """ AttestationData represents an object passed as an input to the Attestation Service.
    
    AttestationData comes in two forms: Binary and JSON. To distinguish between the two, when an :class:`AttestationData`
    object is created, the caller provides an indication that the input binary data will be treated as either JSON or Binary.

    The AttestationData is reflected in the generated :class:`AttestationResult` in two possible ways.
    If the AttestationData is Binary, then the AttestationData is reflected in the AttestationResult.enclave_held_data claim.
    If the AttestationData is JSON, then the AttestationData is expressed as JSON in the AttestationResult.runtime_claims or AttestationResult.inittime_claims claim.

    :param bytes data: Input data to be sent to the attestation service.
    :param bool is_json: True if the attestation service should treat the input data as JSON.
    """
    def __init__(self, data, is_json=None):
        # type:(bytes, bool) -> None
        self._data = data

        # If the caller thought that the input data is JSON, then respect their 
        # choice (this allows a caller to specify JSON data as if it was not JSON).
        if is_json is not None:
            self._is_json = is_json
        else:
            # The caller didn't say if the parameter is JSON or not, try parsing it,
            # and if it parses, assume it's JSON.
            try:
                json.loads(data)
                self._is_json = True
            except Exception:
                self._is_json = False

class TokenValidationOptions(object):
    """ Validation options for an Attestation Token object.

    :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
    :keyword Callable[['AttestationToken', 'AttestationSigner'], bool] validation_callback: Callback to allow clients to perform custom validation of the token.
    :keyword bool validate_signature: if True, validate the signature of the token being validated.
    :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
    :keyword str issuer: Expected issuer, used if validate_issuer is true.
    :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
    :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
    """

    def __init__(self, **kwargs):
        #type: (**Any) -> None

        self.validate_token = kwargs.get('validate_token', True)  # type: bool
        self.validation_callback = kwargs.get('validation_callback') # type:Callable[['AttestationToken', AttestationSigner], bool]
        self.validate_signature = kwargs.get('validate_signature', True)  # type:bool
        self.validate_expiration = kwargs.get('validate_expiration', True)  # type:bool
        self.validate_not_before = kwargs.get('validate_not_before', True)  # type:bool
        self.validate_issuer = kwargs.get('validate_issuer', False)  # type:bool
        self.issuer = kwargs.get('issuer')  # type:str
        self.validation_slack = kwargs.get('validation_slack')  # type:int


class AttestationSigningKey(object):
    """ Represents a signing key used by the attestation service.

    Typically the signing key used by the service consists of two components: An RSA or ECDS private key and an X.509 Certificate wrapped around
    the public key portion of the private key.

    :var signing_key: The RSA or ECDS signing key to sign the token supplied to the customer DER encoded.
    :vartype signing_key: bytes
    :var certificate: A DER encoded X.509 Certificate whose public key matches the signing_key's public key.
    :vartype certificate: bytes
    """

    def __init__(self, signing_key_der, certificate_der):
    # type: (bytes, bytes) -> None
        signing_key = serialization.load_der_private_key(signing_key_der, password=None, backend=default_backend())
        certificate = load_der_x509_certificate(certificate_der, backend=default_backend())

        self._signing_key = signing_key
        self._certificate = certificate

        # We only support ECDS and RSA keys in the MAA service.
        if (not isinstance(signing_key, RSAPrivateKey) and not isinstance(signing_key, EllipticCurvePrivateKey)):
            raise ValueError("Signing keys must be either ECDS or RSA keys.")

        # Ensure that the public key in the certificate matches the public key of the key.
        cert_public_key = certificate.public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        key_public_key = signing_key.public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        if cert_public_key != key_public_key:
            raise ValueError("Signing key must match certificate public key")


class AttestationToken(Generic[T]):
    """ Represents a token returned from the attestation service.

    :keyword Any body: The body of the newly created token, if provided.
    :keyword AttestationSigningKey signer: If specified, the key used to sign the token.
        If the `signer` property is not specified, the token created is unsecured.
    :keyword str token: If no body or signer is provided, the string representation of the token.
    :keyword Type body_type: The underlying type of the body of the 'token' parameter, used to deserialize the underlying body when parsing the token.
    """

    def __init__(self, **kwargs):
        body = kwargs.get('body')  # type: Any
        signer = kwargs.get('signer')  # type: AttestationSigningKey
        if body:
            if signer:
                token = self._create_secured_jwt(body, signer)
            else:
                token = self._create_unsecured_jwt(body)
        else:
            token = kwargs.pop('token')

        self._token = token
        self._body_type = kwargs.get('body_type') #type: Type
        token_parts = token.split('.')
        if len(token_parts) != 3:
            raise ValueError("Malformed JSON Web Token")
        self.header_bytes = Base64Url.decode(token_parts[0])
        self.body_bytes = Base64Url.decode(token_parts[1])
        self.signature_bytes = Base64Url.decode(token_parts[2])
        self._body = JSONDecoder().decode(self.body_bytes.decode('ascii'))
        self._header = JSONDecoder().decode(self.header_bytes.decode('ascii'))

    def __str__(self):
        return self._token

    @property
    def algorithm(self):
        #type:() -> Union[str, None]
        """ Json Web Token Header "alg". 
        
        See `RFC 7515 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.1>`_ for details.

        If the value of algorithm is "none" it indicates that the token is unsecured.
        """
        return self._header.get('alg')

    @property
    def key_id(self):
        #type:() -> Union[str, None]
        """ Json Web Token Header "kid". 
        
        See `RFC 7515 Section 4.1.4 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.4>`_ for details.
        """
        return self._header.get('kid')

    @property
    def expiration_time(self):
        #type:() -> Union[datetime, None]
        """ Expiration time for the token.
        """
        exp = self._body.get('exp')
        if exp:
            return datetime.fromtimestamp(exp)
        return None

    @property
    def not_before_time(self): 
        #type:() -> Union[datetime, None]
        """ Time before which the token is invalid.
        """
        nbf = self._body.get('nbf')
        if nbf:
            return  datetime.fromtimestamp(nbf)
        return None

    @property
    def issuance_time(self): 
        #type:() -> Union[datetime, None]
        """ Time when the token was issued.
        """
        iat = self._body.get('iat')
        if iat:
            return  datetime.fromtimestamp(iat)
        return None

    @property
    def content_type(self): 
        #type:() -> Union[str, None]
        """ Json Web Token Header "content type".
        
        See `RFC 7515 Section 4.1.10 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.10>`_ for details.
        """
        return self._header.get('cty')

    @property
    def critical(self):
        #type() -> # type: Optional[bool]
        """ Json Web Token Header "Critical". 
        
        See `RFC 7515 Section 4.1.11 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.11>`_ for details.
        """
        return self._header.get('crit')

    @property
    def key_url(self): 
        #type:() -> Union[str, None]
        """ Json Web Token Header "Key URL". 
        
        See `RFC 7515 Section 4.1.2 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.2>`_ for details.
        """
        return self._header.get('jku')

    @property
    def x509_url(self): 
        #type:() -> Union[str, None]
        """  Json Web Token Header "X509 URL".

        See `RFC 7515 Section 4.1.5 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.5>`_ for details.
        """
        return self._header.get('x5u')

    @property
    def type(self):
        #type:() -> Union[str, None]
        """ Json Web Token Header "typ".
        
        `RFC 7515 Section 4.1.9 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.9>`_ for details.
        """
        return self._header.get('typ')

    @property
    def certificate_thumbprint(self):
        #type:() -> Union[str, None]
        """ The "thumbprint" of the certificate used to sign the request. 
        
        `RFC 7515 Section 4.1.7 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.7>`_ for details.
        """
        return self._header.get('x5t')

    @property
    def certificate_sha256_thumbprint(self):
        #type:() -> Union[str, None]
        """ The "thumbprint" of the certificate used to sign the request generated using the SHA256 algorithm. 
        
        `RFC 7515 Section 4.1.8 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.8>`_ for details.
        """
        return self._header.get('x5t#256')

    @property
    def issuer(self):
        #type:() -> Union[str, None]
        """ Json Web Token "iss" claim.
        
        `RFC 7519 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.1>`_ for details.
        """
        return self._body.get('iss')

    @property
    def x509_certificate_chain(self):
        #type:() -> Union[list[str], None]
        """ An array of Base64 encoded X.509 certificates which represent a certificate chain used to sign the token. 
        
        See `RFC 7515 Section 4.1.6 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.6>`_ for details.
        """
        x5c = self._header.get('x5c')
        if x5c is not None:
            return x5c
        return None

    def _json_web_key(self):
        #type:() -> Union[JSONWebKey, None]
        jwk = self._header.get('jwk')
        return JSONWebKey.deserialize(jwk)

    def serialize(self):
        """ Serialize the JSON Web Token to a string"""
        return self._token

    def validate_token(self, options=None, signers=None):
        # type: (TokenValidationOptions, list[AttestationSigner]) -> bool
        """ Validate the attestation token based on the options specified in the
         :class:`TokenValidationOptions`.
        
        :param TokenValidationOptions options: Options to be used when validating 
            the token.
        :param list[AttestationSigner] signers: Potential signers for the token.
            If the signers parameter is specified, validate_token will only 
            consider the signers as potential signatories for the token, otherwise
            it will consider attributes in the header of the token.
        :return bool: Returns True if the token successfully validated, False 
            otherwise. 

        :raises: AttestationTokenValidationException
        """
        if (options is None):
            options = TokenValidationOptions(
                validate_token=True, validate_signature=True, validate_expiration=True)
        if not options.validate_token:
            self._validate_static_properties(options)
            if (options.validation_callback is not None):
                options.validation_callback(self, None)
            return True

        signer = None
        if self.algorithm != 'none' and options.validate_signature:
            # validate the signature for the token.
            candidate_certificates = self._get_candidate_signing_certificates(
                signers)
            signer = self._validate_signature(candidate_certificates)
            if (signer is None):
                raise AttestationTokenValidationException(
                    "Could not find the certificate used to sign the token.")
        self._validate_static_properties(options)

        if (options.validation_callback is not None):
            if options.validation_callback(self, signer):
                return True
            raise AttestationTokenValidationException("User validation callback failed the validation request.")

        return True

    def get_body(self):
        # type: () -> T
        """ Returns the body of the attestation token as an object.
        """
        try:
            return self._body_type.deserialize(self._body)
        except AttributeError:
            return self._body

    def _get_candidate_signing_certificates(self, signing_certificates):
        # type: (list[AttestationSigner]) -> list[AttestationSigner]

        candidates = []
        desired_key_id = self.key_id
        if desired_key_id is not None:
            for signer in signing_certificates:
                if (signer.key_id == desired_key_id):
                    candidates.append(signer)
                    break
            # If we didn't find a matching key ID in the supplied certificates,
            # try the JWS header to see if there might be a corresponding key.
            if (len(candidates) == 0):
                jwk = self._json_web_key()
                if jwk is not None:
                    if jwk.kid  == desired_key_id:
                        if (jwk.x5_c):
                            signers = self._get_certificates_from_x5c(jwk.x5_c)
                        candidates.append(AttestationSigner(
                            signers, desired_key_id))
        else:
            # We don't have a signer, so we need to try every possible signer.
            # If the caller provided a list of certificates, use that as the exclusive source,
            # otherwise iterate through the possible certificates.
            if signing_certificates is not None:
                for signer in signing_certificates:
                    candidates.append(signer)
            else:
                jwk = self._json_web_key()
                if jwk.x5_c is not None:
                    signers = self._get_certificates_from_x5c(
                        self._json_web_key().x5_c)
                    candidates.append(AttestationSigner(signers, None))
                candidates.append(self.x509_certificate_chain)

        return candidates

    def _get_certificates_from_x5c(self, x5clist):
        # type:(list[str]) -> list[Certificate]
        return [base64.b64decode(b64cert) for b64cert in x5clist]

    def _validate_signature(self, candidate_certificates):
        # type:(list[AttestationSigner]) -> AttestationSigner
        signed_data = Base64Url.encode(
            self.header_bytes)+'.'+Base64Url.encode(self.body_bytes)
        for signer in candidate_certificates:
            cert = load_der_x509_certificate(signer.certificates[0], backend=default_backend())
            signer_key = cert.public_key()
            # Try to verify the signature with this candidate.
            # If it doesn't work, try the next signer.
            try:
                if isinstance(signer_key, RSAPublicKey):
                    signer_key.verify(
                        self.signature_bytes,
                        signed_data.encode('utf-8'),
                        padding.PKCS1v15(),
                        SHA256())
                else:
                    signer_key.verify(
                        self.signature_bytes,
                        signed_data.encode('utf-8'),
                        SHA256())
                return signer
            except:
                raise AttestationTokenValidationException("Could not verify signature of attestatoin token.")
        return None

    def _validate_static_properties(self, options):
        # type:(TokenValidationOptions) -> bool
        """ Validate the static properties in the attestation token.
        """
        if options.validate_expiration and self.expiration_time is not None:
            if (datetime.now() > self.expiration_time):
                delta = datetime.now() - self.expiration_time
                if delta.total_seconds > options.validation_slack:
                    raise AttestationTokenValidationException(u'Token is expired.')
        if options.validate_not_before and hasattr(self, 'not_before_time') and self.not_before_time is not None:
            if (datetime.now() < self.not_before_time):
                delta = self.expiration_time - datetime.now()
                if delta.total_seconds > options.validation_slack:
                    raise AttestationTokenValidationException(u'Token is not yet valid.')
        if options.validate_issuer and hasattr(self, 'issuer') and self.issuer is not None:
            if (options.issuer != self.issuer):
                raise AttestationTokenValidationException(u'Issuer in token: {} is not the expected issuer: {}.'.format(self.issuer, options.issuer))
        return True

    @staticmethod
    def _create_unsecured_jwt(body):
        # type: (Any) -> str
        """ Return an unsecured JWT expressing the body.
        """
        # Base64Url encoded '{"alg":"none"}'. See https://www.rfc-editor.org/rfc/rfc7515.html#appendix-A.5 for more information.
        return_value = "eyJhbGciOiJub25lIn0."

        # Try to serialize the body by asking the body object to serialize itself.
        # This normalizes the attributes in the body object to conform to the serialized attributes used
        # for transmission to the service.
        try:
            body = body.serialize()
        except AttributeError:
            pass
        json_body = JSONEncoder().encode(body)

        return_value += Base64Url.encode(json_body.encode('utf-8'))
        return_value += '.'
        return return_value

    @staticmethod
    def _create_secured_jwt(body, signer):
        # type: (Any, AttestationSigningKey) -> str
        """ Return a secured JWT expressing the body, secured with the specified signing key.
        :type body:Any - The body of the token to be serialized.
        :type signer:SigningKey - the certificate and key to sign the token.
        """
        header = {
            "alg": "RSA256" if isinstance(signer._signing_key, RSAPrivateKey) else "ECDH256",
            "jwk": {
                "x5c": [
                    base64.b64encode(signer._certificate.public_bytes(
                        Encoding.DER)).decode('utf-8')
                ]
            }
        }
        json_header = JSONEncoder().encode(header)
        return_value = Base64Url.encode(json_header.encode('utf-8'))

        try:
            body = body.serialize()
        except AttributeError:
            pass
        json_body = JSONEncoder().encode(body)
        return_value += '.'
        return_value += Base64Url.encode(json_body.encode('utf-8'))

        # Now we want to sign the return_value.
        if isinstance(signer._signing_key, RSAPrivateKey):
            signature = signer._signing_key.sign(
                return_value.encode('utf-8'),
                algorithm=SHA256(),
                padding=padding.PKCS1v15())
        else:
            signature = signer._signing_key.sign(
                return_value.encode('utf-8'),
                algorithm=SHA256())
        # And finally append the base64url encoded signature.
        return_value += '.'
        return_value += Base64Url.encode(signature)
        return return_value

class AttestationTokenValidationException(Exception):
    """ Thrown when an attestation token validation fails.

    :param str message: Message for caller describing the reason for the failure.
    """
    def __init__(self, message):
        self.message = message
        super(AttestationTokenValidationException, self).__init__(self.message)
        

class AttestationResponse(Generic[T]):
    """ Represents a response from the attestation service.

    :param AttestationToken token: Attestation Token returned from the service.
    :param T value: Value of the body of the attestation token.
    """
    def __init__(self, token, value):
        # type (AttestationToken, T) -> None
        self.token = token #type: AttestationToken
        self.value = value #type: T

class TpmAttestationRequest(object):
    """ Represents a request for TPM attestation.

    :param bytes data: The data to transmit to the Attestation Service for TPM attestation.
    """
    def __init__(self, data):
        #type (bytes) -> None
        self.data = data
   
class TpmAttestationResponse(object):
    """ Represents a request for TPM attestation.

    :param bytes data: The data to transmit to the Attestation Service for TPM attestation.
    """
    def __init__(self, data):
        #type (bytes) -> None
        self.data = data

