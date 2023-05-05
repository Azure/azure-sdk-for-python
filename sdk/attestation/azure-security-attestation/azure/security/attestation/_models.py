# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import base64
from datetime import datetime
import json
from typing import TYPE_CHECKING, TypeVar

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate, load_pem_x509_certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from six import string_types, raise_from

from ._common import (
    base64url_decode,
    base64url_encode,
    pem_from_base64,
    validate_signing_keys,
)
from ._generated.models import (
    PolicyResult as GeneratedPolicyResult,
    AttestationResult as GeneratedAttestationResult,
    StoredAttestationPolicy as GeneratedStoredAttestationPolicy,
    PolicyCertificatesModificationResult as GeneratedPolicyCertificatesModificationResult,
    JSONWebKey,
    CertificateModification,
    PolicyModification,
)


if TYPE_CHECKING:
    from typing import Any, Dict, List, Type, Union

T = TypeVar("T")


class AttestationSigner(object):
    """Represents a signing certificate returned by the Attestation Service.

    :param certificates: A list of Base64 encoded X.509
        Certificates representing an X.509 certificate chain. The first of these
        certificates will be used to sign an :class:`AttestationToken`.

    :type certificates: list[str]

    :param str key_id: A string which identifies a signing key, See
        `RFC 7517 Section 4.5 <https://tools.ietf.org/html/rfc7517#section-4.5>`_

    """

    def __init__(self, certificates, key_id):
        # type: (list[str], str) -> None
        self.certificates = [
            pem_from_base64(cert, "CERTIFICATE") for cert in certificates
        ]
        self.key_id = key_id

    @classmethod
    def _from_generated(cls, generated):
        # type: (JSONWebKey) -> AttestationSigner
        if not generated:
            return None
        return cls(generated.x5_c, generated.kid)


class AttestationPolicyCertificateResult(object):
    """The result of a policy certificate modification.

    :param str certificate_thumbprint: Hex encoded SHA1 Hash of the binary representation certificate
     which was added or removed.
    :param str certificate_resolution: The result of the operation. Possible values include:
     "IsPresent", "IsAbsent".
     ~azure.security.attestation._generated.models.CertificateModification
    """

    def __init__(self, certificate_thumbprint, certificate_resolution):
        # type: (str, Union[str, CertificateModification]) -> None
        self.certificate_thumbprint = certificate_thumbprint
        self.certificate_resolution = certificate_resolution

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedPolicyCertificatesModificationResult) -> AttestationPolicyCertificateResult
        if not generated:
            return None
        return cls(generated.certificate_thumbprint, generated.certificate_resolution)


class AttestationPolicyResult(object):
    """The result of a :meth:`azure.security.attestation.AttestationAdministrationClient.set_policy`
    or :meth:`azure.security.attestation.AttestationAdministrationClient.reset_policy`
    API call.

    The `AttestationPolicyResult` class is returned as the body of an attestation token from
    the attestation service. It can be used to ensure that the attestation service
    received the policy object sent from the client without alteration.

    :param policy_resolution: The result of the policy set or reset call.
    :type policy_resolution: ~azure.security.attestation.PolicyModification
    :param policy_signer: If the call to `set_policy` or `reset_policy`
        had a `signing_certificate` parameter, this will be the certificate
        which was specified in this parameter.
    :type policy_signer: ~azure.security.attestation.AttestationSigner
    :param str policy_token_hash: The hash of the complete JSON Web Signature
        presented to the `set_policy` or `reset_policy` API.

    """

    def __init__(self, policy_resolution, policy_signer, policy_token_hash):
        # type: (PolicyModification, AttestationSigner, str) -> None
        self.policy_resolution = policy_resolution
        self.policy_signer = policy_signer
        self.policy_token_hash = policy_token_hash

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedPolicyResult, str) -> AttestationPolicyResult
        # If we have a generated policy result or policy text, return that.
        if not generated:
            return None
        return AttestationPolicyResult(
            generated.policy_resolution,
            AttestationSigner._from_generated(  # pylint: disable=protected-access
                generated.policy_signer
            ),
            generated.policy_token_hash,
        )


class AttestationResult(object):  # pylint: disable=too-many-instance-attributes
    """Represents the claims returned from the attestation service as a result
    of a call to :meth:`azure.security.attestation.AttestationClient.attest_sgx_enclave`,
    or :meth:`azure.security.attestation.AttestationClient.attest_open_enclave`.

    :keyword str issuer: Entity which issued the attestation token.
    :keyword unique_identifier: Unique identifier for the token.
    :paramtype unique_identifier: str or None
    :keyword nonce: Returns the input `nonce` attribute passed to the `Attest` API.
    :paramtype nonce: str or None
    :keyword str version: Version of the token. Must be "1.0"
    :keyword runtime_claims: Runtime claims passed in from the caller of the attest API.
    :paramtype runtime_claims: dict or None
    :keyword inittime_claims: Inittime claims passed in from the caller of the attest API.
    :paramtype inittime_claims: dict or None
    :keyword enclave_held_data: Runtime data passed in from the caller of the attest API.
    :paramtype enclave_held_data: bytes or None
    :keyword policy_claims: Attestation claims issued by policies.
    :paramtype policy_claims: dict or None
    :keyword str verifier_type: Verifier which generated this token.
    :keyword policy_signer: If the policy which processed the request is signed,
        this will be the certificate which signed the policy.
    :paramtype policy_signer: ~azure.security.attestation.AttestationSigner or None
    :keyword str policy_hash: The hash of the policy which processed the attestation
        evidence.
    :keyword bool is_debuggable: True if a debugger can be attached to the SGX enclave
        being attested.
    :keyword int product_id: Product ID for the SGX enclave being attested.
    :keyword str mr_enclave: MRENCLAVE value for the SGX enclave being attested.
    :keyword str mr_signer: MRSIGNER value for the SGX enclave being attested.
    :keyword int svn: Security version number for the SGX enclave being attested.
    :keyword dict sgx_collateral: Collateral which identifies the collateral used to
        create the token.

    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._issuer = kwargs.pop("issuer")  # type:str
        self._unique_identifier = kwargs.pop(
            "unique_identifier", None
        )  # type: Union[str, None]
        self._nonce = kwargs.pop("nonce", None)  # type: Union[str, None]
        self._version = kwargs.pop("version")  # type: str
        self._runtime_claims = kwargs.pop(
            "runtime_claims", None
        )  # type: Union[Dict, None]
        self._inittime_claims = kwargs.pop(
            "inittime_claims", None
        )  # type: Union[Dict, None]
        self._policy_claims = kwargs.pop(
            "policy_claims", None
        )  # type: Union[Dict, None]
        self._verifier_type = kwargs.pop("verifier_type")  # type: str
        self._policy_signer = kwargs.pop(
            "policy_signer", None
        )  # type: Union[AttestationSigner, None]
        self._policy_hash = kwargs.pop("policy_hash")  # type: str
        self._is_debuggable = kwargs.pop("is_debuggable")  # type: bool
        self._product_id = kwargs.pop("product_id")  # type: int
        self._mr_enclave = kwargs.pop("mr_enclave")  # type: str
        self._mr_signer = kwargs.pop("mr_signer")  # type: str
        self._svn = kwargs.pop("svn")  # type: int
        self._enclave_held_data = kwargs.pop(
            "enclave_held_data", None
        )  # type: Union[bytes, None]
        self._sgx_collateral = kwargs.pop("sgx_collateral")  # type: Dict

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedAttestationResult) -> AttestationResult
        if not generated:
            return None
        return AttestationResult(
            issuer=generated.iss,
            unique_identifier=generated.jti,
            nonce=generated.nonce,
            version=generated.version,
            runtime_claims=generated.runtime_claims,
            inittime_claims=generated.inittime_claims,
            policy_claims=generated.policy_claims,
            verifier_type=generated.verifier_type,
            policy_signer=AttestationSigner._from_generated(  # pylint: disable=protected-access
                generated.policy_signer
            ),
            policy_hash=generated.policy_hash,
            is_debuggable=generated.is_debuggable,
            product_id=generated.product_id,
            mr_enclave=generated.mr_enclave,
            mr_signer=generated.mr_signer,
            svn=generated.svn,
            enclave_held_data=generated.enclave_held_data,
            sgx_collateral=generated.sgx_collateral,
        )

    @property
    def issuer(self):
        # type: () -> str
        """Returns the issuer of the attestation token.

        The issuer for the token MUST be the same as the `endpoint` associated
        with the :class:`azure.security.attestation.AttestationClient` object.
        If it is not, then the token should be rejected.

        See `RFC 7519 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.1>`_ for details.

        :rtype: str

        """
        return self._issuer

    @property
    def unique_id(self):
        # type: () -> Union[str, None]
        """Returns a unique ID claim for the attestation token.

        If present, the unique_id property can be used to distinguish between
        different attestation tokens.

        See `RFC 7519 Section 4.1.7 <https://rfc-editor.org/rfc/rfc7519.html#section-4.1.7>`_ for details.

        :rtype: str or None

        """
        return self._unique_identifier

    @property
    def nonce(self):
        # type: () -> Union[str, None]
        """Returns the value of the "nonce" input to the attestation request.

        :rtype: str or None
        """
        return self._nonce

    @property
    def version(self):
        # type: () -> str
        """Returns the version of the information returned in the token.

        :rtype: str
        """
        return self._version

    @property
    def runtime_claims(self):
        # type: () -> Union[Dict[str, Any], None]
        """Returns the runtime claims in the token.

        This value will match the input `runtime_json` property to the
        :meth:`azure.security.attestation.AttestationClient.attest_sgx_enclave` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        :rtype: dict[str, Any] or None

        .. note:: The `runtime_claims` property will only be populated if the
            `runtime_json` parameter to the `Attest` API is specified. It will
            not be populated if the `runtime_data` parameter is specified.

        """
        return self._runtime_claims

    @property
    def inittime_claims(self):
        # type: () -> Union[Dict[str, Any], None]
        """Returns the inittime claims in the token.

        This value will match the input `inittime_json` property to the
        :meth:`azure.security.attestation.AttestationClient.attest_sgx_enclave` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        :rtype: dict[str, Any] or None

        .. note:: The `inittime_claims` property will only be populated if the
            `inittime_json` parameter to the `Attest` API is specified. It will
            not be populated if the `inittime_data` parameter is specified.


        """
        return self._inittime_claims

    @property
    def policy_claims(self):
        # type: () -> Union[Dict[str, Any], None]
        """Returns the claims for the token generated by attestation policy.

        :rtype: dict[str, Any] or None

        """
        return self._policy_claims

    @property
    def verifier_type(self):
        # type: () -> str
        """Returns the verifier which generated this attestation token.

        :rtype: str
        """
        return self._verifier_type

    @property
    def policy_signer(self):
        # type: () -> Union[AttestationSigner, None]
        """Returns the signing certificate which was used to sign the policy
        which was applied when the token was generated.

        :rtype: ~azure.security.attestation.AttestationSigner or None
        """
        return AttestationSigner._from_generated(  # pylint: disable=protected-access
            self._policy_signer
        )

    @property
    def policy_hash(self):
        # type: () -> str
        """Returns the base64url encoded SHA256 hash of the base64url encoded
        attestation policy which was applied when generating this token.

        :rtype: str
        """
        return self._policy_hash

    @property
    def is_debuggable(self):
        # type: () -> bool
        """Returns "True" if the source evidence being attested indicates
        that the TEE has debugging enabled.

        :rtype: bool
        """
        return self._is_debuggable

    @property
    def product_id(self):
        # type: () -> float
        """Returns the product id associated with the SGX enclave being attested.

        :rtype: float

        """
        return self._product_id

    @property
    def mr_enclave(self):
        # type: () -> str
        """Returns HEX encoded `mr-enclave` value of the SGX enclave being attested.

        :rtype: str
        """
        return self._mr_enclave

    @property
    def mr_signer(self):
        # type: () -> str
        """Returns HEX encoded `mr-signer` value of the SGX enclave being attested.

        :rtype: str
        """
        return self._mr_signer

    @property
    def svn(self):
        # type: () -> int
        """Returns the `svn` value of the SGX enclave being attested.

        :rtype: int
        """
        return self._svn

    @property
    def enclave_held_data(self):
        # type: () -> Union[bytes, None]
        """Returns the value of the runtime_data field specified as an input
        to the :meth:`azure.security.attestation.AttestationClient.attest_sgx_enclave` or
        :meth:`azure.security.attestation.AttestationClient.attest_open_enclave` API.

        .. note:: The `enclave_held_data` property will only be populated if the
            `runtime_data` parameter to the `Attest` API is specified.

        :rtype: bytes or None
        """
        return self._enclave_held_data

    @property
    def sgx_collateral(self):
        # type: () -> Dict[str, Any]
        """Returns a set of information describing the complete set of inputs
        to the `oe_verify_evidence`

        :rtype: dict[str, Any]
        """

        return self._sgx_collateral


class StoredAttestationPolicy(object):
    """Represents an attestation policy in storage.

    When serialized, the `StoredAttestationPolicy` object will base64url encode the
    UTF-8 representation of the `policy` value.

    """

    def __init__(self, policy):
        # type: (str) -> None
        """
        :param str policy: Policy to be saved.
        """
        self._policy = policy.encode("ascii")

    def serialize(self, **kwargs):
        # type: (Any) -> str
        return GeneratedStoredAttestationPolicy(
            attestation_policy=self._policy
        ).serialize(**kwargs)

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedStoredAttestationPolicy) -> StoredAttestationPolicy
        if not generated:
            return None
        return StoredAttestationPolicy(generated.attestation_policy)


class AttestationToken(object):
    """Represents a token returned from the attestation service.

    :keyword Any body: The body of the newly created token, if provided.
    :keyword str signing_key: If specified, the PEM encoded key used to sign the
        token.
    :keyword str signing_certificate: If specified, the PEM encoded certificate
        used to sign the token.
    :keyword str token: If no body or signer is provided, the string representation of the token.

    If the `signing_key` and `signing_certificate` properties are not specified,
    the token created is unsecured.

    """

    def __init__(self, **kwargs):
        token = kwargs.get("token")
        if token is None:
            body = kwargs.pop("body", None)  # type: Any
            signing_key = kwargs.pop("signing_key", None)  # type: str
            signing_certificate = kwargs.pop("signing_certificate", None)  # type: str
            key = None
            if signing_key or signing_certificate:
                if isinstance(signing_key, string_types) or isinstance(
                    signing_certificate, string_types
                ):
                    [key, certificate] = validate_signing_keys(
                        signing_key, signing_certificate
                    )
                else:
                    if not isinstance(signing_certificate, Certificate):
                        raise ValueError(
                            "signing_certificate must be a string or Certificate"
                        )
                    if not isinstance(signing_key, RSAPrivateKey) and not isinstance(
                        signing_key, EllipticCurvePrivateKey
                    ):
                        raise ValueError("signing_key must be a string or Private Key")
                    key = signing_key
                    certificate = signing_certificate
            if key:
                token = self._create_secured_jwt(body, key=key, certificate=certificate)
            else:
                token = self._create_unsecured_jwt(body)

        self._token = token
        self._body_type = kwargs.get("body_type")  # type: Type
        token_parts = token.split(".")
        if len(token_parts) != 3:
            raise ValueError("Malformed JSON Web Token")
        self.header_bytes = base64url_decode(token_parts[0])
        self.body_bytes = base64url_decode(token_parts[1])
        self.signature_bytes = base64url_decode(token_parts[2])
        if len(self.body_bytes) != 0:
            self._body = json.loads(self.body_bytes)
        else:
            self._body = None
        self._header = json.loads(self.header_bytes)

    def __str__(self):
        return self._token

    @property
    def algorithm(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "alg".

        See `RFC 7515 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.1>`_ for details.

        If the value of algorithm is "none" it indicates that the token is unsecured.
        """
        return self._header.get("alg")

    @property
    def key_id(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "kid".

        See `RFC 7515 Section 4.1.4 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.4>`_ for details.
        """
        return self._header.get("kid")

    @property
    def expires(self):
        # type: () -> Union[datetime, None]
        """Expiration time for the token."""
        exp = self._body.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None

    @property
    def not_before(self):
        # type: () -> Union[datetime, None]
        """Time before which the token is invalid."""
        nbf = self._body.get("nbf")
        if nbf:
            return datetime.fromtimestamp(nbf)
        return None

    @property
    def issued(self):
        # type: () -> Union[datetime, None]
        """Time when the token was issued."""
        iat = self._body.get("iat")
        if iat:
            return datetime.fromtimestamp(iat)
        return None

    @property
    def content_type(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "content type".

        See `RFC 7515 Section 4.1.10 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.10>`_ for details.
        """
        return self._header.get("cty")

    @property
    def critical(self):
        # type: () -> Union[bool, None]
        """Json Web Token Header "Critical".

        See `RFC 7515 Section 4.1.11 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.11>`_ for details.
        """
        return self._header.get("crit")

    @property
    def key_url(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "Key URL".

        See `RFC 7515 Section 4.1.2 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.2>`_ for details.
        """
        return self._header.get("jku")

    @property
    def x509_url(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "X509 URL".

        See `RFC 7515 Section 4.1.5 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.5>`_ for details.
        """
        return self._header.get("x5u")

    @property
    def type(self):
        # type: () -> Union[str, None]
        """Json Web Token Header "typ".

        `RFC 7515 Section 4.1.9 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.9>`_ for details.
        """
        return self._header.get("typ")

    @property
    def certificate_thumbprint(self):
        # type: () -> Union[str, None]
        """The "thumbprint" of the certificate used to sign the request.

        `RFC 7515 Section 4.1.7 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.7>`_ for details.
        """
        return self._header.get("x5t")

    @property
    def certificate_sha256_thumbprint(self):
        # type: () -> Union[str, None]
        """The "thumbprint" of the certificate used to sign the request generated using the SHA256 algorithm.

        `RFC 7515 Section 4.1.8 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.8>`_ for details.
        """
        return self._header.get("x5t#256")

    @property
    def issuer(self):
        # type: () -> Union[str, None]
        """Json Web Token "iss" claim.

        `RFC 7519 Section 4.1.1 <https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.1>`_ for details.
        """
        return self._body.get("iss")

    @property
    def x509_certificate_chain(self):
        # type: () -> Union[list[str], None]
        """An array of Base64 encoded X.509 certificates which represent a certificate chain used to sign the token.

        See `RFC 7515 Section 4.1.6 <https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.6>`_ for details.
        """
        x5c = self._header.get("x5c")
        if x5c is not None:
            return x5c
        return None

    def _json_web_key(self):
        # type: () -> Union[JSONWebKey, None]
        jwk = self._header.get("jwk")
        return JSONWebKey.deserialize(jwk)

    def to_jwt_string(self):
        # type: () -> str
        """Returns a string serializing the JSON Web Token

        :rtype: str
        """
        return self._token

    def _validate_token(self, signers=None, **kwargs):
        # type: (List[AttestationSigner], **Any) -> None
        """Validate the attestation token based on the options specified in the
         :class:`TokenValidationOptions`.

        :param azure.security.attestation.TokenValidationOptions options: Options to be used when validating
            the token.
        :param List[azure.security.attestation.AttestationSigner] signers: Potential signers for the token.
            If the signers parameter is specified, validate_token will only
            consider the signers as potential signatories for the token, otherwise
            it will consider attributes in the header of the token.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :raises: ~azure.security.attestation.AttestationTokenValidationException
        """

        if not kwargs.get("validate_token", True):
            self._validate_static_properties(**kwargs)
            if "validation_callback" in kwargs:
                kwargs.get("validation_callback")(self, None)

        signer = None
        if self.algorithm != "none" and kwargs.get("validate_signature", True):
            # validate the signature for the token.
            candidate_certificates = self._get_candidate_signing_certificates(signers)
            signer = self._validate_signature(candidate_certificates)
            if signer is None:
                raise AttestationTokenValidationException(
                    "Could not find the certificate used to sign the token."
                )
        self._validate_static_properties(**kwargs)

        if "validation_callback" in kwargs:
            kwargs.get("validation_callback")(self, signer)

    def _get_body(self):
        # type: () -> Any
        """Returns the body of the attestation token as an object.

        If the `body_type` parameter to :py:class:AttestationToken has a `deserialize`
        method, :meth:get_body will call that method to convert the object from
        the wire format for the object into the expected model type.

        :rtype: Any
        """
        try:
            return self._body_type.deserialize(self._body)
        except AttributeError:
            return self._body

    def _get_candidate_signing_certificates(self, signing_certificates):
        # type: (List[AttestationSigner]) -> List[AttestationSigner]

        candidates = []
        desired_key_id = self.key_id
        if desired_key_id is not None:
            for signer in signing_certificates:
                if signer.key_id == desired_key_id:
                    candidates.append(signer)
                    break
            # If we didn't find a matching key ID in the supplied certificates,
            # try the JWS header to see if there might be a corresponding key.
            if len(candidates) == 0:
                jwk = self._json_web_key()
                if jwk is not None:
                    if jwk.kid == desired_key_id:
                        if jwk.x5_c:
                            signers = jwk.x5_c
                        candidates.append(AttestationSigner(signers, desired_key_id))
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

    @staticmethod
    def _get_certificates_from_x5c(x5clist):
        # type: (list[str]) -> list[Certificate]
        return [base64.b64decode(b64cert) for b64cert in x5clist]

    def _validate_signature(self, candidate_certificates):
        # type: (list[AttestationSigner]) -> AttestationSigner
        signed_data = (
            base64url_encode(self.header_bytes)
            + "."
            + base64url_encode(self.body_bytes)
        )
        for signer in candidate_certificates:
            cert = load_pem_x509_certificate(
                signer.certificates[0].encode("ascii"), backend=default_backend()
            )
            signer_key = cert.public_key()
            # Try to verify the signature with this candidate.
            # If it doesn't work, try the next signer.
            try:
                if isinstance(signer_key, RSAPublicKey):
                    signer_key.verify(
                        self.signature_bytes,
                        signed_data.encode("utf-8"),
                        padding.PKCS1v15(),
                        SHA256(),
                    )
                else:
                    signer_key.verify(
                        self.signature_bytes, signed_data.encode("utf-8"), SHA256()
                    )
                return signer
            except InvalidSignature as ex:
                raise_from(
                    AttestationTokenValidationException(
                        "Could not verify signature of attestation token."
                    ),
                    ex,
                )
        return None

    def _validate_static_properties(self, **kwargs):
        # type: (Any, **Any) -> bool
        """Validate the static properties in the attestation token."""
        if self._body:
            time_now = datetime.now()
            if kwargs.get("validate_expiration", True) and self.expires is not None:
                if time_now > self.expires:
                    delta = time_now - self.expires
                    if delta.total_seconds() > kwargs.get("validation_slack", 0.5):
                        raise AttestationTokenValidationException(
                            u"Token is expired. Now: {}, Not Before: {}".format(
                                time_now.isoformat(), self.not_before.isoformat()
                            )
                        )
            if (
                kwargs.get("validate_not_before", True)
                and hasattr(self, "not_before")
                and self.not_before is not None
            ):
                if time_now < self.not_before:
                    delta = self.not_before - time_now
                    if delta.total_seconds() > kwargs.get("validation_slack", 0.5):
                        raise AttestationTokenValidationException(
                            u"Token is not yet valid. Now: {}, Not Before: {}".format(
                                time_now.isoformat(), self.not_before.isoformat()
                            )
                        )
            if (
                kwargs.get("validate_issuer", False)
                and hasattr(self, "issuer")
                and self.issuer is not None
            ):
                if kwargs.get("issuer", None) != self.issuer:
                    raise AttestationTokenValidationException(
                        u"Issuer in token: {} is not the expected issuer: {}.".format(
                            self.issuer, kwargs.get("issuer", None)
                        )
                    )
        return True

    @staticmethod
    def _create_unsecured_jwt(body):
        # type: (Any) -> str
        """Return an unsecured JWT expressing the body."""
        # Base64url encoded '{"alg":"none"}'. See https://www.rfc-editor.org/rfc/rfc7515.html#appendix-A.5 for
        # more information.
        return_value = "eyJhbGciOiJub25lIn0."

        # Try to serialize the body by asking the body object to serialize itself.
        # This normalizes the attributes in the body object to conform to the serialized attributes used
        # for transmission to the service.
        try:
            body = body.serialize()
        except AttributeError:
            pass
        json_body = ""
        if body is not None:
            json_body = json.dumps(body)

        return_value += base64url_encode(json_body.encode("utf-8"))
        return_value += "."
        return return_value

    @staticmethod
    def _create_secured_jwt(body, **kwargs):
        # type: (Any, **Any) -> str
        """Return a secured JWT expressing the body, secured with the specified signing key.
        :param Any body: The body of the token to be serialized.
        :keyword key: Signing key used to sign the token.
        :kwtype key: cryptography.hazmat.primitives.asymmetric.ec or cryptography.hazmat.primitives.asymmetric.rsa
        :keyword certificate: Certificate to be transmitted to attestation service
            used to validate the token.
        :kwtype certificate: Certificate
        """
        key = kwargs.pop("key", None)
        certificate = kwargs.pop("certificate", None)

        header = {
            "alg": "RSA256" if isinstance(key, RSAPrivateKey) else "ECDH256",
            "jwk": {
                "x5c": [
                    base64.b64encode(certificate.public_bytes(Encoding.DER)).decode(
                        "ascii"
                    )
                ]
            },
        }
        json_header = json.dumps(header)
        return_value = base64url_encode(json_header.encode("ascii"))

        try:
            body = body.serialize()
        except AttributeError:
            pass
        json_body = ""
        if body is not None:
            json_body = json.dumps(body)
        return_value += "."
        return_value += base64url_encode(json_body.encode("utf-8"))

        # Now we want to sign the return_value.
        if isinstance(key, RSAPrivateKey):
            signature = key.sign(
                return_value.encode("utf-8"),
                algorithm=SHA256(),
                padding=padding.PKCS1v15(),
            )
        else:
            signature = key.sign(return_value.encode("utf-8"), algorithm=SHA256())
        # And finally append the base64url encoded signature.
        return_value += "."
        return_value += base64url_encode(signature)
        return return_value


class AttestationPolicyToken(AttestationToken):
    """
    An `AttestationPolicyToken` is an AttestationToken object specialized for
    use in attestation policy :func:`AttestationAdministrationClient.set_policy`
    operations. It expresses the JSON Web Signature object sent to the
    attestation service to set the token.

    This token can thus be used to validate the hash returned by the `set_policy` API.

    :param str policy: Attestation Policy to be used in the body of the token.

    """

    def __init__(self, policy, **kwargs):
        # type: (str, Dict[str, Any]) -> None
        super(  # pylint: disable=super-with-arguments
            AttestationPolicyToken, self
        ).__init__(body=StoredAttestationPolicy(policy), **kwargs)


class AttestationTokenValidationException(ValueError):
    """Thrown when an attestation token validation fails.

    :param str message: Message for caller describing the reason for the failure.
    """

    def __init__(self, message):
        self.message = message
        super(  # pylint: disable=super-with-arguments
            AttestationTokenValidationException, self
        ).__init__(self.message)

class TpmAttestationResult(object):
    """Represents the Tpm Attestation response data returned from the attestation service
    as a result of a call to :meth:`azure.security.attestation.AttestationClient.attest_tpm`.

    :ivar bytes data: The result of the operation.
    """

    def __init__(self, data: bytes):
        self.data = data
