import json
from ._common import Base64Url
from typing import Any, List, Optional, TypeVar, Generic, Callable
from cryptography.hazmat.primitives.asymmetric.dsa import DSAParameterNumbers, DSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import Certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from json import JSONDecoder, JSONEncoder
from datetime import datetime

T = TypeVar('T')

class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    """
    def __init__(self, certificates, key_id, **kwargs): #type: (List[Certificate], str, Any) -> None
        self.certificates = certificates
        self.key_id = key_id

class TokenValidationOptions(object):
    """ Validation options for an Attestation Token object.
    :keyword bool validate_token: if True, validate the returned token, otherwise return the token unvalidated.
    :keyword Callable[['AttestationToken', 'AttestationSigner'], bool] validation_callback: Callback to allow clients to perform custom validation of the token.
    :keyword bool validate_signature: if True, validate the signature of the returned token.
    """
    def __init__(
        self,
        **kwargs):
        self.validate_token = kwargs.get('validate_token') #type: bool
        self.validation_callback = kwargs.get('validation_callback') # Callable[['AttestationToken', AttestationSigner], bool]):
        self.validate_signature = kwargs.get('validate_signature') # type:bool


class SigningKey(object):
    """ Represents a signing key used by the attestation service.

    Typically the signing key used by the service consists of two components: An RSA or ECDS private key and an X.509 Certificate wrapped around
    the public key portion of the private key.

    :var signing_key: The RSA or ECDS signing key to sign the token supplied to the customer.
    :vartype signing_key: (rsa.RSAPrivateKey | EllipticCurvePrivateKey)
    :var certificate: An X.509 Certificate whose public key matches the signing_key's public key.
    :vartype certificate: Certificate
    """
    def __init__(self, signing_key, certificate): #type: ((RSAPrivateKey | EllipticCurvePrivateKey), Certificate) -> None
        self.signing_key = signing_key
        self.certificate = certificate

        # We only support ECDS and RSA keys in the MAA service.
        if (not isinstance(signing_key, RSAPrivateKey) and not isinstance(signing_key, EllipticCurvePrivateKey)):
            raise Exception("Signing keys must be either ECDS or RSA keys.")

        # Ensure that the public key in the certificate matches the public key of the key.
        cert_public_key = certificate.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        key_public_key = signing_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
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
        """
        body = kwargs.get('body') # type: Any
        signer = kwargs.get('signer') #type: SigningKey
        if (body):
            if (signer):
                pass
            else:
                token = self._create_unsecured_jwt(body)
        else:
            token = kwargs.pop('token')

        self._token = token
        token_parts = token.split('.')
        if len(token_parts) != 3:
            raise ValueError("Malformed JSON Web Token")
        self.header_bytes = Base64Url.decode(token_parts[0]).decode('utf-8')
        self.body_bytes =Base64Url.decode(token_parts[1]).decode('utf-8')
        self.signature_bytes = Base64Url.decode(token_parts[2])
        decoder = JSONDecoder()
        self._body = decoder.decode(self.body_bytes)
        self._header = decoder.decode(self.header_bytes)

        # If the caller didn't specify a body when constructing the class, populate the well known attributes from the token.
        if (body is None):
            # Populate the standardized fields in the header.
            self.algorithm = self._header.get('alg')
            self.content_type = self._header.get('cty')
            self.critical = self._header.get('crit') #type: Optional[bool]
            self.key_id = self._header.get('kid')
            self.key_url = self._header.get('jku')
            self.type = self._header.get('typ')
            self.certificate_thumbprint = self._header.get('x5t')
            self.certificate_sha256_thumbprint = self._header.get('x5t#256')
            self.x509_url = self._header.get('x5u')

            # Populate the standardized fields from the body.
            exp = self._body.get('exp')
            if (exp is not None):
                self.expiration_time = datetime.fromtimestamp(exp)
            else:
                self.expiration_time = None

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

    def serialize(self):
        return self._token


    """ Validate the attestation token based on the options specified in the TokenValidationOptions
    """
    def validate_token(self, options, signing_certificates): #type (TokenValidationOptions, List[AttestationSigner]) -> bool
        if not options.validate_token:
            if (options.validation_callback is not None):
                options.validation_callback(self, None)
            return True

        if self.algorithm != 'none' and options.validate_signature:
            # validate the signature for the token.
            pass

        if (options.validation_callback is not None):
            return options.validation_callback(self, None)
        return True


    def get_body(self) -> T:
        return self._body

    @staticmethod
    def _create_unsecured_jwt(body: Any): #type(Any) -> str
        """ Return an unsecured JWT expressing the body.
        """
        # Base64Url encoded '{"alg":"none"}'. See https://www.rfc-editor.org/rfc/rfc7515.html#appendix-A.5 for more information.
        return_value = "eyJhbGciOiJub25lIn0."
        encoder = JSONEncoder()
        encoded_body = encoder.encode(body)
        return_value += Base64Url.encode(encoded_body.encode('utf-8'))
        return_value += '.'
        return return_value

class AttestationResult(Generic[T]):
    def __init__(self, token : AttestationToken, value: T):
        self.token = token
        self.value = value

class StoredAttestationPolicy(object):
    def __init__(self, stored_policy): #type(str) -> None
        self._stored_policy = Base64Url.encode(stored_policy.encode('utf-8'))


class StoredAttestationPolicyDecoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, StoredAttestationPolicy):
            return {
                "AttestationPolicy": o._stored_policy
            }
        return JSONEncoder.default(self, o)
