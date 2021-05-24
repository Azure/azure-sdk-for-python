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
from ._generated.models import (
    PolicyResult as GeneratedPolicyResult, 
    AttestationResult as GeneratedAttestationResult,
    StoredAttestationPolicy as GeneratedStoredAttestationPolicy,
    JSONWebKey,
    CertificateModification,
    AttestationType,
    PolicyModification
)
from typing import Any, Callable, Dict, List, Type, TypeVar, Generic, Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import Certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from json import JSONDecoder, JSONEncoder
from datetime import datetime

T = TypeVar('T')


class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    :param certificates: A list of Base64 encoded X.509
        Certificates representing an X.509 certificate chain. The first of these
        certificates will be used to sign an :class:`AttestationToken`.

    :type certificates: list[bytes] 

    :param str key_id: A string which identifies a signing key, See 
        `RFC 7517 Section 4.5 <https://tools.ietf.org/html/rfc7517#section-4.5>`_

    """
    def __init__(self, certificates, key_id, **kwargs):
        # type: (list[bytes], str, Any) -> None
        self.certificates = [base64.b64decode(cert) for cert in certificates]
        self.key_id = key_id

    @classmethod
    def _from_generated(cls, generated):
        #type:(JSONWebKey)->AttestationSigner
        if not generated:
            return cls
        return cls(generated.x5_c, generated.kid)

class PolicyCertificatesModificationResult(object):
    """The result of a policy certificate modification.

    :param str certificate_thumbprint: Hex encoded SHA1 Hash of the binary representation certificate
     which was added or removed.
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

class PolicyResult(object):
    """ PolicyResult represents the result of a :meth:`azure.security.attestation.AttestationAdministrationClient.set_policy` 
    or :meth:`azure.security.attestation.AttestationAdministrationClient.reset_policy`  API call.

    The `PolicyResult` class is returned as the body of an attestation token from
    the attestation service. It can be used to ensure that the attestation service
    received the policy object sent from the client without alteration.
    
    :param policy_resolution: The result of the policy set or
        reset call.
    :type policy_resolution: azure.security.attestation.PolicyModification
    :param policy_signer: If the call to `set_policy` or `reset_policy`
        had a :class:`AttestationSigningKey` parameter, this will be the certificate
        which was specified in this parameter.
    :type policy_signer: azure.security.attestation.AttestationSigner
    :param str policy_token_hash: The hash of the complete JSON Web Signature
        presented to the `set_policy` or `reset_policy` API.

    """
    def __init__(self, policy_resolution, policy_signer, policy_token_hash):
        #type:(PolicyModification, JSONWebKey, str) -> None
        self.policy_resolution = policy_resolution
        self.policy_signer = AttestationSigner._from_generated(policy_signer)
        self.policy_token_hash = policy_token_hash

    @classmethod
    def _from_generated(cls, generated):
        #type:(GeneratedPolicyResult)->PolicyResult
        if not generated:
            return cls(None, None, None)
        return cls(generated.policy_resolution, generated.policy_signer, generated.policy_token_hash)

class AttestationResult(object):
    """ An AttestationResult represents the claims returned from the attestation
    service as a result of a call to
    :meth:`azure.security.attestation.AttestationClient.attest_sgx`, or :meth:`AttestationClient.attest_open_enclave`.

    """
    def __init__(self, **kwargs):
        #type:(Dict[str,Any])->None
        """
        :keyword issuer: Entity which issued the attestation token.
        :paramtype issuer: str
        :keyword confirmation: Confirmation claim for the token.
        :paramtype confirmation: dict
        :keyword unique_identifier: Unique identifier for the token.
        :paramtype unique_identifier: str
        :keyword nonce: Returns the input `nonce` attribute passed to the `attest` API.
        :paramtype nonce: str
        :keyword version: Version of the token. Must be "1.0"
        :paramtype version: str
        :keyword runtime_claims: Runtime claims passed in from the caller of the attest API.
        :paramtype runtime_claims: dict
        :keyword inittime_claims: Inittime claims passed in from the caller of the attest API.
        :paramtype inittime_claims: dict
        :keyword enclave_held_data: Runtime data passed in from the caller of the attest API.
        :paramtype enclave_held_data: bytes
        :keyword policy_claims: Attestation claims issued by policies.
        :paramtype policy_claims: dict
        :keyword verifier_type: Verifier which generated this token.
        :paramtype verifier_type: str
        :keyword policy_signer: If the policy which processed the request is signed, 
            this will be the certificate which signed the policy.
        :paramtype policy_signer: azure.security.attestation.AttestationSigner
        :keyword policy_hash: The hash of the policy which processed the attestation 
            evidence.
        :paramtype policy_hash: str
        :keyword is_debuggable: True if the SGX enclave being attested is debuggable.
        :paramtype is_debuggable: bool
        :keyword product_id: Product ID for the SGX enclave being attested.
        :paramtype product_id: int
        :keyword mr_enclave: MRENCLAVE value for the SGX enclave being attested.
        :paramtype mr_enclave: str
        :keyword mr_signer: MRSIGNER value for the SGX enclave being attested.
        :paramtype mr_signer: str
        :keyword svn: Security version number for the SGX enclave being attested.
        :paramtype svn: int
        :keyword sgx_collateral: Collateral which identifies the collateral used to 
            create the token.
        :paramtype sgx_collateral: dict
    
        """
        self._issuer = kwargs.pop("issuer", None) #type:Union[str, None]
        self._confirmation = kwargs.pop("confirmation", None) #type:Union[dict, None]
        self._unique_identifier = kwargs.pop("unique_identifier", None) #type:Union[str, None]
        self._nonce = kwargs.pop("nonce", None) #type:Union[str, None]
        self._version = kwargs.pop("version", None) #type:Union[str, None]
        self._runtime_claims = kwargs.pop("runtime_claims", None) #type:Union[dict, None]
        self._inittime_claims = kwargs.pop("inittime_claims", None) #type:Union[dict, None]
        self._policy_claims = kwargs.pop("policy_claims", None) #type:Union[dict, None]
        self._verifier_type = kwargs.pop("verifier_type", None) #type:Union[str. None]
        self._policy_signer = kwargs.pop("policy_signer", None) #type:Union[AttestationSigner, None]
        self._policy_hash = kwargs.pop("policy_hash", None) #type:Union[str, None]
        self._is_debuggable = kwargs.pop("is_debuggable", None) #type:Union[bool, None]
        self._product_id = kwargs.pop("product_id", None) #type:Union[int, None]
        self._mr_enclave = kwargs.pop("mr_enclave", None) #type:Union[str, None]
        self._mr_signer = kwargs.pop("mr_signer", None) #type:Union[str, None]
        self._svn = kwargs.pop("svn", None) #type:Union[int, None]
        self._enclave_held_data = kwargs.pop("enclave_held_data", None) #type:Union[bytes, None]
        self._sgx_collateral = kwargs.pop("sgx_collateral", None) #type:Union[dict, None]

    @classmethod
    def _from_generated(cls, generated):
        #type:(GeneratedAttestationResult) -> AttestationResult
        return AttestationResult(
            issuer=generated.iss,
            confirmation=generated.cnf,
            unique_identifier=generated.jti,
            nonce=generated.nonce,
            version=generated.version,
            runtime_claims=generated.runtime_claims,
            inittime_claims=generated.inittime_claims,
            policy_claims=generated.policy_claims,
            verifier_type=generated.verifier_type,
            policy_signer=AttestationSigner._from_generated(generated.policy_signer) if generated.policy_signer else None,
            policy_hash=generated.policy_hash,
            is_debuggable=generated.is_debuggable,
            product_id=generated.product_id,
            mr_enclave=generated.mr_enclave,
            mr_signer=generated.mr_signer,
            svn=generated.svn,
            enclave_held_data=generated.enclave_held_data,
            sgx_collateral=generated.sgx_collateral)

    @property
    def issuer(self):
        #type:() -> Union[str, None]
        """ Returns the issuer of the attestation token.

        The issuer for the token MUST be the same as the `instance_uri` associated
        with the :class:`azure.security.attestation.AttestationClient` object.
        If it is not, then the token should be rejected.
        
        See `RFC 7519 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.1>`_ for details.

        :rtype: str or None

        """
        return self._issuer

    @property
    def confirmation(self):
        #type:() -> Union[str, None]
        """ Returns the confirmation claim for the attestation token.

        If present, the confirmation property can be used to identify a proof of
        possession of a key.
        
        See `RFC 7800 Section 3.1 <https://www.rfc-editor.org/rfc/rfc7800.html#section-3.1>`_ for details.

        :rtype: str or None

        """
        return self._confirmation

    @property
    def unique_id(self):
        #type:() -> Union[str, None]
        """ Returns a unique ID claim for the attestation token.

        If present, the unique_id property can be used to distinguish between
        different attestation tokens.
        
        See `RFC 7519 Section 4.1.7 <https://rfc-editor.org/rfc/rfc7519.html#section-4.1.7>`_ for details.

        :rtype: str or None

        """
        return self._confirmation

    @property
    def nonce(self):
        #type:() -> Union[str, None]
        """ Returns the value of the "nonce" input to the attestation request.

        :rtype: str or None
        """
        return self._nonce

    @property
    def version(self):
        #type:() -> Union[str, None]
        """ Returns the version of the information returned in the token.

        :rtype: str or None
        """
        return self._version

    @property
    def runtime_claims(self):
        #type:() -> Dict[str, Any]
        """ Returns the runtime claims in the token.

        This value will match the input `runtime_data` property to the 
        :meth:`azure.security.attestation.AttestationClient.attest_sgx` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        :rtype: dict[str, Any] or None

        .. note:: The `runtime_claims` property will only be populated if the
            `runtime_data` parameter to the `Attest` API is marked as being JSON.

        """
        return self._runtime_claims

    @property
    def inittime_claims(self):
        #type:() -> Dict[str, Any]
        """ Returns the inittime claims in the token.

        This value will match the input `inittime_data` property to the 
        :meth:`azure.security.attestation.AttestationClient.attest_sgx` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        :rtype: dict[str, Any] or None

        .. note:: The `inittime_claims` property will only be populated if the
            `inittime_data` parameter to the `Attest` API is marked as being JSON.

        """
        return self._inittime_claims

    @property
    def policy_claims(self):
        #type:() -> Dict[str, Any]
        """ Returns the claims for the token generated by attestation policy.

        :rtype: dict[str, Any] or None

        """
        return self._policy_claims

    @property
    def verifier_type(self):
        #type:() -> Union[str, None]
        """ Returns the verifier which generated this attestation token.

        :rtype: str or None
        """
        return self._verifier_type

    @property
    def policy_signer(self):
        #type:() -> Union[AttestationSigner, None]
        """ Returns the signing certificate which was used to sign the policy
        which was applied when the token was generated.

        :rtype: azure.security.attestation.AttestationSigner or None
        """
        if self._policy_signer:
            return AttestationSigner._from_generated(self._policy_signer)
        return None

    @property
    def policy_hash(self):
        #type:() -> Union[str, None]
        """ Returns the base64url encoded SHA256 hash of the Base64Url encoded
        attestation policy which was applied when generating this token.

        :rtype: str or None
        """
        return self._policy_hash

    @property
    def is_debuggable(self):
        #type:() -> Union[bool, None]
        """ Returns "True" if the source evidence being attested indicates
        that the TEE has debugging enabled.

        :rtype: bool or None
        """
        return self._is_debuggable

    @property
    def product_id(self):
        #type:() -> Union[float, None]
        """ Returns the product id associated with the SGX enclave being attested.

        :rtype: float or None

        """
        return self._product_id

    @property
    def mr_enclave(self):
        #type:() -> Union[str, None]
        """ Returns HEX encoded `mr-enclave` value of the SGX enclave being attested.

        :rtype: str or None
        """
        return self._mr_enclave

    @property
    def mr_signer(self):
        #type:() -> Union[str, None]
        """ Returns HEX encoded `mr-signer` value of the SGX enclave being attested.

        :rtype: str or None
        """
        return self._mr_signer

    @property
    def svn(self):
        #type:() -> Union[int, None]
        """ Returns the `svn` value of the SGX enclave being attested.

        :rtype: int or None
        """
        return self._svn

    @property
    def enclave_held_data(self):
        #type:() -> Union[bytes, None]
        """ Returns the value of the runtime_data field specified as an input
        to the :meth:`azure.security.attestation.AttestationClient.attest_sgx` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        .. note:: The enclave_held_data prperty will only be populated if the 
            `runtime_data` parameter to the `Attest` API is marked as not being 
            JSON.

        :rtype: bytes or None
        """
        return self._enclave_held_data

    @property
    def sgx_collateral(self):
        #type:() -> Union[Dict[str, Any], None]
        """ Returns a set of information describing the complete set of inputs
        to the `oe_verify_evidence`

        :rtype: dict[str, Any] or None

        """
        return self._sgx_collateral

        # Deprecated fields.

class StoredAttestationPolicy(object):
    """ Represents an attestation policy in storage.

    When serialized, the `StoredAttestationPolicy` object will Base64Url encode the
    UTF-8 representation of the `policy` value.

    """
    def __init__(self, policy):
        #type:(str) -> None
        """
        :param str policy: Policy to be saved.
        """
        self._policy = policy.encode("ascii")

    def serialize(self, **kwargs):
        #type:(Any) -> str
        return GeneratedStoredAttestationPolicy(attestation_policy=self._policy).serialize(**kwargs)

    @classmethod
    def _from_generated(cls, generated):
        #type:(GeneratedStoredAttestationPolicy) -> StoredAttestationPolicy
        if generated is None:
            return StoredAttestationPolicy("")
        return StoredAttestationPolicy(generated.attestation_policy)


class AttestationData(object):
    """ AttestationData represents an object passed as an input to the Attestation Service.

    AttestationData comes in two forms: Binary and JSON. To distinguish between the two, when an :class:`AttestationData`
    object is created, the caller provides an indication that the input binary data will be treated as either JSON or Binary.

    If the `is_json` parameter is not provided, then the AttestationData 
    constructor will probe the `data` parameter to determine whether the data
    should be treated as JSON.

    The AttestationData is reflected in the generated :class:`AttestationResult` in two possible ways.
    If the `AttestationData` is Binary, then the `AttestationData` is reflected in the `AttestationResult.enclave_held_data` claim.
    If the `AttestationData` is JSON, then the `AttestationData` is expressed as JSON in the `AttestationResult.runtime_claims` or AttestationResult.inittime_claims claim.

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
    :keyword validation_callback: Callback to allow clients to perform custom validation of the token.
    :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], bool]
    :keyword bool validate_signature: if True, validate the signature of the token being validated.
    :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
    :keyword str issuer: Expected issuer, used if validate_issuer is true.
    :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
    :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
    """

    def __init__(self, **kwargs):
        #type: (**Any) -> None

        self.validate_token = kwargs.get('validate_token', True)  # type: bool
        self.validation_callback = kwargs.get('validation_callback') # type:Callable[[AttestationToken, AttestationSigner], bool]
        self.validate_signature = kwargs.get('validate_signature', True)  # type:bool
        self.validate_expiration = kwargs.get('validate_expiration', True)  # type:bool
        self.validate_not_before = kwargs.get('validate_not_before', True)  # type:bool
        self.validate_issuer = kwargs.get('validate_issuer', False)  # type:bool
        self.issuer = kwargs.get('issuer')  # type:str
        # We assume a default validation slack of a half second to allow for a small
        # amount of timer drift.
        self.validation_slack = kwargs.get('validation_slack', 0.5)  # type:float


class AttestationSigningKey(object):
    """ Represents a signing key used by the attestation service.

    Typically the signing key used by the service consists of two components: An RSA or ECDS private key and an X.509 Certificate wrapped around
    the public key portion of the private key.

    :param bytes signing_key_der: The RSA or ECDS signing key to sign the token supplied to the customer DER encoded.
    :param bytes certificate_der: A DER encoded X.509 Certificate whose public key matches the signing_key's public key.

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
    :keyword signer: If specified, the key used to sign the token.
        If the `signer` property is not specified, the token created is unsecured.
    :paramtype signer: azure.security.attestation.AttestationSigningKey
    :keyword str token: If no body or signer is provided, the string representation of the token.
    :keyword Type body_type: The underlying type of the body of the 'token' parameter, used to deserialize the underlying body when parsing the token.
    """

    def __init__(self, **kwargs):
        token = kwargs.get('token')
        if token is None:
            body = kwargs.get('body')  # type: Any
            signer = kwargs.get('signer')  # type: AttestationSigningKey
            if signer:
                token = self._create_secured_jwt(body, signer)
            else:
                token = self._create_unsecured_jwt(body)


        self._token = token
        self._body_type = kwargs.get('body_type') #type: Type
        token_parts = token.split('.')
        if len(token_parts) != 3:
            raise ValueError("Malformed JSON Web Token")
        self.header_bytes = Base64Url.decode(token_parts[0])
        self.body_bytes = Base64Url.decode(token_parts[1])
        self.signature_bytes = Base64Url.decode(token_parts[2])
        if len(self.body_bytes) != 0:
            self._body = JSONDecoder().decode(self.body_bytes.decode('ascii'))
        else:
            self._body = None
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
        #type:() -> str
        """ Returns a string serializing the JSON Web Token
        
        :rtype: str
        """
        return self._token

    def validate_token(self, options=None, signers=None):
        # type: (TokenValidationOptions, list[AttestationSigner]) -> bool
        """ Validate the attestation token based on the options specified in the
         :class:`TokenValidationOptions`.
        
        :param azure.security.attestation.TokenValidationOptions options: Options to be used when validating 
            the token.
        :param list[azure.security.attestation.AttestationSigner] signers: Potential signers for the token.
            If the signers parameter is specified, validate_token will only 
            consider the signers as potential signatories for the token, otherwise
            it will consider attributes in the header of the token.
        :return bool: Returns True if the token successfully validated, False 
            otherwise. 

        :raises: azure.security.attestation.AttestationTokenValidationException
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

        :rtype: T
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
                            signers = jwk.x5_c
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
                    signers = self._json_web_key().x5_c
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
                raise AttestationTokenValidationException("Could not verify signature of attestation token.")
        return None

    def _validate_static_properties(self, options):
        # type:(TokenValidationOptions) -> bool
        """ Validate the static properties in the attestation token.
        """
        if self._body:
            time_now = datetime.now()
            if options.validate_expiration and self.expiration_time is not None:
                if (time_now > self.expiration_time):
                    delta = time_now - self.expiration_time
                    if delta.total_seconds() > options.validation_slack:
                        raise AttestationTokenValidationException(u'Token is expired. Now: {}, Not Before: {}'.format(time_now.isoformat(), self.not_before_time.isoformat()))
            if options.validate_not_before and hasattr(self, 'not_before_time') and self.not_before_time is not None:
                if (time_now < self.not_before_time):
                    delta = self.not_before_time - time_now
                    if delta.total_seconds() > options.validation_slack:
                        raise AttestationTokenValidationException(u'Token is not yet valid. Now: {}, Not Before: {}'.format(time_now.isoformat(), self.not_before_time.isoformat()))
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
        json_body = ''
        if body is not None:
            json_body = JSONEncoder().encode(body)

        return_value += Base64Url.encode(json_body.encode('utf-8'))
        return_value += '.'
        return return_value

    @staticmethod
    def _create_secured_jwt(body, signer):
        # type: (Any, AttestationSigningKey) -> str
        """ Return a secured JWT expressing the body, secured with the specified signing key.
        :param Any body: The body of the token to be serialized.
        :param signer: the certificate and key to sign the token.
        :type signer: AttestationSigningKey
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
        json_body = ''
        if body is not None:
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

    :param token: Attestation Token returned from the service.
    :type token: azure.security.attestation.AttestationToken
    :param value: Value of the body of the attestation token.
    :type value: T
    """
    def __init__(self, token, value):
        # type (AttestationToken, T) -> None
        self.token = token #type: AttestationToken
        self.value = value #type: T

class TpmAttestationRequest(object):
    """ Represents a request for TPM attestation.

    :param bytes data: The data sent to the Attestation Service in
        the parameter to :meth:`azure.security.attestation.AttestationClient.attest_tpm`.
    """
    def __init__(self, data):
        #type (bytes) -> None
        self.data = data
   
class TpmAttestationResponse(object):
    """ Represents a request for TPM attestation.

    :param bytes data: The data received from the Attestation Service in
        response to a call to :meth:`azure.security.attestation.AttestationClient.attest_tpm`.
    """
    def __init__(self, data):
        #type (bytes) -> None
        self.data = data

