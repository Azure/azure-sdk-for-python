# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Dict, List, Any, Optional, TYPE_CHECKING

from azure.core import PipelineClient

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core._pipeline_client_async import AsyncPipelineClient
    from azure.core.credentials_async import AsyncTokenCredential

from .._generated.aio import AzureAttestationRestClient
from .._generated.models import (
    AttestationType, 
    PolicyResult as GeneratedPolicyResult, 
    PolicyCertificatesResult, 
    JSONWebKey, 
    AttestationCertificateManagementBody, 
    StoredAttestationPolicy as GeneratedStoredAttestationPolicy,
    PolicyCertificatesModificationResult as GeneratedPolicyCertificatesModificationResult
)
from .._configuration import AttestationClientConfiguration
from .._models import (
    AttestationSigner, 
    AttestationToken, 
    AttestationResponse, 
    AttestationSigningKey, 
    PolicyCertificatesModificationResult,
    PolicyResult,
    AttestationTokenValidationException
)
import base64
from azure.core.tracing.decorator_async import distributed_trace_async
from threading import Lock


class AttestationAdministrationClient(object):
    """Provides administrative APIs for managing an instance of the Attestation Service.

    :param str instance_url: base url of the service
    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :keyword AsyncPipelineClient pipeline: If omitted, the standard pipeline is used.
    :keyword AsyncHttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[AsyncHTTPPolicy] policies: If omitted, the standard pipeline is used.

    For additional client creation configuration options, please see https://aka.ms/azsdk/python/options.

    """

    def __init__(
        self,
        credential, #type: AsyncTokenCredential
        instance_url, #type: str
        **kwargs #type: Any
    ): #type: (...) -> None
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(credential, instance_url, **kwargs)
        self._client = AzureAttestationRestClient(credential, instance_url, **kwargs)
        self._statelock = Lock()
        self._signing_certificates = None

    @distributed_trace_async
    async def get_policy(
        self,
        attestation_type, #type: AttestationType
        **kwargs: Any
        ) -> AttestationResponse[str]:
        """ Retrieves the attestation policy for a specified attestation type.

        :param azure.security.attestation.AttestationType attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to retrieve the policy.
        :return: Attestation service response encapsulating a string attestation policy.
        :rtype: azure.security.attestation.AttestationResponse[str]
        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        """
        
        policyResult = await self._client.policy.get(attestation_type, **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token, body_type=GeneratedPolicyResult)
        token_body = token.get_body()
        stored_policy = AttestationToken[GeneratedStoredAttestationPolicy](token=token_body.policy, body_type=GeneratedStoredAttestationPolicy)

        actual_policy = stored_policy.get_body().attestation_policy #type: bytes

        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise AttestationTokenValidationException("Token Validation of get_policy API failed.")

        return AttestationResponse[str](token, actual_policy.decode('utf-8'))

    @distributed_trace_async
    async def set_policy(
        self, 
        attestation_type, #type: AttestationType
        attestation_policy, #type: str
        signing_key=None, #type:AttestationSigningKey
        **kwargs #type: Any
        ): #type: (...) -> AttestationResponse[PolicyResult]
        """ Sets the attestation policy for the specified attestation type.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to set the policy.
        :type attestation_type: azure.security.attestation.AttestationType
        :param str attestation_policy: Attestation policy to be set.
        :param signing_key: Signing key to be
            used to sign the policy before sending it to the service.
        :type signing_key: azure.security.attestation.AttestationSigningKey 
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

        policy_token = AttestationToken[GeneratedStoredAttestationPolicy](
            body=GeneratedStoredAttestationPolicy(attestation_policy = attestation_policy.encode('ascii')),
            signer=signing_key,
            body_type=GeneratedStoredAttestationPolicy)
        policyResult = await self._client.policy.set(attestation_type=attestation_type, new_attestation_policy=policy_token.serialize(), **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token,
            body_type=GeneratedPolicyResult)
        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise AttestationTokenValidationException("Token Validation of set_policy API failed.")

        return AttestationResponse[PolicyResult](token, PolicyResult._from_generated(token.get_body()))

    @distributed_trace_async
    async def reset_policy(
        self, 
        attestation_type, #type: AttestationType
        signing_key=None, #type: AttestationSigningKey
        **kwargs #type: Any
        ): #type: (...) -> AttestationResponse[PolicyResult]
        """ Resets the attestation policy for the specified attestation type to the default value.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for 
            which to set the policy.
        :type attestation_type: azure.security.attestation.AttestationType
        :param str attestation_policy: Attestation policy to be reset.
        :param signing_key: Signing key to be
            used to sign the policy before sending it to the service.

        :type signing_key: azure.security.attestation.AttestationSigningKey

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
        policy_token = AttestationToken(
            body=None,
            signer=signing_key)
        policyResult = await self._client.policy.reset(attestation_type=attestation_type, policy_jws=policy_token.serialize(), **kwargs)
        token = AttestationToken[GeneratedPolicyResult](token=policyResult.token,
            body_type=GeneratedPolicyResult)
        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise AttestationTokenValidationException("Token Validation of reset_policy API failed.")

        return AttestationResponse[PolicyResult](token, PolicyResult._from_generated(token.get_body()))


    @distributed_trace_async
    async def get_policy_management_certificates(
        self, 
        **kwargs #type: Any
        ): #type: (...) -> AttestationResponse[list[list[bytes]]]
        """ Retrieves the set of policy management certificates for the instance.

        The list of policy management certificates will only be non-empty if the
        attestation service instance is in Isolated mode.

        :return: Attestation service response 
            encapsulating a list of DER encoded X.509 certificate chains.
        :rtype: azure.security.attestation.AttestationResponse[list[list[bytes]]]
        """

        cert_response = await self._client.policy_certificates.get(**kwargs)
        token = AttestationToken[PolicyCertificatesResult](
            token=cert_response.token,
            body_type=PolicyCertificatesResult)
        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise AttestationTokenValidationException("Token Validation of PolicyCertificates API failed.")
        certificates = []

        cert_list = token.get_body()

        for key in cert_list.policy_certificates.keys:
            key_certs = [base64.b64decode(cert) for cert in key.x5_c]
            certificates.append(key_certs)
        return AttestationResponse(token, certificates)

    @distributed_trace_async
    async def add_policy_management_certificate(
        self, 
        certificate_to_add, #type: bytes
        signing_key, #type: AttestationSigningKey
        **kwargs #type: Any
        ): #type: (...) -> AttestationResponse[PolicyCertificatesModificationResult]
        """ Adds a new policy management certificate to the set of policy management certificates for the instance.

        :param bytes certificate_to_add: DER encoded X.509 certificate to add to 
            the list of attestation policy management certificates.
        :param azure.security.attestation.AttestationSigningKey signing_key: Signing Key representing one of 
            the *existing* attestation signing certificates.
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
        key=JSONWebKey(kty='RSA', x5_c = [ base64.b64encode(certificate_to_add).decode('ascii')])
        add_body = AttestationCertificateManagementBody(policy_certificate=key)
        cert_add_token = AttestationToken[AttestationCertificateManagementBody](
            body=add_body,
            signer=signing_key,
            body_type=AttestationCertificateManagementBody)

        cert_response = await self._client.policy_certificates.add(cert_add_token.serialize(), **kwargs)
        token = AttestationToken[GeneratedPolicyCertificatesModificationResult](token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult)
        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise Exception("Token Validation of PolicyCertificate Add API failed.")
        return AttestationResponse[PolicyCertificatesModificationResult](token, PolicyCertificatesModificationResult._from_generated(token.get_body()))

    @distributed_trace_async
    async def remove_policy_management_certificate(
        self, 
        certificate_to_add, #type: bytes
        signing_key, #type: AttestationSigningKey
        **kwargs #type: Any
        ): #type: (...) -> AttestationResponse[PolicyCertificatesModificationResult]
        """ Removes a new policy management certificate to the set of policy management certificates for the instance.

        :param bytes certificate_to_add: DER encoded X.509 certificate to add to 
            the list of attestation policy management certificates.
        :param azure.security.attestation.AttestationSigningKey signing_key: Signing Key representing one of 
            the *existing* attestation signing certificates.
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
        key=JSONWebKey(kty='RSA', x5_c = [ base64.b64encode(certificate_to_add).decode('ascii')])
        add_body = AttestationCertificateManagementBody(policy_certificate=key)
        cert_add_token = AttestationToken[AttestationCertificateManagementBody](
            body=add_body,
            signer=signing_key,
            body_type=AttestationCertificateManagementBody)

        cert_response = await self._client.policy_certificates.remove(cert_add_token.serialize(), **kwargs)
        token = AttestationToken[GeneratedPolicyCertificatesModificationResult](token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult)
        if self._config.token_validation_options.validate_token:
            if not token.validate_token(self._config.token_validation_options, await self._get_signers(**kwargs)):
                raise AttestationTokenValidationException("Token Validation of PolicyCertificate Remove API failed.")
        return AttestationResponse[PolicyCertificatesModificationResult](token, PolicyCertificatesModificationResult._from_generated(token.get_body()))

    async def _get_signers(
        self,
        **kwargs): #type: (Any) -> List[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.
        """

        with self._statelock:
            if (self._signing_certificates == None):
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
