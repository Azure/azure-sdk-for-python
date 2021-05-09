# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import List, Any, Optional, TYPE_CHECKING

from azure.core import PipelineClient
from msrest import Deserializer, Serializer

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpRequest, HttpResponse

from ._generated import AzureAttestationRestClient
from ._generated.models import (
    AttestationResult,
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
    AttestationData,
    TpmAttestationRequest,
    TpmAttestationResponse)
import base64
import cryptography.x509
from azure.core.tracing.decorator import distributed_trace
from threading import Lock


class AttestationClient(object):
    """An AttestationClient object enables access to the Attestation family of APIs provided
      by the attestation service.

    :param str base_url: base url of the service
    :param credential: Credentials for the caller used to interact with the service.
    :type credential: ~azure.core.credentials.TokenCredentials
    :keyword Pipeline pipeline: If omitted, the standard pipeline is used.
    :keyword HttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[HTTPPolicy] policies: If omitted, the standard pipeline is used.

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
    def get_openidmetadata(self):
        #type:()->Any
        """ Retrieves the OpenID metadata configuration document for this attestation instance.
        """
        return self._client.metadata_configuration.get()

    @distributed_trace
    def get_signing_certificates(self, **kwargs): 
        # type: (Any) ->list[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.

        :return list[AttestationSigner]: A list of :class:`AttestationSigner` objects.

        For additional request configuration options, please see `Python Request Options <https://aka.ms/azsdk/python/options>`_.

        """
        signing_certificates = self._client.signing_certificates.get(**kwargs)
        signers = []
        for key in signing_certificates.keys:
            # Convert the returned certificate chain into an array of X.509 Certificates.
            certificates = [base64.b64decode(x5c) for x5c in key.x5_c]
            signers.append(AttestationSigner(certificates, key.kid))
        return signers

    @distributed_trace
    def attest_sgx_enclave(self, quote, inittime_data=None, runtime_data=None, draft_policy=None, **kwargs):
        # type:(bytes, Optional[AttestationData], Optional[AttestationData], Optional[str], Any) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an SGX quote.

        :param bytes quote: An SGX quote generated from an Intel(tm) SGX enclave
        :param Optional[AttestationData] inittime_data: Data presented at the time that the SGX enclave was initialized.
        :param Optional[AttestationData] runtime_data: Data presented at the time that the SGX quote was created.
        :param Optional[str] draft_policy: "draft", or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API

        :return AttestationResponse[AttestationResult]: Attestation service response encapsulating an :class:`AttestationResult`.

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

        request = AttestSgxEnclaveRequest(
            quote=quote,
            init_time_data = inittime,
            runtime_data = runtime,
            draft_policy_for_attestation=draft_policy)
        result = self._client.attestation.attest_sgx_enclave(request, **kwargs)
        token = AttestationToken[AttestationResult](token=result.token,
            body_type=AttestationResult)
        token.validate_token(self._config.token_validation_options, self._get_signers(**kwargs))
        return AttestationResponse[AttestationResult](token, token.get_body())

    @distributed_trace
    def attest_open_enclave(self, report, inittime_data=None, runtime_data=None, draft_policy=None, **kwargs):
        # type:(bytes, Optional[AttestationData], Optional[AttestationData], Optional[str], Any) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an Open Enclave report.

        :param bytes report: An open_enclave report generated from an Intel(tm) SGX enclave
        :param Optional[AttestationData] inittime_data: Data presented at the time that the SGX enclave was initialized.
        :param Optional[AttestationData] runtime_data: Data presented at the time that the SGX quote was created.
        :param Optional[str] draft_policy: "draft", or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API.
        :return AttestationResponse[AttestationResult]: Attestation service response encapsulating an :class:`AttestationResult`.

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
            draft_policy_for_attestation = draft_policy)
        result = self._client.attestation.attest_open_enclave(request, **kwargs)
        token = AttestationToken[AttestationResult](token=result.token,
            body_type=AttestationResult)
        token.validate_token(self._config.token_validation_options, self._get_signers(**kwargs))
        return AttestationResponse[AttestationResult](token, token.get_body())

    @distributed_trace
    def attest_tpm(self, request, **kwargs):
        #type:(TpmAttestationRequest, **Any) -> TpmAttestationResponse
        """ Attest a TPM based enclave.

        See the `TPM Attestation Protocol Reference <https://docs.microsoft.com/en-us/azure/attestation/virtualization-based-security-protocol>`_ for more information.

        :param TpmAttestationRequest request: Incoming request to send to the TPM attestation service.
        :returns TpmAttestationResponse: A structure containing the response from the TPM attestation.

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
                    certificates = [base64.b64decode(x5c) for x5c in key.x5_c]
                    self._signing_certificates.append(AttestationSigner(certificates, key.kid))
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
