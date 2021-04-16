from base64 import b64encode, decode, encode
import base64
import json
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding, PKCS1v15
from cryptography.hazmat.primitives.hashes import HashAlgorithm, SHA256
from msrest.exceptions import DeserializationError, SerializationError
from ._common import Base64Url
from ._generated.models import PolicyResult, PolicyCertificatesModificationResult, AttestationResult, StoredAttestationPolicy
from typing import Any, Callable, List, Optional, Type, TypeVar, Generic, Union
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import Certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from json import JSONDecoder, JSONEncoder
from datetime import datetime

T = TypeVar('T', PolicyResult, AttestationResult, StoredAttestationPolicy, PolicyCertificatesModificationResult)


class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    """
    def __init__(self, certificates, key_id, **kwargs):
        # type: (List[Certificate], str, Any) -> None
        self.certificates = certificates
        self.key_id = key_id


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

    def __init__(
            self,
            **kwargs):
        self.validate_token = kwargs.get('validate_token')  # type: bool
        self.validation_callback = kwargs.get(
            'validation_callback') # type:Callable[['AttestationToken', AttestationSigner], bool]
        self.validate_signature = kwargs.get('validate_signature')  # type:bool
        self.validate_expiration = kwargs.get(
            'validate_expiration')  # type:bool
        self.validate_not_before = kwargs.get(
            'validate_not_before')  # type:bool
        self.validate_issuer = kwargs.get('validate_issuer')  # type:bool
        self.issuer = kwargs.get('issuer')  # type:str
        self.validation_slack = kwargs.get('validation_slack')  # type:int


class SigningKey(object):
    """ Represents a signing key used by the attestation service.

    Typically the signing key used by the service consists of two components: An RSA or ECDS private key and an X.509 Certificate wrapped around
    the public key portion of the private key.

    :var signing_key: The RSA or ECDS signing key to sign the token supplied to the customer.
    :vartype signing_key: (rsa.RSAPrivateKey | EllipticCurvePrivateKey)
    :var certificate: An X.509 Certificate whose public key matches the signing_key's public key.
    :vartype certificate: Certificate
    """

    def __init__(self, signing_key, certificate):
    # type: (Union[RSAPrivateKey | EllipticCurvePrivateKey], Certificate) -> None
        self.signing_key = signing_key
        self.certificate = certificate

        # We only support ECDS and RSA keys in the MAA service.
        if (not isinstance(signing_key, RSAPrivateKey) and not isinstance(signing_key, EllipticCurvePrivateKey)):
            raise Exception("Signing keys must be either ECDS or RSA keys.")

        # Ensure that the public key in the certificate matches the public key of the key.
        cert_public_key = certificate.public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        key_public_key = signing_key.public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        if cert_public_key != key_public_key:
            raise Exception("Signing key must match certificate public key")


class AttestationToken(Generic[T]):
    """ Represents a token returned from the attestation service.

    :var algorithm: Json Web Token Header "algorithm". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.1 for details. If the value of algorithm attribute is "none" it indicates that the token is unsecured.
    :vartype algorithm: str

    :var content_type: Json Web Token Header "content type". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.10 for details.
    :vartype content_type: str
    :var type:Json Web Token Header "type". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.9 for details. If present, the value for this field is normally "JWT".
    :vartype type: str

    :var critical: Optional critical indicator - indicates that the token must be valid.
    :vartype critical: Optional[bool]
    :var expiration_time: Time at which the token expires.
    :vartype expiration_time: datetime
    :var issuance_time: Time at which the token was issued.
    :vartype issuance_time: datetime
    :var not_before_time: Before this time, the token is invalid.
    :vartype issuance_time: datetime
    :var issuer: The entity which issued this token.
    :vartype issuer: str
    :var key_id: Json Web Token Header "kid". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.4 for details.
    :vartype key_id: str
    :var key_url: Json Web Token Header "jku". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.2 for details.
    :vartype key_url: str
    :var x509_url: Json Web Token Header "x5u". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.5 for details.
    :vartype key_url: str
    :var certificate_thumbprint: The Base64 encoded SHA1 hash of the certificate which signed this token.
    :vartype certificate_thumbprint: str
    :var certificate_sha256_thumbprint: The Base64 encoded SHA256 hash of the certificate which signed this token.
    :vartype certificate_sha256_thumbprint: str

    :var header_bytes: Decoded header of the attestation token. See https://tools.ietf.org/html/rfc7515 for more details.
    :vartype header_bytes: bytes

    :var body_bytes: Decoded body of the attestation token. See https://tools.ietf.org/html/rfc7515 for more details.
    :vartype body_bytes: bytes

    :var signature_bytes: Decoded signature of the attestation token. See https://tools.ietf.org/html/rfc7515 for more details.
    :vartype signature_bytes: bytes

        public virtual AttestationSigner SigningCertificate { get; }
        public virtual string TokenBody { get; }
        public virtual string TokenHeader { get; }
        public virtual X509Certificate2[] X509CertificateChain { get; }

    """

    def __init__(self, **kwargs):
        """ Create a new instance of an AttestationToken class.
        :keyword Any body: The body of hte newly created token, if provided.
        :keyword SigningKey signer: If specified, the key used to sign the token.
        :keyword str token: If no body or signer is provided, the string representation of the token.
        :keyword Type body_type: The underlying type of the body of the 'token' parameter, used to deserialize the underlying body when parsing the token.
        """
        body = kwargs.get('body')  # type: Any
        signer = kwargs.get('signer')  # type: SigningKey
        if (body):
            if (signer):
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

        # If the caller didn't specify a body when constructing the class, populate the well known attributes from the token.
        if (body is None):
            # Populate the standardized fields in the header.
            self.content_type = self._header.get('cty')
            self.critical = self._header.get('crit')  # type: Optional[bool]
            self.key_url = self._header.get('jku')
            self.type = self._header.get('typ')
            self.certificate_thumbprint = self._header.get('x5t')
            self.certificate_sha256_thumbprint = self._header.get('x5t#256')
            self.x509_url = self._header.get('x5u')

            # Populate the standardized fields from the body.
            iat = self._body.get('iat')
            if (iat is not None):
                self.issuance_time = datetime.fromtimestamp(iat)
            else:
                self.issuance_time = None

            nbf = self._body.get('nbf')
            if (nbf is not None):
                self.not_before_time = datetime.fromtimestamp(nbf)
            else:
                self.not_before_time = None

            self.issuer = self._body.get('iss')

    def __str__(self):
        return self._token

    @property
    def algorithm(self):
        #type:() -> str
        """ Json Web Token Header "algorithm". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.1 for details.
        If the value of Algorithm is "none" it indicates that the token is unsecured.
        """
        return self._header.get('alg')

    @property
    def key_id(self):
        #type:() -> str
        """ Json Web Token Header "Key ID". See https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.4 for details.
        """
        return self._header.get('kid')

    @property
    def expiration_time(self):
        #type:() -> datetime
        """ Expiration time for the token.
        """
        exp = self._body.get('exp')
        if (exp is not None):
            return datetime.fromtimestamp(exp)
        return None
 

    def serialize(self):
        return self._token

    """ Validate the attestation token based on the options specified in the TokenValidationOptions
    """

    def validate_token(self, options=None, signing_certificates=None):
        # type: (TokenValidationOptions, List[AttestationSigner]) -> bool
        if (options is None):
            options = TokenValidationOptions(
                validate_token=True, validate_signature=True, validate_expiration=True)
        if not options.validate_token:
            self._validate_static_properties(options)
            if (options.validation_callback is not None):
                options.validation_callback(self, None)
            return True

        if self.algorithm != 'none' and options.validate_signature:
            # validate the signature for the token.
            candidate_certificates = self._get_candidate_signing_certificates(
                signing_certificates)
            if (not self._validate_signature(candidate_certificates)):
                raise Exception(
                    "Could not find the certificate used to sign the token.")
        self._validate_static_properties(options)

        if (options.validation_callback is not None):
            return options.validation_callback(self, None)
        return True

    def get_body(self):
        # type: () -> T

        try:
            return self._body_type.deserialize(self._body)
        except AttributeError:
            return self._body

        # # Start with StoredAttestationPolicy, returning it if we can decode it.
        # stored_policy = StoredAttestationPolicy.deserialize(self._body)
        # # Do a quick sanity check. A StoredAttestationPolicy must have an attestation_policy attribute.
        # if stored_policy.attestation_policy is not None:
        #     return stored_policy

        # # Maybe this is a PolicyResult, try that.
        # policy_result = PolicyResult.deserialize(self._body)
        # # Do a quick sanity check. A PolicyResult must have either a policy or policy_token_hash attribute.
        # if policy_result is not None and (policy_result.policy is not None or policy_result.policy_token_hash is not None):
        #     return policy_result

        # # Next try the result of an Attest call.
        # attest_result  = AttestationResult.deserialize(self._body)
        # # Do a quick sanity check. An AttestationResult will always have an sgx_collateral attribute.
        # if attest_result is not None and (attest_result.sgx_collateral is not None):
        #     return attest_result

        # # Finally, we give up and just return a dictionary.
        # return self._body

    def _get_candidate_signing_certificates(self, signing_certificates):
        # type: (List[AttestationSigner]) -> List[AttestationSigner]

        candidates = list()
        desired_key_id = self.key_id
        if desired_key_id is not None:
            for signer in signing_certificates:
                if (signer.key_id == desired_key_id):
                    candidates.append(signer)
                    break
            # If we didn't find a matching key ID in the supplied certificates,
            # try the JWS header to see if there might be a corresponding key.
            if (len(candidates) == 0):
                if self._header['jwk']:
                    if self._header['jwk']['kid'] == desired_key_id:
                        if (self._header['jwk']['x5c']):
                            signers = self._get_signers_from_x5c(
                                self._header['jwk']['x5c'])
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
                if self._header.get('jwk'):
                    if (self._header['jwk'].get('x5c')):
                        signers = self._get_signers_from_x5c(
                            self._header['jwk']['x5c'])
                        candidates.append(AttestationSigner(signers, None))
                if self._header.get('x5c'):
                    signers = self._get_signers_from_x5c(self._header['x5c'])
                    candidates.append(AttestationSigner(signers, None))

        return candidates

    def _get_signers_from_x5c(self, x5clist):
        # type:(List[str]) -> List[AttestationSigner]
        signers = list()
        for cert in x5clist:
            signer = load_der_x509_certificate(base64.b64decode(cert))
            signers.append(signer)
        return signers

    def _validate_signature(self, candidate_certificates):
        # type:(List[AttestationSigner]) -> bool
        signed_data = Base64Url.encode(
            self.header_bytes)+'.'+Base64Url.encode(self.body_bytes)
        for signer in candidate_certificates:
            signer_key = signer.certificates[0].public_key()
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
                return True
            except:
                pass
        return False

    def _validate_static_properties(self, options):
        # type:(TokenValidationOptions) -> bool
        """ Validate the static properties in the attestation token.
        """
        if options.validate_expiration and self.expiration_time is not None:
            if (datetime.now() > self.expiration_time):
                delta = datetime.now() - self.expiration_time
                if delta.total_seconds > options.validation_slack:
                    raise Exception(u'Token is expired.')
        if options.validate_not_before and hasattr(self, 'not_before_time') and self.not_before_time is not None:
            if (datetime.now() < self.not_before_time):
                delta = self.expiration_time - datetime.now()
                if delta.total_seconds > options.validation_slack:
                    raise Exception(u'Token is not yet valid.')
        if options.validate_issuer and hasattr(self, 'issuer') and self.issuer is not None:
            if (options.issuer != self.issuer):
                raise Exception(u'Issuer in token: ', self.issuer,
                                ' is not the expected issuer: ', options.issuer, '.')
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
        # type: (Any, SigningKey) -> str
        """ Return a secured JWT expressing the body, secured with the specified signing key.
        :type body:Any - The body of the token to be serialized.
        :type signer:SigningKey - the certificate and key to sign the token.
        """
        header = {
            "alg": "RSA256" if isinstance(signer.signing_key, RSAPrivateKey) else "ECDH256",
            "x5c": [
                base64.b64encode(signer.certificate.public_bytes(
                    Encoding.DER)).decode('utf-8')
            ]
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
        if isinstance(signer.signing_key, RSAPrivateKey):
            signature = signer.signing_key.sign(
                return_value.encode('utf-8'),
                algorithm=SHA256(),
                padding=padding.PKCS1v15())
        else:
            signature = signer.signing_key.sign(
                return_value.encode('utf-8'),
                algorithm=SHA256())
        # And finally append the base64url encoded signature.
        return_value += '.'
        return_value += Base64Url.encode(signature)
        return return_value


class AttestationResponse(Generic[T]):
    def __init__(self, token, value):
        # type (AttestationToken, T) -> None
        self.token = token #type: AttestationToken
        self.value = value #type: T
