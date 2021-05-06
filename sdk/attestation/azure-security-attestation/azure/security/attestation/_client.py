# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

from azure.core import PipelineClient
from msrest import Deserializer, Serializer

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpRequest, HttpResponse

from ._generated import AzureAttestationRestClient
from ._generated.models import AttestationResult, RuntimeData, InitTimeData, DataType, AttestSgxEnclaveRequest, AttestOpenEnclaveRequest
from ._configuration import AttestationClientConfiguration
from ._models import AttestationSigner, AttestationToken, AttestationResponse, AttestationData, TpmAttestationRequest, TpmAttestationResponse
import base64
import cryptography
import cryptography.x509
from typing import List, Any
from azure.core.tracing.decorator import distributed_trace
from threading import Lock


class AttestationClient(object):
    """An AttestationClient object enables access to the Attestation family of APIs provided
      by the attestation service.

    :param str base_url: base url of the service
    :param credential: An object which can provide secrets for the attestation service
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
        self._base_url = '{instance_url}'
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(credential, instance_url, **kwargs)
        self._client = AzureAttestationRestClient(credential, instance_url, **kwargs)
        self._statelock = Lock()
        self._signing_certificates = None

    @property
    def base_url(self):
        #type:()->str
        """ Returns the base URL configured for this instance of the AttestationClient.

        :returns str: The base URL for the client instance.
        """
        return self._base_url

    @distributed_trace
    def get_openidmetadata(self):
        """ Retrieves the OpenID metadata configuration document for this attestation instance.
        """
        return self._client.metadata_configuration.get()

    @distributed_trace
    def get_signing_certificates(self, **kwargs): 
        # type: (Any) ->List[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.

        :return List[AttestationSigner]: A list of :class:`AttestationSigner` objects.

        For additional request configuration options, please see https://aka.ms/azsdk/python/options.

        """
        signing_certificates = self._client.signing_certificates.get(**kwargs)
        signers = []
        for key in signing_certificates.keys:
            assert key.x5_c is not None

            # Convert the returned certificate chain into an array of X.509 Certificates.
            certificates = []
            for x5c in key.x5_c:
                der_cert = base64.b64decode(x5c)
                certificates.append(der_cert)
            signers.append(AttestationSigner(certificates, key.kid))
        return signers

    @distributed_trace
    def attest_sgx_enclave(self, quote, inittime_data=None, runtime_data=None, draft_policy=None, **kwargs):
        # type:(bytes, AttestationData, AttestationData, str, Any) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an SGX quote.

        :param bytes quote: An SGX quote generated from an Intel(tm) SGX enclave
        :param AttestationData inittime_data: Data presented at the time that the SGX enclave was initialized.
        :param AttestationData runtime_data: Data presented at the time that the SGX quote was created.
        :param str draft_policy: "draft", or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API.
        :return AttestationResponse[AttestationResult]: Attestation service response encapsulating an :class:`AttestationResult`.

        For additional request configuration options, please see https://aka.ms/azsdk/python/options.

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
        # type:(bytes, AttestationData, AttestationData, str, Any) -> AttestationResponse[AttestationResult]
        """ Attests the validity of an Open Enclave report.

        :param bytes report: An open_enclave report generated from an Intel(tm) SGX enclave
        :param AttestationData inittime_data: Data presented at the time that the SGX enclave was initialized.
        :param AttestationData runtime_data: Data presented at the time that the SGX quote was created.
        :param str draft_policy: "draft", or "experimental" policy to be used with
            this attestation request. If this parameter is provided, then this 
            policy document will be used for the attestation request.
            This allows a caller to test various policy documents against actual data
            before applying the policy document via the set_policy API.
        :return AttestationResponse[AttestationResult]: Attestation service response encapsulating an :class:`AttestationResult`.

        For additional request configuration options, please see https://aka.ms/azsdk/python/options.

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
    def attest_tpm(self, request):
        #type:(TpmAttestationRequest) -> TpmAttestationResponse
        """ Attest a TPM based enclave.

        See ..seealso:`https://docs.microsoft.com/en-us/azure/attestation/virtualization-based-security-protocol` for more information.

        :param bytes request: Incoming request to send to the TPM attestation service.
        :returns bytes: A structure containing the response from the TPM attestation.</returns>

        """
        response = self._client.attestation.attest_tpm(request.data)
        return TpmAttestationResponse(response.data)

    def _get_signers(self, **kwargs):
        # type:(Any) -> List[AttestationSigner]
        """ Returns the set of signing certificates used to sign attestation tokens.
        """

        with self._statelock:
            if (self._signing_certificates == None):
                signing_certificates = self._client.signing_certificates.get(**kwargs)
                self._signing_certificates = []
                for key in signing_certificates.keys:
                    # Convert the returned certificate chain into an array of X.509 Certificates.
                    certificates = []
                    for x5c in key.x5_c:
                        der_cert = base64.b64decode(x5c)
                        certificates.append(der_cert)
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
