# pylint: disable=line-too-long,useless-suppression,too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
import json
from typing import List, Any, Tuple, Union, Optional, Callable, cast


from threading import Lock
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.x509 import load_pem_x509_certificate, Certificate
from typing_extensions import Self

from azure.core.exceptions import raise_with_traceback  # pylint: disable=no-raise-with-traceback
from azure.core.tracing.decorator import distributed_trace
from azure.core.configuration import Configuration
from azure.core.credentials import TokenCredential
from azure.security.attestation.models import OpenIDConfigurationResponse


from ._client import AttestationClient as AzureAttestationRestClient
from .models import (  # pylint: disable=reimported
    AttestationResult as GeneratedAttestationResult,
    RuntimeData,
    InitTimeData,
    DataType,
    AttestSgxEnclaveRequest,
    AttestOpenEnclaveRequest,
    AttestationResult,
    TpmAttestationResult,
    PolicyResult as GeneratedPolicyResult,
    PolicyCertificatesResult as GeneratedPolicyCertificatesResult,
    JsonWebKey as JSONWebKey,
    AttestationCertificateManagementBody,
    StoredAttestationPolicy as GeneratedStoredAttestationPolicy,
    PolicyCertificatesModificationResult as GeneratedPolicyCertificatesModificationResult,
    AttestationPolicyResult,
    AttestationPolicyCertificateResult,
)

from .models._patch import (
    AttestationTokenValidationException,
    AttestationPolicyToken,
    AttestationSigner,
    AttestationToken,
)

from .models._enums import (
    AttestationType,
)

from ._common import pem_from_base64, validate_signing_keys, merge_validation_args, base64url_decode


class AttestationClient:
    # pylint: disable=protected-access
    """Provides access to the Attestation family of APIs for trusted environment attestation.

    :param str endpoint: The attestation instance base URI, for example https://mytenant.attest.azure.net.
    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials.TokenCredential`
    :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
    :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
        if the token is invalid, the `validation_callback` function should throw
        an exception.
    :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
    :keyword bool validate_signature: If True, validate the signature of the token being validated.
    :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
    :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
    :keyword float validation_slack: Slack time for validation - tolerance applied
        to help account for clock drift between the issuer and the current machine.
    :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
    :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
    :keyword str api_version: The API version to use for the request.

    .. tip::
        The `validate_token`, `validation_callback`, `validate_signature`,
        `validate_expiration`, `validate_not_before_time`, `validate_issuer`, and
        `issuer` keyword arguments are default values applied to each API call within
        the :py:class:`AttestationClient` class. These values can be
        overridden on individual API calls as needed.

    For additional client creation configuration options, please see `Python Request
    Options <https://aka.ms/azsdk/python/options>`_.

    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs) -> None:
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(**kwargs)
        self._client = AzureAttestationRestClient(endpoint, credential, **kwargs)
        self._statelock = Lock()
        self._signing_certificates: list[AttestationSigner] = []

    @distributed_trace
    def get_open_id_metadata(self, **kwargs: Any) -> OpenIDConfigurationResponse:
        """Retrieves the OpenID metadata configuration document for this attestation instance.

        The metadata configuration document is defined in the `OpenID Connect
        Discovery <https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfigurationResponse>`_
        specification.

        The attestation service currently returns the following fields:

        * issuer
        * jwks_uri
        * claims_supported

        :return: OpenID metadata configuration
        :rtype: Dict[str, Any]
        """
        return self._client.metadata_configuration.get(**kwargs)

    @distributed_trace
    def get_signing_certificates(self, **kwargs) -> List[AttestationSigner]:
        """Returns the set of signing certificates used to sign attestation tokens.

        :return: A list of :class:`azure.security.attestation.AttestationSigner` objects.

        :rtype: List[~azure.security.attestation.AttestationSigner]

        For additional request configuration options, please see `Python Request
        Options <https://aka.ms/azsdk/python/options>`_.

        """
        signing_certificates = self._client.signing_certificates.get(**kwargs)
        return [AttestationSigner._from_generated(key) for key in signing_certificates["keys"]]  # type: ignore

    @distributed_trace
    def attest_sgx_enclave(
        self,
        quote: bytes,
        *,
        inittime_data: Optional[bytes] = None,
        inittime_json: Optional[bytes] = None,
        runtime_data: Optional[bytes] = None,
        runtime_json: Optional[bytes] = None,
        draft_policy: Optional[str] = None,
        validate_token: Optional[bool] = None,
        validation_callback: Optional[Callable[["AttestationToken", "AttestationSigner"], None]] = None,
        validate_signature: Optional[bool] = None,
        validate_expiration: Optional[bool] = None,
        issuer: Optional[str] = None,
        validation_slack: Optional[float] = None,
        validate_issuer: Optional[bool] = None,
        validate_not_before_time: Optional[bool] = None,
        **kwargs
    ) -> Tuple[AttestationResult, AttestationToken]:
        """Attests the validity of an SGX quote.

        :param bytes quote: An SGX quote generated from an Intel(tm) SGX enclave
        :keyword bytes inittime_data: Data presented at the time that the SGX
            enclave was initialized.
        :keyword bytes inittime_json: Data presented at the time that the SGX
            enclave was initialized, JSON encoded.
        :keyword bytes runtime_data: Data presented at the time that the open_enclave
            report was created.
        :keyword bytes runtime_json: Data presented at the time that the open_enclave
            report was created. JSON Encoded.
        :keyword str draft_policy: "draft" or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.


        :return: :class:`AttestationResult` containing the claims in the returned attestation token.

        :rtype: Tuple[~azure.security.attestation.AttestationResult, ~azure.security.attestation.AttestationToken]

        .. note::
            Note that if the `draft_policy` parameter is provided, the resulting
            attestation token will be an unsecured attestation token.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_attest_enclave.py
                :start-after: [START attest_sgx_enclave_shared]
                :end-before: [END attest_sgx_enclave_shared]
                :language: python
                :dedent: 8
                :caption: Attesting an SGX Enclave

        For additional request configuration options, please see `Python Request
        Options <https://aka.ms/azsdk/python/options>`_.

        """

        # Handle explicit validation parameters
        validation_args = {
            "validate_token": validate_token,
            "validation_callback": validation_callback,
            "validate_signature": validate_signature,
            "validate_expiration": validate_expiration,
            "issuer": issuer,
            "validation_slack": validation_slack,
            "validate_issuer": validate_issuer,
            "validate_not_before_time": validate_not_before_time,
        }
        # Remove None values
        validation_args = {k: v for k, v in validation_args.items() if v is not None}
        # Add validation args to kwargs for merge_validation_args
        kwargs.update(validation_args)

        if inittime_json and inittime_data:
            raise ValueError("Cannot provide both inittime_json and inittime_data.")
        if runtime_json and runtime_data:
            raise ValueError("Cannot provide both runtime_data and runtime_json.")

        # If the input was JSON, make sure that it's valid JSON before sending it
        # to the service.
        if inittime_json:
            try:
                json.loads(inittime_json)
            except json.JSONDecodeError:
                raise_with_traceback(ValueError, "Content must be valid JSON.")

        if runtime_json:
            try:
                json.loads(runtime_json)
            except json.JSONDecodeError:
                raise_with_traceback(ValueError, "Content must be valid JSON.")

        runtime = None
        if runtime_data:
            runtime = RuntimeData(data=runtime_data, data_type=DataType.BINARY)

        if runtime_json:
            runtime = RuntimeData(data=runtime_json, data_type=DataType.JSON)

        inittime = None
        if inittime_data:
            inittime = InitTimeData(data=inittime_data, data_type=DataType.BINARY)
        if inittime_json:
            inittime = InitTimeData(data=inittime_data, data_type=DataType.JSON)

        request = AttestSgxEnclaveRequest(
            quote=quote,
            init_time_data=inittime,
            runtime_data=runtime,
            draft_policy_for_attestation=draft_policy,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        result = self._client.attestation.attest_sgx_enclave(request, **kwargs)
        token = AttestationToken(token=result.token, body_type=GeneratedAttestationResult)

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)

        return (
            AttestationResult._from_generated(token._get_body()),  # type: ignore
            token,
        )

    @distributed_trace
    def attest_open_enclave(
        self,
        report: bytes,
        *,
        inittime_data: Optional[bytes] = None,
        inittime_json: Optional[bytes] = None,
        runtime_data: Optional[bytes] = None,
        runtime_json: Optional[bytes] = None,
        draft_policy: Optional[str] = None,
        validate_token: Optional[bool] = None,
        validation_callback: Optional[Callable[["AttestationToken", "AttestationSigner"], None]] = None,
        validate_signature: Optional[bool] = None,
        validate_expiration: Optional[bool] = None,
        issuer: Optional[str] = None,
        validation_slack: Optional[float] = None,
        validate_issuer: Optional[bool] = None,
        validate_not_before_time: Optional[bool] = None,
        **kwargs
    ) -> Tuple[AttestationResult, AttestationToken]:
        """Attests the validity of an Open Enclave report.

        :param bytes report: An open_enclave report generated from an Intel(tm)
            SGX enclave
        :keyword bytes inittime_data: Data presented at the time that the SGX
            enclave was initialized.
        :keyword bytes inittime_json: Data presented at the time that the SGX
            enclave was initialized, JSON encoded.
        :keyword bytes runtime_data: Data presented at the time that the open_enclave
            report was created.
        :keyword bytes runtime_json: Data presented at the time that the open_enclave
            report was created. JSON Encoded.
        :keyword str draft_policy: "draft" or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API.
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[AttestationToken, AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: :class:`AttestationResult` containing the claims in the returned attestation token.

        :rtype: Tuple[~azure.security.attestation.AttestationResult, ~azure.security.attestation.AttestationToken]

        .. admonition:: Example: Simple OpenEnclave attestation.

            .. literalinclude:: ../samples/sample_attest_enclave.py
                :start-after: [START attest_open_enclave_shared]
                :end-before: [END attest_open_enclave_shared]
                :language: python
                :dedent: 8
                :caption: Attesting an open_enclave report for an SGX enclave.

        .. admonition:: Example: Simple OpenEnclave attestation with draft attestation policy.

            .. literalinclude:: ../samples/sample_attest_enclave.py
                :start-after: [START attest_open_enclave_shared_draft]
                :end-before: [END attest_open_enclave_shared_draft]
                :language: python
                :dedent: 8
                :caption: Attesting using a draft attestation policy.

        .. note::
            Note that if the `draft_policy` parameter is provided, the resulting
            attestation token will be an unsecured attestation token.

        For additional request configuration options, please see `Python Request
        Options <https://aka.ms/azsdk/python/options>`_.

        """

        # Handle explicit validation parameters
        validation_args = {
            "validate_token": validate_token,
            "validation_callback": validation_callback,
            "validate_signature": validate_signature,
            "validate_expiration": validate_expiration,
            "issuer": issuer,
            "validation_slack": validation_slack,
            "validate_issuer": validate_issuer,
            "validate_not_before_time": validate_not_before_time,
        }
        # Remove None values
        validation_args = {k: v for k, v in validation_args.items() if v is not None}
        # Add validation args to kwargs for merge_validation_args
        kwargs.update(validation_args)

        if inittime_json and inittime_data:
            raise ValueError("Cannot provide both inittime_json and inittime_data.")
        if runtime_json and runtime_data:
            raise ValueError("Cannot provide both runtime_data and runtime_json.")

        # If the input was JSON, make sure that it's valid JSON before sending it
        # to the service.
        if inittime_json:
            try:
                json.loads(inittime_json)
            except json.JSONDecodeError:
                raise_with_traceback(ValueError, "Content must be valid JSON.")

        if runtime_json:
            try:
                json.loads(runtime_json)
            except json.JSONDecodeError:
                raise_with_traceback(ValueError, "Content must be valid JSON.")

        # Now create the RuntimeData object to be sent to the service.
        runtime = None
        if runtime_data:
            runtime = RuntimeData(data=runtime_data, data_type=DataType.BINARY)

        if runtime_json:
            runtime = RuntimeData(data=runtime_json, data_type=DataType.JSON)

        # And the InitTimeData object to be sent to the service.
        inittime = None
        if inittime_data:
            inittime = InitTimeData(data=inittime_data, data_type=DataType.BINARY)
        if inittime_json:
            inittime = InitTimeData(data=inittime_data, data_type=DataType.JSON)

        request = AttestOpenEnclaveRequest(
            report=report,
            init_time_data=inittime,
            runtime_data=runtime,
            draft_policy_for_attestation=draft_policy,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        options = merge_validation_args(self._config._kwargs, kwargs)

        result = self._client.attestation.attest_open_enclave(request, **kwargs)
        token = AttestationToken(token=result.token, body_type=GeneratedAttestationResult)

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)
        return (AttestationResult._from_generated(token._get_body()), token)  # type: ignore

    @distributed_trace
    def attest_tpm(self, content: bytes, **kwargs) -> TpmAttestationResult:
        """Performs TPM attestation.

        :param bytes content: Attestation request for Trusted Platform Module (TPM) attestation.
        :returns: Attestation response for Trusted Platform Module (TPM) attestation.
        :rtype: ~azure.security.attestation.TpmAttestationResult
        """

        response = self._client.attestation.attest_tpm(data=content, **kwargs)
        # Handle response.data as either bytes or base64-encoded string
        data = response.data
        if isinstance(data, str):
            # If it's a base64-encoded string, decode it to bytes
            # Use base64url_decode for proper handling of URL-safe base64
            data = base64url_decode(data)
        result = TpmAttestationResult(cast(bytes, data))
        return result

    def _get_signers(self, **kwargs: Any) -> list[AttestationSigner]:
        """Returns the set of signing certificates used to sign attestation tokens.

        :return: A list of attestation signers used to validate tokens.
        :rtype: list[AttestationSigner]
        """

        with self._statelock:
            if not self._signing_certificates:
                signing_certificates = self._client.signing_certificates.get(**kwargs)
                self._signing_certificates = []
                for key in signing_certificates["keys"]:
                    # Convert the returned certificate chain into an array of X.509 Certificates.
                    self._signing_certificates.append(AttestationSigner._from_generated(key))  # type: ignore
            signers = self._signing_certificates
        return signers

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details) -> None:
        self._client.__exit__(*exc_details)


class AttestationAdministrationClient:
    # pylint: disable = line-too-long, protected-access
    """Provides administrative APIs for managing an instance of the Attestation Service.

    The :class:`~azure.security.attestation.AttestationAdministrationClient` object implements the policy
    management and policy certificate management functions.

    :param str endpoint: The attestation instance base URI, for example https://mytenant.attest.azure.net.
    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials.TokenCredential`
    :keyword str signing_key: PEM encoded signing key to be used for all
        operations.
    :keyword str signing_certificate: PEM encoded X.509 certificate to be used for all
        operations.
    :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
    :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
        if the token is invalid, the `validation_callback` function should throw
        an exception.
    :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
    :keyword bool validate_signature: If True, validate the signature of the token being validated.
    :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
    :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
    :keyword float validation_slack: Slack time for validation - tolerance applied
        to help account for clock drift between the issuer and the current machine.
    :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
    :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
    :keyword str api_version: The API version to use for the request.

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

    For additional client creation configuration options, please see `Python Request
    Options <https://aka.ms/azsdk/python/options>`_.

    """

    def __init__(self, endpoint: str, credential: TokenCredential, **kwargs: Any) -> None:
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(**kwargs)
        self._client = AzureAttestationRestClient(endpoint, credential, **kwargs)
        self._statelock = Lock()
        self._signing_certificates: list[AttestationSigner] = []

        self._signing_key = None
        self._signing_certificate = None

        signing_key = kwargs.pop("signing_key", None)
        signing_certificate = kwargs.pop("signing_certificate", None)
        if signing_key or signing_certificate:
            self._signing_key, self._signing_certificate = validate_signing_keys(signing_key, signing_certificate)

    @distributed_trace
    def get_policy(
        self,
        attestation_type: Union[str, AttestationType],
        *,
        validation_slack: float = 0.5,
        validate_signature: bool = True,
        validate_issuer: bool = True,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        validate_expiration: bool = True,
        issuer: Optional[str] = None,
        validate_token: bool = True,
        validate_not_before_time: bool = True,
        **kwargs: Any
    ) -> Tuple[str, AttestationToken]:
        """Retrieves the attestation policy for a specified attestation type.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for
            which to retrieve the policy.
        :type attestation_type: Union[str, ~azure.security.attestation.AttestationType]
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: A tuple containing the attestation policy and the token returned
            by the service..

        :rtype: Tuple[str, ~azure.security.attestation.AttestationToken]

        :raises ~azure.security.attestation.AttestationTokenValidationException: Raised
            when an attestation token is invalid.

        .. note::
            The Azure Attestation Policy language is defined `here
            <https://docs.microsoft.com/azure/attestation/author-sign-policy>`_

        .. admonition:: Example: Retrieving the current policy on an attestation instance.

            .. literalinclude:: ../samples/sample_get_set_policy.py
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
        validation_args = {
            "validation_slack": validation_slack,
            "validate_signature": validate_signature,
            "validate_issuer": validate_issuer,
            "validation_callback": validation_callback,
            "validate_expiration": validate_expiration,
            "issuer": issuer,
            "validate_token": validate_token,
            "validate_not_before_time": validate_not_before_time,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        policyResult = self._client.policy.get(attestation_type, **kwargs)
        token = AttestationToken(token=policyResult.token, body_type=GeneratedPolicyResult)
        token_body = token._get_body()
        stored_policy = AttestationToken(token=token_body.policy, body_type=GeneratedStoredAttestationPolicy)

        policy_body = stored_policy._get_body()
        actual_policy = policy_body.attestation_policy if policy_body else "".encode("ascii")  # type: bytes

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)

        if isinstance(actual_policy, bytes):
            return actual_policy.decode("utf-8"), token

        return actual_policy, token

    @distributed_trace
    def set_policy(
        self,
        attestation_type: Union[str, AttestationType],
        attestation_policy: str,
        *,
        validation_slack: float = 0.5,
        validate_not_before_time: bool = True,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        issuer: Optional[str] = None,
        signing_key: Optional[Union[str, RSAPrivateKey, EllipticCurvePrivateKey]] = None,
        signing_certificate: Optional[Union[str, Certificate]] = None,
        validate_issuer: bool = True,
        validate_signature: bool = True,
        validate_token: bool = True,
        validate_expiration: bool = True,
        **kwargs: Any
    ) -> Tuple[AttestationPolicyResult, AttestationToken]:
        """Sets the attestation policy for the specified attestation type.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for
            which to set the policy.
        :type attestation_type: Union[str, ~azure.security.attestation.AttestationType]
        :param str attestation_policy: Attestation policy to be set.
        :keyword str signing_key: PEM encoded signing key to be used to sign the policy
            before sending it to the service.
        :keyword str signing_certificate: PEM encoded X.509 certificate to be sent to the
            service along with the policy.
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: Result of set policy operation.

        :rtype: Tuple[~azure.security.attestation.AttestationPolicyResult, ~azure.security.attestation.AttestationToken]

        :raises ~azure.security.attestation.AttestationTokenValidationException: Raised
            when an attestation token is invalid.

        .. admonition:: Example: Setting the attestation policy on an AAD mode
            attestation instance (no signing key required).

            .. literalinclude:: ../samples/sample_get_set_policy.py
                :start-after: [BEGIN set_policy_unsecured]
                :end-before: [END set_policy_unsecured]
                :language: python
                :dedent: 0
                :caption: Setting a security policy without a signing key.

        .. admonition:: Example: Setting the attestation policy and verifying
            that the policy was received by the service.

            .. literalinclude:: ../samples/sample_get_set_policy.py
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

        # If the caller provided a signing key and certificate, validate that,
        # otherwise use the default values from the service.

        # Note that the signing_key and signing_certificate argument to AttestationToken
        # is polymorphic - it can be either a PEM encoded string or a cryptography
        # object. The self._signing_key and self._signing_certificate are cryptography
        # objects, the keyword arguments are strings. The AttestationToken knows
        # how to tease these two apart.
        if not signing_key:
            signing_key = self._signing_key
        if not signing_certificate:
            signing_certificate = self._signing_certificate

        policy_token = AttestationToken(
            body=GeneratedStoredAttestationPolicy(attestation_policy=attestation_policy.encode("ascii")),
            signing_key=signing_key,
            signing_certificate=signing_certificate,
            body_type=GeneratedStoredAttestationPolicy,
        )

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        validation_args = {
            "validation_slack": validation_slack,
            "validate_not_before_time": validate_not_before_time,
            "validation_callback": validation_callback,
            "issuer": issuer,
            "validate_issuer": validate_issuer,
            "validate_signature": validate_signature,
            "validate_token": validate_token,
            "validate_expiration": validate_expiration,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        policyResult = self._client.policy.set(
            attestation_type=attestation_type, new_attestation_policy=policy_token.to_jwt_string(), **kwargs
        )
        token = AttestationToken(token=policyResult.token, body_type=GeneratedPolicyResult)

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)

        return (
            AttestationPolicyResult._from_generated(token._get_body()),  # type: ignore
            token,
        )

    @distributed_trace
    def reset_policy(
        self,
        attestation_type: Union[str, AttestationType],
        *,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        validate_issuer: bool = True,
        validate_token: bool = True,
        validation_slack: float = 0.5,
        signing_key: Optional[str] = None,
        signing_certificate: Optional[str] = None,
        issuer: Optional[str] = None,
        validate_signature: bool = True,
        validate_not_before_time: bool = True,
        validate_expiration: bool = True,
        **kwargs: Any
    ) -> Tuple[AttestationPolicyResult, AttestationToken]:
        """Resets the attestation policy for the specified attestation type to the default value.

        :param attestation_type: :class:`azure.security.attestation.AttestationType` for
            which to set the policy.
        :type attestation_type: Union[str, ~azure.security.attestation.AttestationType]
        :keyword str signing_key: PEM encoded signing key to be used to sign the policy
            before sending it to the service.
        :keyword str signing_certificate: PEM encoded X.509 certificate to be sent to the
            service along with the policy.
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: A policy set result reflecting the outcome of the policy removal and
            the token which contained the result.

        :rtype: Tuple[~azure.security.attestation.AttestationPolicyResult, ~azure.security.attestation.AttestationToken]

        :raises ~azure.security.attestation.AttestationTokenValidationException: Raised
            when an attestation token is invalid.

        .. note::
            If the attestation instance is in *Isolated* mode, then the
            `signing_key` parameter MUST be a signing key containing one of the
            certificates returned by :meth:`get_policy_management_certificates`.

            If the attestation instance is in *AAD* mode, then the `signing_key`
            parameter does not need to be provided.

        .. admonition:: Example: Resetting the attestation policy on an AAD mode
            attestation instance (no signing key required).

            .. literalinclude:: ../samples/sample_get_set_policy.py
                :start-after: [BEGIN reset_aad_policy]
                :end-before: [END reset_aad_policy]
                :language: python
                :dedent: 8
                :caption: Resetting an AAD mode attestation instance.

        .. admonition:: Example: Resetting the attestation policy on an Isolated mode
            attestation instance (signing key required).

            .. literalinclude:: ../samples/sample_get_set_policy.py
                :start-after: [BEGIN reset_isolated_policy]
                :end-before: [END reset_isolated_policy]
                :language: python
                :dedent: 8
                :caption: Resetting an AAD mode attestation instance.

        """

        # If the caller provided a signing key and certificate, validate that,
        # otherwise use the default values from the service.
        if not signing_key:
            signing_key = self._signing_key  # type: ignore
        if not signing_certificate:
            signing_certificate = self._signing_certificate  # type: ignore

        policy_token = AttestationToken(body=None, signing_key=signing_key, signing_certificate=signing_certificate)

        # Merge our existing config options with the options for this API call.
        # Note that this must be done before calling into the implementation
        # layer because the implementation layer doesn't like keyword args that
        # it doesn't expect :(.
        validation_args = {
            "validation_callback": validation_callback,
            "validate_issuer": validate_issuer,
            "validate_token": validate_token,
            "validation_slack": validation_slack,
            "issuer": issuer,
            "validate_signature": validate_signature,
            "validate_not_before_time": validate_not_before_time,
            "validate_expiration": validate_expiration,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        policyResult = self._client.policy.reset(
            attestation_type=attestation_type, policy_jws=policy_token.to_jwt_string(), **kwargs
        )
        token = AttestationToken(token=policyResult.token, body_type=GeneratedPolicyResult)

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)

        return (AttestationPolicyResult._from_generated(token._get_body()), token)  # type: ignore

    @distributed_trace
    def get_policy_management_certificates(
        self,
        *,
        validate_issuer: bool = True,
        validate_token: bool = True,
        validate_expiration: bool = True,
        validate_not_before_time: bool = True,
        issuer: Optional[str] = None,
        validation_slack: float = 0.5,
        validate_signature: bool = True,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        **kwargs: Any
    ) -> Tuple[List[List[str]], AttestationToken]:
        """Retrieves the set of policy management certificates for the instance.

        The list of policy management certificates will only have values if the
        attestation service instance is in Isolated mode.

        :keyword bool validate_token: If True, validate the token, otherwise
            return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to
            perform custom validation of the token. If the token is invalid,
            the `validation_callback` function should throw an exception to cause
            the API call to fail.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the
            token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time
            of the token being validated.
        :keyword float validation_slack: Slack time for validation - tolerance
            applied to help account for clock drift between the issuer and
            the current machine.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword bool validate_issuer: If True, validate that the issuer of the
            token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the
            "Not Before" time in the token.

        :return: A tuple containing the list of PEM encoded X.509 certificate chains and an attestation token.
        :rtype: Tuple[List[List[str]], ~azure.security.attestation.AttestationToken]

        .. admonition:: Example: Retrieving the set of policy management certificates
            for an isolated attestation instance.

            .. literalinclude:: ../samples/sample_get_set_policy.py
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
        validation_args = {
            "validate_issuer": validate_issuer,
            "validate_token": validate_token,
            "validate_expiration": validate_expiration,
            "validate_not_before_time": validate_not_before_time,
            "issuer": issuer,
            "validation_slack": validation_slack,
            "validate_signature": validate_signature,
            "validation_callback": validation_callback,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        cert_response = self._client.policy_certificates.get(**kwargs)
        token = AttestationToken(token=cert_response.token, body_type=GeneratedPolicyCertificatesResult)

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)
        certificates = []

        cert_list = token._get_body()

        for key in cert_list.policy_certificates["keys"]:
            key_certs = [pem_from_base64(cert, "CERTIFICATE") for cert in key.x5_c]
            certificates.append(key_certs)
        return certificates, token

    @distributed_trace
    def add_policy_management_certificate(
        self,
        certificate_to_add: str,
        *,
        signing_certificate: Optional[str] = None,
        validate_signature: bool = True,
        validate_expiration: bool = True,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        validation_slack: float = 0.5,
        validate_not_before_time: bool = True,
        validate_issuer: bool = True,
        signing_key: Optional[str] = None,
        issuer: Optional[str] = None,
        validate_token: bool = True,
        **kwargs: Any
    ) -> Tuple[AttestationPolicyCertificateResult, AttestationToken]:
        """Adds a new policy management certificate to the set of policy management certificates for the instance.

        :param str certificate_to_add: Required. PEM encoded X.509 certificate to add to
            the list of attestation policy management certificates.
        :keyword str signing_key: PEM encoded signing Key representing the key
            associated with one of the *existing* attestation signing certificates.
        :keyword str signing_certificate: PEM encoded signing certificate which is one of
            the *existing* attestation signing certificates.
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.

        :return: AttestationPolicyCertificateResult object describing the status
            of the add request and the token sent from the service which
            contained the response.

        :rtype: Tuple[~azure.security.attestation.AttestationPolicyCertificateResult, ~azure.security.attestation.AttestationToken]

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

            .. literalinclude:: ../samples/sample_get_set_policy.py
                :start-after: [BEGIN add_policy_management_certificate]
                :end-before: [END add_policy_management_certificate]
                :language: python
                :dedent: 12
                :caption: Adding a policy management certificate.

        """

        if not signing_key:
            signing_key = self._signing_key  # type: ignore
        if not signing_certificate:
            signing_certificate = self._signing_certificate  # type: ignore

        if not signing_key or not signing_certificate:
            raise ValueError("A signing certificate and key must be provided to add_policy_management_certificate.")

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        parsed_certificate = load_pem_x509_certificate(certificate_to_add.encode("ascii"))

        jwk = JSONWebKey(
            kty="RSA",
            x5_c=[base64.b64encode(parsed_certificate.public_bytes(serialization.Encoding.DER)).decode("ascii")],
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
        validation_args = {
            "validate_signature": validate_signature,
            "validate_expiration": validate_expiration,
            "validation_callback": validation_callback,
            "validation_slack": validation_slack,
            "validate_not_before_time": validate_not_before_time,
            "validate_issuer": validate_issuer,
            "issuer": issuer,
            "validate_token": validate_token,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        cert_response = self._client.policy_certificates.add(cert_add_token.to_jwt_string(), **kwargs)  # type: ignore
        token = AttestationToken(
            token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult,
        )

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)
        return (
            AttestationPolicyCertificateResult._from_generated(token._get_body()),  # type: ignore
            token,
        )

    @distributed_trace
    def remove_policy_management_certificate(
        self,
        certificate_to_remove: str,
        *,
        signing_key: Optional[str] = None,
        validate_token: bool = True,
        issuer: Optional[str] = None,
        signing_certificate: Optional[str] = None,
        validate_issuer: bool = True,
        validation_callback: Optional[Callable[[AttestationToken, AttestationSigner], None]] = None,
        validation_slack: float = 0.5,
        validate_signature: bool = True,
        validate_not_before_time: bool = True,
        validate_expiration: bool = True,
        **kwargs: Any
    ) -> Tuple[AttestationPolicyCertificateResult, AttestationToken]:
        """Removes a policy management certificate from the set of policy management certificates for the instance.

        :param str certificate_to_remove: Required. PEM encoded X.509 certificate to remove from
            the list of attestation policy management certificates.
        :keyword str signing_key: PEM encoded signing Key representing the key
            associated with one of the *existing* attestation signing certificates.
        :keyword str signing_certificate: PEM encoded signing certificate which is one of
            the *existing* attestation signing certificates.
        :keyword bool validate_token: If True, validate the token, otherwise return the token unvalidated.
        :keyword validation_callback: Function callback to allow clients to perform custom validation of the token.
            if the token is invalid, the `validation_callback` function should throw
            an exception.
        :paramtype validation_callback: ~typing.Callable[[~azure.security.attestation.AttestationToken, ~azure.security.attestation.AttestationSigner], None]
        :keyword bool validate_signature: If True, validate the signature of the token being validated.
        :keyword bool validate_expiration: If True, validate the expiration time of the token being validated.
        :keyword str issuer: Expected issuer, used if `validate_issuer` is true.
        :keyword float validation_slack: Slack time for validation - tolerance applied
            to help account for clock drift between the issuer and the current machine.
        :keyword bool validate_issuer: If True, validate that the issuer of the token matches the expected issuer.
        :keyword bool validate_not_before_time: If true, validate the "Not Before" time in the token.
        :return: Result describing the outcome of the certificate removal.
        :rtype: Tuple[~azure.security.attestation.AttestationPolicyCertificateResult, ~azure.security.attestation.AttestationToken]

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

            .. literalinclude:: ../samples/sample_get_set_policy.py
                :start-after: [BEGIN remove_policy_management_certificate]
                :end-before: [END remove_policy_management_certificate]
                :language: python
                :dedent: 8
                :caption: Removing a policy management certificate.

        """

        if not signing_key:
            signing_key = self._signing_key  # type: ignore
        if not signing_certificate:
            signing_certificate = self._signing_certificate  # type: ignore

        if not signing_key or not signing_certificate:
            raise ValueError("A signing certificate and key must be provided to remove_policy_management_certificate.")

        # Verify that the provided certificate is a valid PEM encoded X.509 certificate
        parsed_certificate = load_pem_x509_certificate(certificate_to_remove.encode("ascii"))

        jwk = JSONWebKey(
            kty="RSA",
            x5_c=[base64.b64encode(parsed_certificate.public_bytes(serialization.Encoding.DER)).decode("ascii")],
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
        validation_args = {
            "validate_token": validate_token,
            "issuer": issuer,
            "validate_issuer": validate_issuer,
            "validation_callback": validation_callback,
            "validation_slack": validation_slack,
            "validate_signature": validate_signature,
            "validate_not_before_time": validate_not_before_time,
            "validate_expiration": validate_expiration,
        }
        # Merge validation_args with kwargs to include any additional parameters
        validation_args.update(kwargs)
        options = merge_validation_args(self._config._kwargs, validation_args)

        cert_response = self._client.policy_certificates.remove(cert_add_token.to_jwt_string(), **kwargs)  # type: ignore
        token = AttestationToken(
            token=cert_response.token,
            body_type=GeneratedPolicyCertificatesModificationResult,
        )

        if options.get("validate_token", True):
            token._validate_token(self._get_signers(**kwargs), **options)
        return (
            AttestationPolicyCertificateResult._from_generated(token._get_body()),  # type: ignore
            token,
        )

    def _get_signers(self, **kwargs: Any) -> List[AttestationSigner]:
        """Returns the set of signing certificates used to sign attestation tokens.

        :return: A list of attestation signers used to validate tokens.
        :rtype: List[AttestationSigner]
        """

        with self._statelock:
            if not self._signing_certificates:
                signing_certificates = self._client.signing_certificates.get(**kwargs)
                self._signing_certificates = []
                for key in signing_certificates["keys"]:
                    # Convert the returned certificate chain into an array of X.509 Certificates.
                    self._signing_certificates.append(AttestationSigner._from_generated(key))  # type: ignore
            signers: list[AttestationSigner] = self._signing_certificates
        return signers

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details) -> None:
        self._client.__exit__(*exc_details)


class AttestationClientConfiguration(Configuration):
    """Configuration for AttestationClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

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
    """

    def __init__(self, **kwargs: Any) -> None:
        super(AttestationClientConfiguration, self).__init__(**kwargs)  # pylint: disable=super-with-arguments

        self._kwargs = kwargs.copy()


__all__: List[str] = [
    "AttestationClient",
    "AttestationAdministrationClient",
    "AttestationSigner",
    "AttestationToken",
    "AttestationTokenValidationException",
    "AttestationPolicyToken",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
