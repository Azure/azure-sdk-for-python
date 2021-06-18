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

    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpRequest, HttpResponse

from ._generated import AzureAttestationRestClient
from ._generated.models import (
    AttestationResult as GeneratedAttestationResult,
    RuntimeData,
    InitTimeData,
    DataType,
    AttestSgxEnclaveRequest,
    AttestOpenEnclaveRequest)
from ._configuration import AttestationClientConfiguration
from ._models import (
    AttestationSigner,
    AttestationToken,
    AttestationResponse,
    AttestationResult,
    AttestationData,
    TpmAttestationRequest,
    TpmAttestationResponse)
import base64
from azure.core.tracing.decorator import distributed_trace
from threading import Lock


class AttestationClient(object):
    """An AttestationClient object enables access to the Attestation family of APIs provided
      by the attestation service.

    :param str instance_url: base url of the service
    :param credential: Credentials for the caller used to interact with the service.
    :type credential: :class:`~azure.core.credentials.TokenCredential`
    :keyword pipeline: If omitted, the standard pipeline is used.
    :paramtype pipeline: Pipeline
    :keyword policies: If omitted, the standard pipeline is used.
    :paramtype policies: list[HTTPPolicy]
    :keyword HttpTransport transport: If omitted, the standard pipeline is used.
    :paramtype transport: HttpTransport

    For additional client creation configuration options, please see https://aka.ms/azsdk/python/options.

    """

    def __init__(
        self,
        credential,  # type: "TokenCredential"
        instance_url,  # type: str
        **kwargs  # type: Any
    ):
        # type: (TokenCredential, str, Any) -> None

        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(credential, instance_url, **kwargs)
        self._client = AzureAttestationRestClient(credential, instance_url, **kwargs)
        self._statelock = Lock()
        self._signing_certificates = None

    @distributed_trace
    def get_openidmetadata(self, **kwargs):
        #type:(Dict[str, Any]) -> Any
        """ Retrieves the OpenID metadata configuration document for this attestation instance.

        :return: OpenID metadata configuration
        :rtype: Any
        """
        return self._client.metadata_configuration.get(**kwargs)

    @distributed_trace
    def get_signing_certificates(self, **kwargs): 
        # type: (Any) -> list[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.

        :return: A list of :class:`azure.security.attestation.AttestationSigner` objects.

        :rtype: list[azure.security.attestation.AttestationSigner]

        For additional request configuration options, please see `Python Request Options <https://aka.ms/azsdk/python/options>`_.

        """
        signing_certificates = self._client.signing_certificates.get(**kwargs)
        signers = []
        for key in signing_certificates.keys:
            # Convert the returned certificate chain into an array of X.509 Certificates.
            signers.append(AttestationSigner._from_generated(key))
        return signers

    @distributed_trace
    def attest_sgx_enclave(self, quote, inittime_data=None, runtime_data=None, **kwargs):
        # type:(bytes, AttestationData, AttestationData, Dict[str, Any]) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an SGX quote.

        :param bytes quote: An SGX quote generated from an Intel(tm) SGX enclave
        :param inittime_data: Data presented at the time that the SGX enclave was initialized.
        :type inittime_data: azure.security.attestation.AttestationData 
        :param runtime_data: Data presented at the time that the SGX quote was created.
        :type runtime_data: azure.security.attestation.AttestationData
        :keyword draft_policy: "draft" or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API

        :paramtype draft_policy: str

        :return: Attestation service response encapsulating an :class:`AttestationResult`.
        
        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.AttestationResult]

        .. note::
            Note that if the `draft_policy` parameter is provided, the resulting attestation token will be an unsecured attestation token.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_attest_enclave.py
                :start-after: [START attest_sgx_enclave_shared]
                :end-before: [END attest_sgx_enclave_shared]
                :language: python
                :dedent: 8
                :caption: Attesting an SGX Enclave

        For additional request configuration options, please see `Python Request Options <https://aka.ms/azsdk/python/options>`_.

        """
        runtime = None
        if runtime_data:
            runtime = RuntimeData(data=runtime_data._data, data_type=DataType.JSON if runtime_data._is_json else DataType.BINARY)

        inittime = None
        if inittime_data:
            inittime = InitTimeData(data=inittime_data._data, data_type=DataType.JSON if inittime_data._is_json else DataType.BINARY)

        request = AttestSgxEnclaveRequest(
            quote=quote,
            init_time_data = inittime,
            runtime_data = runtime,
            draft_policy_for_attestation=kwargs.pop('draft_policy', None))

        result = self._client.attestation.attest_sgx_enclave(request, **kwargs)
        token = AttestationToken[GeneratedAttestationResult](token=result.token,
            body_type=GeneratedAttestationResult)
        token.validate_token(self._config.token_validation_options, self._get_signers(**kwargs))
        return AttestationResponse[AttestationResult](token, AttestationResult._from_generated(token.get_body()))

    @distributed_trace
    def attest_open_enclave(self, report, inittime_data=None, runtime_data=None, **kwargs):
        # type:(bytes, AttestationData, AttestationData, Dict[str, Any]) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an Open Enclave report.

        :param bytes report: An open_enclave report generated from an Intel(tm) SGX enclave
        :param inittime_data: Data presented at the time that the SGX enclave was initialized.
        :type inittime_data: azure.security.attestation.AttestationData 
        :param runtime_data: Data presented at the time that the open_enclave report was created.
        :type runtime_data: azure.security.attestation.AttestationData 
        :keyword draft_policy: "draft" or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API.

        :paramtype draft_policy: str

        :return: Attestation service response encapsulating an :class:`AttestationResult`.

        :rtype: azure.security.attestation.AttestationResponse[azure.security.attestation.AttestationResult]

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
            Note that if the `draft_policy` parameter is provided, the resulting attestation token will be an unsecured attestation token.

        For additional request configuration options, please see `Python Request Options <https://aka.ms/azsdk/python/options>`_.

        """

        runtime = None
        if runtime_data:
            runtime = RuntimeData(data=runtime_data._data, data_type=DataType.JSON if runtime_data._is_json else DataType.BINARY)

        inittime = None
        if inittime_data:
            inittime = InitTimeData(data=inittime_data._data, data_type=DataType.JSON if inittime_data._is_json else DataType.BINARY)
        request = AttestOpenEnclaveRequest(
            report=report,
            init_time_data = inittime,
            runtime_data = runtime,
            draft_policy_for_attestation = kwargs.pop('draft_policy', None))
        result = self._client.attestation.attest_open_enclave(request, **kwargs)
        token = AttestationToken[GeneratedAttestationResult](token=result.token,
            body_type=GeneratedAttestationResult)
        token.validate_token(self._config.token_validation_options, self._get_signers(**kwargs))
        return AttestationResponse[AttestationResult](token, AttestationResult._from_generated(token.get_body()))

    @distributed_trace
    def attest_tpm(self, request, **kwargs):
        #type:(TpmAttestationRequest, **Any) -> TpmAttestationResponse
        """ Attest a TPM based enclave.

        See the `TPM Attestation Protocol Reference <https://docs.microsoft.com/en-us/azure/attestation/virtualization-based-security-protocol>`_ for more information.

        :param request: Incoming request to send to the TPM attestation service.
        :type request: azure.security.attestation.TpmAttestationRequest
        :returns: A structure containing the response from the TPM attestation.
        :rtype: azure.security.attestation.TpmAttestationResponse
        """
        response = self._client.attestation.attest_tpm(request.data, **kwargs)
        return TpmAttestationResponse(response.data)

    def _get_signers(self, **kwargs):
        # type:(Any) -> list[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.
        """

        with self._statelock:
            if self._signing_certificates is None:
                signing_certificates = self._client.signing_certificates.get(**kwargs)
                self._signing_certificates = []
                for key in signing_certificates.keys:
                    # Convert the returned certificate chain into an array of X.509 Certificates.
                    self._signing_certificates.append(AttestationSigner._from_generated(key))
            signers = self._signing_certificates
        return signers

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> AttestationClient
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._client.__exit__(*exc_details)
