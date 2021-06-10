# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Dict, List, Any, Optional, TYPE_CHECKING

from azure.core import PipelineClient
from cryptography.hazmat.primitives import serialization
from cryptography.x509.base import load_pem_x509_certificate

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core._pipeline_client_async import AsyncPipelineClient
    from azure.core.credentials_async import AsyncTokenCredential

from .._generated.aio import AzureAttestationRestClient
from .._generated.models import (
    AttestationType, 
    PolicyResult as GeneratedPolicyResult, 
    PolicyCertificatesResult as GeneratedPolicyCertificatesResult, 
    JSONWebKey, 
    AttestationCertificateManagementBody, 
    StoredAttestationPolicy as GeneratedStoredAttestationPolicy,
    PolicyCertificatesModificationResult as GeneratedPolicyCertificatesModificationResult
)
from .._configuration import AttestationClientConfiguration
from .._models import (
    AttestationSigner, 
    AttestationToken, 
    PolicyCertificatesModificationResult,
    PolicyCertificatesResult,
    AttestationPolicyResult,
    AttestationTokenValidationException
)
from .._common import SigningKeyUtils, PemUtils, merge_validation_args
import base64
from azure.core.tracing.decorator_async import distributed_trace_async
from threading import Lock


class AttestationAdministrationClient(object):
    """Provides administrative APIs for managing an instance of the Attestation Service.

    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :param str endpoint: The attestation instance base URI, for example https://mytenant.attest.azure.net.
    :keyword str signing_key: PEM encoded signing key to be used for all
        operations.
    :keyword str signing_certificate: PEM encoded X.509 certificate to be used for all
        operations.
    :keyword AsyncPipelineClient pipeline: If omitted, the standard pipeline is used.
    :keyword AsyncHttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[AsyncHTTPPolicy] policies: If omitted, the standard pipeline is used.

    For additional client creation configuration options, please see https://aka.ms/azsdk/python/options.

    """

    def __init__(
        self,
        credential, #type: AsyncTokenCredential
        endpoint,
        **kwargs #type: Any
    ): #type: (...) -> None
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(**kwargs)
        self._client = AzureAttestationRestClient(credential, endpoint, **kwargs)
        self._statelock = Lock()
        self._signing_certificates = None

        self._signing_key = None
        self._signing_certificate = None

        signing_key = kwargs.pop('signing_key', None)
        signing_certificate = kwargs.pop('signing_certificate', None)
        if signing_key or signing_certificate:
            self._signing_key, self._signing_certificate = SigningKeyUtils.validate_signing_keys(signing_key, signing_certificate)


    @distributed_trace_async
    async def get_policy(
        self,
        attestation_type, #type: AttestationType
        **kwargs: Any
        ) -> AttestationPolicyResult:
        """ Retrieves the attestation policy for a specified attestation type.

        :param azure.security.attestation.AttestationType attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to retrieve the policy.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response encapsulating a string attestation policy.
        :rtype: azure.security.attestation.AttestationPolicyResult
        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        """

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        policyResult = await self._client.policy.get(attestation_type, **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token, body_type=GeneratedPolicyResult)
        token_body = token.get_body()
        stored_policy = AttestationToken[GeneratedStoredAttestationPolicy](token=token_body.policy, body_type=GeneratedStoredAttestationPolicy)

        actual_policy = stored_policy.get_body().attestation_policy #type: bytes

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return AttestationPolicyResult._from_generated(None, token, actual_policy.decode('utf-8'))

    @distributed_trace_async
    async def set_policy(
        self, 
        attestation_type, #type: AttestationType
        attestation_policy, #type: str
        **kwargs #type: Any
        ): #type: (...) -> AttestationPolicyResult
        """ Sets the attestation policy for the specified attestation type.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to set the policy.
        :type attestation_type: azure.security.attestation.AttestationType
        :param str attestation_policy: Attestation policy to be set.
        :keyword str signing_key: PEM encoded signing key to be
            used to sign the policy before sending it to the service.
        :keyword str signing_certificate: PEM encoded X509 certificate sent to the 
            attestation service to validate the attestation policy.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response encapsulating a :class:`PolicyResult`.
        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.PolicyResult]
        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        .. note::
            If the attestation instance is in *Isolated* mode, then the 
            `signing_key` parameter MUST be a signing key containing one of the
            certificates returned by :meth:`get_policy_management_certificates`.

            If the attestation instance is in *AAD* mode, then the `signing_key` 
            parameter does not need to be provided.

        """
        signing_key = kwargs.pop('signing_key', None)
        signing_certificate = kwargs.pop('signing_certificate', None)
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        policy_token = AttestationToken[GeneratedStoredAttestationPolicy](
            body=GeneratedStoredAttestationPolicy(attestation_policy = attestation_policy.encode('ascii')),
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=GeneratedStoredAttestationPolicy)

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        policyResult = await self._client.policy.set(attestation_type=attestation_type, new_attestation_policy=policy_token.to_jwt_string(), **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token,
            body_type=GeneratedPolicyResult)

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return AttestationPolicyResult._from_generated(token.get_body(), token, None)

    @distributed_trace_async
    async def reset_policy(
        self, 
        attestation_type, #type: AttestationType
        **kwargs #type: Any
        ): #type: (...) -> AttestationPolicyResult
        """ Resets the attestation policy for the specified attestation type to the default value.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to set the policy.
        :type attestation_type: azure.security.attestation.AttestationType
        :param str attestation_policy: Attestation policy to be reset.
        :keyword str signing_key: PEM encoded signing key to be
            used to sign the policy before sending it to the service.
        :keyword str signing_certificate: PEM encoded X509 certificate sent to the 
            attestation service to validate the attestation policy.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: Attestation service response encapsulating a :class:`PolicyResult`.
        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.PolicyResult]
        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        .. note::
            If the attestation instance is in *Isolated* mode, then the 
            `signing_key` parameter MUST be a signing key containing one of the
            certificates returned by :meth:`get_policy_management_certificates`.

            If the attestation instance is in *AAD* mode, then the `signing_key` 
            parameter does not need to be provided.
        """
        signing_key = kwargs.pop('signing_key', None)
        signing_certificate = kwargs.pop('signing_certificate', None)
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        policy_token = AttestationToken(body=None, signing_key=signing_key, signing_certificate=signing_certificate)

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        policyResult = await self._client.policy.reset(attestation_type=attestation_type, policy_jws=policy_token.to_jwt_string(), **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token,
            body_type=GeneratedPolicyResult)

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return AttestationPolicyResult._from_generated(token.get_body(), token, None)


    @distributed_trace_async
    async def get_policy_management_certificates(
        self, 
        **kwargs #type: Any
        ): #type: (...) -> PolicyCertificatesResult
        """ Retrieves the set of policy management certificates for the instance.

        The list of policy management certificates will only be non-empty if the
        attestation service instance is in Isolated mode.

        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response 
            encapsulating a list of PEM encoded X.509 certificate chains.
        :rtype: PolicyCertificateResult
        """

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        cert_response = await self._client.policy_certificates.get(**kwargs)
        token = AttestationToken[GeneratedPolicyCertificatesResult](
            token=cert_response.token,
            body_type=GeneratedPolicyCertificatesResult)

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        certificates = []

        cert_list = token.get_body()

        for key in cert_list.policy_certificates.keys:
            key_certs = [PemUtils.pem_from_base64(cert, "CERTIFICATE") for cert in key.x5_c]
            certificates.append(key_certs)
        return PolicyCertificatesResult(token, certificates)

    @distributed_trace_async
    async def add_policy_management_certificate(
        self, 
        certificate_to_add, #type: bytes
        **kwargs #type: Any
        ): #type: (...) -> PolicyCertificatesModificationResult
        """ Adds a new policy management certificate to the set of policy management certificates for the instance.

        :param bytes certificate_to_add: DER encoded X.509 certificate to add to 
            the list of attestation policy management certificates.
        :param azure.security.attestation.AttestationSigningKey signing_key: Signing Key representing one of 
            the *existing* attestation signing certificates.
        :keyword str signing_key: PEM encoded signing key to be
            used to sign the policy before sending it to the service.
        :keyword str signing_certificate: PEM encoded X509 certificate sent to the 
            attestation service to validate the attestation policy.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response 
            encapsulating the status of the add request.

        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.PolicyCertificatesModificationResult]

        The :class:`PolicyCertificatesModificationResult` response to the 
        :meth:`add_policy_management_certificate` API contains two attributes
        of interest. 
        
        The first is `certificate_resolution`, which indicates 
        whether the certificate in question is present in the set of policy 
        management certificates after the operation has completed, or if it is 
        absent.

        The second is the `thumbprint` of the certificate added. The `thumbprint`
        for the certificate is the SHA1 hash of the DER encoding of the
        certificate.

        """
        signing_key = kwargs.pop('signing_key', None)
        signing_certificate = kwargs.pop('signing_certificate', None)
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        if not signing_key or not signing_certificate:
            raise ValueError("A signing certificate and key must be provided to add_policy_management_certificate.")

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        certificate_to_add = load_pem_x509_certificate(certificate_to_add.encode('ascii'))

        jwk=JSONWebKey(kty='RSA', x5_c = [ base64.b64encode(certificate_to_add.public_bytes(serialization.Encoding.DER)).decode('ascii')])
        add_body = AttestationCertificateManagementBody(policy_certificate=jwk)
        cert_add_token = AttestationToken[AttestationCertificateManagementBody](
            body=add_body,
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=AttestationCertificateManagementBody)

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        cert_response = await self._client.policy_certificates.add(cert_add_token.to_jwt_string(), **kwargs)
        token = AttestationToken[GeneratedPolicyCertificatesModificationResult](token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult)

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        return PolicyCertificatesModificationResult._from_generated(token.get_body(), token)

    @distributed_trace_async
    async def remove_policy_management_certificate(
        self, 
        certificate_to_remove, #type: bytes
        **kwargs #type: Any
        ): #type: (...) -> PolicyCertificatesModificationResult
        """ Removes a new policy management certificate to the set of policy management certificates for the instance.

        :param bytes certificate_to_add: DER encoded X.509 certificate to add to 
            the list of attestation policy management certificates.
        :keyword str signing_key: PEM encoded signing key to be
            used to sign the policy before sending it to the service.
        :keyword str signing_certificate: PEM encoded X509 certificate sent to the 
            attestation service to validate the attestation policy.
        :keyword bool validate_token: if True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw 
            an exception.
        :paramtype validation_callback: Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied 
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response 
            encapsulating a list of DER encoded X.509 certificate chains.
        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.PolicyCertificatesModificationResult]

        The :class:`PolicyCertificatesModificationResult` response to the 
        :meth:`remove_policy_management_certificate` API contains two attributes
        of interest. 
        
        The first is `certificate_resolution`, which indicates 
        whether the certificate in question is present in the set of policy 
        management certificates after the operation has completed, or if it is 
        absent.

        The second is the `thumbprint` of the certificate added. The `thumbprint`
        for the certificate is the SHA1 hash of the DER encoding of the
        certificate.
        
        """
        signing_key = kwargs.pop('signing_key', None)
        signing_certificate = kwargs.pop('signing_certificate', None)
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        if not signing_key or not signing_certificate:
            raise ValueError("A signing certificate and key must be provided to remove_policy_management_certificate.")

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        certificate_to_remove = load_pem_x509_certificate(certificate_to_remove.encode('ascii'))

        jwk=JSONWebKey(kty='RSA', x5_c = [ base64.b64encode(certificate_to_remove.public_bytes(serialization.Encoding.DER)).decode('ascii')])
        add_body = AttestationCertificateManagementBody(policy_certificate=jwk)
        cert_add_token = AttestationToken[AttestationCertificateManagementBody](
            body=add_body,
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=AttestationCertificateManagementBody)

        # Merge our existing config options with the options for this API call. 
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._args, kwargs)

        cert_response = await self._client.policy_certificates.remove(cert_add_token.to_jwt_string(), **kwargs)
        token = AttestationToken[GeneratedPolicyCertificatesModificationResult](token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult)

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        return PolicyCertificatesModificationResult._from_generated(token.get_body(), token)

    async def _get_signers(
        self,
        **kwargs): #type: (Any) -> List[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.
        """

        with self._statelock:
            if self._signing_certificates == None:
                signing_certificates = await self._client.signing_certificates.get(**kwargs)
                self._signing_certificates = []
                for key in signing_certificates.keys:
                    self._signing_certificates.append(AttestationSigner._from_generated(key))
            signers = self._signing_certificates
        return signers

    async def close(self):
        # type: () -> None
        await self._client.close()

    async def __aenter__(self):
        # type: () -> AttestationAdministrationClient
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        # type: (Any) -> None
        await self._client.__aexit__(*exc_details)
