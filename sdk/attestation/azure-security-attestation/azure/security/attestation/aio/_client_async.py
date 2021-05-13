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

from .._generated.aio._azure_attestation_rest_client import AzureAttestationRestClient
from .._configuration import AttestationClientConfiguration
from .._models import AttestationSigner
import base64
import cryptography
import cryptography.x509
from typing import List, Any
from azure.core.tracing.decorator_async import distributed_trace_async


class AttestationClient(object):
    """Describes the interface for the per-tenant enclave service.
    :param str base_url: base url of the service
    :param credential: An object which can provide secrets for the attestation service
    :type credential: azure.TokenCredentials or azure.AsyncTokenCredentials
    :keyword Pipeline pipeline: If omitted, the standard pipeline is used.
    :keyword HttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[HTTPPolicy] policies: If omitted, the standard pipeline is used.
    """

    def __init__(
        self,
        credential,  # type: "TokenCredential"
        instance_url,  # type: str
        **kwargs  # type: Any
    ):
        # type: (TokenCredential, str, **Any) -> None
        if not credential:
            raise ValueError("Missing credential.")
        self._config = AttestationClientConfiguration(credential, instance_url, **kwargs)
        self._client = AzureAttestationRestClient(credential, instance_url, **kwargs)

    @distributed_trace_async
    async def get_openidmetadata(self):
        """ Retrieves the OpenID metadata configuration document for this attestation instance.
        """
        return await self._client.metadata_configuration.get()

    @distributed_trace_async
    async def get_signing_certificates(self) -> List[AttestationSigner]:
        """ Returns the set of signing certificates used to sign attestation tokens.
        """
        signing_certificates = await self._client.signing_certificates.get()
        assert signing_certificates.keys is not None
        signers = []
        for key in signing_certificates.keys:
            assert key.x5_c is not None

            # Convert the returned certificate chain into an array of X.509 Certificates.
            certificates = [base64.b64decode(x5c) for x5c in key.x5_c]
            signers.append(AttestationSigner(certificates, key.kid))
        return signers

    async def close(self):
        # type: () -> None
        self._client.close()

    async def __aenter__(self):
        # type: () -> AttestationClient
        self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        # type: (Any) -> None
        self._client.__aexit__(*exc_details)
