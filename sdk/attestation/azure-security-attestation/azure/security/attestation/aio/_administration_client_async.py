# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Dict, List, Any, Optional, TYPE_CHECKING, Tuple

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
    PolicyCertificatesModificationResult as GeneratedPolicyCertificatesModificationResult,
)
from .._configuration import AttestationClientConfiguration
from .._models import (
    AttestationSigner,
    AttestationToken,
    AttestationPolicyCertificateResult,
    AttestationPolicyResult,
    AttestationTokenValidationException,
)
from .._common import pem_from_base64, validate_signing_keys, merge_validation_args
import base64
from azure.core.tracing.decorator_async import distributed_trace_async
from threading import Lock


class AttestationAdministrationClient(object):
    """Provides administrative APIs for managing an instance of the Attestation Service.

    The :class:`~AttestationAdministrationClient` object implements the policy
    management and policy certificate management functions.

    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :param str endpoint: The attestation instance base URI, for example https://mytenant.attest.azure.net.
    :keyword str signing_key: PEM encoded signing key to be used for all
        operations.
    :keyword str signing_certificate: PEM encoded X.509 certificate to be used for all
        operations.

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

    :keyword ~azure.core.pipeline.Pipeline pipeline: If omitted, the standard pipeline is used.
    :keyword ~azure.core.pipeline.transport.HttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[~azure.core.pipeline.policies.HTTPPolicy] policies: If omitted, the standard pipeline is used.

    If the `signing_key` and `signing_certificate` parameters
    are provided, they will be applied to the following APIs:

    * :py:func:`set_policy`
    * :py:func:`reset_policy`
    * :py:func:`add_policy_management_certificate`
    * :py:func:`remove_policy_management_certificate`

    .. note::
        The `signing_key` and `signing_certificate` parameters are a pair. If one
        is present, the other must also be provided. In addition, the public key
        in the `signing_key` and the public key in the `signing_certificate` must
        match to ensure that the `signing_certificate` can be used to validate an
        object signed by `signing_key`.

    .. tip::
        The `validate_token`, `validation_callback`, `validate_signature`,
        `validate_expiration`, `validate_not_before_time`, `validate_issuer`, and
        `issuer` keyword arguments are default values applied to each API call within
        the :py:class:`AttestationAdministrationClient` class. These values can be
        overridden on individual API calls as needed.

    For additional client creation configuration options, please see https://aka.ms/azsdk/python/options.

    """

    def __init__(
        self, credential: "AsyncTokenCredential", endpoint: str, **kwargs: Any
    ) -> None:
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(**kwargs)
        self._client = AzureAttestationRestClient(credential, endpoint, **kwargs)
        self._statelock = Lock()
        self._signing_certificates = None

        self._signing_key = None
        self._signing_certificate = None

        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            self._signing_key, self._signing_certificate = validate_signing_keys(
                signing_key, signing_certificate
            )

    @distributed_trace_async
    async def get_policy(
        self, attestation_type: AttestationType, **kwargs: Any
    ) -> Tuple[str, AttestationToken]:
        """Retrieves the attestation policy for a specified attestation type.

        :param azure.security.attestation.AttestationType attestation_type: :class:`azure.security.attestation.AttestationType` for
            which to retrieve the policy.
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

        :return: A tuple containing the attestation policy and the token returned
            by the service..

        :rtype: ~typing.Tuple[str, AttestationToken]

        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        .. note::
            The Azure Attestation Policy language is defined `here <https://docs.microsoft.com/azure/attestation/author-sign-policy>`_

        .. admonition:: Example: Retrieving the current policy on an attestation instance.


            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [BEGIN get_policy]
                :end-before: [END get_policy]
                :language: python
                :dedent: 8
                :caption: Getting the current policy document.

        """

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        policyResult = await self._client.policy.get(attestation_type, **kwargs)
        token = AttestationToken(
            token=policyResult.token, body_type=GeneratedPolicyResult
        )
        token_body = token.get_body()
        stored_policy = AttestationToken(
            token=token_body.policy, body_type=GeneratedStoredAttestationPolicy
        )

        policy_body = stored_policy.get_body()
        actual_policy = (
            policy_body.attestation_policy if policy_body else "".encode("ascii")
        )  # type: bytes

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return actual_policy.decode("utf-8"), token

    @distributed_trace_async
    async def set_policy(
        self, attestation_type: AttestationType, attestation_policy: str, **kwargs: Any
    ) -> AttestationPolicyResult:
        """Sets the attestation policy for the specified attestation type.

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
        :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Attestation service response encapsulating a :class:`PolicyResult`.

        :return: Result of set policy operation.

        :rtype: ~azure.security.attestation.AttestationPolicyResult

        :raises ~azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        .. admonition:: Example: Setting the attestation policy on an AAD mode
            attestation instance (no signing key required).

            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [BEGIN set_policy_unsecured]
                :end-before: [END set_policy_unsecured]
                :language: python
                :dedent: 0
                :caption: Setting a security policy without a signing key.

        .. admonition:: Example: Setting the attestation policy and verifying
            that the policy was recieved by the service.

            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [START validate_policy_hash]
                :end-before: [END validate_policy_hash]
                :language: python
                :dedent: 0
                :caption: Setting the attestation policy with hash verification.

        .. note::
            If the attestation instance is in *Isolated* mode, then the
            `signing_key` parameter MUST be a signing key containing one of the
            certificates returned by :meth:`get_policy_management_certificates`.

            If the attestation instance is in *AAD* mode, then the `signing_key`
            parameter does not need to be provided.

        """
        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            signing_key, signing_certificate = validate_signing_keys(
                signing_key, signing_certificate
            )

        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        policy_token = AttestationToken(
            body=GeneratedStoredAttestationPolicy(
                attestation_policy=attestation_policy.encode("ascii")
            ),
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=GeneratedStoredAttestationPolicy,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        policyResult = await self._client.policy.set(
            attestation_type=attestation_type,
            new_attestation_policy=policy_token.to_jwt_string(),
            **kwargs
        )
        token = AttestationToken(
            token=policyResult.token, body_type=GeneratedPolicyResult
        )

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return AttestationPolicyResult._from_generated(token.get_body(), token)

    @distributed_trace_async
    async def reset_policy(
        self, attestation_type: AttestationType, **kwargs: Any
    ) -> AttestationPolicyResult:
        """Resets the attestation policy for the specified attestation type to the default value.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for
            which to set the policy.
        :type attestation_type: azure.security.attestation.AttestationType
        :keyword str signing_key: PEM encoded signing key to be
            used to sign the policy before sending it to the service.
        :keyword str signing_certificate: PEM encoded X509 certificate sent to the
            attestation service to validate the attestation policy.
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

        :return: An :class:`AttestationPolicyResult` object expressing the result of the removal.
        :rtype: azure.security.attestation.AttestationPolicyResult
        :raises azure.security.attestation.AttestationTokenValidationException: Raised when an attestation token is invalid.

        .. note::
            If the attestation instance is in *Isolated* mode, then the
            `signing_key` parameter MUST be a signing key containing one of the
            certificates returned by :meth:`get_policy_management_certificates`.

            If the attestation instance is in *AAD* mode, then the `signing_key`
            parameter does not need to be provided.
        """
        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            signing_key, signing_certificate = validate_signing_keys(
                signing_key, signing_certificate
            )
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        policy_token = AttestationToken(
            body=None, signing_key=signing_key, signing_certificate=signing_certificate
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        policyResult = await self._client.policy.reset(
            attestation_type=attestation_type,
            policy_jws=policy_token.to_jwt_string(),
            **kwargs
        )
        token = AttestationToken(
            token=policyResult.token, body_type=GeneratedPolicyResult
        )

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)

        return AttestationPolicyResult._from_generated(token.get_body(), token)

    @distributed_trace_async
    async def get_policy_management_certificates(
        self, **kwargs: Any
    ) -> Tuple[List[List[str]], AttestationToken]:
        """Retrieves the set of policy management certificates for the instance.

        The list of policy management certificates will only have values if the
        attestation service instance is in Isolated mode.

        :keyword bool validate_token: if True, validate the token, otherwise
            return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to
            perform custom validation of the token. If the token is invalid,
            the `validation_callback` function should throw an exception to cause
            the API call to fail.
        :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: if True, validate the signature of the
            token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time
            of the token being validated.
        :keyword float validation_slack: Slack time for validation - tolerance
            applied to help account for clock drift between the issuer and
            the current machine.
        :keyword str issuer: Expected issuer, used if validate_issuer is true.
        :keyword bool validate_issuer: If True, validate that the issuer of the
            token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the
            "Not Before" time in the token.

        :return: A tuple containing the list of PEM encoded X.509 certificate chains and an attestation token.
        :rtype: Tuple[list[list[string]], AttestationToken]

        .. admonition:: Example: Retrieving the set of policy management certificates
            for an isolated attestation instance.

            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [BEGIN get_policy_management_certificate]
                :end-before: [END get_policy_management_certificate]
                :language: python
                :dedent: 8
                :caption: Retrieving the policy management certificates.
        """

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        cert_response = await self._client.policy_certificates.get(**kwargs)
        token = AttestationToken(
            token=cert_response.token, body_type=GeneratedPolicyCertificatesResult
        )

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        certificates = []

        cert_list = token.get_body()

        for key in cert_list.policy_certificates.keys:
            key_certs = [pem_from_base64(cert, "CERTIFICATE") for cert in key.x5_c]
            certificates.append(key_certs)
        return certificates, token

    @distributed_trace_async
    async def add_policy_management_certificate(
        self, certificate_to_add: str, **kwargs: Any
    ) -> AttestationPolicyCertificateResult:
        """Adds a new policy management certificate to the set of policy management certificates for the instance.

        :param str certificate_to_add: PEM encoded X.509 certificate to add to
            the list of attestation policy management certificates.
        :keyword  str signing_key: PEM encoded signing Key representing the key
            associated with one of the *existing* attestation signing certificates.
        :keyword str signing_certificate: PEM encoded signing certificate which is one of
            the *existing* attestation signing certificates.
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

        :return: Attestation service response
            encapsulating the status of the add request.

        :rtype: azure.security.attestation.AttestationPolicyCertificateResult

        The :class:`AttestationPolicyCertificatesResult` response to the
        :meth:`add_policy_management_certificate` API contains two attributes
        of interest.

        The first is `certificate_resolution`, which indicates
        whether the certificate in question is present in the set of policy
        management certificates after the operation has completed, or if it is
        absent.

        The second is the `thumbprint` of the certificate added. The `thumbprint`
        for the certificate is the SHA1 hash of the DER encoding of the
        certificate.

        .. admonition:: Example: Generating and adding a new policy management
            certificates for an isolated attestation instance.

            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [BEGIN add_policy_management_certificate]
                :end-before: [END add_policy_management_certificate]
                :language: python
                :dedent: 0
                :caption: Adding a policy management certificate.

        """
        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            signing_key, signing_certificate = validate_signing_keys(
                signing_key, signing_certificate
            )
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        if not signing_key or not signing_certificate:
            raise ValueError(
                "A signing certificate and key must be provided to add_policy_management_certificate."
            )

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        certificate_to_add = load_pem_x509_certificate(
            certificate_to_add.encode("ascii")
        )

        jwk = JSONWebKey(
            kty="RSA",
            x5_c=[
                base64.b64encode(
                    certificate_to_add.public_bytes(serialization.Encoding.DER)
                ).decode("ascii")
            ],
        )
        add_body = AttestationCertificateManagementBody(policy_certificate=jwk)
        cert_add_token = AttestationToken(
            body=add_body,
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=AttestationCertificateManagementBody,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        cert_response = await self._client.policy_certificates.add(
            cert_add_token.to_jwt_string(), **kwargs
        )
        token = AttestationToken(
            token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult,
        )

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        return AttestationPolicyCertificateResult._from_generated(
            token.get_body(), token
        )

    @distributed_trace_async
    async def remove_policy_management_certificate(
        self, certificate_to_remove: str, **kwargs: Any
    ) -> AttestationPolicyCertificateResult:
        """Removes a policy management certificate from the set of policy management certificates for the instance.

        :param str certificate_to_remove: PEM encoded X.509 certificate to remove from
            the list of attestation policy management certificates.
        :keyword  str signing_key: PEM encoded signing Key representing the key
            associated with one of the *existing* attestation signing certificates.
        :keyword str signing_certificate: PEM encoded signing certificate which is one of
            the *existing* attestation signing certificates.
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
        :return: Result describing the outcome of the certificate removal.
        :rtype: ~azure.security.attestation.AttestationPolicyCertificateResult

        The :class:`AttestationPolicyCertificateResult` response to the
        :meth:`remove_policy_management_certificate` API contains two attributes
        of interest.

        The first is `certificate_resolution`, which indicates
        whether the certificate in question is present in the set of policy
        management certificates after the operation has completed, or if it is
        absent.

        The second is the `thumbprint` of the certificate added. The `thumbprint`
        for the certificate is the SHA1 hash of the DER encoding of the
        certificate.

        .. admonition:: Example: Removing an added policy management
            certificate for an isolated attestation instance.

            .. literalinclude:: ../samples/sample_get_set_policy_async.py
                :start-after: [BEGIN remove_policy_management_certificate]
                :end-before: [END remove_policy_management_certificate]
                :language: python
                :dedent: 8
                :caption: Removing a policy management certificate.

        """
        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            signing_key, signing_certificate = validate_signing_keys(
                signing_key, signing_certificate
            )
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        if not signing_key or not signing_certificate:
            raise ValueError(
                "A signing certificate and key must be provided to remove_policy_management_certificate."
            )

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        certificate_to_remove = load_pem_x509_certificate(
            certificate_to_remove.encode("ascii")
        )

        jwk = JSONWebKey(
            kty="RSA",
            x5_c=[
                base64.b64encode(
                    certificate_to_remove.public_bytes(serialization.Encoding.DER)
                ).decode("ascii")
            ],
        )
        add_body = AttestationCertificateManagementBody(policy_certificate=jwk)
        cert_add_token = AttestationToken(
            body=add_body,
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=AttestationCertificateManagementBody,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        cert_response = await self._client.policy_certificates.remove(
            cert_add_token.to_jwt_string(), **kwargs
        )
        token = AttestationToken(
            token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult,
        )

        if options.get("validate_token", True):
            token._validate_token(await self._get_signers(**kwargs), **options)
        return AttestationPolicyCertificateResult._from_generated(
            token.get_body(), token
        )

    async def _get_signers(self, **kwargs: Any) -> List[AttestationSigner]:
        """Returns the set of signing certificates used to sign attestation tokens."""

        with self._statelock:
            if self._signing_certificates == None:
                signing_certificates = await self._client.signing_certificates.get(
                    **kwargs
                )
                self._signing_certificates = []
                for key in signing_certificates.keys:
                    self._signing_certificates.append(
                        AttestationSigner._from_generated(key)
                    )
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
